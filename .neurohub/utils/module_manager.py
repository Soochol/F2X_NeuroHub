"""
Module Manager - Manages modular directory structure for F2X NeuroHub

This utility creates and manages module-centric directory structures,
preventing file mixing when running /full for different features.

Structure:
modules/
├── {module_name}/
│   ├── current/              # Active version
│   │   ├── requirements/
│   │   ├── design/
│   │   ├── src/
│   │   ├── tests/
│   │   └── verification/
│   ├── history/              # Session history
│   │   └── {session_id}/
│   │       ├── snapshot/
│   │       ├── logs/
│   │       └── metrics.json
│   └── module.json           # Module metadata
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ModuleManager:
    """Manages module directory structure and metadata."""

    def __init__(self, base_dir: str = "modules"):
        """
        Initialize ModuleManager.

        Args:
            base_dir: Base directory for all modules (default: "modules")
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_module(self, module_name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new module with standard directory structure.

        Args:
            module_name: Name of the module (e.g., "inventory", "order")
            description: Optional description of the module

        Returns:
            Dict with module creation info
        """
        module_dir = self.base_dir / module_name

        # Check if module already exists
        if module_dir.exists():
            return {
                'success': False,
                'message': f'Module "{module_name}" already exists',
                'path': str(module_dir)
            }

        # Create module directory structure
        directories = [
            module_dir / "current" / "requirements",
            module_dir / "current" / "design" / "architecture",
            module_dir / "current" / "design" / "api",
            module_dir / "current" / "design" / "database",
            module_dir / "current" / "design" / "structure",
            module_dir / "current" / "design" / "component",
            module_dir / "current" / "src" / "domain" / "entities",
            module_dir / "current" / "src" / "domain" / "services",
            module_dir / "current" / "src" / "application" / "services",
            module_dir / "current" / "src" / "application" / "dtos",
            module_dir / "current" / "src" / "infrastructure" / "repositories",
            module_dir / "current" / "src" / "infrastructure" / "database",
            module_dir / "current" / "src" / "presentation" / "api",
            module_dir / "current" / "tests" / "unit",
            module_dir / "current" / "tests" / "integration",
            module_dir / "current" / "tests" / "e2e",
            module_dir / "current" / "verification",
            module_dir / "history"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep to preserve empty directories
            (directory / ".gitkeep").touch()

        # Create module metadata
        metadata = {
            'name': module_name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'sessions': [],
            'status': 'initialized',
            'version': '0.1.0'
        }

        metadata_file = module_dir / "module.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return {
            'success': True,
            'message': f'Module "{module_name}" created successfully',
            'path': str(module_dir),
            'metadata': metadata
        }

    def get_module_path(self, module_name: str, subpath: str = "") -> Path:
        """
        Get the full path to a module directory or subdirectory.

        Args:
            module_name: Name of the module
            subpath: Optional subdirectory path (e.g., "current/design")

        Returns:
            Path object to the requested directory
        """
        module_dir = self.base_dir / module_name
        if subpath:
            return module_dir / subpath
        return module_dir

    def get_current_path(self, module_name: str, artifact_type: str) -> Path:
        """
        Get the current working directory path for a specific artifact type.

        Args:
            module_name: Name of the module
            artifact_type: Type of artifact (requirements, design, src, tests, verification)

        Returns:
            Path object to the current artifact directory
        """
        valid_types = ['requirements', 'design', 'src', 'tests', 'verification']
        if artifact_type not in valid_types:
            raise ValueError(f'Invalid artifact_type. Must be one of: {valid_types}')

        return self.get_module_path(module_name, f"current/{artifact_type}")

    def module_exists(self, module_name: str) -> bool:
        """
        Check if a module exists.

        Args:
            module_name: Name of the module

        Returns:
            True if module exists, False otherwise
        """
        module_dir = self.base_dir / module_name
        return module_dir.exists() and (module_dir / "module.json").exists()

    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get module metadata.

        Args:
            module_name: Name of the module

        Returns:
            Dict with module metadata, or None if module doesn't exist
        """
        if not self.module_exists(module_name):
            return None

        metadata_file = self.get_module_path(module_name) / "module.json"
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_module_metadata(self, module_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update module metadata.

        Args:
            module_name: Name of the module
            updates: Dict of fields to update

        Returns:
            True if successful, False otherwise
        """
        if not self.module_exists(module_name):
            return False

        metadata_file = self.get_module_path(module_name) / "module.json"

        # Read current metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Update fields
        metadata.update(updates)
        metadata['last_updated'] = datetime.now().isoformat()

        # Write back
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return True

    def list_modules(self) -> List[Dict[str, Any]]:
        """
        List all modules.

        Returns:
            List of module metadata dicts
        """
        modules = []

        if not self.base_dir.exists():
            return modules

        for module_dir in self.base_dir.iterdir():
            if module_dir.is_dir() and (module_dir / "module.json").exists():
                with open(module_dir / "module.json", 'r', encoding='utf-8') as f:
                    modules.append(json.load(f))

        return modules

    def delete_module(self, module_name: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete a module and all its contents.

        Args:
            module_name: Name of the module
            confirm: Must be True to actually delete (safety check)

        Returns:
            Dict with deletion status
        """
        if not confirm:
            return {
                'success': False,
                'message': 'Deletion not confirmed. Set confirm=True to delete.'
            }

        if not self.module_exists(module_name):
            return {
                'success': False,
                'message': f'Module "{module_name}" does not exist'
            }

        module_dir = self.get_module_path(module_name)

        try:
            shutil.rmtree(module_dir)
            return {
                'success': True,
                'message': f'Module "{module_name}" deleted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting module: {str(e)}'
            }

    def get_module_stats(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics about a module.

        Args:
            module_name: Name of the module

        Returns:
            Dict with module statistics, or None if module doesn't exist
        """
        if not self.module_exists(module_name):
            return None

        module_dir = self.get_module_path(module_name)
        current_dir = module_dir / "current"
        history_dir = module_dir / "history"

        def count_files(directory: Path, pattern: str = "*") -> int:
            """Count files recursively matching pattern."""
            if not directory.exists():
                return 0
            return len(list(directory.rglob(pattern)))

        stats = {
            'module_name': module_name,
            'total_files': count_files(current_dir, "*.*"),
            'requirements_docs': count_files(current_dir / "requirements", "*.md"),
            'design_docs': count_files(current_dir / "design", "*.md"),
            'source_files': count_files(current_dir / "src", "*.py"),
            'test_files': count_files(current_dir / "tests", "*.py"),
            'verification_reports': count_files(current_dir / "verification", "*.md"),
            'total_sessions': len(list(history_dir.iterdir())) if history_dir.exists() else 0,
            'disk_usage_mb': self._get_directory_size(module_dir) / (1024 * 1024)
        }

        return stats

    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        for item in directory.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size

    def ensure_module_exists(self, module_name: str, auto_create: bool = True) -> bool:
        """
        Ensure a module exists, optionally creating it if it doesn't.

        Args:
            module_name: Name of the module
            auto_create: If True, create the module if it doesn't exist

        Returns:
            True if module exists (or was created), False otherwise
        """
        if self.module_exists(module_name):
            return True

        if auto_create:
            result = self.create_module(module_name)
            return result['success']

        return False


# Convenience functions for agents to use

def get_agent_output_path(module_name: str, agent_type: str) -> Path:
    """
    Get the output path for a specific agent.

    Args:
        module_name: Name of the module
        agent_type: Type of agent (requirements, design, implementation, testing, verification)

    Returns:
        Path where the agent should write its outputs

    Example:
        >>> path = get_agent_output_path('inventory', 'design')
        >>> # Returns: modules/inventory/current/design/
    """
    manager = ModuleManager()

    # Ensure module exists
    manager.ensure_module_exists(module_name, auto_create=True)

    # Map agent types to artifact types
    agent_to_artifact = {
        'requirements': 'requirements',
        'design': 'design',
        'implementation': 'src',
        'testing': 'tests',
        'verification': 'verification'
    }

    artifact_type = agent_to_artifact.get(agent_type)
    if not artifact_type:
        raise ValueError(f'Invalid agent_type: {agent_type}')

    return manager.get_current_path(module_name, artifact_type)


def get_module_manager() -> ModuleManager:
    """
    Get a ModuleManager instance.

    Returns:
        ModuleManager instance
    """
    return ModuleManager()


if __name__ == '__main__':
    # Demo usage
    manager = ModuleManager()

    print("=== Module Manager Demo ===\n")

    # Create a test module
    print("1. Creating 'inventory' module...")
    result = manager.create_module('inventory', 'Inventory management module')
    print(f"   Status: {result['message']}")
    print(f"   Path: {result['path']}\n")

    # Get module info
    print("2. Getting module info...")
    info = manager.get_module_info('inventory')
    print(f"   Name: {info['name']}")
    print(f"   Status: {info['status']}")
    print(f"   Created: {info['created_at']}\n")

    # Get specific paths
    print("3. Getting artifact paths...")
    design_path = manager.get_current_path('inventory', 'design')
    src_path = manager.get_current_path('inventory', 'src')
    print(f"   Design path: {design_path}")
    print(f"   Source path: {src_path}\n")

    # List all modules
    print("4. Listing all modules...")
    modules = manager.list_modules()
    for mod in modules:
        print(f"   - {mod['name']} ({mod['status']})")
    print()

    # Get module stats
    print("5. Getting module statistics...")
    stats = manager.get_module_stats('inventory')
    print(f"   Total files: {stats['total_files']}")
    print(f"   Disk usage: {stats['disk_usage_mb']:.2f} MB")
