#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WEBAPP_PORT="${WEBAPP_PORT:-8765}"
WEBAPP_TUNNEL="${WEBAPP_TUNNEL:-auto}"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
  WEBAPP_PORT="${WEBAPP_PORT:-8765}"
  WEBAPP_TUNNEL="${WEBAPP_TUNNEL:-auto}"
fi

echo "Stopping old bot processes..."
pkill -f "python3 -m quotes_bot" 2>/dev/null || true
sleep 2

start_webapp_background() {
  echo "Starting webapp for tunnel check..." >&2
  python3 -m quotes_bot >> /tmp/quotes-bot.log 2>&1 &
  WEBAPP_PID=$!
  for _ in $(seq 1 40); do
    if curl -s -o /dev/null --max-time 2 "http://127.0.0.1:${WEBAPP_PORT}/"; then
      echo "Webapp ready on port ${WEBAPP_PORT}" >&2
      return 0
    fi
    if ! kill -0 "$WEBAPP_PID" 2>/dev/null; then
      echo "Bot process exited during startup. Log tail:" >&2
      tail -30 /tmp/quotes-bot.log >&2 || true
      return 1
    fi
    sleep 1
  done
  echo "Webapp did not become ready in time" >&2
  return 1
}

stop_webapp_background() {
  if [[ -n "${WEBAPP_PID:-}" ]] && kill -0 "$WEBAPP_PID" 2>/dev/null; then
    kill "$WEBAPP_PID" 2>/dev/null || true
    wait "$WEBAPP_PID" 2>/dev/null || true
  fi
  pkill -f "python3 -m quotes_bot" 2>/dev/null || true
  sleep 2
}

stop_tunnels() {
  echo "Stopping old tunnels..." >&2
  pkill -f "cloudflared tunnel --url http://127.0.0.1:${WEBAPP_PORT}" 2>/dev/null || true
  pkill -f "localtunnel --port ${WEBAPP_PORT}" 2>/dev/null || true
  pkill -f "ssh.*nokey@localhost.run" 2>/dev/null || true
  pkill -f "ssh.*localhost.run" 2>/dev/null || true
  pkill -f "ssh.*a.pinggy.io" 2>/dev/null || true
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

verify_tunnel() {
  local URL="$1"
  if [[ -z "$URL" ]]; then
    return 1
  fi
  local STATUS BODY
  STATUS="$(curl -s -o /tmp/tunnel-check.html -w "%{http_code}" --max-time 20 "$URL/" || echo "000")"
  BODY="$(tr '[:upper:]' '[:lower:]' < /tmp/tunnel-check.html | head -c 800 || true)"
  if [[ "$STATUS" != "200" ]]; then
    echo "Tunnel check failed: HTTP ${STATUS} for ${URL}" >&2
    return 1
  fi
  if [[ "$BODY" == *"no tunnel here"* ]]; then
    echo "Tunnel check failed: endpoint returned 'no tunnel here'" >&2
    return 1
  fi
  if [[ "$BODY" == *"cloudflare"* && "$BODY" == *"error"* ]]; then
    echo "Tunnel check failed: Cloudflare error page" >&2
    return 1
  fi
  echo "Tunnel OK: ${URL}" >&2
  return 0
}

start_pinggy_tunnel() {
  echo "Starting Pinggy tunnel..." >&2
  : > /tmp/pinggy-quotes.log
  nohup ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -p 443 \
    -R0:127.0.0.1:${WEBAPP_PORT} \
    a.pinggy.io >> /tmp/pinggy-quotes.log 2>&1 &

  local URL=""
  for _ in $(seq 1 30); do
    URL="$(grep -oE 'https://[^ ]+\.free\.pinggy\.net' /tmp/pinggy-quotes.log | head -1 || true)"
    if [[ -n "$URL" ]]; then
      break
    fi
    sleep 1
  done

  if [[ -z "$URL" ]]; then
    echo "Pinggy tunnel failed. Log tail:" >&2
    tail -20 /tmp/pinggy-quotes.log >&2 || true
  fi
  printf '%s' "$URL"
}

start_localhost_tunnel() {
  echo "Starting localhost.run tunnel..." >&2
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

try_tunnel_provider() {
  local provider="$1"
  local candidate=""
  case "$provider" in
    pinggy) candidate="$(start_pinggy_tunnel)" ;;
    localhost|localhost.run|lhr) candidate="$(start_localhost_tunnel)" ;;
    cloudflare|cloudflared) candidate="$(start_cloudflare_tunnel)" ;;
    *) return 1 ;;
  esac
  if [[ -z "$candidate" ]]; then
    stop_tunnels
    return 1
  fi
  sleep 2
  if verify_tunnel "$candidate"; then
    printf '%s' "$candidate"
    return 0
  fi
  echo "Discarding bad tunnel from ${provider}: ${candidate}" >&2
  stop_tunnels
  return 1
}

stop_tunnels

if ! start_webapp_background; then
  echo "ERROR: could not start webapp. See /tmp/quotes-bot.log" >&2
  exit 1
fi

URL=""
case "$WEBAPP_TUNNEL" in
  pinggy)
    URL="$(try_tunnel_provider pinggy || true)"
    ;;
  localhost|localhost.run|lhr)
    URL="$(try_tunnel_provider localhost || true)"
    ;;
  cloudflare|cloudflared)
    URL="$(try_tunnel_provider cloudflare || true)"
    ;;
  auto)
    for provider in pinggy localhost cloudflare; do
      echo "Trying tunnel provider: ${provider}" >&2
      URL="$(try_tunnel_provider "$provider" || true)"
      if [[ -n "$URL" ]]; then
        WEBAPP_TUNNEL="$provider"
        break
      fi
    done
    ;;
  none|custom)
    echo "WEBAPP_TUNNEL=${WEBAPP_TUNNEL}: using WEBAPP_URL from .env as-is"
    ;;
  *)
    echo "Unknown WEBAPP_TUNNEL=${WEBAPP_TUNNEL}, using auto" >&2
    WEBAPP_TUNNEL=auto
    for provider in pinggy localhost cloudflare; do
      URL="$(try_tunnel_provider "$provider" || true)"
      if [[ -n "$URL" ]]; then
        WEBAPP_TUNNEL="$provider"
        break
      fi
    done
    ;;
esac

if [[ -n "$URL" ]]; then
  update_webapp_env "$URL"
elif [[ "$WEBAPP_TUNNEL" != "none" && "$WEBAPP_TUNNEL" != "custom" ]]; then
  echo "WARNING: no working tunnel found. Mini App will be unavailable." >&2
fi

stop_webapp_background

echo "Starting quotes bot..."
exec python3 -m quotes_bot
