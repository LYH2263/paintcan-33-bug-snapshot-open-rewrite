import pytest
from fastapi.testclient import TestClient

from app import db as db_mod
from app import seed
from app.services.paint_service import PaintService


@pytest.fixture()
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db_mod, "DB_PATH", tmp_path / "app.db")
    seed.init_db()
    with PaintService() as s:
        yield s


def run_count(s):
    return int(s._c.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"])


def test_persist_snapshot_fields(svc):
    r = svc.estimate(1, True)
    assert r["run_id"] is not None
    d = svc.run_detail(r["run_id"])
    res = d["result"]
    assert res["net_m2"] == 46.41
    assert res["openings_m2"] == 3.99
    assert res["liters"] == 11.6
    assert res["coverage"] == 8.0
    assert res["coats"] == 2


def test_snapshot_frozen_after_room_change(svc):
    first = svc.estimate(1, True)
    old_id = first["run_id"]
    before = svc.run_detail(old_id)["result"]

    # 写入后改层高并增加一扇门
    svc._c.execute("UPDATE rooms SET height=3.2 WHERE id=1")
    svc._c.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (1,'door',1.0,1.0)")
    svc._c.commit()

    # 旧编号仍是写入时的净面积与升数
    again = svc.run_detail(old_id)["result"]
    assert again["net_m2"] == before["net_m2"] == 46.41
    assert again["liters"] == before["liters"] == 11.6

    # 当场再估才反映新参数，且只追加新编号，不覆盖旧编号
    second = svc.estimate(1, True)
    assert second["run_id"] != old_id
    assert second["net_m2"] == 52.61
    assert second["liters"] == 13.15
    still_old = svc.run_detail(old_id)["result"]
    assert still_old["net_m2"] == 46.41 and still_old["liters"] == 11.6


def test_missing_id_is_none_and_no_row_added(svc):
    before = run_count(svc)
    assert svc.run_detail(999999) is None
    assert run_count(svc) == before


def test_http_missing_id_404_and_count_unchanged(svc):
    from app.main import app
    before = run_count(svc)
    with TestClient(app) as client:
        resp = client.get("/api/history/999999")
    assert resp.status_code == 404
    assert run_count(svc) == before


def test_list_and_detail_share_liters(svc):
    r = svc.estimate(1, True)
    rid = r["run_id"]
    detail = svc.run_detail(rid)
    summary = next(h for h in svc.history() if h["id"] == rid)
    assert summary["result"]["liters"] == detail["result"]["liters"] == r["liters"]
    assert summary["result"]["net_m2"] == detail["result"]["net_m2"]
