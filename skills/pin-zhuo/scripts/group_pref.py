"""Group preference intersection algorithm for pin-zhuo."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "pinzhuo_sessions.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            group_id  TEXT PRIMARY KEY,
            members   TEXT NOT NULL,
            date      TEXT NOT NULL,
            status    TEXT DEFAULT 'collecting'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS constraints (
            group_id      TEXT NOT NULL,
            member_id     TEXT NOT NULL,
            location_lat  REAL,
            location_lng  REAL,
            location_area TEXT DEFAULT '',
            budget_max    INTEGER DEFAULT 200,
            dietary_exclude TEXT DEFAULT '[]',
            cuisine_prefer  TEXT DEFAULT '[]',
            time_windows    TEXT DEFAULT '[]',
            PRIMARY KEY (group_id, member_id)
        )
    """)
    conn.commit()
    return conn


AREA_COORDS = {
    "海淀": {"lat": 39.9809, "lng": 116.3060},
    "朝阳": {"lat": 39.9289, "lng": 116.4434},
    "西城": {"lat": 39.9120, "lng": 116.3660},
    "东城": {"lat": 39.9170, "lng": 116.4180},
    "丰台": {"lat": 39.8585, "lng": 116.2870},
    "浦东": {"lat": 31.2350, "lng": 121.5440},
    "徐汇": {"lat": 31.1883, "lng": 121.4369},
    "静安": {"lat": 31.2280, "lng": 121.4480},
    "中关村": {"lat": 39.9809, "lng": 116.3060},
    "五道口": {"lat": 39.9920, "lng": 116.3380},
    "三里屯": {"lat": 39.9330, "lng": 116.4540},
    "望京": {"lat": 39.9880, "lng": 116.4720},
    "国贸": {"lat": 39.9080, "lng": 116.4600},
    "西直门": {"lat": 39.9420, "lng": 116.3530},
}


def start_session(group_id: str, members: list[str], date: str) -> dict:
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO sessions (group_id, members, date, status) VALUES (?, ?, ?, 'collecting')",
        (group_id, json.dumps(members), date),
    )
    conn.commit()
    conn.close()
    return {"group_id": group_id, "members": members, "date": date, "status": "collecting"}


def add_constraint(group_id: str, member_id: str, location: str = "",
                   budget_max: int = 200, dietary_exclude: list[str] | None = None,
                   cuisine_prefer: list[str] | None = None,
                   time_windows: list[str] | None = None) -> dict:
    coords = AREA_COORDS.get(location, {"lat": 39.95, "lng": 116.35})
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO constraints "
        "(group_id, member_id, location_lat, location_lng, location_area, "
        "budget_max, dietary_exclude, cuisine_prefer, time_windows) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (group_id, member_id, coords["lat"], coords["lng"], location,
         budget_max, json.dumps(dietary_exclude or []),
         json.dumps(cuisine_prefer or []), json.dumps(time_windows or [])),
    )
    conn.commit()
    conn.close()
    return {"status": "constraint_added", "group_id": group_id,
            "member_id": member_id, "location": location}


def get_all_constraints(group_id: str) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM constraints WHERE group_id = ?", (group_id,)).fetchall()
    conn.close()
    return [
        {
            "member_id": r["member_id"],
            "location": {"lat": r["location_lat"], "lng": r["location_lng"],
                         "area": r["location_area"]},
            "budget_max": r["budget_max"],
            "dietary_exclude": json.loads(r["dietary_exclude"]),
            "cuisine_prefer": json.loads(r["cuisine_prefer"]),
            "time_windows": json.loads(r["time_windows"]),
        }
        for r in rows
    ]
