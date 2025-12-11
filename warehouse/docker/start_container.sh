#!/usr/bin/env bash
set -euo pipefail
set -x

# Detect docker compose
if command -v docker compose >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "❌ docker compose not installed"
    exit 1
fi

BASE_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$BASE_DIR"

echo "▶ Starting all containers..."
$DC up -d
echo "✔ All containers started"
