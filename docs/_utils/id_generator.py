"""
Document ID Generator

Generates unique document IDs based on manifest and module information.
"""

import json
import re
from pathlib import Path
from typing import Optional


# Module code mapping
MODULE_CODES = {
    "inventory": "INV",
    "order": "ORD",
    "production": "PRD",
    "quality": "QLT",
    "user": "USR",
    "auth": "AUT",
    "equipment": "EQP",
    "material": "MAT",
    "warehouse": "WHS",
    "shipping": "SHP",
}

# Type code mapping
TYPE_CODES = {
    # Requirements
    "requirement": "FR",

    # Design
    "api": "API",
    "database": "DB",
    "architecture": "ARCH",
    "component": "COMP",
    "security": "SEC",

    # Implementation
    "model": "MDL",
    "service": "SVC",
    "router": "RTR",
    "component_fe": "CMP",

    # Testing
    "unit_test": "TEST",
    "integration_test": "ITEST",
    "e2e_test": "E2E",

    # Deployment
    "deployment": "DPL",
    "docker": "DCK",
    "nginx": "NGX",
}


def get_module_code(module: str) -> str:
    """
    Get 3-letter module code.

    Args:
        module: Module name (e.g., "inventory")

    Returns:
        3-letter code (e.g., "INV")
    """
    if module.lower() in MODULE_CODES:
        return MODULE_CODES[module.lower()]

    # Auto-generate if not in mapping
    return module[:3].upper()


def get_next_sequence(manifest_path: Path, type_code: str, module_code: str) -> int:
    """
    Get next sequence number for a document type and module.

    Args:
        manifest_path: Path to _manifest.json
        type_code: Document type code (e.g., "SVC")
        module_code: Module code (e.g., "INV")

    Returns:
        Next sequence number
    """
    if not manifest_path.exists():
        return 1

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    if not manifest.get("index"):
        return 1

    # Find documents with matching prefix
    prefix = f"{type_code}-{module_code}-"
    matching_docs = [
        doc["id"] for doc in manifest["index"]
        if doc["id"].startswith(prefix)
    ]

    if not matching_docs:
        return 1

    # Extract sequence numbers
    sequences = []
    for doc_id in matching_docs:
        # Extract last part (sequence)
        match = re.search(r'-(\d+)$', doc_id)
        if match:
            sequences.append(int(match.group(1)))

    if not sequences:
        return 1

    return max(sequences) + 1


def generate_doc_id(
    phase: str,
    doc_type: str,
    module: str,
    manifest_path: Optional[Path] = None
) -> str:
    """
    Generate document ID.

    Args:
        phase: Phase name (e.g., "implementation")
        doc_type: Document type (e.g., "service")
        module: Module name (e.g., "inventory")
        manifest_path: Path to manifest (optional, will auto-detect)

    Returns:
        Document ID (e.g., "SVC-INV-001")
    """
    # Get codes
    type_code = TYPE_CODES.get(doc_type.lower(), doc_type[:3].upper())
    module_code = get_module_code(module)

    # Auto-detect manifest path
    if manifest_path is None:
        manifest_path = Path(f"docs/{phase}/_manifest.json")

    # Get next sequence
    seq = get_next_sequence(manifest_path, type_code, module_code)

    # Format: TYPE-MOD-SEQ (3 digits)
    return f"{type_code}-{module_code}-{seq:03d}"


def generate_filename(doc_id: str, title: str) -> str:
    """
    Generate filename from document ID and title.

    Args:
        doc_id: Document ID (e.g., "SVC-INV-001")
        title: Document title (e.g., "Inventory Service Implementation")

    Returns:
        Filename (e.g., "SVC-INV-001-inventory-service.md")
    """
    # Convert title to kebab-case
    readable = title.lower()

    # Remove common suffixes
    readable = re.sub(r'\s+(implementation|specification|design|config)', '', readable)

    # Replace spaces with hyphens
    readable = readable.strip().replace(' ', '-')

    # Remove special characters
    readable = re.sub(r'[^a-z0-9-]', '', readable)

    # Remove multiple hyphens
    readable = re.sub(r'-+', '-', readable)

    return f"{doc_id}-{readable}.md"


if __name__ == "__main__":
    # Test
    print("Test ID Generation:")
    print(f"Service: {generate_doc_id('implementation', 'service', 'inventory')}")
    print(f"API: {generate_doc_id('design', 'api', 'order')}")
    print(f"Test: {generate_doc_id('testing', 'unit_test', 'production')}")

    print("\nTest Filename Generation:")
    print(generate_filename("SVC-INV-001", "Inventory Service Implementation"))
    print(generate_filename("API-ORD-002", "Create Order Endpoint"))
