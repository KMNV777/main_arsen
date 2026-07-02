import sqlite3
from contextlib import contextmanager
from pathlib import Path

from quotes_bot.config import DATABASE_PATH


def init_db(db_path: Path | None = None) -> None:
    path = db_path or DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    with connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                bio TEXT NOT NULL DEFAULT '',
                years TEXT NOT NULL DEFAULT '',
                photo_url TEXT
            );

            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS packs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                emoji TEXT NOT NULL DEFAULT '📦',
                description TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS pack_members (
                pack_id INTEGER NOT NULL,
                person_id INTEGER NOT NULL,
                PRIMARY KEY (pack_id, person_id),
                FOREIGN KEY (pack_id) REFERENCES packs(id) ON DELETE CASCADE,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                tickets INTEGER NOT NULL DEFAULT 5,
                packs_opened INTEGER NOT NULL DEFAULT 0,
                duplicate_dust INTEGER NOT NULL DEFAULT 0,
                username TEXT,
                display_name TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_cards (
                user_id INTEGER NOT NULL,
                quote_id INTEGER NOT NULL,
                obtained_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, quote_id),
                FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_quotes_person_id ON quotes(person_id);
            CREATE INDEX IF NOT EXISTS idx_user_cards_user_id ON user_cards(user_id);

            CREATE TABLE IF NOT EXISTS user_card_stats (
                user_id INTEGER NOT NULL,
                quote_id INTEGER NOT NULL,
                duplicate_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, quote_id),
                FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                offered_quote_id INTEGER NOT NULL,
                requested_quote_id INTEGER,
                returned_quote_id INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT,
                FOREIGN KEY (offered_quote_id) REFERENCES quotes(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_trades_to_user ON trades(to_user_id, status);
            CREATE INDEX IF NOT EXISTS idx_trades_from_user ON trades(from_user_id, status);
            """
        )
        _migrate_user_profiles(conn)


def _migrate_user_profiles(conn) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(user_profiles)")}
    if "duplicate_dust" not in columns:
        conn.execute(
            "ALTER TABLE user_profiles ADD COLUMN duplicate_dust INTEGER NOT NULL DEFAULT 0"
        )
    if "username" not in columns:
        conn.execute("ALTER TABLE user_profiles ADD COLUMN username TEXT")
    if "display_name" not in columns:
        conn.execute("ALTER TABLE user_profiles ADD COLUMN display_name TEXT")


@contextmanager
def connect(db_path: Path | None = None):
    path = db_path or DATABASE_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
