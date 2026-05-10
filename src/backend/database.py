import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            -- ----------------------------------------------------------------
            -- USERS
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- ----------------------------------------------------------------
            -- PETS  (the profiles being swiped on)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS pets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name        TEXT    NOT NULL,
                species     TEXT    NOT NULL,
                breed       TEXT,
                age_years   REAL,
                gender      TEXT,
                bio         TEXT,
                photo_url   TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- ----------------------------------------------------------------
            -- SWIPES  (like | pass)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS swipes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                swiper_pet_id   INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
                swiped_pet_id   INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
                direction       TEXT    NOT NULL CHECK(direction IN ('like', 'pass')),
                created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                UNIQUE(swiper_pet_id, swiped_pet_id)
            );

            -- ----------------------------------------------------------------
            -- MATCHES  (mutual likes)
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS matches (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_a_id    INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
                pet_b_id    INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                UNIQUE(pet_a_id, pet_b_id)
            );

            -- ----------------------------------------------------------------
            -- DIRECT MESSAGING
            -- ----------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS conversations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id    INTEGER REFERENCES matches(id) ON DELETE SET NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS participants (
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                user_id         INTEGER NOT NULL REFERENCES users(id)         ON DELETE CASCADE,
                joined_at       TEXT    NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (conversation_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                sender_id       INTEGER NOT NULL REFERENCES users(id)         ON DELETE CASCADE,
                body            TEXT    NOT NULL,
                read_at         TEXT,
                created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            -- ----------------------------------------------------------------
            -- INDEXES
            -- ----------------------------------------------------------------
            CREATE INDEX IF NOT EXISTS idx_pets_owner        ON pets(owner_id);
            CREATE INDEX IF NOT EXISTS idx_swipes_swiper     ON swipes(swiper_pet_id);
            CREATE INDEX IF NOT EXISTS idx_swipes_swiped     ON swipes(swiped_pet_id);
            CREATE INDEX IF NOT EXISTS idx_matches_pet_a     ON matches(pet_a_id);
            CREATE INDEX IF NOT EXISTS idx_matches_pet_b     ON matches(pet_b_id);
            CREATE INDEX IF NOT EXISTS idx_participants_user ON participants(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_conv     ON messages(conversation_id);
        """)


if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
