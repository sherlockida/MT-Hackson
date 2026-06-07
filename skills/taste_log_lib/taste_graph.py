"""Taste profile CRUD – builds and queries a user's flavor graph."""
from __future__ import annotations
import json
import os
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "taste_graph.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS taste_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT NOT NULL,
            poi_id      TEXT NOT NULL,
            poi_name    TEXT DEFAULT '',
            category    TEXT DEFAULT '',
            subcategory TEXT DEFAULT '',
            score       REAL NOT NULL,
            note        TEXT DEFAULT '',
            tags        TEXT DEFAULT '[]',
            timestamp   REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS taste_profile (
            user_id     TEXT NOT NULL,
            category    TEXT NOT NULL,
            avg_score   REAL NOT NULL,
            count       INTEGER NOT NULL,
            keywords    TEXT DEFAULT '[]',
            last_update REAL NOT NULL,
            PRIMARY KEY (user_id, category)
        )
    """)
    conn.commit()
    return conn


def log_entry(user_id: str, poi_id: str, score: float, note: str = "",
              tags: list[str] | None = None, poi_name: str = "",
              category: str = "", subcategory: str = "") -> dict:
    conn = _get_conn()
    tag_json = json.dumps(tags or [], ensure_ascii=False)
    ts = time.time()
    cur = conn.execute(
        "INSERT INTO taste_entries (user_id, poi_id, poi_name, category, subcategory, score, note, tags, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, poi_id, poi_name, category, subcategory, score, note, tag_json, ts),
    )
    entry_id = cur.lastrowid
    _update_profile(conn, user_id, category)
    conn.commit()
    conn.close()
    return {"entry_id": entry_id, "status": "logged", "user_id": user_id,
            "poi_id": poi_id, "score": score, "category": category}


def _update_profile(conn: sqlite3.Connection, user_id: str, category: str):
    if not category:
        return
    rows = conn.execute(
        "SELECT score, tags FROM taste_entries WHERE user_id = ? AND category = ?",
        (user_id, category),
    ).fetchall()
    if not rows:
        return
    avg = sum(r["score"] for r in rows) / len(rows)
    all_tags = []
    for r in rows:
        all_tags.extend(json.loads(r["tags"]))
    keyword_counts: dict[str, int] = {}
    for t in all_tags:
        keyword_counts[t] = keyword_counts.get(t, 0) + 1
    top_keywords = sorted(keyword_counts, key=keyword_counts.get, reverse=True)[:10]
    conn.execute(
        "INSERT INTO taste_profile (user_id, category, avg_score, count, keywords, last_update) "
        "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(user_id, category) DO UPDATE SET "
        "avg_score=excluded.avg_score, count=excluded.count, keywords=excluded.keywords, "
        "last_update=excluded.last_update",
        (user_id, category, round(avg, 2), len(rows),
         json.dumps(top_keywords, ensure_ascii=False), time.time()),
    )


def get_profile(user_id: str) -> dict:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT category, avg_score, count, keywords, last_update FROM taste_profile WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    entry_count = conn.execute(
        "SELECT COUNT(*) as c FROM taste_entries WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]
    conn.close()
    categories = {}
    for r in rows:
        categories[r["category"]] = {
            "avg_score": r["avg_score"],
            "count": r["count"],
            "keywords": json.loads(r["keywords"]),
        }
    return {"user_id": user_id, "total_entries": entry_count, "categories": categories}


def query_category(user_id: str, category: str) -> dict:
    conn = _get_conn()
    prof = conn.execute(
        "SELECT avg_score, count, keywords FROM taste_profile WHERE user_id = ? AND category = ?",
        (user_id, category),
    ).fetchone()
    entries = conn.execute(
        "SELECT poi_id, poi_name, score, note, tags, timestamp FROM taste_entries "
        "WHERE user_id = ? AND category = ? ORDER BY timestamp DESC LIMIT 10",
        (user_id, category),
    ).fetchall()
    conn.close()
    if not prof:
        return {"user_id": user_id, "category": category, "found": False,
                "message": f"暂无「{category}」相关记录"}
    return {
        "user_id": user_id, "category": category, "found": True,
        "avg_score": prof["avg_score"], "count": prof["count"],
        "keywords": json.loads(prof["keywords"]),
        "recent_entries": [
            {"poi_id": e["poi_id"], "poi_name": e["poi_name"], "score": e["score"],
             "note": e["note"], "tags": json.loads(e["tags"])}
            for e in entries
        ],
    }


def export_profile(user_id: str) -> dict:
    conn = _get_conn()
    entries = conn.execute(
        "SELECT poi_id, poi_name, category, subcategory, score, note, tags, timestamp "
        "FROM taste_entries WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    profile = get_profile(user_id)
    profile["entries"] = [
        {"poi_id": e["poi_id"], "poi_name": e["poi_name"], "category": e["category"],
         "subcategory": e["subcategory"], "score": e["score"], "note": e["note"],
         "tags": json.loads(e["tags"]), "timestamp": e["timestamp"]}
        for e in entries
    ]
    return profile


def delete_entry(entry_id: int) -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT user_id, category FROM taste_entries WHERE id = ?", (entry_id,)).fetchone()
    if not row:
        conn.close()
        return {"status": "not_found", "entry_id": entry_id}
    user_id, category = row["user_id"], row["category"]
    conn.execute("DELETE FROM taste_entries WHERE id = ?", (entry_id,))
    _update_profile(conn, user_id, category)
    conn.commit()
    conn.close()
    return {"status": "deleted", "entry_id": entry_id}


def clear_user(user_id: str) -> dict:
    conn = _get_conn()
    conn.execute("DELETE FROM taste_entries WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM taste_profile WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "cleared", "user_id": user_id}


def category_recency(user_id: str, category: str, now: float | None = None) -> float:
    conn = _get_conn()
    row = conn.execute(
        "SELECT MAX(timestamp) as last_ts FROM taste_entries WHERE user_id = ? AND category = ?",
        (user_id, category),
    ).fetchone()
    conn.close()
    if not row or not row["last_ts"]:
        return 0.0
    now = now or time.time()
    days_ago = (now - row["last_ts"]) / 86400
    if days_ago <= 7:
        return 1.0
    if days_ago >= 30:
        return 0.0
    return 1.0 - (days_ago - 7) / 23


def area_familiarity(user_id: str, area: str) -> float:
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) as c FROM taste_entries WHERE user_id = ? AND note LIKE ?",
        (user_id, f"%{area}%"),
    ).fetchone()
    conn.close()
    count = row["c"] if row else 0
    if count >= 5:
        return 1.0
    return count / 5
