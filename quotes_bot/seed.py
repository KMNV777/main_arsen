from quotes_bot.db import connect


SEED_DATA: list[dict] = [
    {
        "name": "Альберт Эйнштейн",
        "years": "1879–1955",
        "bio": "Физик, создатель теории относительности, лауреат Нобелевской премии.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Albert_Einstein_Head.jpg",
        "quotes": [
            "Воображение важнее знания.",
            "Жизнь — как езда на велосипеде. Чтобы сохранить равновесие, ты должен двигаться.",
            "Не все, что можно измерить, важно, и не всё важное можно измерить.",
        ],
    },
    {
        "name": "Марк Твен",
        "years": "1835–1910",
        "bio": "Американский писатель и сатирик, автор «Приключений Тома Сойера».",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Mark_Twain_by_AF_Bradley.jpg",
        "quotes": [
            "Два самых важных дня в твоей жизни — день, когда ты родился, и день, когда понял зачем.",
            "Если ты говоришь правду, тебе не нужно ничего запоминать.",
            "Секрет успеха — начать.",
        ],
    },
    {
        "name": "Махатма Ганди",
        "years": "1869–1948",
        "bio": "Лидер индийского движения за независимость, проповедник ненасильственного сопротивления.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Mahatma-Gandhi%2C-studio%2C-1931.jpg",
        "quotes": [
            "Стань тем изменением, которое хочешь видеть в мире.",
            "Сила не приходит от физической способности. Она приходит от несгибаемой воли.",
            "Счастье — это когда то, что ты думаешь, говоришь и делаешь, находится в гармонии.",
        ],
    },
    {
        "name": "Мария Кюри",
        "years": "1867–1934",
        "bio": "Физик и химик, дважды лауреат Нобелевской премии, пионер исследований радиоактивности.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Marie_Curie_c1920.jpg",
        "quotes": [
            "В жизни нет ничего такого, чего нужно бояться, есть только то, что нужно понять.",
            "Нужно иметь веру в себя и свои силы.",
            "Ничто в жизни не пугает меня, я просто хочу понять.",
        ],
    },
    {
        "name": "Леонардо да Винчи",
        "years": "1452–1519",
        "bio": "Художник эпохи Возрождения, изобретатель, учёный и архитектор.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Leonardo_da_Vinci_-_presumed_self-portrait_-_WGA12798.jpg",
        "quotes": [
            "Простота — высшая степень изощрённости.",
            "Учиться никогда не поздно.",
            "Движение — причина жизни.",
        ],
    },
    {
        "name": "Сократ",
        "years": "470–399 до н.э.",
        "bio": "Древнегреческий философ, один из основателей западной философии.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Socrates_Louvre.jpg",
        "quotes": [
            "Я знаю, что ничего не знаю.",
            "Непроверенная жизнь не стоит того, чтобы её жить.",
            "Мудрость начинается с удивления.",
        ],
    },
    {
        "name": "Оскар Уайльд",
        "years": "1854–1900",
        "bio": "Ирландский писатель, поэт и драматург, мастер афоризмов.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Oscar_Wilde_Sarony.jpg",
        "quotes": [
            "Будь самим собой; все остальные роли уже заняты.",
            "Опыт — это имя, которое каждый даёт своим ошибкам.",
            "Кто, кроме портного, может понять человека?",
        ],
    },
    {
        "name": "Конфуций",
        "years": "551–479 до н.э.",
        "bio": "Китайский мыслитель и философ, основатель конфуцианства.",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Kong_Qiu.jpg",
        "quotes": [
            "Выбирай работу, которую любишь, и тебе не придётся работать ни одного дня.",
            "Путь в тысячу ли начинается с первого шага.",
            "Учиться без размышления бесполезно, размышлять без учения опасно.",
        ],
    },
]


def seed_database(force: bool = False) -> None:
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
        if count > 0 and not force:
            return

        if force:
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
                    entry["bio"],
                    entry["years"],
                    entry.get("photo_url"),
                ),
            )
            person_id = cursor.lastrowid
            for quote_text in entry["quotes"]:
                conn.execute(
                    "INSERT INTO quotes (person_id, text) VALUES (?, ?)",
                    (person_id, quote_text),
                )
