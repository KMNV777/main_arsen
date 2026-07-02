# Quotes Bot — карточки людей с цитатами

Telegram-бот, который показывает **карточки известных людей** с их биографией и цитатами.

## Возможности

- Случайная карточка с фото, биографией и цитатой
- Листание цитат одного автора (◀️ / ▶️)
- Переход между людьми
- Список всех авторов
- Поиск по имени, описанию или тексту цитаты

## Быстрый старт

### 1. Создайте бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Команда `/newbot` → получите токен

### 2. Настройте окружение

```bash
cd /workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -r quotes_bot/requirements.txt

cp quotes_bot/.env.example .env
# Укажите TELEGRAM_BOT_TOKEN в .env
```

### 3. Запуск

```bash
python -m quotes_bot
```

При первом запуске база SQLite создаётся автоматически и заполняется вашими карточками (4 человека).

## Структура

```
quotes_bot/
├── __main__.py       # точка входа
├── config.py         # настройки из .env
├── db.py             # SQLite
├── models.py         # запросы к БД
├── seed.py           # начальные данные
├── formatters.py     # формат карточки
├── keyboards.py      # клавиатуры
└── handlers/         # обработчики команд
```

## Команды бота

| Действие | Описание |
|----------|----------|
| `/start` | Приветствие и главное меню |
| `/help` | Справка |
| `/search` | Поиск людей и цитат |
| 🎴 Случайная карточка | Случайный человек и цитата |
| 📚 Все люди | Список авторов |
| 🔍 Поиск | Поиск по тексту |

## Добавление своих данных

Данные хранятся в SQLite (`quotes_bot/data/quotes.db`). Можно:

- отредактировать `seed.py` и пересоздать базу;
- добавить записи напрямую в таблицы `people` и `quotes`.

Пример SQL:

```sql
INSERT INTO people (name, bio, years, photo_url)
VALUES ('Пушкин', 'Русский поэт', '1799–1837', NULL);

INSERT INTO quotes (person_id, text)
VALUES (last_insert_rowid(), 'Мы ларцы, полные пустоты...');
```

## Зависимости

- [python-telegram-bot](https://python-telegram-bot.org/) 21.x
- python-dotenv
