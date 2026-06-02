# Архитектурные схемы КМГ и ЭМГ

Редактируемые диаграммы в формате **draw.io** (`.drawio`) — каталог [`docs/drawio/`](docs/drawio/).

## Главная схема (корпоративные сети + интеграции)

| Формат | Файл |
|--------|------|
| **draw.io** | [`docs/drawio/08-kmg-emg-corporate-networks.drawio`](docs/drawio/08-kmg-emg-corporate-networks.drawio) |
| SVG (просмотр) | [`docs/svg/08-kmg-emg-corporate-networks.svg`](docs/svg/08-kmg-emg-corporate-networks.svg) |

**Открытие:** GitHub → файл `.drawio` → **Open with draw.io** (при включённой интеграции) или скачать и открыть в [app.diagrams.net](https://app.diagrams.net).

Полное описание и остальные схемы: [`docs/architecture-emg-integrations.md`](docs/architecture-emg-integrations.md) · каталог draw.io: [`docs/drawio/README.md`](docs/drawio/README.md).

### Пересборка draw.io

```bash
pip install -r requirements.txt
python3 scripts/build_kmg_emg_network_diagram.py   # общая схема КМГ/ЭМГ
python3 scripts/build_emg_c4_component.py          # C4-компоненты ЭМГ
python3 scripts/mmd_to_drawio.py                   # остальные схемы из Mermaid
```
