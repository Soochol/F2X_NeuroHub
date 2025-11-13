"""
Module Explorer - Interactive CLI for managing modular structure

This tool provides a command-line interface for:
- Viewing module status and statistics
- Listing sessions and snapshots
- Rolling back to previous states
- Comparing module versions
- Visualizing module dependencies
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

from utils.module_manager import ModuleManager
from utils.session_manager import SessionManager


class ModuleExplorer:
    """Interactive CLI for exploring and managing modules."""

    def __init__(self):
        """Initialize ModuleExplorer."""
        self.module_manager = ModuleManager()
        self.session_manager = SessionManager()

    def list_modules(self, verbose: bool = False) -> None:
        """
        List all modules with their status.

        Args:
            verbose: If True, show detailed information
        """
        modules = self.module_manager.list_modules()

        if not modules:
            print("No modules found.")
            return

        print(f"\n{'=' * 80}")
        print(f"F2X NeuroHub Modules ({len(modules)} total)")
        print(f"{'=' * 80}\n")

        for module in modules:
            print(f"📦 {module['name']}")
            print(f"   Status: {module['status']}")
            print(f"   Created: {module['created_at']}")

            if verbose:
                stats = self.module_manager.get_module_stats(module['name'])
                if stats:
                    print(f"   Files: {stats['total_files']}")
                    print(f"   Sessions: {stats['total_sessions']}")
                    print(f"   Size: {stats['disk_usage_mb']:.2f} MB")

                sessions = module.get('sessions', [])
                if sessions:
                    print(f"   Last session: {sessions[-1]['session_id']}")

            print()

    def show_module_status(self, module_name: str) -> None:
        """
        Show detailed status for a specific module.

        Args:
            module_name: Name of the module
        """
        if not self.module_manager.module_exists(module_name):
            print(f"❌ Module '{module_name}' not found")
            return

        print(f"\n{'=' * 80}")
        print(f"Module: {module_name}")
        print(f"{'=' * 80}\n")

        # Module info
        info = self.module_manager.get_module_info(module_name)
        print(f"Status: {info['status']}")
        print(f"Version: {info['version']}")
        print(f"Created: {info['created_at']}")
        print(f"Last Updated: {info['last_updated']}")

        if info.get('description'):
            print(f"Description: {info['description']}")

        # Statistics
        print(f"\n{'Statistics':-^80}")
        stats = self.module_manager.get_module_stats(module_name)
        if stats:
            print(f"Total Files: {stats['total_files']}")
            print(f"  - Requirements: {stats['requirements_docs']}")
            print(f"  - Design Docs: {stats['design_docs']}")
            print(f"  - Source Files: {stats['source_files']}")
            print(f"  - Test Files: {stats['test_files']}")
            print(f"  - Verification: {stats['verification_reports']}")
            print(f"Total Sessions: {stats['total_sessions']}")
            print(f"Disk Usage: {stats['disk_usage_mb']:.2f} MB")

        # Recent sessions
        sessions = self.session_manager.list_sessions(module_name)
        if sessions:
            print(f"\n{'Recent Sessions':-^80}")
            for session in sessions[:5]:  # Show last 5 sessions
                status_emoji = "✅" if session['status'] == 'completed' else "🔄"
                print(f"{status_emoji} {session['session_id']}")
                print(f"   Type: {session['session_type']}")
                print(f"   Status: {session['status']}")
                print(f"   Created: {session['created_at']}")
                if session.get('description'):
                    print(f"   Description: {session['description']}")

                agents = session.get('agents_executed', [])
                if agents:
                    print(f"   Agents: {', '.join([a['agent_name'] for a in agents])}")

                print()

    def list_sessions(self, module_name: str, limit: int = 10) -> None:
        """
        List sessions for a module.

        Args:
            module_name: Name of the module
            limit: Maximum number of sessions to show
        """
        if not self.module_manager.module_exists(module_name):
            print(f"❌ Module '{module_name}' not found")
            return

        sessions = self.session_manager.list_sessions(module_name)

        if not sessions:
            print(f"No sessions found for module '{module_name}'")
            return

        print(f"\n{'=' * 80}")
        print(f"Sessions for module: {module_name} ({len(sessions)} total)")
        print(f"{'=' * 80}\n")

        for session in sessions[:limit]:
            status_emoji = {
                'completed': '✅',
                'in_progress': '🔄',
                'failed': '❌',
                'cancelled': '⏹️'
            }.get(session['status'], '❓')

            print(f"{status_emoji} {session['session_id']}")
            print(f"   Type: {session['session_type']}")
            print(f"   Status: {session['status']}")
            print(f"   Created: {session['created_at']}")

            if session.get('completed_at'):
                print(f"   Completed: {session['completed_at']}")

            if session.get('description'):
                print(f"   Description: {session['description']}")

            # Metrics
            metrics = session.get('metrics', {})
            if metrics.get('execution_time_seconds'):
                duration = metrics['execution_time_seconds']
                print(f"   Duration: {duration:.1f}s ({duration/60:.1f}m)")

            if metrics.get('total_files'):
                print(f"   Files: {metrics['total_files']}")

            if metrics.get('test_coverage'):
                print(f"   Coverage: {metrics['test_coverage']:.1f}%")

            # Agents executed
            agents = session.get('agents_executed', [])
            if agents:
                agent_names = [a['agent_name'] for a in agents]
                print(f"   Agents: {', '.join(agent_names)}")

            print()

    def show_session_details(self, module_name: str, session_id: str) -> None:
        """
        Show detailed information about a session.

        Args:
            module_name: Name of the module
            session_id: ID of the session
        """
        session = self.session_manager.get_session_info(module_name, session_id)

        if not session:
            print(f"❌ Session '{session_id}' not found for module '{module_name}'")
            return

        print(f"\n{'=' * 80}")
        print(f"Session Details: {session_id}")
        print(f"{'=' * 80}\n")

        print(f"Module: {module_name}")
        print(f"Type: {session['session_type']}")
        print(f"Status: {session['status']}")
        print(f"Created: {session['created_at']}")

        if session.get('completed_at'):
            print(f"Completed: {session['completed_at']}")

        if session.get('description'):
            print(f"Description: {session['description']}")

        # Metrics
        print(f"\n{'Metrics':-^80}")
        metrics = session.get('metrics', {})
        for key, value in metrics.items():
            print(f"{key}: {value}")

        # Agent execution log
        agents = session.get('agents_executed', [])
        if agents:
            print(f"\n{'Agent Execution Log':-^80}")
            for agent in agents:
                status_emoji = "✅" if agent['status'] == 'success' else "❌"
                print(f"{status_emoji} {agent['agent_name']}")
                print(f"   Executed: {agent['executed_at']}")
                print(f"   Duration: {agent['duration_seconds']:.1f}s")
                print(f"   Status: {agent['status']}")

                if agent.get('artifacts'):
                    print(f"   Artifacts: {len(agent['artifacts'])} files")
                    for artifact in agent['artifacts'][:5]:  # Show first 5
                        print(f"      - {artifact}")
                print()

        # Snapshots
        snapshot_count = session.get('snapshot_count', 0)
        if snapshot_count > 0:
            print(f"\n{'Snapshots':-^80}")
            print(f"Total snapshots: {snapshot_count}")

    def rollback(self, module_name: str, session_id: str, snapshot_name: str) -> None:
        """
        Rollback module to a specific snapshot.

        Args:
            module_name: Name of the module
            session_id: ID of the session
            snapshot_name: Name of the snapshot
        """
        print(f"\n⚠️  Rolling back module '{module_name}' to snapshot '{snapshot_name}'...")
        print(f"   Session: {session_id}")
        print(f"\n   This will replace the current state with the snapshot.")

        # In a real CLI, we'd ask for confirmation here
        print(f"\n   Creating backup before rollback...")

        result = self.session_manager.rollback_to_snapshot(
            module_name,
            session_id,
            snapshot_name,
            create_backup=True
        )

        if result['success']:
            print(f"\n✅ {result['message']}")
            if result.get('backup'):
                print(f"\n   Backup created:")
                print(f"      Session: {result['backup']['session_id']}")
                print(f"      Snapshot: {result['backup']['snapshot_name']}")
        else:
            print(f"\n❌ Rollback failed: {result['message']}")

    def compare_sessions(self, module_name: str, session1: str, session2: str) -> None:
        """
        Compare two sessions (placeholder for future implementation).

        Args:
            module_name: Name of the module
            session1: First session ID
            session2: Second session ID
        """
        sess1 = self.session_manager.get_session_info(module_name, session1)
        sess2 = self.session_manager.get_session_info(module_name, session2)

        if not sess1 or not sess2:
            print("❌ One or both sessions not found")
            return

        print(f"\n{'=' * 80}")
        print(f"Comparing Sessions")
        print(f"{'=' * 80}\n")

        print(f"Session 1: {session1}")
        print(f"  Type: {sess1['session_type']}")
        print(f"  Created: {sess1['created_at']}")
        print(f"  Status: {sess1['status']}")

        print(f"\nSession 2: {session2}")
        print(f"  Type: {sess2['session_type']}")
        print(f"  Created: {sess2['created_at']}")
        print(f"  Status: {sess2['status']}")

        print(f"\n{'Metrics Comparison':-^80}")
        metrics1 = sess1.get('metrics', {})
        metrics2 = sess2.get('metrics', {})

        all_keys = set(metrics1.keys()) | set(metrics2.keys())
        for key in sorted(all_keys):
            val1 = metrics1.get(key, 'N/A')
            val2 = metrics2.get(key, 'N/A')
            print(f"{key}:")
            print(f"  Session 1: {val1}")
            print(f"  Session 2: {val2}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='F2X NeuroHub Module Explorer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all modules
  python module_explorer.py list

  # Show module status
  python module_explorer.py status inventory

  # List sessions for a module
  python module_explorer.py sessions inventory

  # Show session details
  python module_explorer.py session inventory 2025-01-15-10-30-feature

  # Rollback to a snapshot
  python module_explorer.py rollback inventory 2025-01-15-10-30-feature auto-20250115-103045
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List modules
    list_parser = subparsers.add_parser('list', help='List all modules')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')

    # Show module status
    status_parser = subparsers.add_parser('status', help='Show module status')
    status_parser.add_argument('module', help='Module name')

    # List sessions
    sessions_parser = subparsers.add_parser('sessions', help='List sessions for a module')
    sessions_parser.add_argument('module', help='Module name')
    sessions_parser.add_argument('--limit', type=int, default=10, help='Maximum sessions to show')

    # Show session details
    session_parser = subparsers.add_parser('session', help='Show session details')
    session_parser.add_argument('module', help='Module name')
    session_parser.add_argument('session_id', help='Session ID')

    # Rollback
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to a snapshot')
    rollback_parser.add_argument('module', help='Module name')
    rollback_parser.add_argument('session_id', help='Session ID')
    rollback_parser.add_argument('snapshot', help='Snapshot name')

    # Compare sessions
    compare_parser = subparsers.add_parser('compare', help='Compare two sessions')
    compare_parser.add_argument('module', help='Module name')
    compare_parser.add_argument('session1', help='First session ID')
    compare_parser.add_argument('session2', help='Second session ID')

    args = parser.parse_args()

    explorer = ModuleExplorer()

    if args.command == 'list':
        explorer.list_modules(verbose=args.verbose)
    elif args.command == 'status':
        explorer.show_module_status(args.module)
    elif args.command == 'sessions':
        explorer.list_sessions(args.module, limit=args.limit)
    elif args.command == 'session':
        explorer.show_session_details(args.module, args.session_id)
    elif args.command == 'rollback':
        explorer.rollback(args.module, args.session_id, args.snapshot)
    elif args.command == 'compare':
        explorer.compare_sessions(args.module, args.session1, args.session2)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
