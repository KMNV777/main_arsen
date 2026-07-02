#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Stopping old bot processes..."
pkill -f "python3 -m quotes_bot" 2>/dev/null || true
sleep 2

echo "Restarting cloudflared tunnel..."
pkill -f "cloudflared tunnel --url http://127.0.0.1:8765" 2>/dev/null || true
sleep 1

if [[ -x /tmp/cloudflared ]]; then
  nohup /tmp/cloudflared tunnel --url http://127.0.0.1:8765 --no-autoupdate > /tmp/cloudflared-quotes.log 2>&1 &
  sleep 5
  URL="$(grep -o 'https://[^ ]*trycloudflare.com' /tmp/cloudflared-quotes.log | head -1 || true)"
  if [[ -n "$URL" && -f .env ]]; then
    VERSION="$(date +%s)"
    sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=${URL}|" .env
    if grep -q '^WEBAPP_CACHE_VERSION=' .env; then
      sed -i "s|^WEBAPP_CACHE_VERSION=.*|WEBAPP_CACHE_VERSION=${VERSION}|" .env
    else
      echo "WEBAPP_CACHE_VERSION=${VERSION}" >> .env
    fi
    echo "WEBAPP_URL=${URL}"
    echo "WEBAPP_CACHE_VERSION=${VERSION}"
  fi
else
  echo "cloudflared not found at /tmp/cloudflared"
fi

echo "Starting quotes bot..."
exec python3 -m quotes_bot
