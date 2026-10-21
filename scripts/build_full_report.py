#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Единый HTML для ревью: описание процесса + схемы + ТРЗ/FTE + ревью + готовые тексты для Confluence.

В каждом разделе есть поле «Ваши правки»; кнопки внизу скачивают/копируют все правки одним текстом.
Запуск:  python3 scripts/build_full_report.py   (после build_release_process.py и build_trz.py)
"""

from pathlib import Path

import build_confluence as C
import build_release_process as B

OUT = Path(__file__).resolve().parents[1] / "docs" / "release-process-full.html"


def main() -> None:
    pages = [B.page_process(), B.page_branches(), B.page_matrix(), B.page_jira(), B.page_review()]
    extra = [("cf-" + i, "Confluence · " + t, fn()) for i, t, fn in C.PAGES if i not in ("trz", "review")]
    intro = ("<p class='muted'>Блоки «Confluence · …» — готовый текст страниц: после согласования правок их можно копировать в Confluence "
             "(пакет с кнопками копирования — <code>docs/confluence/confluence-pages.html</code>). Ниже в каждом разделе — поле для ваших правок.</p>")
    html = B.build_html(pages, extra=extra, trz=C.page_trz(), title="Процесс выпуска релиза ЕАРМ — материалы для ревью", comments=True)
    html = html.replace('<main>', '<main>' + intro, 1)
    OUT.write_text(html, encoding="utf-8")
    print("OK:", OUT, f"{len(html) // 1024} KB")


if __name__ == "__main__":
    main()
