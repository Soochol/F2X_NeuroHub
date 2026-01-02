"""
CRUD operations for Sequence models.

Provides database operations for sequence management including
upload, versioning, and deployment tracking.
"""

import base64
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sequence import Sequence, SequenceDeployment, SequenceVersion
from app.schemas.sequence import (
    SequenceCreate,
    SequenceListParams,
    SequenceManifest,
    SequenceUpdate,
)


class SequenceCRUD:
    """CRUD operations for sequences."""

    # ========================================================================
    # Sequence CRUD
    # ========================================================================

    async def get_by_id(
        self,
        db: AsyncSession,
        sequence_id: int,
    ) -> Optional[Sequence]:
        """Get sequence by ID."""
        result = await db.execute(
            select(Sequence).where(Sequence.id == sequence_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Optional[Sequence]:
        """Get sequence by name."""
        result = await db.execute(
            select(Sequence).where(Sequence.name == name)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        params: SequenceListParams,
    ) -> Tuple[List[Sequence], int]:
        """
        Get list of sequences with filtering and pagination.

        Returns:
            Tuple of (sequences, total_count)
        """
        # Build base query
        query = select(Sequence)
        count_query = select(func.count(Sequence.id))

        # Apply filters
        filters = []
        if params.is_active is not None:
            filters.append(Sequence.is_active == params.is_active)
        if params.is_deprecated is not None:
            filters.append(Sequence.is_deprecated == params.is_deprecated)
        if params.process_id is not None:
            filters.append(Sequence.process_id == params.process_id)
        if params.search:
            search_term = f"%{params.search}%"
            filters.append(
                or_(
                    Sequence.name.ilike(search_term),
                    Sequence.display_name.ilike(search_term),
                    Sequence.description.ilike(search_term),
                )
            )

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.order_by(Sequence.updated_at.desc())
            .offset(params.skip)
            .limit(params.limit)
        )

        result = await db.execute(query)
        sequences = list(result.scalars().all())

        return sequences, total

    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        version: str,
        package_data: str,
        checksum: str,
        package_size: int,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        hardware: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
        process_id: Optional[int] = None,
        uploaded_by: Optional[int] = None,
    ) -> Sequence:
        """Create a new sequence."""
        sequence = Sequence(
            name=name,
            version=version,
            display_name=display_name or name,
            description=description,
            package_data=package_data,
            checksum=checksum,
            package_size=package_size,
            hardware=hardware or {},
            parameters=parameters or {},
            steps=steps or [],
            process_id=process_id,
            uploaded_by=uploaded_by,
            is_active=True,
            is_deprecated=False,
        )
        db.add(sequence)
        await db.flush()
        await db.refresh(sequence)
        return sequence

    async def update(
        self,
        db: AsyncSession,
        sequence: Sequence,
        update_data: SequenceUpdate,
    ) -> Sequence:
        """Update sequence metadata."""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(sequence, field, value)
        await db.flush()
        await db.refresh(sequence)
        return sequence

    async def update_package(
        self,
        db: AsyncSession,
        sequence: Sequence,
        *,
        version: str,
        package_data: str,
        checksum: str,
        package_size: int,
        hardware: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
        uploaded_by: Optional[int] = None,
        change_notes: Optional[str] = None,
    ) -> Tuple[Sequence, SequenceVersion]:
        """
        Update sequence package and create version history.

        Returns:
            Tuple of (updated_sequence, created_version)
        """
        # Save current version to history
        version_record = await self.create_version(
            db,
            sequence=sequence,
            change_notes=change_notes,
        )

        # Update sequence
        sequence.version = version
        sequence.package_data = package_data
        sequence.checksum = checksum
        sequence.package_size = package_size
        if hardware is not None:
            sequence.hardware = hardware
        if parameters is not None:
            sequence.parameters = parameters
        if steps is not None:
            sequence.steps = steps
        if uploaded_by is not None:
            sequence.uploaded_by = uploaded_by

        await db.flush()
        await db.refresh(sequence)

        return sequence, version_record

    async def delete(
        self,
        db: AsyncSession,
        sequence: Sequence,
    ) -> None:
        """Delete sequence (cascades to versions and deployments)."""
        await db.delete(sequence)
        await db.flush()

    # ========================================================================
    # Version CRUD
    # ========================================================================

    async def get_versions(
        self,
        db: AsyncSession,
        sequence_id: int,
        limit: int = 20,
    ) -> List[SequenceVersion]:
        """Get version history for a sequence."""
        result = await db.execute(
            select(SequenceVersion)
            .where(SequenceVersion.sequence_id == sequence_id)
            .order_by(SequenceVersion.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_version(
        self,
        db: AsyncSession,
        sequence_id: int,
        version: str,
    ) -> Optional[SequenceVersion]:
        """Get specific version of a sequence."""
        result = await db.execute(
            select(SequenceVersion).where(
                and_(
                    SequenceVersion.sequence_id == sequence_id,
                    SequenceVersion.version == version,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_version(
        self,
        db: AsyncSession,
        sequence: Sequence,
        change_notes: Optional[str] = None,
    ) -> SequenceVersion:
        """Create version record from current sequence state."""
        version = SequenceVersion(
            sequence_id=sequence.id,
            version=sequence.version,
            package_data=sequence.package_data,
            checksum=sequence.checksum,
            package_size=sequence.package_size,
            hardware=sequence.hardware,
            parameters=sequence.parameters,
            steps=sequence.steps,
            change_notes=change_notes,
            uploaded_by=sequence.uploaded_by,
        )
        db.add(version)
        await db.flush()
        await db.refresh(version)
        return version

    # ========================================================================
    # Deployment CRUD
    # ========================================================================

    async def get_deployments(
        self,
        db: AsyncSession,
        sequence_id: Optional[int] = None,
        station_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[SequenceDeployment]:
        """Get deployment records with optional filtering."""
        query = select(SequenceDeployment)

        filters = []
        if sequence_id is not None:
            filters.append(SequenceDeployment.sequence_id == sequence_id)
        if station_id is not None:
            filters.append(SequenceDeployment.station_id == station_id)
        if status is not None:
            filters.append(SequenceDeployment.status == status)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(SequenceDeployment.created_at.desc()).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_deployment(
        self,
        db: AsyncSession,
        *,
        sequence_id: int,
        version: str,
        station_id: str,
        batch_id: Optional[str] = None,
        deployed_by: Optional[int] = None,
    ) -> SequenceDeployment:
        """Create deployment record."""
        deployment = SequenceDeployment(
            sequence_id=sequence_id,
            version=version,
            station_id=station_id,
            batch_id=batch_id,
            status="pending",
            deployed_by=deployed_by,
        )
        db.add(deployment)
        await db.flush()
        await db.refresh(deployment)
        return deployment

    async def update_deployment_status(
        self,
        db: AsyncSession,
        deployment: SequenceDeployment,
        status: str,
        error_message: Optional[str] = None,
    ) -> SequenceDeployment:
        """Update deployment status."""
        deployment.status = status
        if status == "deployed":
            deployment.deployed_at = datetime.now(timezone.utc)
        if error_message:
            deployment.error_message = error_message
        await db.flush()
        await db.refresh(deployment)
        return deployment

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        """Calculate SHA-256 checksum of data."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def encode_package(data: bytes) -> str:
        """Encode package data to Base64 string."""
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def decode_package(encoded: str) -> bytes:
        """Decode package data from Base64 string."""
        return base64.b64decode(encoded.encode("utf-8"))


# Singleton instance
sequence_crud = SequenceCRUD()
