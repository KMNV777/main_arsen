# Dominion E2E — Excel / CSV для импорта

## Файлы

| Файл | Назначение |
|------|------------|
| **`Dominion_E2E_TestCases.xlsx`** | Основной workbook (4 листа) |
| **`Dominion_E2E_Steps_Import.csv`** | Плоский импорт: 1 строка = 1 шаг |
| **`Dominion_E2E_TestCases_Import.csv`** | 1 строка = 1 кейс (шаги в одной ячейке) |

## Листы Excel

| Лист | Формат | Для чего |
|------|--------|----------|
| **Инструкция** | Справка | Как импортировать |
| **TestCases** | 1 кейс = 1 строка | Обзор, фильтры, статусы прогона |
| **Steps** | **1 шаг = 1 строка** | Основной импорт: `Step (Action)` + `Expected Result` |
| **Сводка** | Счётчики | 84 кейса / 206 шагов |

## Формат шага (лист Steps)

| Case ID | Step # | Step (Action) | Expected Result |
|---------|--------|---------------|-----------------|
| TC-ADM-001 | 1 | Открыть Админка → Dictionary → Создать предмет | Открыта форма создания definition |
| TC-ADM-001 | 2 | Заполнить поля… | Поля принимают значения без ошибок |

## Импорт в TestRail / Zephyr / Xray

1. **TestRail** — Import Cases → CSV/Excel → map:
   - `Case ID` → Case ID / Custom
   - `Title` → Title
   - `Module` → Section
   - `Priority` → Priority
   - `Preconditions` → Preconditions
   - `Step (Action)` → Step Action
   - `Expected Result` → Expected Result
2. **Zephyr Scale** — Import → CSV с колонками Step / Expected
3. **Xray** — Import Test Cases → map Steps sheet

## Пересборка

```bash
python3 scripts/generate_dominion_e2e_excel.py
```

Требуется: `openpyxl` (`pip install openpyxl`).

## Статистика

- **84** тест-кейса
- **206** шагов
- P0: 33 | P1: 33 | P2: 16 | P3: 2
- NFT — out of scope
