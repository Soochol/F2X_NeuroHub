"""
Sync Repository for Station Service.

Provides CRUD operations for SyncQueue entities.
Handles offline synchronization queue for backend communication.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from station_service.storage.database import Database

logger = logging.getLogger(__name__)


class SyncRepository:
    """
    Repository for SyncQueue CRUD operations.

    Handles persistence of sync queue entries for offline mode.
    When backend is unavailable, operations are queued for later sync.

    Usage:
        db = await get_database()
        repo = SyncRepository(db)

        # Queue an execution for sync
        await repo.enqueue(
            entity_type="execution",
            entity_id="exec_123",
            action="create",
            payload={"status": "completed", "overall_pass": True}
        )

        # Get pending items
        items = await repo.get_pending_items(limit=10)

        # Mark as synced (delete from queue)
        await repo.dequeue(item_id)

        # Handle retry on failure
        await repo.mark_failed(item_id, "Connection timeout")
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize repository with database instance.

        Args:
            db: Database instance for queries.
        """
        self._db = db

    async def enqueue(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: dict[str, Any],
    ) -> int:
        """
        Add item to sync queue.

        Args:
            entity_type: Type of entity (execution, log).
            entity_id: ID of the entity.
            action: Action to perform (create, update).
            payload: Data payload as dict.

        Returns:
            Created queue item ID.
        """
        payload_json = json.dumps(payload)

        row_id = await self._db.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, action, payload_json)
            VALUES (?, ?, ?, ?)
            """,
            (entity_type, entity_id, action, payload_json),
        )

        logger.debug(f"Enqueued sync item: {entity_type}/{entity_id} ({action})")
        return row_id

    async def get_item(self, id: int) -> Optional[dict[str, Any]]:
        """
        Get sync queue item by ID.

        Args:
            id: Queue item ID.

        Returns:
            Queue item as dict or None if not found.
        """
        row = await self._db.fetch_one(
            "SELECT * FROM sync_queue WHERE id = ?",
            (id,),
        )

        if row and row.get("payload_json"):
            row["payload"] = json.loads(row["payload_json"])
            del row["payload_json"]

        return row

    async def get_pending_items(
        self,
        entity_type: Optional[str] = None,
        limit: int = 100,
        max_retries: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Get pending items from sync queue.

        Args:
            entity_type: Filter by entity type.
            limit: Maximum number of items.
            max_retries: Maximum retry count to include.

        Returns:
            List of pending queue items ordered by creation time.
        """
        query = "SELECT * FROM sync_queue WHERE retry_count < ?"
        params: list[Any] = [max_retries]

        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)

        query += " ORDER BY created_at ASC LIMIT ?"
        params.append(limit)

        rows = await self._db.fetch_all(query, params)

        for row in rows:
            if row.get("payload_json"):
                row["payload"] = json.loads(row["payload_json"])
                del row["payload_json"]

        return rows

    async def get_items_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[dict[str, Any]]:
        """
        Get all queue items for a specific entity.

        Args:
            entity_type: Entity type.
            entity_id: Entity ID.

        Returns:
            List of queue items for the entity.
        """
        rows = await self._db.fetch_all(
            """
            SELECT * FROM sync_queue
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY created_at ASC
            """,
            (entity_type, entity_id),
        )

        for row in rows:
            if row.get("payload_json"):
                row["payload"] = json.loads(row["payload_json"])
                del row["payload_json"]

        return rows

    async def dequeue(self, id: int) -> bool:
        """
        Remove item from sync queue (mark as synced).

        Args:
            id: Queue item ID.

        Returns:
            True if removed, False otherwise.
        """
        result = await self._db.execute(
            "DELETE FROM sync_queue WHERE id = ?",
            (id,),
        )

        if result > 0:
            logger.debug(f"Dequeued sync item: {id}")

        return result > 0

    async def dequeue_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> int:
        """
        Remove all queue items for a specific entity.

        Args:
            entity_type: Entity type.
            entity_id: Entity ID.

        Returns:
            Number of removed items.
        """
        return await self._db.execute(
            "DELETE FROM sync_queue WHERE entity_type = ? AND entity_id = ?",
            (entity_type, entity_id),
        )

    async def mark_failed(
        self,
        id: int,
        error: str,
    ) -> bool:
        """
        Mark sync attempt as failed and increment retry count.

        Args:
            id: Queue item ID.
            error: Error message.

        Returns:
            True if updated, False otherwise.
        """
        result = await self._db.execute(
            """
            UPDATE sync_queue
            SET retry_count = retry_count + 1, last_error = ?
            WHERE id = ?
            """,
            (error, id),
        )

        if result > 0:
            logger.warning(f"Sync item {id} failed: {error}")

        return result > 0

    async def reset_retries(self, id: int) -> bool:
        """
        Reset retry count for a queue item.

        Args:
            id: Queue item ID.

        Returns:
            True if updated, False otherwise.
        """
        result = await self._db.execute(
            "UPDATE sync_queue SET retry_count = 0, last_error = NULL WHERE id = ?",
            (id,),
        )
        return result > 0

    async def count_pending(
        self,
        entity_type: Optional[str] = None,
        max_retries: int = 5,
    ) -> int:
        """
        Count pending items in sync queue.

        Args:
            entity_type: Filter by entity type.
            max_retries: Maximum retry count to include.

        Returns:
            Count of pending items.
        """
        query = "SELECT COUNT(*) FROM sync_queue WHERE retry_count < ?"
        params: list[Any] = [max_retries]

        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)

        result = await self._db.fetch_value(query, params)
        return result or 0

    async def count_failed(self, min_retries: int = 5) -> int:
        """
        Count failed items (exceeded retry limit).

        Args:
            min_retries: Minimum retry count to be considered failed.

        Returns:
            Count of failed items.
        """
        result = await self._db.fetch_value(
            "SELECT COUNT(*) FROM sync_queue WHERE retry_count >= ?",
            (min_retries,),
        )
        return result or 0

    async def get_failed_items(
        self,
        min_retries: int = 5,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get failed items that exceeded retry limit.

        Args:
            min_retries: Minimum retry count to be considered failed.
            limit: Maximum number of items.

        Returns:
            List of failed queue items.
        """
        rows = await self._db.fetch_all(
            """
            SELECT * FROM sync_queue
            WHERE retry_count >= ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (min_retries, limit),
        )

        for row in rows:
            if row.get("payload_json"):
                row["payload"] = json.loads(row["payload_json"])
                del row["payload_json"]

        return rows

    async def cleanup_old_items(
        self,
        days: int = 7,
        max_retries: int = 10,
    ) -> int:
        """
        Clean up old failed items from queue.

        Args:
            days: Delete items older than this many days.
            max_retries: Delete items with retry count >= this.

        Returns:
            Number of deleted items.
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)

        return await self._db.execute(
            """
            DELETE FROM sync_queue
            WHERE (created_at < ? AND retry_count >= ?)
            """,
            (cutoff.isoformat(), max_retries),
        )

    async def clear_queue(self, entity_type: Optional[str] = None) -> int:
        """
        Clear all items from sync queue.

        Args:
            entity_type: Only clear items of this type.

        Returns:
            Number of deleted items.
        """
        if entity_type:
            return await self._db.execute(
                "DELETE FROM sync_queue WHERE entity_type = ?",
                (entity_type,),
            )
        else:
            return await self._db.execute("DELETE FROM sync_queue")

    async def update_payload(
        self,
        id: int,
        payload: dict[str, Any],
    ) -> bool:
        """
        Update payload of a queue item.

        Args:
            id: Queue item ID.
            payload: New payload data.

        Returns:
            True if updated, False otherwise.
        """
        payload_json = json.dumps(payload)

        result = await self._db.execute(
            "UPDATE sync_queue SET payload_json = ? WHERE id = ?",
            (payload_json, id),
        )
        return result > 0
