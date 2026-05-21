# SVG-схемы архитектуры ЭМГ

Все диаграммы из [`architecture-emg-integrations.md`](../architecture-emg-integrations.md) и общий ландшафт.

| Файл | Раздел документа | Описание |
|------|------------------|----------|
| [`00-summary-architecture.svg`](00-summary-architecture.svg) | §0 | Сводная архитектура: КМГ + ЭМГ + интеграции |
| [`01-corporate-landscape.svg`](01-corporate-landscape.svg) | §1 | Общий ландшафт корпоративных систем |
| [`02-1-emg-abai-focus.svg`](02-1-emg-abai-focus.svg) | §2.1 | Фокус ЭМГ: ABAI и смежные ИС |
| [`03-abai-im-architecture.svg`](03-abai-im-architecture.svg) | §3 | Архитектура ИМ / ABAI (10.32.10.99) |
| [`04-sap-erp-integrations.svg`](04-sap-erp-integrations.svg) | §4 | Интеграции SAP ERP |
| [`05-abai-layers.svg`](05-abai-layers.svg) | §5 | Слои L1–L4 (OT → ИМ → сервисы) |
| [`06-it-landscape-general.svg`](06-it-landscape-general.svg) | ландшафт | Общий ИТ-ландшафт по слоям L0–L5 |
| [`07-it-landscape-mermaid-detailed.svg`](07-it-landscape-mermaid-detailed.svg) | ландшафт | Детальная Mermaid-версия ландшафта |

Исходники Mermaid: `*.mmd` в этой папке.

Пересборка:

```bash
cd docs/svg
npx @mermaid-js/mermaid-cli -i 00-summary-architecture.mmd -o 00-summary-architecture.svg -b transparent
```
