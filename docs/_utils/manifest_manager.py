"""
Manifest Manager

Manages _manifest.json files for tracking documents and dependencies.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ManifestManager:
    """Manages manifest files for document tracking."""

    def __init__(self, phase: str):
        """
        Initialize manifest manager.

        Args:
            phase: Phase name (requirements, design, implementation, testing, deployment)
        """
        self.phase = phase
        self.manifest_path = Path(f"docs/{phase}/_manifest.json")

    def load(self) -> Dict[str, Any]:
        """Load manifest file."""
        if not self.manifest_path.exists():
            return self._create_empty_manifest()

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, manifest: Dict[str, Any]) -> None:
        """
        Save manifest file.

        Args:
            manifest: Manifest data
        """
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def _create_empty_manifest(self) -> Dict[str, Any]:
        """Create empty manifest structure."""
        return {
            "phase": self.phase,
            "last_updated": None,
            "total_documents": 0,
            "documents_by_module": {},
            "index": [],
            "dependency_graph": {},
            "modules": {}
        }

    def add_document(
        self,
        doc_id: str,
        uuid: str,
        file_path: str,
        title: str,
        module: str,
        doc_type: str,
        dependencies: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        version: int = 1
    ) -> None:
        """
        Add or update document in manifest.

        Args:
            doc_id: Document ID (e.g., "SVC-INV-001")
            uuid: UUID
            file_path: Relative file path
            title: Document title
            module: Module name
            doc_type: Document type
            dependencies: List of dependency document IDs
            outputs: List of generated file paths
            version: Document version
        """
        manifest = self.load()

        # Check if document exists
        existing_idx = self._find_document_index(manifest, doc_id)

        now = datetime.utcnow().isoformat() + "Z"

        doc_entry = {
            "id": doc_id,
            "uuid": uuid,
            "file": file_path,
            "title": title,
            "module": module,
            "type": doc_type,
            "status": "created",
            "version": version,
            "dependencies": dependencies or [],
            "outputs": outputs or [],
            "updated": now
        }

        if existing_idx >= 0:
            # Update existing
            doc_entry["created"] = manifest["index"][existing_idx].get("created", now)
            manifest["index"][existing_idx] = doc_entry
        else:
            # Add new
            doc_entry["created"] = now
            manifest["index"].append(doc_entry)

        # Update dependency graph
        if dependencies:
            manifest["dependency_graph"][doc_id] = {
                "depends_on": dependencies,
                "used_by": []
            }

            # Update reverse dependencies
            for dep_id in dependencies:
                if dep_id in manifest["dependency_graph"]:
                    if doc_id not in manifest["dependency_graph"][dep_id]["used_by"]:
                        manifest["dependency_graph"][dep_id]["used_by"].append(doc_id)
                else:
                    manifest["dependency_graph"][dep_id] = {
                        "depends_on": [],
                        "used_by": [doc_id]
                    }

        # Update module stats
        if module not in manifest["modules"]:
            manifest["modules"][module] = {
                "status": "in_progress",
                "documents": [],
                "completion_percentage": 0
            }

        if doc_id not in manifest["modules"][module]["documents"]:
            manifest["modules"][module]["documents"].append(doc_id)

        # Update counts
        manifest["total_documents"] = len(manifest["index"])
        manifest["documents_by_module"] = {
            mod: len(data["documents"])
            for mod, data in manifest["modules"].items()
        }
        manifest["last_updated"] = now

        self.save(manifest)

    def _find_document_index(self, manifest: Dict[str, Any], doc_id: str) -> int:
        """
        Find document index in manifest.

        Args:
            manifest: Manifest data
            doc_id: Document ID

        Returns:
            Index in manifest["index"], or -1 if not found
        """
        for idx, doc in enumerate(manifest.get("index", [])):
            if doc["id"] == doc_id:
                return idx
        return -1

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document data or None
        """
        manifest = self.load()
        idx = self._find_document_index(manifest, doc_id)

        if idx >= 0:
            return manifest["index"][idx]

        return None

    def get_documents_by_module(self, module: str) -> List[Dict[str, Any]]:
        """
        Get all documents for a module.

        Args:
            module: Module name

        Returns:
            List of document data
        """
        manifest = self.load()

        return [
            doc for doc in manifest.get("index", [])
            if doc["module"] == module
        ]

    def update_document_status(self, doc_id: str, status: str) -> None:
        """
        Update document status.

        Args:
            doc_id: Document ID
            status: New status (created, in_progress, implemented, tested, deployed)
        """
        manifest = self.load()
        idx = self._find_document_index(manifest, doc_id)

        if idx >= 0:
            manifest["index"][idx]["status"] = status
            manifest["index"][idx]["updated"] = datetime.utcnow().isoformat() + "Z"
            self.save(manifest)

    def get_dependencies(self, doc_id: str) -> List[str]:
        """
        Get dependencies for a document.

        Args:
            doc_id: Document ID

        Returns:
            List of dependency document IDs
        """
        manifest = self.load()
        return manifest.get("dependency_graph", {}).get(doc_id, {}).get("depends_on", [])

    def get_dependents(self, doc_id: str) -> List[str]:
        """
        Get documents that depend on this document.

        Args:
            doc_id: Document ID

        Returns:
            List of dependent document IDs
        """
        manifest = self.load()
        return manifest.get("dependency_graph", {}).get(doc_id, {}).get("used_by", [])


if __name__ == "__main__":
    # Test
    import uuid

    manager = ManifestManager("implementation")

    manager.add_document(
        doc_id="SVC-INV-001",
        uuid=str(uuid.uuid4()),
        file_path="backend/services/SVC-INV-001-inventory-service.md",
        title="Inventory Service",
        module="inventory",
        doc_type="service",
        dependencies=["API-INV-001", "DB-INV-001"],
        outputs=["app/services/inventory_service.py"],
        version=1
    )

    print("Manifest updated successfully!")
    print(f"Document: {manager.get_document('SVC-INV-001')}")
