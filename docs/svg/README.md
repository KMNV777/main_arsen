# SVG-схемы архитектуры ЭМГ

Все диаграммы из [`architecture-emg-integrations.md`](../architecture-emg-integrations.md) и общий ландшафт.

**Редактируемые схемы (draw.io):** [`../drawio/`](../drawio/) — полный каталог в [`../drawio/README.md`](../drawio/README.md).

| Файл | Раздел документа | Техническое описание | Бизнес-объяснение |
|------|------------------|----------------------|-------------------|
| [`00-summary-architecture.svg`](00-summary-architecture.svg) | §0 | Сводная архитектура: КМГ + ЭМГ + интеграции | Верхнеуровневое объяснение, как ЭМГ встроен в цифровой контур КМГ. |
| [`01-corporate-landscape.svg`](01-corporate-landscape.svg) | §1 | Общий ландшафт корпоративных систем | Видно, какие системы обеспечивают ключевые бизнес-функции и как они взаимозависимы. |
| [`02-1-emg-abai-focus.svg`](02-1-emg-abai-focus.svg) | §2.1 | Фокус ЭМГ: ABAI и смежные ИС | Показывает влияние ABAI на смежные процессы и риски изменений в производственном контуре. |
| [`03-abai-im-architecture.svg`](03-abai-im-architecture.svg) | §3 | Архитектура ИМ / ABAI (10.32.10.99) | Отражает жизненный цикл промысловых данных: сбор, обработка, доставка аналитики. |
| [`04-sap-erp-integrations.svg`](04-sap-erp-integrations.svg) | §4 | Интеграции SAP ERP | Поясняет роль SAP как центра сквозных процессов: финансы, закупки, кадры, внешние контрагенты. |
| [`05-abai-layers.svg`](05-abai-layers.svg) | §5 | Слои L1-L4 (OT → ИМ → сервисы) | Объясняет уровни архитектуры для обсуждения ответственности и точек отказа. |
| [`06-it-landscape-general.svg`](06-it-landscape-general.svg) | ландшафт | Общий ИТ-ландшафт по слоям L0-L5 | Базовая карта для руководителей: критичные системы и их связи в одном слайде. |
| [`07-it-landscape-mermaid-detailed.svg`](07-it-landscape-mermaid-detailed.svg) | ландшафт | Детальная Mermaid-версия ландшафта | Нужна для детального разбора интеграций после обзорной презентации. |
| [`10-kmg-emg-architecture.svg`](10-kmg-emg-architecture.svg) | §8 | **Общая архитектура КМГ + ЭМГ**: выделены корпоративная сеть КМГ и сеть ЭМГ, проброшены интеграции между системами | Показывает границу сетей КМГ/ЭМГ и кросс-сетевые интеграции на одном слайде для руководства. |

Исходники Mermaid: `*.mmd` в этой папке. Файл `10-kmg-emg-architecture.svg` генерируется скриптом `scripts/build_kmg_emg_architecture.py` (Mermaid-исходника не имеет).

Пересборка:

```bash
cd docs/svg
npx @mermaid-js/mermaid-cli -i 00-summary-architecture.mmd -o 00-summary-architecture.svg -b transparent
```
