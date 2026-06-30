#!/usr/bin/env bash
# Build PDF from release 14.1 reference case markdown.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/release-14.1-reference-case.md"
OUT="$ROOT/docs/release-14.1-reference-case.pdf"

if [[ ! -f "$SRC" ]]; then
  echo "Source not found: $SRC" >&2
  echo "Run: python3 scripts/generate_release_14_1_reference_case.py" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null; then
  echo "pandoc is required. Install: apt-get install pandoc texlive-xetex texlive-fonts-recommended" >&2
  exit 1
fi

pandoc "$SRC" -o "$OUT" \
  --pdf-engine=xelatex \
  -V mainfont="DejaVu Sans" \
  -V monofont="DejaVu Sans Mono" \
  -V geometry:margin=2cm \
  -V fontsize=11pt \
  -V lang=ru \
  -V colorlinks=true \
  -V linkcolor=blue \
  --toc \
  --toc-depth=2

echo "Wrote $OUT ($(du -h "$OUT" | cut -f1))"
