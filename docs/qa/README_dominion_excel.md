# Dominion E2E — Excel / CSV (1 строка = 1 шаг)

## Формат

**Каждая строка Excel = один шаг тест-кейса.**

| Case ID | Module | Title | Priority | Preconditions | Step # | Step (Action) | Expected Result |
|---------|--------|-------|----------|---------------|--------|---------------|-----------------|
| TC-ADM-001 | Админка / Dictionary | Создание definition… | P1 | Авторизован U-ADMIN… | 1 | Открыть Админка → Dictionary → Создать предмет | Открыта форма создания definition |
| TC-ADM-001 | Админка / Dictionary | Создание definition… | P1 | Авторизован U-ADMIN… | 2 | Заполнить: name=… | Поля принимают значения без ошибок |
| TC-ADM-001 | Админка / Dictionary | Создание definition… | P1 | Авторизован U-ADMIN… | 3 | Нажать «Сохранить» | Definition создан |

Метаданные кейса (Case ID, Title, Priority, Preconditions) **повторяются на каждой строке шага**.

## Файлы

| Файл | Назначение |
|------|------------|
| **`Dominion_E2E_TestCases.xlsx`** | Лист **Steps** (основной) + Инструкция + Сводка |
| **`Dominion_E2E_Steps_Import.csv`** | Тот же формат для CSV-импорта (UTF-8 BOM) |

## Пересборка

```bash
python3 scripts/generate_dominion_e2e_excel.py
```

## Статистика

- **84** кейса → **206** строк-шагов
- NFT — out of scope
