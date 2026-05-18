# Draw.io — редактируемые схемы ИТ-ландшафта КМГ

Сконвертировано из Mermaid-диаграмм [PR #9](https://github.com/KMNV777/main_arsen/pull/9) конвертером [mermaid-to-drawio](https://github.com/amitkumarom/mermaid-to-drawio) (раскладка узлов и рёбер, поддержка `subgraph`).

## Как открыть

1. [diagrams.net](https://app.diagrams.net/) или Desktop Draw.io
2. **File → Open from → Device** — выбрать `.drawio`
3. После открытия: **Arrange → Layout →** *Organic* / *Horizontal Flow* — при необходимости подправить плотную раскладку

## Пересборка

```bash
cd scripts && python3 convert-all-to-drawio.py
```

## Файлы

| Файл | Источник | Описание |
|------|----------|----------|
| [`01-overview.drawio`](./01-overview.drawio) | `01-overview.md` | C4-style общий вид |
| [`02-domains.drawio`](./02-domains.drawio) | `02-domains.md` | Карта доменов и систем |
| [`03-integrations-01-abai.drawio`](./03-integrations-01-abai.drawio) | `03-integrations.md` | 3.1. Интеграции ИС ABAI |
| [`03-integrations-02-asdc.drawio`](./03-integrations-02-asdc.drawio) | `03-integrations.md` | 3.2. Интеграции АСДЦ (analytics) |
| [`03-integrations-03-sapfir.drawio`](./03-integrations-03-sapfir.drawio) | `03-integrations.md` | 3.3. Интеграции САПФИР (СЭД) |
| [`03-integrations-04-sdd.drawio`](./03-integrations-04-sdd.drawio) | `03-integrations.md` | 3.4. Интеграции СДД (контракты) |
| [`03-integrations-05-hr.drawio`](./03-integrations-05-hr.drawio) | `03-integrations.md` | 3.5. Интеграции HR-кластера (Team / Work) |
| [`03-integrations-06-compliance.drawio`](./03-integrations-06-compliance.drawio) | `03-integrations.md` | 3.6. Интеграции Compliance Control |
| [`03-integrations-07-procu.drawio`](./03-integrations-07-procu.drawio) | `03-integrations.md` | 3.7. Интеграции Procu / Price (ЗАКУПКИ) |
| [`03-integrations-08-isup.drawio`](./03-integrations-08-isup.drawio) | `03-integrations.md` | 3.8. Интеграции ИСУП и Интранета |
| [`04-infrastructure.drawio`](./04-infrastructure.drawio) | `04-infrastructure.md` | 04-infrastructure |
| [`05-data.drawio`](./05-data.drawio) | `05-data.md` | Карта данных по типам хранилищ |

## Примечания

- Исходный Mermaid — в `architecture/*.md`; SVG-рендеры — в `architecture/svg/`.
- Сложные `classDef` и emoji могут отличаться от GitHub; цвета правятся в Draw.io после открытия.
