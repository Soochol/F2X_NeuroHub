"""
Session Manager - Manages development sessions and history tracking

This utility creates and manages development sessions, allowing for:
- Session history tracking
- Snapshot creation
- Rollback to previous states
- Session comparison

Each session captures a complete state of the module at a point in time.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from .module_manager import ModuleManager


class SessionManager:
    """Manages development sessions and history for modules."""

    def __init__(self, base_dir: str = "modules"):
        """
        Initialize SessionManager.

        Args:
            base_dir: Base directory for modules
        """
        self.base_dir = Path(base_dir)
        self.module_manager = ModuleManager(base_dir)

    def create_session(
        self,
        module_name: str,
        session_type: str = "auto",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new development session.

        Args:
            module_name: Name of the module
            session_type: Type of session (initial, refactor, feature, bugfix, auto)
            description: Description of what this session accomplishes
            metadata: Optional additional metadata

        Returns:
            Dict with session creation info
        """
        # Ensure module exists
        if not self.module_manager.module_exists(module_name):
            return {
                'success': False,
                'message': f'Module "{module_name}" does not exist'
            }

        # Generate session ID (timestamp-based)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        session_id = f"{timestamp}-{session_type}"

        # Create session directory structure
        module_dir = self.module_manager.get_module_path(module_name)
        session_dir = module_dir / "history" / session_id

        directories = [
            session_dir / "snapshot",
            session_dir / "logs"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Create session metadata
        session_metadata = {
            'session_id': session_id,
            'module_name': module_name,
            'session_type': session_type,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'agents_executed': [],
            'artifacts_created': [],
            'metrics': {
                'total_files': 0,
                'lines_of_code': 0,
                'test_coverage': 0.0,
                'execution_time_seconds': 0
            }
        }

        if metadata:
            session_metadata.update(metadata)

        # Save session metadata
        session_file = session_dir / "session.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_metadata, f, indent=2, ensure_ascii=False)

        # Update module metadata with new session
        module_info = self.module_manager.get_module_info(module_name)
        if module_info:
            sessions = module_info.get('sessions', [])
            sessions.append({
                'session_id': session_id,
                'created_at': session_metadata['created_at'],
                'type': session_type
            })
            self.module_manager.update_module_metadata(module_name, {'sessions': sessions})

        return {
            'success': True,
            'message': f'Session "{session_id}" created for module "{module_name}"',
            'session_id': session_id,
            'path': str(session_dir),
            'metadata': session_metadata
        }

    def save_snapshot(
        self,
        module_name: str,
        session_id: str,
        snapshot_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Save a snapshot of the current module state.

        Args:
            module_name: Name of the module
            session_id: ID of the session
            snapshot_type: Type of snapshot (auto, manual, pre-agent, post-agent)

        Returns:
            Dict with snapshot info
        """
        # Verify module and session exist
        if not self.module_manager.module_exists(module_name):
            return {
                'success': False,
                'message': f'Module "{module_name}" does not exist'
            }

        module_dir = self.module_manager.get_module_path(module_name)
        session_dir = module_dir / "history" / session_id

        if not session_dir.exists():
            return {
                'success': False,
                'message': f'Session "{session_id}" does not exist'
            }

        # Create snapshot directory
        snapshot_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_name = f"{snapshot_type}-{snapshot_timestamp}"
        snapshot_dir = session_dir / "snapshot" / snapshot_name

        # Copy current state to snapshot
        current_dir = module_dir / "current"

        try:
            shutil.copytree(current_dir, snapshot_dir, dirs_exist_ok=False)

            # Create snapshot metadata
            snapshot_metadata = {
                'snapshot_name': snapshot_name,
                'snapshot_type': snapshot_type,
                'created_at': datetime.now().isoformat(),
                'module_name': module_name,
                'session_id': session_id,
                'file_count': self._count_files(snapshot_dir),
                'size_bytes': self._get_directory_size(snapshot_dir)
            }

            snapshot_file = snapshot_dir / "snapshot.json"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_metadata, f, indent=2, ensure_ascii=False)

            return {
                'success': True,
                'message': f'Snapshot "{snapshot_name}" created',
                'snapshot_name': snapshot_name,
                'path': str(snapshot_dir),
                'metadata': snapshot_metadata
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating snapshot: {str(e)}'
            }

    def finalize_session(
        self,
        module_name: str,
        session_id: str,
        status: str = "completed",
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Finalize a session and save final snapshot.

        Args:
            module_name: Name of the module
            session_id: ID of the session
            status: Final status (completed, failed, cancelled)
            metrics: Final metrics for the session

        Returns:
            Dict with finalization info
        """
        # Update session metadata
        module_dir = self.module_manager.get_module_path(module_name)
        session_dir = module_dir / "history" / session_id
        session_file = session_dir / "session.json"

        if not session_file.exists():
            return {
                'success': False,
                'message': f'Session "{session_id}" not found'
            }

        # Read current session metadata
        with open(session_file, 'r', encoding='utf-8') as f:
            session_metadata = json.load(f)

        # Update status and metrics
        session_metadata['status'] = status
        session_metadata['completed_at'] = datetime.now().isoformat()

        if metrics:
            session_metadata['metrics'].update(metrics)

        # Save updated metadata
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_metadata, f, indent=2, ensure_ascii=False)

        # Create final snapshot
        snapshot_result = self.save_snapshot(module_name, session_id, "final")

        return {
            'success': True,
            'message': f'Session "{session_id}" finalized with status: {status}',
            'session_id': session_id,
            'status': status,
            'snapshot': snapshot_result
        }

    def list_sessions(self, module_name: str) -> List[Dict[str, Any]]:
        """
        List all sessions for a module.

        Args:
            module_name: Name of the module

        Returns:
            List of session metadata dicts
        """
        if not self.module_manager.module_exists(module_name):
            return []

        module_dir = self.module_manager.get_module_path(module_name)
        history_dir = module_dir / "history"

        if not history_dir.exists():
            return []

        sessions = []
        for session_dir in sorted(history_dir.iterdir(), reverse=True):
            if session_dir.is_dir():
                session_file = session_dir / "session.json"
                if session_file.exists():
                    with open(session_file, 'r', encoding='utf-8') as f:
                        sessions.append(json.load(f))

        return sessions

    def get_session_info(self, module_name: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a session.

        Args:
            module_name: Name of the module
            session_id: ID of the session

        Returns:
            Dict with session info, or None if not found
        """
        module_dir = self.module_manager.get_module_path(module_name)
        session_file = module_dir / "history" / session_id / "session.json"

        if not session_file.exists():
            return None

        with open(session_file, 'r', encoding='utf-8') as f:
            session_info = json.load(f)

        # Add snapshot count
        snapshot_dir = module_dir / "history" / session_id / "snapshot"
        if snapshot_dir.exists():
            session_info['snapshot_count'] = len(list(snapshot_dir.iterdir()))
        else:
            session_info['snapshot_count'] = 0

        return session_info

    def rollback_to_snapshot(
        self,
        module_name: str,
        session_id: str,
        snapshot_name: str,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Rollback module to a previous snapshot.

        Args:
            module_name: Name of the module
            session_id: ID of the session
            snapshot_name: Name of the snapshot to restore
            create_backup: If True, backup current state before rollback

        Returns:
            Dict with rollback status
        """
        module_dir = self.module_manager.get_module_path(module_name)
        snapshot_dir = module_dir / "history" / session_id / "snapshot" / snapshot_name
        current_dir = module_dir / "current"

        if not snapshot_dir.exists():
            return {
                'success': False,
                'message': f'Snapshot "{snapshot_name}" not found'
            }

        try:
            # Create backup if requested
            backup_info = None
            if create_backup and current_dir.exists():
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_session_id = f"{timestamp}-rollback-backup"
                backup_result = self.create_session(
                    module_name,
                    session_type="backup",
                    description=f"Backup before rollback to {snapshot_name}"
                )
                if backup_result['success']:
                    backup_snapshot = self.save_snapshot(
                        module_name,
                        backup_result['session_id'],
                        "pre-rollback"
                    )
                    backup_info = {
                        'session_id': backup_result['session_id'],
                        'snapshot_name': backup_snapshot.get('snapshot_name')
                    }

            # Remove current directory
            if current_dir.exists():
                shutil.rmtree(current_dir)

            # Restore from snapshot
            shutil.copytree(snapshot_dir, current_dir)

            return {
                'success': True,
                'message': f'Rolled back to snapshot "{snapshot_name}"',
                'snapshot_name': snapshot_name,
                'backup': backup_info
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error during rollback: {str(e)}'
            }

    def log_agent_execution(
        self,
        module_name: str,
        session_id: str,
        agent_name: str,
        status: str,
        duration_seconds: float,
        artifacts: List[str] = None
    ) -> bool:
        """
        Log an agent execution to the session.

        Args:
            module_name: Name of the module
            session_id: ID of the session
            agent_name: Name of the agent that executed
            status: Execution status (success, failed)
            duration_seconds: Execution duration in seconds
            artifacts: List of artifacts created by the agent

        Returns:
            True if successful, False otherwise
        """
        module_dir = self.module_manager.get_module_path(module_name)
        session_file = module_dir / "history" / session_id / "session.json"

        if not session_file.exists():
            return False

        # Read current session metadata
        with open(session_file, 'r', encoding='utf-8') as f:
            session_metadata = json.load(f)

        # Add agent execution log
        execution_log = {
            'agent_name': agent_name,
            'status': status,
            'executed_at': datetime.now().isoformat(),
            'duration_seconds': duration_seconds,
            'artifacts': artifacts or []
        }

        session_metadata['agents_executed'].append(execution_log)

        if artifacts:
            session_metadata['artifacts_created'].extend(artifacts)

        # Update total execution time
        session_metadata['metrics']['execution_time_seconds'] += duration_seconds

        # Save updated metadata
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_metadata, f, indent=2, ensure_ascii=False)

        return True

    def _count_files(self, directory: Path) -> int:
        """Count files recursively."""
        return len([f for f in directory.rglob('*') if f.is_file()])

    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        for item in directory.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size


# Convenience functions

def get_session_manager() -> SessionManager:
    """Get a SessionManager instance."""
    return SessionManager()


def create_auto_session(module_name: str, description: str = "") -> str:
    """
    Create an automatic session with timestamp.

    Args:
        module_name: Name of the module
        description: Description of the session

    Returns:
        Session ID
    """
    manager = SessionManager()
    result = manager.create_session(module_name, "auto", description)
    if result['success']:
        return result['session_id']
    else:
        raise RuntimeError(result['message'])


if __name__ == '__main__':
    # Demo usage
    from .module_manager import ModuleManager

    print("=== Session Manager Demo ===\n")

    # Ensure module exists
    module_mgr = ModuleManager()
    if not module_mgr.module_exists('inventory'):
        module_mgr.create_module('inventory', 'Inventory management')

    session_mgr = SessionManager()

    # Create a session
    print("1. Creating session...")
    result = session_mgr.create_session(
        'inventory',
        session_type='feature',
        description='Add stock level tracking'
    )
    print(f"   Status: {result['message']}")
    session_id = result['session_id']
    print(f"   Session ID: {session_id}\n")

    # Save a snapshot
    print("2. Saving snapshot...")
    snapshot_result = session_mgr.save_snapshot('inventory', session_id, 'pre-design')
    print(f"   Status: {snapshot_result['message']}\n")

    # Log agent execution
    print("3. Logging agent execution...")
    session_mgr.log_agent_execution(
        'inventory',
        session_id,
        'design-agent',
        'success',
        120.5,
        ['API-INV-001.md', 'DB-INV-001.md']
    )
    print("   Agent execution logged\n")

    # List sessions
    print("4. Listing sessions...")
    sessions = session_mgr.list_sessions('inventory')
    for sess in sessions:
        print(f"   - {sess['session_id']} ({sess['status']})")
    print()

    # Finalize session
    print("5. Finalizing session...")
    finalize_result = session_mgr.finalize_session(
        'inventory',
        session_id,
        'completed',
        {'test_coverage': 87.5, 'total_files': 15}
    )
    print(f"   Status: {finalize_result['message']}")
