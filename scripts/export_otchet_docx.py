#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the ИТ-landscape report (Markdown) to DOCX.

Конвертирует docs/otchet-it-landshaft-emg.md → docs/otchet-it-landshaft-emg.docx
через pandoc (pypandoc). Ручное «Оглавление» из Markdown заменяется на нативное
оглавление Word (--toc), таблицы GFM переносятся как таблицы Word.

Запуск:
    pip install -r requirements.txt
    python3 scripts/export_otchet_docx.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "otchet-it-landshaft-emg.md"
OUT = ROOT / "docs" / "otchet-it-landshaft-emg.docx"


def preprocess(md: str) -> str:
    """Убрать ручное Оглавление (его заменит нативный --toc Word)."""
    md = re.sub(r"\n## Оглавление\n.*?\n---\n", "\n", md, count=1, flags=re.DOTALL)
    return md


def main() -> None:
    md = preprocess(SRC.read_text(encoding="utf-8"))
    pypandoc.convert_text(
        md,
        to="docx",
        format="gfm",
        outputfile=str(OUT),
        extra_args=[
            "--toc",
            "--toc-depth=3",
            "--metadata", "title=Отчёт по результатам исследования ИТ-ландшафта АО «Эмбамунайгаз»",
            "--metadata", "lang=ru-RU",
        ],
    )
    print(f"OK docx -> {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
