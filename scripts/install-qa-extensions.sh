#!/usr/bin/env bash
# Install VS Code / Cursor extensions for manual QA workflows (Open VSX).
set -euo pipefail

EXTENSIONS_DIR="${CURSOR_EXTENSIONS_DIR:-$HOME/.cursor-server/extensions}"
TMP_DIR="${TMPDIR:-/tmp}/qa-vsix-$$"
mkdir -p "$EXTENSIONS_DIR" "$TMP_DIR"
trap 'rm -rf "$TMP_DIR"' EXIT

EXTENSIONS=(
  humao.rest-client
  rangav.vscode-thunder-client
  ms-playwright.playwright
  cweijan.vscode-database-client2
  redhat.vscode-yaml
  redhat.vscode-xml
  42Crunch.vscode-openapi
  eamodio.gitlens
  usernamehw.errorlens
  mikestead.dotenv
  mechatroner.rainbow-csv
  esbenp.prettier-vscode
  formulahendry.code-runner
  johnpapa.vscode-peacock
  yzhang.markdown-all-in-one
  hediet.vscode-drawio
  postman.postman-for-vscode
)

install_one() {
  local id="$1"
  local publisher="${id%%.*}"
  local name="${id#*.}"
  local api_url="https://open-vsx.org/api/${publisher}/${name}"

  echo "==> ${id}"

  local meta
  if ! meta="$(curl -fsSL "$api_url" 2>/dev/null)"; then
    echo "    SKIP: not found on Open VSX (${api_url})"
    return 1
  fi

  local version download_url target_dir vsix
  version="$(echo "$meta" | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])")"
  download_url="$(echo "$meta" | python3 -c "import sys,json; print(json.load(sys.stdin)['files']['download'])")"
  target_dir="${EXTENSIONS_DIR}/${publisher}.${name}-${version}"
  vsix="${TMP_DIR}/${publisher}.${name}-${version}.vsix"

  if [[ -d "$target_dir" && -f "${target_dir}/package.json" ]]; then
    echo "    OK: already installed (${target_dir})"
    return 0
  fi

  local extract_dir="${TMP_DIR}/extract-${publisher}.${name}"
  curl -fsSL "$download_url" -o "$vsix"
  rm -rf "$target_dir" "$extract_dir"
  mkdir -p "$extract_dir"
  unzip -q "$vsix" -d "$extract_dir"
  rm -f "$vsix"

  if [[ -d "${extract_dir}/extension" ]]; then
    mv "${extract_dir}/extension" "$target_dir"
  else
    mv "$extract_dir" "$target_dir"
  fi
  rm -rf "$extract_dir"

  echo "    OK: ${target_dir}"
}

installed=0
skipped=0

for id in "${EXTENSIONS[@]}"; do
  if install_one "$id"; then
    ((installed++)) || true
  else
    ((skipped++)) || true
  fi
done

EXTENSIONS_DIR="$EXTENSIONS_DIR" python3 <<'PY'
import json
import os
from pathlib import Path

ext_dir = Path(os.environ["EXTENSIONS_DIR"])
entries = []
for child in sorted(ext_dir.iterdir()):
    pkg = child / "package.json"
    if not pkg.is_file():
        continue
    data = json.loads(pkg.read_text(encoding="utf-8"))
    identifier = {"id": f"{data['publisher']}.{data['name']}"}
    version = data.get("version", "")
    entries.append(
        {
            "identifier": identifier,
            "version": version,
            "location": {"$mid": 1, "path": str(child), "scheme": "file"},
            "relativeLocation": child.name,
        }
    )

manifest = ext_dir / "extensions.json"
manifest.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {manifest} ({len(entries)} extensions)")
PY

echo ""
echo "Done: ${installed} installed/updated, ${skipped} skipped."
echo "Extensions directory: ${EXTENSIONS_DIR}"
echo "Reload Cursor window to activate new extensions."
