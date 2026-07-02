from quotes_bot.db import connect

SEED_VERSION = 2

SEED_DATA: list[dict] = [
    {
        "name": "Ваня WYHM",
        "years": "",
        "bio": "",
        "photo_url": None,
        "quotes": [
            "КАК-ТО ТАК-ТО",
            "Молодежная карта Сбер",
            "Обожаю русский рэп-баттл",
        ],
    },
    {
        "name": "Машинка",
        "years": "",
        "bio": "",
        "photo_url": None,
        "quotes": [
            "Круассаны",
        ],
    },
    {
        "name": "Хуров Азамат",
        "years": "",
        "bio": "",
        "photo_url": None,
        "quotes": [
            "Мне двойной шаурма в сырной и самса говядина",
        ],
    },
    {
        "name": "Арсен Сенсей",
        "years": "",
        "bio": "",
        "photo_url": None,
        "quotes": [],
    },
]


def seed_database(force: bool = False) -> None:
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"
        )
        current = conn.execute(
            "SELECT value FROM meta WHERE key = 'seed_version'"
        ).fetchone()
        if (
            not force
            and current
            and current["value"] == str(SEED_VERSION)
            and conn.execute("SELECT COUNT(*) FROM people").fetchone()[0] > 0
        ):
            return

        conn.execute("DELETE FROM quotes")
        conn.execute("DELETE FROM people")

        for entry in SEED_DATA:
            cursor = conn.execute(
                """
                INSERT INTO people (name, bio, years, photo_url)
                VALUES (?, ?, ?, ?)
                """,
                (
                    entry["name"],
                    entry.get("bio", ""),
                    entry.get("years", ""),
                    entry.get("photo_url"),
                ),
            )
            person_id = cursor.lastrowid
            for quote_text in entry.get("quotes", []):
                conn.execute(
                    "INSERT INTO quotes (person_id, text) VALUES (?, ?)",
                    (person_id, quote_text),
                )

        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', ?)",
            (str(SEED_VERSION),),
        )
