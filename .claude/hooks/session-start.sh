#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

npm install

if npx playwright install 2>&1; then
  echo "Playwright browsers installed successfully."
else
  echo "WARNING: Playwright browser download failed (cdn.playwright.dev may not be in network allowlist)." >&2
  echo "Add cdn.playwright.dev to your environment's network allowlist to enable browser testing." >&2
fi
