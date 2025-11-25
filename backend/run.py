"""
Uvicorn Runner with Timestamp Logging and Colors

Usage:
    uv run python run.py

Or with options:
    uv run python run.py --port 8080
"""
import sys
import os

# Ensure colorama is initialized for Windows terminal color support
try:
    import colorama
    colorama.init()
except ImportError:
    pass

import uvicorn
from log_config import LOGGING_CONFIG

if __name__ == "__main__":
    # Default settings
    host = "0.0.0.0"
    port = 8000
    reload = True

    # Parse simple command line args
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
        elif arg == "--host" and i + 1 < len(args):
            host = args[i + 1]
        elif arg == "--no-reload":
            reload = False

    print(f"\n🚀 Starting F2X NeuroHub API Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Docs: http://localhost:{port}/api/v1/docs\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_config=LOGGING_CONFIG,
    )
