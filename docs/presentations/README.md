# Презентация: варианты интеграции ЦМ ИМА и ЕАРМ

## Файлы

| Файл | Описание |
|------|----------|
| `CM_IMA_EAPM_variants_comparison.pptx` | Итоговая презентация (сравнение 3 вариантов) |
| `assets/variant1_transfer.png` | Диаграмма варианта 1 (1-file.feUnSR) |
| `assets/variant2_embedding.png` | Диаграмма варианта 2 (2_file.OVCeIx) |
| `assets/variant3_integration.png` | Диаграмма варианта 3 (3_file.ekYFFz) |
| `assets/variants_comparison_charts.png` | Диаграммы: ТРЗ, рейтинг, критерии, плюсы/минусы |

## Соответствие источников

| Вариант | Архитектурная схема | Бэклог Excel | ТРЗ |
|---------|---------------------|--------------|-----|
| 1 — перенос функционала | 1-file.feUnSR | — | не оценивался |
| 2 — встраивание (ЕАРМ-1) | 2_file.OVCeIx | Бэклог ЦМ ИМА в ЕАРМ-1 | 281,7 / 221,5 ч/д |
| 3 — интеграция (ЕАРМ-2) | 3_file.ekYFFz | Бэклог ЦМ ИМА в ЕАРМ-2 | 126,6 / 135,5 ч/д |

## Пересборка

Требуется системный Graphviz (`apt install graphviz` или `brew install graphviz`).

```bash
pip install -r requirements.txt
python3 scripts/build_cm_ima_diagrams.py
python3 scripts/build_cm_ima_eapm_presentation.py
```

Схемы вариантов строятся через **Graphviz** (автоматическая раскладка).
Рейтинг — **тепловая карта** (heatmap) с блоком методологии на изображении.
Оформление слайдов — модуль `scripts/presentation_theme.py` (деловой стиль).
