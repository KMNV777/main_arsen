#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WEBAPP_PORT="${WEBAPP_PORT:-8765}"
WEBAPP_TUNNEL="${WEBAPP_TUNNEL:-localhost}"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
  WEBAPP_PORT="${WEBAPP_PORT:-8765}"
  WEBAPP_TUNNEL="${WEBAPP_TUNNEL:-localhost}"
fi

echo "Stopping old bot processes..."
pkill -f "python3 -m quotes_bot" 2>/dev/null || true
sleep 2

stop_tunnels() {
  echo "Stopping old tunnels..."
  pkill -f "cloudflared tunnel --url http://127.0.0.1:${WEBAPP_PORT}" 2>/dev/null || true
  pkill -f "localtunnel --port ${WEBAPP_PORT}" 2>/dev/null || true
  pkill -f "ssh.*nokey@localhost.run" 2>/dev/null || true
  pkill -f "ssh.*localhost.run" 2>/dev/null || true
  sleep 1
}

update_webapp_env() {
  local URL="$1"
  if [[ -z "$URL" || ! -f .env ]]; then
    return
  fi
  local VERSION
  VERSION="$(date +%s)"
  sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=${URL}|" .env
  if grep -q '^WEBAPP_CACHE_VERSION=' .env; then
    sed -i "s|^WEBAPP_CACHE_VERSION=.*|WEBAPP_CACHE_VERSION=${VERSION}|" .env
  else
    echo "WEBAPP_CACHE_VERSION=${VERSION}" >> .env
  fi
  if grep -q '^WEBAPP_TUNNEL=' .env; then
    sed -i "s|^WEBAPP_TUNNEL=.*|WEBAPP_TUNNEL=${WEBAPP_TUNNEL}|" .env
  else
    echo "WEBAPP_TUNNEL=${WEBAPP_TUNNEL}" >> .env
  fi
  echo "WEBAPP_URL=${URL}"
  echo "WEBAPP_TUNNEL=${WEBAPP_TUNNEL}"
  echo "WEBAPP_CACHE_VERSION=${VERSION}"
}

start_localhost_tunnel() {
  echo "Starting localhost.run tunnel (works better from RU than Cloudflare)..." >&2
  : > /tmp/lhr-quotes.log
  nohup ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    -R "80:127.0.0.1:${WEBAPP_PORT}" \
    nokey@localhost.run >> /tmp/lhr-quotes.log 2>&1 &

  local URL=""
  for _ in $(seq 1 30); do
    URL="$(grep -oE 'https://[a-f0-9]+\.lhr\.life' /tmp/lhr-quotes.log | head -1 || true)"
    if [[ -n "$URL" ]]; then
      break
    fi
    sleep 1
  done

  if [[ -z "$URL" ]]; then
    echo "localhost.run tunnel failed. Log tail:" >&2
    tail -20 /tmp/lhr-quotes.log >&2 || true
  fi
  printf '%s' "$URL"
}

start_cloudflare_tunnel() {
  echo "Starting cloudflared tunnel..." >&2
  if [[ ! -x /tmp/cloudflared ]]; then
    echo "cloudflared not found at /tmp/cloudflared" >&2
    return 0
  fi
  : > /tmp/cloudflared-quotes.log
  nohup /tmp/cloudflared tunnel --url "http://127.0.0.1:${WEBAPP_PORT}" --no-autoupdate \
    >> /tmp/cloudflared-quotes.log 2>&1 &
  sleep 6
  grep -o 'https://[^ ]*trycloudflare.com' /tmp/cloudflared-quotes.log | head -1 || true
}

stop_tunnels

URL=""
case "$WEBAPP_TUNNEL" in
  localhost|localhost.run|lhr)
    URL="$(start_localhost_tunnel)"
    ;;
  cloudflare|cloudflared)
    URL="$(start_cloudflare_tunnel)"
    ;;
  auto)
    URL="$(start_localhost_tunnel)"
    if [[ -z "$URL" ]]; then
      echo "Falling back to cloudflared..." >&2
      URL="$(start_cloudflare_tunnel)"
    fi
    ;;
  none|custom)
    echo "WEBAPP_TUNNEL=${WEBAPP_TUNNEL}: using WEBAPP_URL from .env as-is"
    ;;
  *)
    echo "Unknown WEBAPP_TUNNEL=${WEBAPP_TUNNEL}, using localhost"
    URL="$(start_localhost_tunnel)"
    ;;
esac

if [[ -n "$URL" ]]; then
  update_webapp_env "$URL"
elif [[ "$WEBAPP_TUNNEL" != "none" && "$WEBAPP_TUNNEL" != "custom" ]]; then
  echo "WARNING: tunnel URL not detected. Mini App may be unavailable."
fi

echo "Starting quotes bot..."
exec python3 -m quotes_bot
