#!/bin/bash
set -e

echo "========================================"
echo "  F2X Station Service - Update and Run"
echo "========================================"

cd "$(dirname "$0")"

echo ""
echo "[1/3] Updating from GitHub..."
git pull origin main

echo ""
echo "[2/3] Installing dependencies..."
source .venv/bin/activate
pip install -e . --quiet

echo ""
echo "[3/3] Starting Station Service..."
echo "Press Ctrl+C to stop"
python -m station_service.main
