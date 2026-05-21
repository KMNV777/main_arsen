# Draw.io-схемы архитектуры ЭМГ

Редактируемые диаграммы в формате **`.drawio`** (diagrams.net / draw.io Desktop). Откройте файл двойным щелчком или через [app.diagrams.net](https://app.diagrams.net) → **File → Open**.

Соответствуют SVG из [`../svg/`](../svg/) и разделам [`architecture-emg-integrations.md`](../architecture-emg-integrations.md).

| Файл | § | Описание |
|------|---|----------|
| [`00-summary-architecture.drawio`](00-summary-architecture.drawio) | §0 | Сводная архитектура: КМГ + ЭМГ + интеграции |
| [`01-corporate-landscape.drawio`](01-corporate-landscape.drawio) | §1 | Общий ландшафт корпоративных систем |
| [`02-1-emg-abai-focus.drawio`](02-1-emg-abai-focus.drawio) | §2.1 | Фокус ЭМГ: ABAI и смежные ИС |
| [`03-abai-im-architecture.drawio`](03-abai-im-architecture.drawio) | §3 | Архитектура ИМ / ABAI (10.32.10.99) |
| [`04-sap-erp-integrations.drawio`](04-sap-erp-integrations.drawio) | §4 | Интеграции SAP ERP |
| [`05-abai-layers.drawio`](05-abai-layers.drawio) | §5 | Слои L1–L4 (OT → ИМ → сервисы) |
| [`06-it-landscape-general.drawio`](06-it-landscape-general.drawio) | ландшафт | Общий ИТ-ландшафт по слоям L0–L5 |
| [`it-landscape-emg-general.drawio`](it-landscape-emg-general.drawio) | ландшафт | То же, что `06` (для [`it-landscape-emg.md`](../it-landscape-emg.md)) |
| [`07-it-landscape-mermaid-detailed.drawio`](07-it-landscape-mermaid-detailed.drawio) | ландшафт | Детальная версия из `it-landscape-emg.mmd` |

## Пересборка из Mermaid

```bash
pip install drawpyo
python3 scripts/mmd_to_drawio.py
```

Исходники: `docs/svg/*.mmd`, `docs/it-landscape-emg.mmd`. Слойный ландшафт L0–L5 генерируется отдельно в скрипте (`build_it_landscape_drawio`).

## Редактирование

- Узлы сгруппированы в **swimlane**-контейнеры по subgraph Mermaid.
- Цвета: зелёный — ЭМГ/ABAI, синий — SAP/AD/шина, жёлтый — OT, красный — ИБ.
- Связи сохранены; пунктир — `-.->` в Mermaid.

После правок в draw.io сохраните `.drawio` в эту папку. При необходимости экспортируйте SVG (**File → Export as → SVG**) для вставки в Word/PPT.
