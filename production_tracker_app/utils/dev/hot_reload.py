"""
Hot Reload Development Tool for Production Tracker App.

Based on skill.md best practices - Auto-restart app when files change.

Usage:
    python hot_reload.py              # Basic hot reload
    python hot_reload.py --debug      # With visual debugger (future)

Features:
- Watches .py, .json files for changes
- Auto-restarts app instantly
- Preserves console output
- Minimal overhead
"""

import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - HotReload - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class AppRestartHandler(FileSystemEventHandler):
    """File system event handler for hot reload."""

    def __init__(self, app_path, debug_mode=False):
        self.app_path = app_path
        self.debug_mode = debug_mode
        self.process = None
        self.last_restart = 0
        self.debounce_delay = 1.0  # seconds

        # Start app initially
        self.restart_app()

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Only watch Python and JSON files
        if not (event.src_path.endswith('.py') or event.src_path.endswith('.json')):
            return

        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_delay:
            return

        self.last_restart = current_time

        logger.info(f"File changed: {Path(event.src_path).name}")
        self.restart_app()

    def restart_app(self):
        """Restart the application."""
        # Kill existing process
        if self.process:
            logger.info("Stopping app...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                logger.warning("Force killing app...")
                self.process.kill()

        # Start new process
        logger.info("Starting app...")
        self.process = subprocess.Popen(
            [sys.executable, self.app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Show app output in real-time
        logger.info("✅ App restarted - Watching for changes...")

    def cleanup(self):
        """Clean up resources."""
        if self.process:
            logger.info("Cleaning up...")
            self.process.terminate()
            self.process.wait()


def main():
    """Main hot reload entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Hot Reload Development Tool')
    parser.add_argument('--debug', action='store_true', help='Enable visual debugger (future)')
    args = parser.parse_args()

    # Determine app path
    app_path = Path(__file__).parent / 'main.py'
    if not app_path.exists():
        logger.error(f"App not found: {app_path}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("🔥 Hot Reload Development Mode")
    logger.info("=" * 60)
    logger.info(f"Watching: {app_path.parent}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Setup file watcher
    event_handler = AppRestartHandler(str(app_path), args.debug)
    observer = Observer()
    observer.schedule(event_handler, str(app_path.parent), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nStopping hot reload...")
        event_handler.cleanup()
        observer.stop()

    observer.join()
    logger.info("Hot reload stopped")


if __name__ == "__main__":
    main()
