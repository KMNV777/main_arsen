#!/usr/bin/env bash
# Копирует скиллы и агентов из этого репозитория в ~/.claude (для всех проектов на этом компьютере).
# Существующие у вас файлы не перезаписываются. Запуск: bash scripts/install-skills-local.sh
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/.claude"
DST="${CLAUDE_HOME:-$HOME/.claude}"

[ -d "$SRC/skills" ] || { echo "Не найдена папка $SRC/skills"; exit 1; }
mkdir -p "$DST/skills" "$DST/agents"

before=$(ls "$DST/skills" | wc -l | tr -d ' ')
cp -Rn "$SRC/skills/." "$DST/skills/"
[ -d "$SRC/agents" ] && cp -Rn "$SRC/agents/." "$DST/agents/"
after=$(ls "$DST/skills" | wc -l | tr -d ' ')

# В скиллах seo-* зашиты пути облачного окружения: заменяем их на путь этого компьютера
grep -rlI "/home/user/main_arsen/.claude" "$DST/skills" "$DST/agents" 2>/dev/null \
  | xargs -I{} perl -pi -e "s#/home/user/main_arsen/\.claude#$DST#g" {} || true

echo "Готово. Скиллов было: $before, стало: $after. Папка: $DST"
echo "Перезапустите Claude Code, чтобы скиллы подхватились."
