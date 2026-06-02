# main_arsen

Набор расширений Cursor/VS Code для автоматизации рутины ручного тестировщика.

## Установка расширений

```bash
./scripts/install-qa-extensions.sh
```

После установки перезагрузите окно Cursor (`Developer: Reload Window`).

## Что входит

| Расширение | Назначение |
|------------|------------|
| REST Client, Thunder Client, Postman | API-тестирование |
| Playwright | E2E и запись сценариев |
| Database Client | Проверка данных в БД |
| OpenAPI, YAML, XML | Спеки и контракты API |
| GitLens | История изменений между сборками |
| Rainbow CSV, Prettier, DotENV | Тестовые данные и окружения |
| Peacock | Цвет окна по среде (dev/stage/prod) |
| Draw.io, Markdown All in One | Документация и схемы |
| Error Lens, Code Runner | Быстрая отладка и скрипты |

Пример HTTP-запросов: `tests/api/example.http`.
