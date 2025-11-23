#!/usr/bin/env python
"""
Swagger/OpenAPI Validation Automation Script

Validates FastAPI OpenAPI schema without running full test suite.
Useful for quick validation during development and CI/CD.

Usage:
    python scripts/validate_swagger.py
    python scripts/validate_swagger.py --save schema.json
    python scripts/validate_swagger.py --compare schema_v1.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app


class SwaggerValidator:
    """OpenAPI/Swagger validation automation."""

    def __init__(self):
        self.client = TestClient(app)
        self.schema = None
        self.errors = []
        self.warnings = []

    def fetch_schema(self) -> Dict[str, Any]:
        """Fetch OpenAPI schema from running app."""
        response = self.client.get("/api/v1/openapi.json")

        if response.status_code != 200:
            raise Exception(f"Failed to fetch OpenAPI schema: {response.status_code}")

        self.schema = response.json()
        return self.schema

    def validate_structure(self) -> bool:
        """Validate basic OpenAPI structure."""
        print("\n[*] Validating OpenAPI Structure...")

        if not self.schema:
            self.errors.append("Schema not loaded")
            return False

        # Required fields
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in self.schema:
                self.errors.append(f"Missing required field: {field}")
            else:
                print(f"  [OK] {field}")

        # Validate OpenAPI version
        if "openapi" in self.schema:
            version = self.schema["openapi"]
            if not version.startswith("3."):
                self.errors.append(f"Expected OpenAPI 3.x, got {version}")
            else:
                print(f"  [OK] OpenAPI Version: {version}")

        # Validate info
        if "info" in self.schema:
            info = self.schema["info"]
            info_fields = ["title", "version", "description"]
            for field in info_fields:
                if field not in info:
                    self.warnings.append(f"Missing recommended info field: {field}")
                else:
                    print(f"  [OK] {field}: {info[field][:50]}...")

        return len(self.errors) == 0

    def validate_endpoints(self) -> Tuple[int, List[str]]:
        """Validate endpoint documentation."""
        print("\n[*] Validating Endpoint Documentation...")

        paths = self.schema.get("paths", {})
        total_endpoints = 0
        undocumented = []

        methods = ["get", "post", "put", "delete", "patch"]

        for path, path_methods in paths.items():
            for method, details in path_methods.items():
                if method in methods:
                    total_endpoints += 1

                    # Check for documentation
                    if not details.get("summary") and not details.get("description"):
                        undocumented.append(f"{method.upper()} {path}")
                        self.warnings.append(f"Undocumented: {method.upper()} {path}")

                    # Check for responses
                    if not details.get("responses"):
                        self.errors.append(f"No responses defined: {method.upper()} {path}")

        print(f"  [OK] Total endpoints: {total_endpoints}")
        if undocumented:
            print(f"  [WARN] Undocumented endpoints: {len(undocumented)}")
        else:
            print("  [OK] All endpoints documented")

        return total_endpoints, undocumented

    def validate_security(self) -> bool:
        """Validate security schemes."""
        print("\n[*] Validating Security Schemes...")

        components = self.schema.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        if not security_schemes:
            self.warnings.append("No security schemes defined")
            print("  [WARN] No security schemes defined")
            return False

        for scheme_name, scheme_details in security_schemes.items():
            scheme_type = scheme_details.get("type")
            print(f"  [OK] {scheme_name}: {scheme_type}")

            if scheme_type == "http":
                http_scheme = scheme_details.get("scheme")
                print(f"    - Scheme: {http_scheme}")

        return True

    def validate_schemas(self) -> int:
        """Validate reusable schemas."""
        print("\n[*] Validating Reusable Schemas...")

        components = self.schema.get("components", {})
        schemas = components.get("schemas", {})

        if not schemas:
            self.warnings.append("No reusable schemas defined")
            print("  [WARN] No reusable schemas defined")
            return 0

        print(f"  [OK] Total schemas: {len(schemas)}")

        # Show first 10 schema names
        schema_names = list(schemas.keys())[:10]
        for name in schema_names:
            print(f"    - {name}")

        if len(schemas) > 10:
            print(f"    ... and {len(schemas) - 10} more")

        return len(schemas)

    def validate_tags(self) -> bool:
        """Validate tag consistency."""
        print("\n[*] Validating Tags...")

        # Get defined tags
        defined_tags = {tag["name"] for tag in self.schema.get("tags", [])}

        # Get used tags
        used_tags = set()
        paths = self.schema.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    tags = details.get("tags", [])
                    used_tags.update(tags)

        print(f"  [OK] Defined tags: {len(defined_tags)}")
        print(f"  [OK] Used tags: {len(used_tags)}")

        # Check for undefined tags
        undefined_tags = used_tags - defined_tags
        if undefined_tags:
            print(f"  [INFO] Auto-generated tags: {undefined_tags}")

        return True

    def validate_with_spec_validator(self) -> bool:
        """Validate schema using openapi-spec-validator."""
        print("\n[*] Validating with OpenAPI Spec Validator...")

        try:
            from openapi_spec_validator import validate_spec

            validate_spec(self.schema)
            print("  [OK] Schema is valid according to OpenAPI 3.x spec")
            return True

        except ImportError:
            msg = "openapi-spec-validator not installed"
            self.warnings.append(msg)
            print("  [WARN] openapi-spec-validator not installed")
            print("    Install with: pip install openapi-spec-validator")
            return False

        except Exception as e:
            self.errors.append(f"Schema validation failed: {str(e)}")
            print(f"  [FAIL] Validation failed: {str(e)}")
            return False

    def save_schema(self, filepath: str):
        """Save OpenAPI schema to file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.schema, f, indent=2, ensure_ascii=False)

        print(f"\n[*] Schema saved to: {output_path}")

    def compare_schemas(self, old_schema_path: str):
        """Compare current schema with previous version."""
        print(f"\n[*] Comparing schemas...")

        old_schema_file = Path(old_schema_path)
        if not old_schema_file.exists():
            print(f"  [FAIL] File not found: {old_schema_path}")
            return

        with open(old_schema_file, "r", encoding="utf-8") as f:
            old_schema = json.load(f)

        # Compare versions
        old_version = old_schema.get("info", {}).get("version", "unknown")
        new_version = self.schema.get("info", {}).get("version", "unknown")

        print(f"  Old version: {old_version}")
        print(f"  New version: {new_version}")

        # Compare endpoint counts
        old_paths = old_schema.get("paths", {})
        new_paths = self.schema.get("paths", {})

        old_count = sum(
            len([m for m in methods if m in ["get", "post", "put", "delete", "patch"]])
            for methods in old_paths.values()
        )
        new_count = sum(
            len([m for m in methods if m in ["get", "post", "put", "delete", "patch"]])
            for methods in new_paths.values()
        )

        print(f"\n  Endpoint count: {old_count} → {new_count} ({new_count - old_count:+d})")

        # Find new endpoints
        old_endpoints = set(f"{method.upper()} {path}" for path in old_paths for method in old_paths[path] if method in ["get", "post", "put", "delete", "patch"])
        new_endpoints = set(f"{method.upper()} {path}" for path in new_paths for method in new_paths[path] if method in ["get", "post", "put", "delete", "patch"])

        added = new_endpoints - old_endpoints
        removed = old_endpoints - new_endpoints

        if added:
            print(f"\n  [+] Added endpoints ({len(added)}):")
            for endpoint in sorted(added):
                print(f"    - {endpoint}")

        if removed:
            print(f"\n  [-] Removed endpoints ({len(removed)}):")
            for endpoint in sorted(removed):
                print(f"    - {endpoint}")

        if not added and not removed:
            print("  [OK] No endpoint changes")

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)

        if self.errors:
            print(f"\n[ERROR] Found {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n[WARNING] Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n[OK] All validations passed!")

        print("="*60)

        return len(self.errors) == 0

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("[*] Starting OpenAPI/Swagger Validation")
        print("="*60)

        # Fetch schema
        try:
            self.fetch_schema()
            print("[OK] Schema fetched successfully")
        except Exception as e:
            print(f"[FAIL] Failed to fetch schema: {e}")
            return False

        # Run validations
        self.validate_structure()
        self.validate_endpoints()
        self.validate_security()
        self.validate_schemas()
        self.validate_tags()
        self.validate_with_spec_validator()

        # Print summary
        return self.print_summary()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate FastAPI OpenAPI/Swagger schema"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save schema to file (e.g., schema.json)",
        metavar="FILE"
    )
    parser.add_argument(
        "--compare",
        type=str,
        help="Compare with previous schema file",
        metavar="FILE"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with error code if validation fails"
    )

    args = parser.parse_args()

    # Create validator
    validator = SwaggerValidator()

    # Run validations
    success = validator.run_all_validations()

    # Save schema if requested
    if args.save:
        validator.save_schema(args.save)

    # Compare schemas if requested
    if args.compare:
        validator.compare_schemas(args.compare)

    # Exit with appropriate code in CI mode
    if args.ci and not success:
        sys.exit(1)

    sys.exit(0 if success else 0)  # Always exit 0 unless in CI mode


if __name__ == "__main__":
    main()
