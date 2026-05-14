import sqlite3
from pathlib import Path
from typing import Optional

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
            -- PETS
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
            -- SWIPES
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
            -- MATCHES
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


def create_user(email: str, password_hash: str) -> sqlite3.Row:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            (email, password_hash),
        )
        user_id = cursor.lastrowid
        return conn.execute(
            """
            SELECT id, username, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()


def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, username, password, created_at
            FROM users
            WHERE username = ?
            """,
            (email,),
        ).fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, username, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()


def get_pet_owned_by_user(pet_id: int, user_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, owner_id, name, species, breed, age_years, gender, bio, photo_url, created_at, updated_at
            FROM pets
            WHERE id = ? AND owner_id = ?
            """,
            (pet_id, user_id),
        ).fetchone()


def get_pet_by_id(pet_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, owner_id, name, species, breed, age_years, gender, bio, photo_url, created_at, updated_at
            FROM pets
            WHERE id = ?
            """,
            (pet_id,),
        ).fetchone()


def create_pet(
    owner_id: int,
    name: str,
    species: str,
    breed: Optional[str],
    age_years: Optional[float],
    gender: Optional[str],
    bio: Optional[str],
    photo_url: Optional[str],
) -> sqlite3.Row:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO pets (owner_id, name, species, breed, age_years, gender, bio, photo_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (owner_id, name, species, breed, age_years, gender, bio, photo_url),
        )
        pet_id = cursor.lastrowid
        return conn.execute(
            """
            SELECT id, owner_id, name, species, breed, age_years, gender, bio, photo_url, created_at, updated_at
            FROM pets
            WHERE id = ?
            """,
            (pet_id,),
        ).fetchone()


def list_pets_owned_by_user(user_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, owner_id, name, species, breed, age_years, gender, bio, photo_url, created_at, updated_at
            FROM pets
            WHERE owner_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()


def list_swipe_candidates(swiper_pet_id: int, user_id: int, limit: int = 25) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT p.id, p.owner_id, p.name, p.species, p.breed, p.age_years, p.gender, p.bio, p.photo_url, p.created_at
            FROM pets p
            WHERE p.owner_id != ?
              AND p.id != ?
              AND NOT EXISTS (
                SELECT 1
                FROM swipes s
                WHERE s.swiper_pet_id = ? AND s.swiped_pet_id = p.id
              )
            ORDER BY p.created_at DESC
            LIMIT ?
            """,
            (user_id, swiper_pet_id, swiper_pet_id, limit),
        ).fetchall()


def record_swipe(swiper_pet_id: int, swiped_pet_id: int, direction: str) -> sqlite3.Row:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO swipes (swiper_pet_id, swiped_pet_id, direction)
            VALUES (?, ?, ?)
            ON CONFLICT(swiper_pet_id, swiped_pet_id)
            DO UPDATE SET direction = excluded.direction, created_at = datetime('now')
            """,
            (swiper_pet_id, swiped_pet_id, direction),
        )
        return conn.execute(
            """
            SELECT id, swiper_pet_id, swiped_pet_id, direction, created_at
            FROM swipes
            WHERE swiper_pet_id = ? AND swiped_pet_id = ?
            """,
            (swiper_pet_id, swiped_pet_id),
        ).fetchone()


def has_like_swipe(swiper_pet_id: int, swiped_pet_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM swipes
            WHERE swiper_pet_id = ? AND swiped_pet_id = ? AND direction = 'like'
            """,
            (swiper_pet_id, swiped_pet_id),
        ).fetchone()
        return row is not None


def create_or_get_match(pet_one_id: int, pet_two_id: int) -> sqlite3.Row:
    pet_a_id, pet_b_id = sorted((pet_one_id, pet_two_id))
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO matches (pet_a_id, pet_b_id)
            VALUES (?, ?)
            ON CONFLICT(pet_a_id, pet_b_id) DO NOTHING
            """,
            (pet_a_id, pet_b_id),
        )
        return conn.execute(
            """
            SELECT id, pet_a_id, pet_b_id, created_at
            FROM matches
            WHERE pet_a_id = ? AND pet_b_id = ?
            """,
            (pet_a_id, pet_b_id),
        ).fetchone()


def list_matches_for_pet(pet_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                m.id AS match_id,
                m.created_at AS matched_at,
                CASE WHEN m.pet_a_id = ? THEN m.pet_b_id ELSE m.pet_a_id END AS other_pet_id,
                p.owner_id AS other_owner_id,
                p.name AS other_name,
                p.species AS other_species,
                p.breed AS other_breed,
                p.age_years AS other_age_years,
                p.gender AS other_gender,
                p.bio AS other_bio,
                p.photo_url AS other_photo_url
            FROM matches m
            JOIN pets p
              ON p.id = CASE WHEN m.pet_a_id = ? THEN m.pet_b_id ELSE m.pet_a_id END
            WHERE m.pet_a_id = ? OR m.pet_b_id = ?
            ORDER BY m.created_at DESC
            """,
            (pet_id, pet_id, pet_id, pet_id),
        ).fetchall()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
