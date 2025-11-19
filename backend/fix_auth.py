"""
Script to add authentication dependencies to API endpoints that are missing them.
"""
import re
from pathlib import Path

# Files to fix and their endpoint patterns
files_to_fix = [
    "app/api/v1/lots.py",
    "app/api/v1/process_data.py",
    "app/api/v1/serials.py",
]

AUTH_IMPORT = "from app.models import User"
AUTH_PARAM = "current_user: User = Depends(deps.get_current_active_user),"

def fix_file(file_path: Path):
    """Add authentication to endpoints in the given file."""
    print(f"\nProcessing {file_path}...")

    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # Check if User is imported
    if "from app.models import User" not in content and "from app.models import (" not in content:
        # Need to add User import
        # Find the models import line and add User
        import_pattern = r"(from app\.models import [^)]+)"
        match = re.search(import_pattern, content)
        if match:
            imports = match.group(1)
            if "User" not in imports:
                # Add User to imports
                if imports.endswith(")"):
                    content = content.replace(imports, imports[:-1] + ",\n    User\n)")
                else:
                    content = content.replace(imports, imports + ", User")

    # Find all function definitions and add auth if missing
    # Pattern: def function_name(\n    param1: Type = ...,\n    db: Session = Depends(...),\n) -> ReturnType:
    pattern = r"(def \w+\([^)]*?)(db: Session = Depends\(deps\.get_db\),?)(\s*\) -> )"

    def add_auth(match):
        before = match.group(1)
        db_param = match.group(2)
        after = match.group(3)

        # Check if current_user already exists
        if "current_user" in before:
            return match.group(0)

        # Add current_user parameter after db
        return f"{before}{db_param}\n    current_user: User = Depends(deps.get_current_active_user),{after}"

    content = re.sub(pattern, add_auth, content)

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Fixed {file_path}")
        return True
    else:
        print(f"  - No changes needed for {file_path}")
        return False

def main():
    base_dir = Path(__file__).parent
    fixed_count = 0

    for file_rel_path in files_to_fix:
        file_path = base_dir / file_rel_path
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"  ✗ File not found: {file_path}")

    print(f"\n✓ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
