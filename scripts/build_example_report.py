#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Отдельный HTML: пример анализа сроков EARM 26.2.1 / 26.2.2 (диаграмма Ганта) и факторный анализ причин сдвига.

Раздел остаётся и в общем отчёте (build_full_report.py); здесь он выпускается самостоятельным файлом в той же теме.
Запуск:  python3 scripts/build_example_report.py
"""

from pathlib import Path

import example_html as EX
import html_theme as TH
import plan_html as PH

OUT = Path(__file__).resolve().parents[1] / "docs" / "release-process-example-26-2.html"


def main() -> None:
    title = "Анализ сроков EARM 26.2.1 / 26.2.2 и факторный анализ сдвига Прода"
    secs = [("gantt", "Диаграмма Ганта и сроки", EX.example_html(False)), ("factor", "Факторный анализ причин сдвига", EX.factor_html().replace("<h3>Факторный анализ причин сдвига</h3>", "", 1))]
    nav = "".join(f'<a href="#{i}">{t}</a>' for i, t, _ in secs)
    body = "".join(f'<section id="{i}"><span class="kicker">Раздел {n}</span><h2>{t}</h2>{c}</section>' for n, (i, t, c) in enumerate(secs, 1))
    html = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><style>{TH.CSS}{PH.CSS_PLAN}</style></head><body>'
            f'<header class="top"><h1>{title}</h1><div class="muted">Выделено из общего отчёта (раздел 8); в общем отчёте раздел сохранён · сгенерировано <code>scripts/build_example_report.py</code></div></header>'
            f'<nav><div class="in">{nav}</div></nav><main>{body}</main></body></html>')
    OUT.write_text(html, encoding="utf-8")
    print("OK:", OUT, f"{len(html) // 1024} KB")


if __name__ == "__main__":
    main()
