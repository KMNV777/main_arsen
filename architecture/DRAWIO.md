# Draw.io — схемы ИТ-ландшафта КМГ

## Файлы

| Файл | Назначение |
|------|------------|
| [`kmg-it-landscape.drawio`](./kmg-it-landscape.drawio) | Общий ландшафт: пользователи, источники, внешние сервисы, ИС, слои + **84 связи** |
| [`kmg-integrations.drawio`](./kmg-integrations.drawio) | Только потоки интеграций (реестр), по группам — **67 потоков** в swimlane |
| [`kmg-connections.csv`](./kmg-connections.csv) | Таблица связей для правок / импорта (источник;приёмник;технология;группа) |
| [`ИТ Ландшафт КМГ.drawio`](./%D0%98%D0%A2%20%D0%9B%D0%B0%D0%BD%D0%B4%D1%88%D0%B0%D1%84%D1%82%20%D0%9A%D0%9C%D0%93.drawio) | **Ваша схема** (страница «Страница-1») + **59 интеграционных связей** из реестра |

## Как открыть

1. [https://app.diagrams.net/](https://app.diagrams.net/) (draw.io) или Desktop-приложение.
2. **File → Open from → Device** → выбрать `.drawio` файл.
3. Либо перетащить файл в окно draw.io.

Формат **полностью редактируемый**: узлы, подписи на стрелках, цвета, расположение.

## Добавить связи в свой draw.io (viewer URL)

1. Сохраните ссылку viewer или экспортируйте `.drawio` в `architecture/viewer_fragment.txt` (полный URL или фрагмент после `#R`).
2. Выполните:

```bash
cd architecture
python3 merge_drawio_edges.py --url-fragment viewer_fragment.txt -o "ИТ Ландшафт КМГ.drawio"
```

Скрипт декодирует сжатый `#R`-фрагмент diagrams.net и добавляет потоки из `generate_drawio_integrations.FLOWS`, сопоставляя узлы по подписям (в т.ч. «ИС ABAI», «САПФИР (Directum RX)», агрегат MySQL SCADA-буферы).

## Как перегенерировать из репозитория

```bash
cd architecture
python3 generate_drawio.py
python3 generate_drawio_integrations.py
python3 -c "
import csv
from generate_drawio_integrations import FLOWS
with open('kmg-connections.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f,delimiter=';')
    w.writerow(['Источник','Приёмник','Технология/частота','Группа'])
    for row in FLOWS:
        w.writerow(row)
print('kmg-connections.csv')
"
```

## Легенда на схеме ландшафта

| Цвет | Тип |
|------|-----|
| Голубой | Пользователи |
| Оранжевый | Гос. сервисы |
| Розовый | Внешние коммерческие |
| Фиолетовый | Внутренние источники |
| Зелёный | Прикладные ИС (PROD) |
| Жёлтый | ТЕСТ (Procu/Price) |
| Красный | ВЫВОД / ОТКЛЮЧЕНА |
| Серый пунктир | Технологические слои |

## Примечания

- Связи **не проходят через ABAI как единый data layer** — отражены фактические point-to-point интеграции из реестра.
- На общей схеме много пересечений стрелок; для детальной работы удобнее **`kmg-integrations.drawio`** (группы по доменам).
- После открытия рекомендуется: **Arrange → Layout → Vertical/Horizontal** для отдельных swimlane при необходимости.
