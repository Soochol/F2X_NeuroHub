"""
Migration Script - Migrate from old structure to modular structure

This script helps migrate existing F2X NeuroHub projects from the old
flat directory structure to the new module-centric structure.

Old structure:
docs/
├── requirements/
├── design/
└── verification/
app/
tests/

New structure:
modules/
├── {module_name}/
│   ├── current/
│   │   ├── requirements/
│   │   ├── design/
│   │   ├── src/
│   │   ├── tests/
│   │   └── verification/
│   └── history/
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Add parent directory to path to import utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))

from utils.module_manager import ModuleManager
from utils.session_manager import SessionManager


class StructureMigrator:
    """Migrates from old flat structure to new modular structure."""

    def __init__(self, dry_run: bool = True):
        """
        Initialize migrator.

        Args:
            dry_run: If True, only show what would be migrated without actually doing it
        """
        self.dry_run = dry_run
        self.module_manager = ModuleManager()
        self.session_manager = SessionManager()

        # Old directory paths
        self.old_paths = {
            'requirements': Path('docs/requirements/modules'),
            'design': Path('docs/design'),
            'verification': Path('docs/verification'),
            'src': Path('app'),
            'tests': Path('tests')
        }

    def detect_modules(self) -> Set[str]:
        """
        Detect module names from existing files.

        Returns:
            Set of detected module names
        """
        modules = set()

        # Extract from requirements (e.g., FR-INV-001.md -> "inventory")
        req_path = self.old_paths['requirements']
        if req_path.exists():
            for module_dir in req_path.iterdir():
                if module_dir.is_dir():
                    modules.add(module_dir.name)

        # Extract from design files (e.g., API-INV-001.md -> "INV")
        design_path = self.old_paths['design']
        if design_path.exists():
            for doc_file in design_path.rglob('*.md'):
                match = re.search(r'-([A-Z]{3})-\d+', doc_file.stem)
                if match:
                    module_code = match.group(1)
                    modules.add(self._code_to_module_name(module_code))

        # Extract from verification (e.g., docs/verification/inventory/)
        verify_path = self.old_paths['verification']
        if verify_path.exists():
            for module_dir in verify_path.iterdir():
                if module_dir.is_dir():
                    modules.add(module_dir.name)

        return modules

    def _code_to_module_name(self, code: str) -> str:
        """
        Convert module code to full name.

        Args:
            code: 3-letter module code (e.g., "INV")

        Returns:
            Full module name (e.g., "inventory")
        """
        code_map = {
            'INV': 'inventory',
            'ORD': 'order',
            'PRD': 'production',
            'QLT': 'quality',
            'USR': 'user',
            'GUI': 'gui',
            'RPT': 'report'
        }
        return code_map.get(code.upper(), code.lower())

    def _module_name_to_code(self, module_name: str) -> str:
        """
        Convert module name to code.

        Args:
            module_name: Full module name (e.g., "inventory")

        Returns:
            3-letter module code (e.g., "INV")
        """
        name_map = {
            'inventory': 'INV',
            'order': 'ORD',
            'production': 'PRD',
            'quality': 'QLT',
            'user': 'USR',
            'gui': 'GUI',
            'report': 'RPT'
        }
        return name_map.get(module_name.lower(), module_name[:3].upper())

    def categorize_files(self, modules: Set[str]) -> Dict[str, List[Path]]:
        """
        Categorize files by module.

        Args:
            modules: Set of detected module names

        Returns:
            Dict mapping module names to lists of (old_path, artifact_type) tuples
        """
        file_map = defaultdict(list)

        for module in modules:
            module_code = self._module_name_to_code(module)

            # Requirements files
            req_module_dir = self.old_paths['requirements'] / module
            if req_module_dir.exists():
                for file in req_module_dir.glob('*.md'):
                    file_map[module].append((file, 'requirements'))

            # Design files (match by module code in filename)
            design_path = self.old_paths['design']
            if design_path.exists():
                for subdir in ['architecture', 'api', 'database', 'structure', 'component']:
                    subdir_path = design_path / subdir
                    if subdir_path.exists():
                        for file in subdir_path.glob('*.md'):
                            if f'-{module_code}-' in file.stem:
                                file_map[module].append((file, f'design/{subdir}'))

            # Verification files
            verify_module_dir = self.old_paths['verification'] / module
            if verify_module_dir.exists():
                for file in verify_module_dir.rglob('*.md'):
                    file_map[module].append((file, 'verification'))

            # Source files (match by directory name)
            src_path = self.old_paths['src']
            if src_path.exists():
                # Check for module-specific directories
                for layer in ['domain', 'application', 'infrastructure', 'presentation']:
                    layer_path = src_path / layer
                    if layer_path.exists():
                        for file in layer_path.rglob('*.py'):
                            # Check if file/directory name contains module name
                            if module in str(file).lower():
                                relative_path = file.relative_to(src_path)
                                file_map[module].append((file, f'src/{relative_path.parent}'))

            # Test files (match by directory/file name)
            tests_path = self.old_paths['tests']
            if tests_path.exists():
                for test_type in ['unit', 'integration', 'e2e']:
                    test_type_path = tests_path / test_type
                    if test_type_path.exists():
                        for file in test_type_path.rglob('*.py'):
                            if module in str(file).lower():
                                relative_path = file.relative_to(tests_path)
                                file_map[module].append((file, f'tests/{relative_path.parent}'))

        return file_map

    def migrate_module(self, module_name: str, files: List[tuple]) -> Dict:
        """
        Migrate a single module.

        Args:
            module_name: Name of the module
            files: List of (old_path, artifact_type) tuples

        Returns:
            Dict with migration results
        """
        results = {
            'module_name': module_name,
            'files_migrated': 0,
            'files_failed': 0,
            'errors': []
        }

        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Migrating module: {module_name}")
        print(f"  Found {len(files)} files to migrate")

        # Create module if it doesn't exist
        if not self.dry_run:
            if not self.module_manager.module_exists(module_name):
                create_result = self.module_manager.create_module(
                    module_name,
                    f"Migrated from old structure"
                )
                if not create_result['success']:
                    results['errors'].append(f"Failed to create module: {create_result['message']}")
                    return results

            # Create migration session
            session_result = self.session_manager.create_session(
                module_name,
                session_type='migration',
                description='Migration from old flat structure to modular structure'
            )
            session_id = session_result['session_id']
        else:
            print(f"  Would create module: {module_name}")

        # Migrate each file
        for old_path, artifact_type in files:
            try:
                # Determine new path
                if not self.dry_run:
                    new_base = self.module_manager.get_module_path(module_name) / "current"
                    new_path = new_base / artifact_type / old_path.name
                else:
                    new_path = Path(f"modules/{module_name}/current/{artifact_type}/{old_path.name}")

                print(f"    {old_path} -> {new_path}")

                if not self.dry_run:
                    # Create parent directory
                    new_path.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    shutil.copy2(old_path, new_path)

                    results['files_migrated'] += 1
                else:
                    results['files_migrated'] += 1

            except Exception as e:
                error_msg = f"Failed to migrate {old_path}: {str(e)}"
                results['errors'].append(error_msg)
                results['files_failed'] += 1
                print(f"    ERROR: {error_msg}")

        # Finalize session
        if not self.dry_run:
            self.session_manager.finalize_session(
                module_name,
                session_id,
                'completed',
                {'files_migrated': results['files_migrated']}
            )

        return results

    def migrate_all(self) -> Dict:
        """
        Migrate all detected modules.

        Returns:
            Dict with overall migration results
        """
        print("=" * 70)
        print(f"{'DRY RUN: ' if self.dry_run else ''}F2X NeuroHub Structure Migration")
        print("=" * 70)

        # Detect modules
        print("\n1. Detecting modules...")
        modules = self.detect_modules()
        print(f"   Found {len(modules)} modules: {', '.join(sorted(modules))}")

        if not modules:
            print("\n   No modules detected. Nothing to migrate.")
            return {'total_modules': 0, 'modules': []}

        # Categorize files
        print("\n2. Categorizing files by module...")
        file_map = self.categorize_files(modules)

        total_files = sum(len(files) for files in file_map.values())
        print(f"   Categorized {total_files} files across {len(file_map)} modules")

        # Migrate each module
        print("\n3. Migrating modules...")
        all_results = {
            'total_modules': len(file_map),
            'total_files': 0,
            'total_migrated': 0,
            'total_failed': 0,
            'modules': []
        }

        for module_name, files in sorted(file_map.items()):
            result = self.migrate_module(module_name, files)
            all_results['modules'].append(result)
            all_results['total_files'] += len(files)
            all_results['total_migrated'] += result['files_migrated']
            all_results['total_failed'] += result['files_failed']

        # Print summary
        print("\n" + "=" * 70)
        print(f"{'DRY RUN ' if self.dry_run else ''}Migration Summary")
        print("=" * 70)
        print(f"  Total modules: {all_results['total_modules']}")
        print(f"  Total files: {all_results['total_files']}")
        print(f"  Successfully migrated: {all_results['total_migrated']}")
        print(f"  Failed: {all_results['total_failed']}")

        if self.dry_run:
            print("\n  This was a DRY RUN. No files were actually migrated.")
            print("  Run with --execute to perform the actual migration.")
        else:
            print("\n  Migration completed!")
            print("  Old files are still in their original locations.")
            print("  You can safely delete them after verifying the migration.")

        return all_results


def main():
    """Main entry point for migration script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrate F2X NeuroHub from old structure to modular structure'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually perform the migration (default is dry run)'
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Migrate only a specific module'
    )

    args = parser.parse_args()

    migrator = StructureMigrator(dry_run=not args.execute)

    if args.module:
        # Migrate single module
        print(f"Migrating single module: {args.module}")
        modules = {args.module}
        file_map = migrator.categorize_files(modules)

        if args.module not in file_map:
            print(f"Error: Module '{args.module}' not found or has no files to migrate")
            return

        migrator.migrate_module(args.module, file_map[args.module])
    else:
        # Migrate all modules
        migrator.migrate_all()


if __name__ == '__main__':
    main()
