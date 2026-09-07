#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "========================================================"
echo "  🧹 Shared Household Chore Manager - Dev Server"
echo "========================================================"
echo ""

if command -v uv >/dev/null 2>&1; then
    echo "[INFO] Running server with uv..."
    exec uv run python manage.py runserver "$@"
elif command -v python3 >/dev/null 2>&1; then
    echo "[INFO] Running server with python3..."
    exec python3 manage.py runserver "$@"
elif command -v python >/dev/null 2>&1; then
    echo "[INFO] Running server with python..."
    exec python manage.py runserver "$@"
else
    echo "[ERROR] Python or uv was not found in your PATH."
    exit 1
fi
