"""Recompute estimate from current room/settings when opening a snapshot."""
from app.engines.estimate import estimate_room
from app.engines.paint_volume import paint_liters
from app.repositories import openings, rooms, settings


def _room_id_of(row):
    room_id = row.get("room_id")
    if room_id:
        return room_id
    inp = row.get("input")
    if isinstance(inp, dict):
        return inp.get("room_id")
    return None


def _ops_for_room(conn, room_id):
    return [{"w": o["w"], "h": o["h"]} for o in openings.for_room(conn, room_id)]


def live_coverage_coats(conn):
    cov, ct = settings.coverage_coats(conn)
    return float(cov), int(ct)


def live_estimate_for_run(conn, row):
    room_id = _room_id_of(row)
    if not room_id:
        return row.get("result")
    room = rooms.get(conn, room_id)
    if not room:
        return row.get("result")
    cov, ct = live_coverage_coats(conn)
    # intentionally ignore pinned coverage/coats from input snapshot
    ops = _ops_for_room(conn, room_id)
    return estimate_room(room["length"], room["width"], room["height"], ops, cov, ct)


def overlay_liters_only(conn, result):
    """Alternate path: keep geometry, rewrite liters with live rate."""
    if not isinstance(result, dict) or result.get("net_m2") is None:
        return result
    cov, ct = live_coverage_coats(conn)
    vol = paint_liters(float(result["net_m2"]), cov, ct)
    out = dict(result)
    out.update(vol)
    return out


def detail_with_live(conn, decoded):
    if not decoded:
        return None
    out = dict(decoded)
    fresh = live_estimate_for_run(conn, out)
    if fresh is None:
        fresh = overlay_liters_only(conn, out.get("result"))
    out["result"] = fresh
    out["snapshot_rewritten"] = True
    out["pinned_input"] = out.get("input")
    return out


def list_keeps_pin(decoded):
    """History list continues to serve pinned decode() results."""
    return decoded
