# Draw.io — C4-архитектура ЭМГ

## Файл

- [`emg-c4-architecture.drawio`](./emg-c4-architecture.drawio)

## Страницы

1. **01 — C4 Context** — пользователи, ИТ-ландшафт ЭМГ, внешние системы (ABAI, КМГ, Qazcloud, Самрук-Казына)
2. **02 — C4 Container** — SAP, 1С, Directum, SCADA, мониторинг, пробелы (🔴)
3. **03 — C4 Data** — ABAI-модули, SAP/1С/Alfresco, Historian, отсутствие MDM/КХД/ESB
4. **04 — C4 ABAI** — компоненты ABAI (6/58 отчётов, 🔴 ГТМ/ГНО/ИМ)
5. **05 — C4 OT/SCADA** — WinCC, DeltaV, ArgusPro, PetroLine
6. **06 — C4 Deployment** — Qazcloud IaaS vs собственный ЦОД

## Цветовая легенда

| Цвет | Значение |
|---|---|
| Зелёный | В промышленной эксплуатации |
| Жёлтый | Планируется замена / развитие |
| Красный | Средство цифровизации отсутствует |
| Фиолетовый (пунктир) | Внешняя система (КМГ, подрядчик) |
| Голубое облако | Qazcloud / облако |

Пунктирные красные связи — потоки, не подтверждённые в ответах ЭМГ.

## Генератор

```bash
python3 scripts/generate_emg_c4_drawio.py
```

Исходник: [`scripts/generate_emg_c4_drawio.py`](../scripts/generate_emg_c4_drawio.py)
