"""
Git Sync Service for automatic sequence synchronization.

Provides background polling of Git repositories and automatic
upload of changed sequences.
"""

import asyncio
import io
import logging
import time
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import httpx
import yaml

from app.crud.git_sync import git_sync_crud
from app.crud.sequence import sequence_crud
from app.database import AsyncSessionLocal
from app.models.git_sync import GitSyncConfig
from app.schemas.git_sync import (
    GitRepoInfoResponse,
    GitSyncResultResponse,
    GitSyncStatusResponse,
)

logger = logging.getLogger(__name__)


class GitSyncService:
    """
    Service for syncing sequences from Git repositories.

    Provides:
    - Polling Git repositories for changes
    - Downloading and uploading changed sequences
    - Background task management
    """

    def __init__(self):
        self._polling_tasks: Dict[int, asyncio.Task] = {}
        self._running = False

    # =========================================================================
    # GitHub API Helpers
    # =========================================================================

    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo."""
        parsed = urlparse(url)

        if parsed.netloc != "github.com":
            raise ValueError("Only GitHub URLs are supported")

        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")

        owner = path_parts[0]
        repo = path_parts[1].replace(".git", "")

        return owner, repo

    async def _get_latest_commit(
        self,
        owner: str,
        repo: str,
        branch: str,
        auth_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get latest commit info from GitHub."""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "F2X-NeuroHub-GitSync",
        }

        if auth_token:
            headers["Authorization"] = f"token {auth_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise ValueError(f"Branch '{branch}' not found")
            elif response.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded")
            elif response.status_code != 200:
                raise ValueError(f"GitHub API error: {response.status_code}")

            return response.json()

    async def _list_folder_contents(
        self,
        owner: str,
        repo: str,
        branch: str,
        folder_path: str,
        auth_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List contents of a folder in the repo."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_path}"
        if branch:
            url = f"{url}?ref={branch}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "F2X-NeuroHub-GitSync",
        }

        if auth_token:
            headers["Authorization"] = f"token {auth_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                return []
            elif response.status_code != 200:
                raise ValueError(f"GitHub API error: {response.status_code}")

            return response.json()

    async def _download_folder_as_zip(
        self,
        owner: str,
        repo: str,
        branch: str,
        folder_path: str,
        auth_token: Optional[str] = None,
    ) -> bytes:
        """Download a folder from GitHub as a ZIP file."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "F2X-NeuroHub-GitSync",
        }

        if auth_token:
            headers["Authorization"] = f"token {auth_token}"

        async def fetch_contents(path: str) -> List[Dict]:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            if branch:
                url = f"{url}?ref={branch}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code != 200:
                    return []
                data = response.json()
                return data if isinstance(data, list) else [data]

        async def download_file(download_url: str) -> bytes:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(download_url, headers=headers)
                return response.content if response.status_code == 200 else b""

        async def process_contents(path: str, files: Dict[str, bytes]) -> None:
            contents = await fetch_contents(path)

            for item in contents:
                item_path = item["path"]
                if folder_path:
                    rel_path = item_path[len(folder_path):].lstrip("/")
                else:
                    rel_path = item_path

                if item["type"] == "file":
                    file_content = await download_file(item["download_url"])
                    if file_content:
                        files[rel_path] = file_content
                elif item["type"] == "dir":
                    await process_contents(item_path, files)

        files: Dict[str, bytes] = {}
        await process_contents(folder_path, files)

        if not files:
            raise ValueError("No files found in the specified path")

        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path, content in files.items():
                zf.writestr(file_path, content)

        return zip_buffer.getvalue()

    # =========================================================================
    # Sync Operations
    # =========================================================================

    async def check_for_updates(self, config: GitSyncConfig) -> GitSyncStatusResponse:
        """Check if there are updates in the Git repository."""
        try:
            owner, repo = self._parse_github_url(config.repository_url)
            auth_token = config.auth_token if config.auth_type == "token" else None

            # Get latest commit
            commit_data = await self._get_latest_commit(
                owner, repo, config.branch, auth_token
            )

            remote_sha = commit_data["sha"]
            has_updates = config.last_commit_sha != remote_sha

            # List sequences in folder
            sequences_changed = []
            if has_updates and config.folder_path:
                contents = await self._list_folder_contents(
                    owner, repo, config.branch, config.folder_path, auth_token
                )
                sequences_changed = [
                    item["name"] for item in contents
                    if item["type"] == "dir"
                ]

            return GitSyncStatusResponse(
                config_name=config.name,
                repository_url=config.repository_url,
                branch=config.branch,
                enabled=config.enabled,
                sync_status=config.sync_status,
                last_commit_sha=config.last_commit_sha,
                remote_commit_sha=remote_sha,
                has_updates=has_updates,
                last_sync_at=config.last_sync_at,
                last_check_at=datetime.now(),
                sequences_changed=sequences_changed,
            )

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return GitSyncStatusResponse(
                config_name=config.name,
                repository_url=config.repository_url,
                branch=config.branch,
                enabled=config.enabled,
                sync_status="error",
                last_commit_sha=config.last_commit_sha,
                has_updates=False,
                last_sync_at=config.last_sync_at,
                last_check_at=datetime.now(),
                last_error=str(e),
            )

    async def sync_sequences(
        self,
        config: GitSyncConfig,
        force: bool = False,
        sequence_names: Optional[List[str]] = None,
        user_id: Optional[int] = None,
    ) -> GitSyncResultResponse:
        """
        Sync sequences from Git repository.

        Args:
            config: Git sync configuration
            force: Force sync even if no changes detected
            sequence_names: Specific sequences to sync (None = all)
            user_id: User ID for upload tracking

        Returns:
            Sync result with updated/created sequences
        """
        start_time = time.time()
        result = GitSyncResultResponse(
            config_name=config.name,
            success=False,
            message="",
        )

        try:
            owner, repo = self._parse_github_url(config.repository_url)
            auth_token = config.auth_token if config.auth_type == "token" else None

            # Get latest commit
            commit_data = await self._get_latest_commit(
                owner, repo, config.branch, auth_token
            )
            remote_sha = commit_data["sha"]

            # Check if update needed
            if not force and config.last_commit_sha == remote_sha:
                result.success = True
                result.message = "Already up to date"
                result.commit_sha = remote_sha
                result.duration_seconds = time.time() - start_time
                return result

            # List sequences in folder
            folder_path = config.folder_path or ""
            contents = await self._list_folder_contents(
                owner, repo, config.branch, folder_path, auth_token
            )

            sequence_folders = [
                item for item in contents
                if item["type"] == "dir"
                and (sequence_names is None or item["name"] in sequence_names)
            ]

            # Sync each sequence
            async with AsyncSessionLocal() as db:
                for folder in sequence_folders:
                    seq_name = folder["name"]
                    seq_path = f"{folder_path}/{seq_name}" if folder_path else seq_name

                    try:
                        # Download sequence folder as ZIP
                        zip_data = await self._download_folder_as_zip(
                            owner, repo, config.branch, seq_path, auth_token
                        )

                        # Parse manifest
                        manifest = self._parse_manifest(zip_data)
                        if not manifest:
                            result.sequences_failed.append(seq_name)
                            continue

                        # Calculate checksum and encode
                        checksum = sequence_crud.calculate_checksum(zip_data)
                        package_data = sequence_crud.encode_package(zip_data)
                        package_size = len(zip_data)

                        # Check if sequence exists
                        existing = await sequence_crud.get_by_name(db, manifest["name"])

                        if existing:
                            # Skip if unchanged
                            if existing.checksum == checksum:
                                continue

                            # Update existing
                            new_version = sequence_crud.increment_version(existing.version)
                            await sequence_crud.update_package(
                                db,
                                existing,
                                version=new_version,
                                package_data=package_data,
                                checksum=checksum,
                                package_size=package_size,
                                hardware=manifest.get("hardware"),
                                parameters=manifest.get("parameters"),
                                steps=manifest.get("steps"),
                                uploaded_by=user_id,
                                change_notes=f"Auto-synced from Git: {remote_sha[:8]}",
                            )
                            result.sequences_updated.append(seq_name)
                        else:
                            # Create new
                            await sequence_crud.create(
                                db,
                                name=manifest["name"],
                                version="1.0.0",
                                package_data=package_data,
                                checksum=checksum,
                                package_size=package_size,
                                display_name=manifest.get("display_name"),
                                description=manifest.get("description"),
                                hardware=manifest.get("hardware"),
                                parameters=manifest.get("parameters"),
                                steps=manifest.get("steps"),
                                uploaded_by=user_id,
                            )
                            result.sequences_created.append(seq_name)

                    except Exception as e:
                        logger.error(f"Failed to sync sequence {seq_name}: {e}")
                        result.sequences_failed.append(seq_name)

                # Update config status
                await git_sync_crud.update_sync_status(
                    db, config, "synced", commit_sha=remote_sha
                )
                await db.commit()

            result.success = True
            result.commit_sha = remote_sha
            result.message = (
                f"Synced {len(result.sequences_updated)} updated, "
                f"{len(result.sequences_created)} created"
            )

        except Exception as e:
            logger.exception(f"Sync failed: {e}")
            result.success = False
            result.message = str(e)

            # Update error status
            async with AsyncSessionLocal() as db:
                await git_sync_crud.update_sync_status(
                    db, config, "error", error=str(e)
                )
                await db.commit()

        result.duration_seconds = time.time() - start_time
        return result

    def _parse_manifest(self, zip_data: bytes) -> Optional[Dict[str, Any]]:
        """Parse manifest.yaml from ZIP data."""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
                for name in zf.namelist():
                    if name.endswith("manifest.yaml") or name.endswith("manifest.yml"):
                        with zf.open(name) as f:
                            return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to parse manifest: {e}")
        return None

    # =========================================================================
    # Repository Info
    # =========================================================================

    async def get_repo_info(self, config: GitSyncConfig) -> GitRepoInfoResponse:
        """Get information about the Git repository."""
        owner, repo = self._parse_github_url(config.repository_url)
        auth_token = config.auth_token if config.auth_type == "token" else None

        commit_data = await self._get_latest_commit(
            owner, repo, config.branch, auth_token
        )

        # List sequences
        folder_path = config.folder_path or ""
        contents = await self._list_folder_contents(
            owner, repo, config.branch, folder_path, auth_token
        )
        sequences = [item["name"] for item in contents if item["type"] == "dir"]

        return GitRepoInfoResponse(
            repository_url=config.repository_url,
            branch=config.branch,
            latest_commit_sha=commit_data["sha"],
            latest_commit_message=commit_data["commit"]["message"].split("\n")[0],
            latest_commit_date=datetime.fromisoformat(
                commit_data["commit"]["committer"]["date"].replace("Z", "+00:00")
            ),
            sequences_found=sequences,
        )

    # =========================================================================
    # Background Polling
    # =========================================================================

    async def start_polling(self) -> None:
        """Start background polling for all enabled configs."""
        if self._running:
            return

        self._running = True
        logger.info("Starting Git sync background polling")

        async with AsyncSessionLocal() as db:
            configs = await git_sync_crud.get_enabled(db)

            for config in configs:
                self._start_polling_task(config)

    async def stop_polling(self) -> None:
        """Stop all background polling tasks."""
        self._running = False

        for task in self._polling_tasks.values():
            task.cancel()

        self._polling_tasks.clear()
        logger.info("Stopped Git sync background polling")

    def _start_polling_task(self, config: GitSyncConfig) -> None:
        """Start polling task for a config."""
        if config.id in self._polling_tasks:
            return

        task = asyncio.create_task(self._polling_loop(config))
        self._polling_tasks[config.id] = task
        logger.info(f"Started polling for {config.name}")

    async def _polling_loop(self, config: GitSyncConfig) -> None:
        """Polling loop for a single config."""
        while self._running:
            try:
                # Check for updates
                status = await self.check_for_updates(config)

                if status.has_updates and config.auto_upload:
                    logger.info(f"Updates detected for {config.name}, syncing...")
                    await self.sync_sequences(config)

                # Wait for next poll
                await asyncio.sleep(config.poll_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Polling error for {config.name}: {e}")
                await asyncio.sleep(60)  # Wait before retry


# Global service instance
git_sync_service = GitSyncService()
