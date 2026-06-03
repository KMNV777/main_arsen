# Draw.io-схемы архитектуры ЭМГ

Редактируемые диаграммы в формате **`.drawio`** (diagrams.net / draw.io Desktop). Откройте файл двойным щелчком или через [app.diagrams.net](https://app.diagrams.net) → **File → Open**.

Соответствуют SVG из [`../svg/`](../svg/) и разделам [`architecture-emg-integrations.md`](../architecture-emg-integrations.md).

| Файл | § | Техническое описание | Бизнес-объяснение |
|------|---|----------------------|-------------------|
| [`00-summary-architecture.drawio`](00-summary-architecture.drawio) | §0 | Сводная архитектура: КМГ + ЭМГ + интеграции | Верхнеуровневая карта: как устроен цифровой контур ЭМГ в группе КМГ. |
| [`01-corporate-landscape.drawio`](01-corporate-landscape.drawio) | §1 | Общий ландшафт корпоративных систем | Показывает покрытие ключевых бизнес-функций (финансы, кадры, документооборот, ИБ, производство). |
| [`02-1-emg-abai-focus.drawio`](02-1-emg-abai-focus.drawio) | §2.1 | Фокус ЭМГ: ABAI и смежные ИС | Быстро объясняет, от каких систем зависит работа ABAI и какие процессы ЭМГ это затрагивает. |
| [`03-abai-im-architecture.drawio`](03-abai-im-architecture.drawio) | §3 | Архитектура ИМ / ABAI (10.32.10.99) | Демонстрирует путь производственных данных: от источников телеметрии до аналитических сервисов. |
| [`04-sap-erp-integrations.drawio`](04-sap-erp-integrations.drawio) | §4 | Интеграции SAP ERP | Показывает SAP как центр управления финансовыми, кадровыми и закупочными процессами. |
| [`05-abai-layers.drawio`](05-abai-layers.drawio) | §5 | Слои L1-L4 (OT → ИМ → сервисы) | Объясняет ответственность уровней: где данные рождаются, где обрабатываются, где используются бизнесом. |
| [`06-it-landscape-general.drawio`](06-it-landscape-general.drawio) | ландшафт | Общий ИТ-ландшафт по слоям L0-L5 | Базовая карта для обсуждения приоритетов развития и критичных зависимостей ИТ-ландшафта. |
| [`it-landscape-emg-general.drawio`](it-landscape-emg-general.drawio) | ландшафт | То же, что `06` (для [`it-landscape-emg.md`](../it-landscape-emg.md)) | Та же бизнес-картина в альтернативном файле для основного обзорного документа. |
| [`07-it-landscape-mermaid-detailed.drawio`](07-it-landscape-mermaid-detailed.drawio) | ландшафт | Детальная версия из `it-landscape-emg.mmd` | Используется, когда нужно перейти от общей картины к конкретным интеграционным потокам. |
| [`10-kmg-emg-architecture.drawio`](10-kmg-emg-architecture.drawio) | §8 | **Сетевая топология КМГ + ЭМГ** (генератор `scripts/build_kmg_emg_architecture.py`) | Три сегмента КСПД (КМГ / ЭМГ / НГДУ-ТСПД), транспорты ЕСПД и L2VPN, размещение систем по сегментам и межсегментные интеграции. |

| [`11-kmg-emg-c4-component.drawio`](11-kmg-emg-c4-component.drawio) | §8 (C4) | **C4 Component диаграмма КМГ + ЭМГ** по сетевым контурам (генератор `scripts/build_kmg_emg_c4_component.py`) | Те же сегменты КСПД в нотации C4: системы как «component», границы сетей, отношения с протоколами, Person. |

## Общая архитектура КМГ + ЭМГ (отдельный генератор)

`10-kmg-emg-architecture.drawio` строится воспроизводимым скриптом по реальной сетевой топологии: три сегмента КСПД (КМГ — синий, ЭМГ/АУП — зелёный, НГДУ/ТСПД — оранжевый), транспорты ЕСПД и L2VPN через МСЭ/криптошлюзы/маршрутизаторы; системы размещены по сегментам (ABAI, ИСУН, SAP ERP, Nedra — в КСПД КМГ), показаны межсегментные интеграции с протоколами.

```bash
pip install -r requirements.txt
python3 scripts/build_kmg_emg_architecture.py
```

## Пересборка из Mermaid

```bash
pip install -r requirements.txt
python3 scripts/mmd_to_drawio.py
```

Исходники: `docs/svg/*.mmd`, `docs/it-landscape-emg.mmd`. Слойный ландшафт L0–L5 генерируется отдельно в скрипте (`build_it_landscape_drawio`) и включает подписанные связи из реестра интеграций.

## Редактирование

- Узлы сгруппированы в **swimlane**-контейнеры по subgraph Mermaid.
- Цвета: зелёный — ЭМГ/ABAI, синий — SAP/AD/шина, жёлтый — OT, красный — ИБ.
- Связи сохранены; пунктир — `-.->` в Mermaid.

После правок в draw.io сохраните `.drawio` в эту папку. При необходимости экспортируйте SVG (**File → Export as → SVG**) для вставки в Word/PPT.
