-- =====================================================
-- 逛 Guang - 数据库初始化脚本
-- 用法:
--   sqlite3 data/pinzhuo_sessions.db < init_db.sql    (拼桌)
--   sqlite3 data/taste_graph.db      < init_db.sql    (记味)
--   或直接用 init_db.sh 一键执行
-- =====================================================

-- — 拼桌 pin-zhuo ——————————————————————————————————

CREATE TABLE IF NOT EXISTS sessions (
    group_id   TEXT PRIMARY KEY,
    members    TEXT NOT NULL,
    date       TEXT NOT NULL,
    status     TEXT DEFAULT 'collecting'
);

CREATE TABLE IF NOT EXISTS constraints (
    group_id         TEXT NOT NULL,
    member_id        TEXT NOT NULL,
    location_lat     REAL,
    location_lng     REAL,
    location_area    TEXT DEFAULT '',
    budget_max       INTEGER DEFAULT 200,
    dietary_exclude  TEXT DEFAULT '[]',
    cuisine_prefer   TEXT DEFAULT '[]',
    time_windows     TEXT DEFAULT '[]',
    PRIMARY KEY (group_id, member_id)
);

-- — 记味 taste-log ——————————————————————————————————

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
);

CREATE TABLE IF NOT EXISTS taste_profile (
    user_id     TEXT NOT NULL,
    category    TEXT NOT NULL,
    avg_score   REAL NOT NULL,
    count       INTEGER NOT NULL,
    keywords    TEXT DEFAULT '[]',
    last_update REAL NOT NULL,
    PRIMARY KEY (user_id, category)
);
