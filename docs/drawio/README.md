# Draw.io-схемы архитектуры ЭМГ

Редактируемые диаграммы в формате **`.drawio`** (diagrams.net / draw.io Desktop). Откройте файл двойным щелчком или через [app.diagrams.net](https://app.diagrams.net) → **File → Open**.

Соответствуют SVG из [`../svg/`](../svg/) и разделам [`architecture-emg-integrations.md`](../architecture-emg-integrations.md).

| Файл | § | Техническое описание | Бизнес-объяснение |
|------|---|----------------------|-------------------|
| [`08-kmg-emg-corporate-networks.drawio`](08-kmg-emg-corporate-networks.drawio) | общая | **Общая схема КМГ и ЭМГ**: корпоративные сети + все ключевые интеграции | Главная презентационная схема: две сети, протоколы, точки стыковки ЭМГ↔КМГ. |
| [`00-summary-architecture.drawio`](00-summary-architecture.drawio) | §0 | Сводная архитектура: КМГ + ЭМГ + интеграции | Упрощённая карта верхнего уровня. |
| [`01-corporate-landscape.drawio`](01-corporate-landscape.drawio) | §1 | Общий ландшафт корпоративных систем | Показывает покрытие ключевых бизнес-функций (финансы, кадры, документооборот, ИБ, производство). |
| [`02-1-emg-abai-focus.drawio`](02-1-emg-abai-focus.drawio) | §2.1 | Фокус ЭМГ: ABAI и смежные ИС | Быстро объясняет, от каких систем зависит работа ABAI и какие процессы ЭМГ это затрагивает. |
| [`03-abai-im-architecture.drawio`](03-abai-im-architecture.drawio) | §3 | Архитектура ИМ / ABAI (10.32.10.99) | Демонстрирует путь производственных данных: от источников телеметрии до аналитических сервисов. |
| [`04-sap-erp-integrations.drawio`](04-sap-erp-integrations.drawio) | §4 | Интеграции SAP ERP | Показывает SAP как центр управления финансовыми, кадровыми и закупочными процессами. |
| [`05-abai-layers.drawio`](05-abai-layers.drawio) | §5 | Слои L1-L4 (OT → ИМ → сервисы) | Объясняет ответственность уровней: где данные рождаются, где обрабатываются, где используются бизнесом. |
| [`06-it-landscape-general.drawio`](06-it-landscape-general.drawio) | ландшафт | Общий ИТ-ландшафт по слоям L0-L5 | Базовая карта для обсуждения приоритетов развития и критичных зависимостей ИТ-ландшафта. |
| [`it-landscape-emg-general.drawio`](it-landscape-emg-general.drawio) | ландшафт | То же, что `06` (для [`it-landscape-emg.md`](../it-landscape-emg.md)) | Та же бизнес-картина в альтернативном файле для основного обзорного документа. |
| [`07-it-landscape-mermaid-detailed.drawio`](07-it-landscape-mermaid-detailed.drawio) | ландшафт | Детальная версия из `it-landscape-emg.mmd` | Используется, когда нужно перейти от общей картины к конкретным интеграционным потокам. |
| [`09-emg-c4-component.drawio`](09-emg-c4-component.drawio) | §9 | **Единая C4 Component диаграмма ЭМГ** (генератор `scripts/build_emg_c4_component.py`) | Одна компонентная схема всего цифрового контура ЭМГ со всеми интеграциями из матрицы 19 систем (протоколы, форматы, направления). |

## Схема корпоративных сетей КМГ/ЭМГ (отдельный генератор)

`08-kmg-emg-corporate-networks.drawio` строится скриптом `scripts/build_kmg_emg_network_diagram.py`
(зелёная зона — сеть ЭМГ, синяя — сеть КМГ, подписанные интеграции между контурами).

```bash
pip install -r requirements.txt
python3 scripts/build_kmg_emg_network_diagram.py
```

## C4 Component диаграмма ЭМГ (отдельный генератор)

`09-emg-c4-component.drawio` строится воспроизводимым скриптом в стиле эталонной C4-диаграммы
(контуры-контейнеры, узлы «component», связи с протоколами/форматами, легенда). Источники данных:
матрица интеграций (19 систем, [`../it-landscape-emg-registry.md`](../it-landscape-emg-registry.md)),
верхнеуровневая сводная архитектура и черновик общего ландшафта.

```bash
pip install -r requirements.txt
python3 scripts/build_emg_c4_component.py
```

`.drawio` — редактируемый источник истины; одноимённый SVG ([`../svg/09-emg-c4-component.svg`](../svg/09-emg-c4-component.svg)) — статичный просмотр.

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
