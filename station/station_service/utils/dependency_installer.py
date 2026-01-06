"""
Sequence dependency installer.

Reads pyproject.toml from sequence directories and installs missing dependencies.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# Python 3.11+ has tomllib in stdlib, fallback to tomli for older versions
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


# Mapping from pip package name to import name
PACKAGE_IMPORT_MAP = {
    "pyserial": "serial",
    "pyyaml": "yaml",
    "pillow": "PIL",
    "scikit-learn": "sklearn",
    "opencv-python": "cv2",
}


def get_import_name(package: str) -> str:
    """
    Get the import name for a pip package.

    Args:
        package: Package name (with optional version specifier)

    Returns:
        Import name
    """
    # Remove version specifiers
    base_name = package.split(">=")[0].split("<=")[0].split("==")[0]
    base_name = base_name.split("<")[0].split(">")[0].split("~=")[0]
    base_name = base_name.strip().lower()

    return PACKAGE_IMPORT_MAP.get(base_name, base_name.replace("-", "_"))


def is_installed(package: str) -> bool:
    """
    Check if a package is installed.

    Args:
        package: Package name (with optional version specifier)

    Returns:
        True if installed
    """
    import_name = get_import_name(package)

    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def get_missing_packages(packages: List[str]) -> List[str]:
    """
    Get list of packages that are not installed.

    Args:
        packages: List of package specs

    Returns:
        List of missing package specs
    """
    return [pkg for pkg in packages if not is_installed(pkg)]


def install_sequence_dependencies(sequence_dir: Path) -> List[str]:
    """
    Install dependencies from sequence's pyproject.toml.

    Args:
        sequence_dir: Path to sequence directory

    Returns:
        List of newly installed packages
    """
    if tomllib is None:
        logger.warning("tomllib/tomli not available, cannot parse pyproject.toml")
        return []

    pyproject_path = sequence_dir / "pyproject.toml"
    if not pyproject_path.exists():
        return []

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        logger.warning(f"Failed to parse {pyproject_path}: {e}")
        return []

    deps = data.get("project", {}).get("dependencies", [])
    if not deps:
        return []

    # Filter to only missing packages
    missing = get_missing_packages(deps)
    if not missing:
        logger.debug(f"All dependencies already installed for {sequence_dir.name}")
        return []

    logger.info(f"Installing missing dependencies for {sequence_dir.name}: {missing}")

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", *missing],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        logger.info(f"Successfully installed: {missing}")
        return missing
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return []
