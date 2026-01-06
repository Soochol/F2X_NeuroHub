#!/bin/bash
set -e

echo "========================================"
echo "  F2X Station 2 - Update and Run"
echo "  Port: 8081"
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
echo "[3/3] Starting Station 2..."
echo "Press Ctrl+C to stop"
export STATION_CONFIG=./config/station2.yaml
python -m station_service.main
