#!/bin/bash
# 逛 Guang — 一键初始化数据库
# 用法: bash init_db.sh
# 效果: 清空旧数据, 重建空数据库 (demo.py 运行时会自动填充数据)

set -e
cd "$(dirname "$0")"

mkdir -p data

echo "清理旧数据库..."
rm -f data/pinzhuo_sessions.db data/taste_graph.db

echo "创建 pinzhuo_sessions.db..."
sqlite3 data/pinzhuo_sessions.db <<'SQL'
CREATE TABLE sessions (
    group_id  TEXT PRIMARY KEY,
    members   TEXT NOT NULL,
    date      TEXT NOT NULL,
    status    TEXT DEFAULT 'collecting'
);

CREATE TABLE constraints (
    group_id        TEXT NOT NULL,
    member_id       TEXT NOT NULL,
    location_lat    REAL,
    location_lng    REAL,
    location_area   TEXT DEFAULT '',
    budget_max      INTEGER DEFAULT 200,
    dietary_exclude TEXT DEFAULT '[]',
    cuisine_prefer  TEXT DEFAULT '[]',
    time_windows    TEXT DEFAULT '[]',
    PRIMARY KEY (group_id, member_id)
);
SQL

echo "创建 taste_graph.db..."
sqlite3 data/taste_graph.db <<'SQL'
CREATE TABLE taste_entries (
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
);

CREATE TABLE taste_profile (
    user_id     TEXT NOT NULL,
    category    TEXT NOT NULL,
    avg_score   REAL NOT NULL,
    count       INTEGER NOT NULL,
    keywords    TEXT DEFAULT '[]',
    last_update REAL NOT NULL,
    PRIMARY KEY (user_id, category)
);
SQL

echo "✅ 数据库初始化完成"
echo "  data/pinzhuo_sessions.db  (拼桌: sessions + constraints)"
echo "  data/taste_graph.db       (记味: taste_entries + taste_profile)"
