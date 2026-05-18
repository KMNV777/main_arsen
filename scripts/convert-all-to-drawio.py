#!/usr/bin/env python3
"""Convert all Mermaid blocks in architecture/*.md to .drawio via layout-aware converter."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ARCH = Path(__file__).resolve().parent.parent / "architecture"
OUT = ARCH / "drawio"
SCRIPTS = Path(__file__).resolve().parent

FILES = [
    "01-overview.md",
    "02-domains.md",
    "03-integrations.md",
    "04-infrastructure.md",
    "05-data.md",
]

ASCII = {
    "abai": re.compile(r"abai", re.I),
    "asdc": re.compile(r"асдц|asdc|analytics", re.I),
    "sapfir": re.compile(r"сапфир|sapfir|сэд", re.I),
    "sdd": re.compile(r"сдд|контракт", re.I),
    "hr": re.compile(r"hr|team|work", re.I),
    "compliance": re.compile(r"compliance", re.I),
    "procu": re.compile(r"procu|price|закупк", re.I),
    "isup": re.compile(r"исуп|интранет", re.I),
}


def slugify(text: str) -> str:
    for key, pattern in ASCII.items():
        if pattern.search(text):
            return key
    section = re.search(r"(\d+)\.(\d+)", text)
    if section:
        return f"{section.group(1)}-{section.group(2)}"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug[:40] or "diagram"


def extract_diagrams(md_path: Path) -> list[tuple[str, str]]:
    content = md_path.read_text(encoding="utf-8")
    base = md_path.stem
    last_heading = base
    diagrams: list[tuple[str, str]] = []

    in_mermaid = False
    lines: list[str] = []

    for line in content.splitlines():
        h2 = re.match(r"^## (.+)$", line)
        if h2:
            last_heading = h2.group(1)
        if line.strip() == "```mermaid":
            in_mermaid = True
            lines = []
            continue
        if in_mermaid and line.strip() == "```":
            in_mermaid = False
            diagrams.append((last_heading, "\n".join(lines)))
            continue
        if in_mermaid:
            lines.append(line)

    result = []
    for i, (heading, source) in enumerate(diagrams):
        suffix = ""
        if len(diagrams) > 1:
            suffix = f"-{i + 1:02d}-{slugify(heading)}"
        result.append((f"{base}{suffix}", heading, source))
    return result


def convert_one(name: str, title: str, source: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / f"{name}.drawio"

    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False, encoding="utf-8") as tmp:
        tmp.write(source)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "mermaid_to_drawio.converter",
                tmp_path,
                "-o",
                str(out_path),
                "--theme",
                "default",
            ],
            cwd=SCRIPTS,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or proc.stdout)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    xml = out_path.read_text(encoding="utf-8")
    safe_title = title.replace('"', "&quot;")
    xml = xml.replace('name="Mermaid Diagram"', f'name="{safe_title}"')
    out_path.write_text(xml, encoding="utf-8")
    return out_path


def main() -> None:
    manifest: list[tuple[str, str, str]] = []

    for file in FILES:
        md_path = ARCH / file
        if not md_path.exists():
            print(f"skip missing {file}")
            continue
        for name, title, source in extract_diagrams(md_path):
            path = convert_one(name, title, source)
            manifest.append((path.name, file, title))
            print(f"OK {path}")

    readme = OUT / "README.md"
    readme.write_text(
        """# Draw.io — редактируемые схемы ИТ-ландшафта КМГ

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
"""
        + "\n".join(
            f"| [`{f}`](./{f}) | `{src}` | {title} |" for f, src, title in manifest
        )
        + """

## Примечания

- Исходный Mermaid — в `architecture/*.md`; SVG-рендеры — в `architecture/svg/`.
- Сложные `classDef` и emoji могут отличаться от GitHub; цвета правятся в Draw.io после открытия.
""",
        encoding="utf-8",
    )
    print(f"\nDone: {len(manifest)} diagrams → {OUT}")


if __name__ == "__main__":
    main()
