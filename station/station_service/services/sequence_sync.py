"""
Sequence synchronization service.

Handles pulling sequences from Backend API and managing
local sequence packages.
"""

import asyncio
import base64
import hashlib
import io
import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from station_service.models.config import BackendConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Models
# ============================================================================


class SequenceInfo(BaseModel):
    """Information about a sequence from Backend."""

    name: str
    version: str
    checksum: str
    package_size: int
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class PullResult(BaseModel):
    """Result of a sequence pull operation."""

    name: str
    version: str
    checksum: str
    package_size: int
    needs_update: bool
    updated: bool = False
    error: Optional[str] = None
    installed_at: Optional[datetime] = None


class SyncResult(BaseModel):
    """Result of a sync operation."""

    synced_at: datetime
    sequences_checked: int = 0
    sequences_updated: int = 0
    sequences_failed: int = 0
    results: List[PullResult] = Field(default_factory=list)
    error: Optional[str] = None


class LocalSequenceInfo(BaseModel):
    """Information about a locally installed sequence."""

    name: str
    version: str
    checksum: str
    installed_at: datetime
    package_path: str


# ============================================================================
# Service
# ============================================================================


class SequenceSyncService:
    """
    Service for synchronizing sequences from Backend API.

    Handles:
    - Checking for sequence updates
    - Downloading sequence packages
    - Installing/updating local sequence packages
    - Version tracking and rollback
    """

    def __init__(
        self,
        backend_config: BackendConfig,
        sequences_dir: str = "sequences",
    ):
        """
        Initialize sync service.

        Args:
            backend_config: Backend connection configuration
            sequences_dir: Directory for sequence packages
        """
        self.backend_config = backend_config
        self.sequences_dir = Path(sequences_dir)
        self._client: Optional[httpx.AsyncClient] = None
        self._sync_lock = asyncio.Lock()
        self._token_manager = None  # TokenManager for dynamic station_api_key

        # Ensure sequences directory exists
        self.sequences_dir.mkdir(parents=True, exist_ok=True)

    def set_token_manager(self, token_manager) -> None:
        """
        Set TokenManager for dynamic station_api_key.

        When set, prioritizes station_api_key from TokenManager
        (issued at operator login) over static config api_key.

        Args:
            token_manager: TokenManager instance
        """
        self._token_manager = token_manager
        # Reset client to pick up new auth
        if self._client and not self._client.is_closed:
            asyncio.create_task(self._client.aclose())
            self._client = None

    @property
    def backend_url(self) -> str:
        """Get Backend API URL."""
        url = self.backend_config.url.rstrip("/")
        if not url:
            raise ValueError("Backend URL not configured")
        return url

    @property
    def station_id(self) -> str:
        """Get station ID for sync."""
        station_id = self.backend_config.station_id
        if not station_id:
            raise ValueError("Station ID not configured")
        return station_id

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for authentication.

        Priority:
        1. Dynamic station_api_key from TokenManager (issued at operator login)
        2. Static api_key from config (fallback)

        Returns:
            API key string or None
        """
        # Priority 1: TokenManager's station_api_key (from login)
        if self._token_manager:
            station_api_key = self._token_manager.get_station_api_key()
            if station_api_key:
                return station_api_key

        # Priority 2: Static config api_key
        return self.backend_config.api_key

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.backend_url,
                timeout=self.backend_config.timeout,
            )

        # Update API key header on each access (may change after login)
        api_key = self._get_api_key()
        if api_key:
            self._client.headers["X-API-Key"] = api_key
        elif "X-API-Key" in self._client.headers:
            del self._client.headers["X-API-Key"]

        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # =========================================================================
    # Sequence List Operations
    # =========================================================================

    async def list_available_sequences(self) -> List[SequenceInfo]:
        """
        List available sequences from Backend.

        Returns:
            List of available sequences with metadata
        """
        client = await self._get_client()

        try:
            response = await client.get("/api/v1/sequences")
            response.raise_for_status()
            data = response.json()

            sequences = []
            for item in data.get("items", []):
                sequences.append(SequenceInfo(
                    name=item["name"],
                    version=item["version"],
                    checksum=item.get("checksum", ""),
                    package_size=item.get("package_size", 0),
                    display_name=item.get("display_name"),
                    description=item.get("description"),
                    is_active=item.get("is_active", True),
                ))
            return sequences

        except httpx.HTTPError as e:
            logger.error(f"Failed to list sequences from Backend: {e}")
            raise

    async def get_sequence_info(self, sequence_name: str) -> Optional[SequenceInfo]:
        """
        Get sequence info from Backend.

        Args:
            sequence_name: Name of the sequence

        Returns:
            Sequence info if found, None otherwise
        """
        client = await self._get_client()

        try:
            response = await client.get(f"/api/v1/sequences/{sequence_name}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

            return SequenceInfo(
                name=data["name"],
                version=data["version"],
                checksum=data.get("checksum", ""),
                package_size=data.get("package_size", 0),
                display_name=data.get("display_name"),
                description=data.get("description"),
                is_active=data.get("is_active", True),
            )

        except httpx.HTTPError as e:
            logger.error(f"Failed to get sequence info: {e}")
            raise

    # =========================================================================
    # Local Sequence Operations
    # =========================================================================

    def get_local_sequence_info(self, sequence_name: str) -> Optional[LocalSequenceInfo]:
        """
        Get locally installed sequence info.

        Args:
            sequence_name: Name of the sequence

        Returns:
            Local sequence info if installed, None otherwise
        """
        package_path = self.sequences_dir / sequence_name
        if not package_path.exists():
            return None

        manifest_path = package_path / "manifest.yaml"
        if not manifest_path.exists():
            return None

        try:
            import yaml
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            # Calculate checksum from package
            checksum = self._calculate_package_checksum(package_path)

            # Get modification time
            installed_at = datetime.fromtimestamp(manifest_path.stat().st_mtime)

            return LocalSequenceInfo(
                name=manifest.get("name", sequence_name),
                version=manifest.get("version", "0.0.0"),
                checksum=checksum,
                installed_at=installed_at,
                package_path=str(package_path),
            )

        except Exception as e:
            logger.warning(f"Failed to read local sequence info: {e}")
            return None

    def _calculate_package_checksum(self, package_path: Path) -> str:
        """Calculate checksum of a package directory."""
        hasher = hashlib.sha256()

        # Hash all files in sorted order for consistency
        for file_path in sorted(package_path.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                with open(file_path, "rb") as f:
                    hasher.update(file_path.relative_to(package_path).as_posix().encode())
                    hasher.update(f.read())

        return hasher.hexdigest()

    def list_local_sequences(self) -> List[LocalSequenceInfo]:
        """
        List all locally installed sequences.

        Returns:
            List of local sequence info
        """
        sequences = []
        for item in self.sequences_dir.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_")):
                info = self.get_local_sequence_info(item.name)
                if info:
                    sequences.append(info)
        return sequences

    # =========================================================================
    # Pull Operations
    # =========================================================================

    async def pull_sequence(
        self,
        sequence_name: str,
        force: bool = False,
    ) -> PullResult:
        """
        Pull a sequence from Backend.

        Checks if update is needed and downloads if necessary.

        Args:
            sequence_name: Name of the sequence to pull
            force: Force download even if up-to-date

        Returns:
            Pull result with status and any errors
        """
        async with self._sync_lock:
            return await self._pull_sequence_internal(sequence_name, force)

    async def _pull_sequence_internal(
        self,
        sequence_name: str,
        force: bool = False,
    ) -> PullResult:
        """Internal pull implementation."""
        client = await self._get_client()

        # Get local version info
        local_info = self.get_local_sequence_info(sequence_name)
        current_version = local_info.version if local_info else None

        try:
            # Request pull from Backend
            response = await client.post(
                f"/api/v1/sequences/{sequence_name}/pull",
                json={
                    "station_id": self.station_id,
                    "current_version": None if force else current_version,
                },
            )

            if response.status_code == 404:
                return PullResult(
                    name=sequence_name,
                    version=current_version or "unknown",
                    checksum="",
                    package_size=0,
                    needs_update=False,
                    updated=False,
                    error=f"Sequence '{sequence_name}' not found on Backend",
                )

            response.raise_for_status()
            data = response.json()

            needs_update = data.get("needs_update", False)

            if not needs_update and not force:
                logger.info(f"Sequence '{sequence_name}' is up-to-date (v{data['version']})")
                return PullResult(
                    name=sequence_name,
                    version=data["version"],
                    checksum=data["checksum"],
                    package_size=data["package_size"],
                    needs_update=False,
                    updated=False,
                )

            # Download and install package
            package_data = data.get("package_data")
            if not package_data:
                return PullResult(
                    name=sequence_name,
                    version=data["version"],
                    checksum=data["checksum"],
                    package_size=data["package_size"],
                    needs_update=True,
                    updated=False,
                    error="No package data in response",
                )

            # Decode and install
            await self._install_package(
                sequence_name,
                package_data,
                data["checksum"],
                backend_version=data["version"],
            )

            logger.info(
                f"Installed sequence '{sequence_name}' v{data['version']} "
                f"(was: {current_version or 'not installed'})"
            )

            return PullResult(
                name=sequence_name,
                version=data["version"],
                checksum=data["checksum"],
                package_size=data["package_size"],
                needs_update=True,
                updated=True,
                installed_at=datetime.now(),
            )

        except httpx.HTTPError as e:
            logger.error(f"Failed to pull sequence '{sequence_name}': {e}")
            return PullResult(
                name=sequence_name,
                version=current_version or "unknown",
                checksum="",
                package_size=0,
                needs_update=False,
                updated=False,
                error=str(e),
            )

    async def _install_package(
        self,
        sequence_name: str,
        package_data: str,
        expected_checksum: str,
        backend_version: Optional[str] = None,
    ) -> None:
        """
        Install a package from base64-encoded data.

        Args:
            sequence_name: Name of the sequence
            package_data: Base64-encoded ZIP data
            expected_checksum: Expected SHA-256 checksum
            backend_version: Version from backend to update in manifest
        """
        # Decode package
        zip_data = base64.b64decode(package_data)

        # Verify checksum
        actual_checksum = hashlib.sha256(zip_data).hexdigest()
        if actual_checksum != expected_checksum:
            raise ValueError(
                f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
            )

        # Extract to temp directory first
        temp_dir = self.sequences_dir / f".{sequence_name}_temp"
        target_dir = self.sequences_dir / sequence_name

        try:
            # Clean up any existing temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

            # Extract ZIP
            with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
                # Find the root directory in ZIP (might be nested)
                root_prefix = self._find_zip_root(zf, sequence_name)

                temp_dir.mkdir(parents=True, exist_ok=True)

                for info in zf.infolist():
                    if info.is_dir():
                        continue

                    # Remove root prefix if present
                    if root_prefix:
                        if not info.filename.startswith(root_prefix):
                            continue
                        rel_path = info.filename[len(root_prefix):]
                    else:
                        rel_path = info.filename

                    if not rel_path:
                        continue

                    # Extract file
                    target_file = temp_dir / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info) as src, open(target_file, "wb") as dst:
                        dst.write(src.read())

            # Verify manifest exists
            if not (temp_dir / "manifest.yaml").exists():
                raise ValueError("Package missing manifest.yaml")

            # Backup existing and swap
            backup_dir = self.sequences_dir / f".{sequence_name}_backup"
            if target_dir.exists():
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                target_dir.rename(backup_dir)

            try:
                temp_dir.rename(target_dir)
                # Success - remove backup
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)

                # Update manifest.yaml with backend version
                if backend_version:
                    self._update_manifest_version(target_dir, backend_version)

            except Exception:
                # Restore backup
                if backup_dir.exists():
                    backup_dir.rename(target_dir)
                raise

        finally:
            # Cleanup temp
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def _find_zip_root(self, zf: zipfile.ZipFile, expected_name: str) -> str:
        """Find the root directory prefix in a ZIP file."""
        names = zf.namelist()

        # Check if files are directly in root
        for name in names:
            if "/" not in name or name.split("/")[0] == expected_name:
                if name.startswith(f"{expected_name}/"):
                    return f"{expected_name}/"
        return ""

    def _update_manifest_version(self, package_dir: Path, version: str) -> None:
        """
        Update manifest.yaml with the backend-managed version.

        This ensures local manifest version matches the backend version,
        since the backend manages versions independently.

        Args:
            package_dir: Path to the sequence package directory
            version: Version string from backend
        """
        manifest_path = package_dir / "manifest.yaml"
        if not manifest_path.exists():
            logger.warning(f"Manifest not found at {manifest_path}")
            return

        try:
            import yaml

            # Read current manifest
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse to get current version for logging
            manifest = yaml.safe_load(content)
            old_version = manifest.get("version", "unknown")

            if old_version == version:
                return  # Already matches

            # Update version field using regex to preserve formatting/comments
            import re
            updated_content = re.sub(
                r'^(version:\s*["\']?)[\d.]+(["\']?)(\s*)$',
                rf'\g<1>{version}\g<2>\g<3>',
                content,
                flags=re.MULTILINE,
            )

            # Write updated manifest
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            logger.info(
                f"Updated manifest version: {old_version} -> {version} "
                f"(synced with backend)"
            )

        except Exception as e:
            logger.warning(f"Failed to update manifest version: {e}")

    # =========================================================================
    # Sync Operations
    # =========================================================================

    async def sync_all(self, sequence_names: Optional[List[str]] = None) -> SyncResult:
        """
        Sync all or specified sequences from Backend.

        Args:
            sequence_names: Optional list of sequences to sync.
                           If None, syncs all available sequences.

        Returns:
            Sync result with status for each sequence
        """
        async with self._sync_lock:
            result = SyncResult(synced_at=datetime.now())

            try:
                if sequence_names is None:
                    # Get all available sequences
                    available = await self.list_available_sequences()
                    sequence_names = [s.name for s in available if s.is_active]

                result.sequences_checked = len(sequence_names)

                for name in sequence_names:
                    pull_result = await self._pull_sequence_internal(name)
                    result.results.append(pull_result)

                    if pull_result.error:
                        result.sequences_failed += 1
                    elif pull_result.updated:
                        result.sequences_updated += 1

            except Exception as e:
                logger.exception(f"Sync failed: {e}")
                result.error = str(e)

            return result

    async def check_updates(self) -> Dict[str, Dict[str, Any]]:
        """
        Check for updates without downloading.

        Returns:
            Dict mapping sequence names to update status
        """
        updates = {}

        try:
            available = await self.list_available_sequences()
            local_sequences = {s.name: s for s in self.list_local_sequences()}

            for seq in available:
                if not seq.is_active:
                    continue

                local = local_sequences.get(seq.name)
                updates[seq.name] = {
                    "remote_version": seq.version,
                    "local_version": local.version if local else None,
                    "needs_update": local is None or local.version != seq.version,
                    "installed": local is not None,
                }

        except Exception as e:
            logger.error(f"Failed to check updates: {e}")
            raise

        return updates

    # =========================================================================
    # Delete Operations
    # =========================================================================

    def delete_sequence(self, sequence_name: str) -> bool:
        """
        Delete a locally installed sequence.

        Args:
            sequence_name: Name of the sequence to delete

        Returns:
            True if deleted, False if not found
        """
        package_path = self.sequences_dir / sequence_name
        if not package_path.exists():
            return False

        shutil.rmtree(package_path)
        logger.info(f"Deleted sequence '{sequence_name}'")
        return True
