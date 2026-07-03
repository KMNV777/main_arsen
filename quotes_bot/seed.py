from quotes_bot.db import connect

SEED_VERSION = 7

PACKS = [
    {
        "slug": "wyhm",
        "name": "WYHM Pack",
        "emoji": "🎤",
        "description": "Ваня WYHM и Гриша — рейдж, рэп и колхоз.",
        "members": ["Ваня WYHM", "Гриша"],
    },
    {
        "slug": "sensei",
        "name": "SENSEI Pack",
        "emoji": "⚡",
        "description": "Два Арсена — tilt, пиво и пиздец.",
        "members": ["Арсен Сенсей", "Арсен Акманов"],
    },
    {
        "slug": "snack",
        "name": "SNACK Pack",
        "emoji": "🥐",
        "description": "Машинка и Хуров Азамат — еда и Winline.",
        "members": ["Машинка", "Хуров Азамат"],
    },
    {
        "slug": "chaos",
        "name": "CHAOS Pack",
        "emoji": "🌸",
        "description": "Артемида и Йомма — ботики, аниме и храп.",
        "members": ["Артемида", "Йомма"],
    },
]

SEED_DATA: list[dict] = [
    {
        "name": "Ваня WYHM",
        "photo_url": "vanya_wyhm.jpg",
        "quotes": [
            "КАК-ТО ТАК-ТО",
            "Молодежная карта Сбер",
            "Обожаю русский рэп-баттл",
            "Нужен ксанакс",
            "Меня ебнул диабет",
            "Всем привет дорогие друзья",
            "Где мой Red Bull бля",
            "Я в ахуе если честно",
            "Слушайте Oxxxymiron сейчас",
            "У меня сахар как у деда",
            "Это база базируется",
            "Я щас в тiltе жёстком",
            "Рэп-баттл решает всё",
            "Мне нужен Snickers и покой",
            "Дорогие друзья я снова тут",
            "WYHM на связи бля",
        ],
    },
    {
        "name": "Машинка",
        "photo_url": "mashinka.jpg",
        "quotes": [
            "Круассаны",
            "МММ Винлайн дал круассан",
            "Чмок",
            "Это не круассан это lifestyle",
            "Winline спасает утро",
            "Я хочу чмок и кофе",
            "Ещё один круассан не убьёт",
            "Не трогай мой Winline",
            "Мммм вкусно сказала она",
            "Третий круассан за сегодня",
            "Чмок чмок всем сладких снов",
            "Я на кассе Winline стою",
            "Это был лучший круассан в жизни",
            "Круассан > ranked",
            "Winline дал again",
        ],
    },
    {
        "name": "Хуров Азамат",
        "photo_url": "khurov_azamat.jpg",
        "quotes": [
            "Мне двойной шаурма в сырной и самса говядина",
            "Тройной шаурма или паника",
            "Самса сочная как мечта",
            "Дайте лимонад и шаурму",
            "Я голодный как волк бля",
            "Сырная это не обсуждается",
            "Ещё самсу но с курицей",
            "Азамат заказывает жрать",
            "Шаурма это мой киберспорт",
            "Мне combo номер три",
            "После шаурмы только сон",
            "Двойной сыр extra",
            "Самса говядина must have",
            "Я не играю я ем",
            "Шаурма carry мой вечер",
        ],
    },
    {
        "name": "Арсен Сенсей",
        "photo_url": "arsen_sensei.jpg",
        "quotes": [
            "Блядь Акманов опять насрал",
            "Ебаные цыгане",
            "Ебаный сырник",
            "Пегов",
            "Акманов опять всё испортил",
            "Где мой сырник блядь",
            "Цыгане взяли мой tilt",
            "Пегов знает всё",
            "Я sensei а не стажёр",
            "Сырник злится на меня",
            "Это пizдец а не день",
            "Акманов выйди из комнаты",
            "Мой tilt максимальный",
            "Сенсей не спит из-за сырника",
            "Пегов был прав",
        ],
    },
    {
        "name": "Арсен Акманов",
        "photo_url": "arsen_akmanov.jpg",
        "quotes": [
            "Втирай в меня светлое нефильтрованное",
            "Блядь",
            "Пиздец",
            "Светлое нефильтрованное база",
            "Блядь это я сказал",
            "Пиздец полный ребят",
            "Втирай глубже бля",
            "Я пивной philosopher",
            "Это не пиво это искусство",
            "Блядь блядь блядь ok",
            "Нефильтрованное or nothing",
            "Акманов mode activated",
            "Пиздец но красиво",
            "Ещё светлое пж",
            "Втирай медленнее",
        ],
    },
    {
        "name": "Гриша",
        "photo_url": "grisha.jpg",
        "quotes": [
            "Ну я ебал в рот",
            "Ебаный ФКС БЛЯДЬ",
            "Ну ебаный колхоз блядь",
            "Бля может в Шанхай ебануть",
            "FC Köln forever бля",
            "Колхоз mode on",
            "Шанхай зовёт меня",
            "Я ебал в рот этот patch",
            "ФКС опять проебали",
            "Ебаный offside блядь",
            "Гриша в rage queue",
            "Колхозники на спавне",
            "Shanghai trip when",
            "Это не баг это колхоз",
            "ФКС why always ФКС",
        ],
    },
    {
        "name": "Артемида",
        "photo_url": "artemida.jpg",
        "quotes": [
            "Ебаные дебилы блядь",
            "Ботики",
            "Паша A'VI неприятный чел",
            "Ботики опять lag",
            "Pasha AVI выйди",
            "Дебилы в voice chat",
            "Это не баг это feature",
            "Артемида в tilt",
            "Зачем вы все такие",
            "Ботики carry me",
            "AVI опять toxic",
            "Я в ахуе с tier 3",
            "Дебилы но милые",
            "Ботики fix pls",
            "AVI неприятный again",
        ],
    },
    {
        "name": "Йомма",
        "photo_url": "yomma.jpg",
        "quotes": [
            "Хочу тян с аниме",
            "Гриша мешал мне спать",
            "Гриша опять храпит",
            "Тян из аниме когда",
            "Хочу waifu и sleep",
            "Гриша мешает dream",
            "Аниме > reality",
            "Йомма не спит бля",
            "Ещё одну серию и спать",
            "Гриша выключи mic",
            "Waifu pack when",
            "Sleep is optional",
            "Тян carry my mood",
            "Гриша snore OP",
            "Аниме marathon go",
        ],
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

        conn.execute("DELETE FROM user_cards")
        conn.execute("DELETE FROM user_profiles")
        conn.execute("DELETE FROM pack_members")
        conn.execute("DELETE FROM packs")
        conn.execute("DELETE FROM quotes")
        conn.execute("DELETE FROM people")

        person_ids: dict[str, int] = {}
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
            person_ids[entry["name"]] = cursor.lastrowid
            for quote_text in entry.get("quotes", []):
                conn.execute(
                    "INSERT INTO quotes (person_id, text) VALUES (?, ?)",
                    (cursor.lastrowid, quote_text),
                )

        for pack in PACKS:
            cursor = conn.execute(
                """
                INSERT INTO packs (slug, name, emoji, description)
                VALUES (?, ?, ?, ?)
                """,
                (pack["slug"], pack["name"], pack["emoji"], pack["description"]),
            )
            pack_id = cursor.lastrowid
            for member_name in pack["members"]:
                conn.execute(
                    "INSERT INTO pack_members (pack_id, person_id) VALUES (?, ?)",
                    (pack_id, person_ids[member_name]),
                )

        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', ?)",
            (str(SEED_VERSION),),
        )
