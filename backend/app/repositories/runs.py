import json
from datetime import datetime, timezone

# 列表摘要与按号详情共用同一套结果解析，避免升数口径分叉
def decode(row):
    d = dict(row)
    try:
        d["input"] = json.loads(d.pop("input_json") or "{}")
    except json.JSONDecodeError:
        d["input"] = {}
    try:
        d["result"] = json.loads(d.pop("result_json") or "{}")
    except json.JSONDecodeError:
        d["result"] = {}
    return d

def insert(conn, kind, payload, result, room_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,room_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, room_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)

def get_by_id(conn, rid):
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (rid,)).fetchone()
    return decode(row) if row else None

def list_recent(conn, limit=50):
    return [decode(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def count(conn):
    return int(conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"])


def raw_result(row):
    """Pinned result without live rewrite (list path uses decode directly)."""
    d = decode(row) if not isinstance(row, dict) or "result" not in row else row
    return d.get("result")
