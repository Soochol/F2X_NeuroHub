"""
Unit tests for sequence upload API routes.

Tests sequence package validation, upload, deletion, and download.
"""

import io
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml
from fastapi import HTTPException

from station_service.api.routes import sequence_upload


class TestExtractAndValidateZip:
    """Tests for _extract_and_validate_zip helper function."""

    def _create_test_zip(self, files: dict) -> io.BytesIO:
        """Create a test ZIP file with given files."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        zip_buffer.seek(0)
        return zip_buffer

    def test_valid_package(self):
        """Test validation of a valid sequence package."""
        manifest = {
            "name": "test_sequence",
            "version": "1.0.0",
            "display_name": "Test Sequence",
            "description": "A test sequence",
            "entry_point": {
                "module": "sequence",
                "class_name": "TestSequence",
            },
            "hardware": {},
            "parameters": {},
        }

        files = {
            "test_sequence/manifest.yaml": yaml.dump(manifest),
            "test_sequence/sequence.py": "# Test sequence file",
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is True
        assert result["name"] == "test_sequence"
        assert result["version"] == "1.0.0"
        assert result["errors"] == []

    def test_empty_zip(self):
        """Test validation of empty ZIP file."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            pass  # Empty zip
        zip_buffer.seek(0)

        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is False
        assert "ZIP file is empty" in result["errors"]

    def test_missing_manifest(self):
        """Test validation when manifest.yaml is missing."""
        files = {
            "test_sequence/sequence.py": "# Test sequence",
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is False
        assert "manifest.yaml not found" in result["errors"][0]

    def test_empty_manifest(self):
        """Test validation when manifest.yaml is empty."""
        files = {
            "test_sequence/manifest.yaml": "",
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is False
        assert "manifest.yaml is empty" in result["errors"]

    def test_invalid_yaml_in_manifest(self):
        """Test validation when manifest has invalid YAML."""
        files = {
            "test_sequence/manifest.yaml": "{ invalid yaml: [",
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is False
        assert any("Invalid YAML" in err for err in result["errors"])

    def test_missing_required_fields(self):
        """Test validation when manifest missing required fields."""
        manifest = {
            "name": "test_sequence",
            # Missing version, entry_point, etc.
        }

        files = {
            "test_sequence/manifest.yaml": yaml.dump(manifest),
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_missing_entry_point_file(self):
        """Test validation when entry point module file is missing."""
        manifest = {
            "name": "test_sequence",
            "version": "1.0.0",
            "display_name": "Test Sequence",
            "description": "A test sequence",
            "entry_point": {
                "module": "sequence",
                "class_name": "TestSequence",
            },
            "hardware": {},
            "parameters": {},
        }

        files = {
            "test_sequence/manifest.yaml": yaml.dump(manifest),
            # sequence.py is missing
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is False
        assert any("Entry point module" in err for err in result["errors"])

    def test_missing_hardware_driver_warning(self):
        """Test that missing hardware driver generates warning."""
        manifest = {
            "name": "test_sequence",
            "version": "1.0.0",
            "display_name": "Test Sequence",
            "description": "A test sequence",
            "entry_point": {
                "module": "sequence",
                "class": "TestSequence",
            },
            "hardware": {
                "power_supply": {
                    "display_name": "Power Supply",
                    "driver": "my_custom_driver",
                    "class": "PowerSupplyDriver",
                },
            },
            "parameters": {},
        }

        files = {
            "test_sequence/manifest.yaml": yaml.dump(manifest),
            "test_sequence/sequence.py": "# Test sequence",
            # my_custom_driver.py is missing
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        # Should be valid but with warnings
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert any("my_custom_driver" in w for w in result["warnings"])

    def test_extracts_hardware_list(self):
        """Test that hardware definitions are extracted."""
        manifest = {
            "name": "test_sequence",
            "version": "1.0.0",
            "display_name": "Test Sequence",
            "description": "A test sequence",
            "entry_point": {
                "module": "sequence",
                "class": "TestSequence",
            },
            "hardware": {
                "power_supply": {
                    "display_name": "Power Supply",
                    "driver": "simulation",
                    "class": "SimulationDriver",
                },
                "dmm": {
                    "display_name": "Digital Multimeter",
                    "driver": "simulation",
                    "class": "SimulationDriver",
                },
            },
            "parameters": {},
        }

        files = {
            "test_sequence/manifest.yaml": yaml.dump(manifest),
            "test_sequence/sequence.py": "# Test sequence",
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is True
        assert "power_supply" in result["hardware"]
        assert "dmm" in result["hardware"]

    def test_extracts_parameters_list(self):
        """Test that parameters are extracted."""
        manifest = {
            "name": "test_sequence",
            "version": "1.0.0",
            "display_name": "Test Sequence",
            "description": "A test sequence",
            "entry_point": {
                "module": "sequence",
                "class": "TestSequence",
            },
            "hardware": {},
            "parameters": {
                "voltage_limit": {
                    "display_name": "Voltage Limit",
                    "type": "float",
                    "default": 5.0,
                    "description": "Max voltage",
                },
                "retry_count": {
                    "display_name": "Retry Count",
                    "type": "integer",
                    "default": 3,
                    "description": "Number of retries",
                },
            },
        }

        files = {
            "test_sequence/manifest.yaml": yaml.dump(manifest),
            "test_sequence/sequence.py": "# Test sequence",
        }

        zip_buffer = self._create_test_zip(files)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            result = sequence_upload._extract_and_validate_zip(zf)

        assert result["valid"] is True
        assert "voltage_limit" in result["parameters"]
        assert "retry_count" in result["parameters"]


class TestValidateSequence:
    """Tests for POST /api/sequences/validate endpoint."""

    @pytest.mark.asyncio
    async def test_non_zip_file_rejected(self):
        """Test that non-ZIP files are rejected."""
        mock_file = MagicMock()
        mock_file.filename = "test.txt"

        with pytest.raises(HTTPException) as exc_info:
            await sequence_upload.validate_sequence(file=mock_file)

        assert exc_info.value.status_code == 400
        assert ".zip" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_empty_file_returns_invalid(self):
        """Test that empty file returns invalid result."""
        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        mock_file.read = AsyncMock(return_value=b"")

        result = await sequence_upload.validate_sequence(file=mock_file)

        assert result.success is True
        assert result.data.valid is False
        # errors is a list of ValidationErrorDetail objects
        assert "empty" in result.data.errors[0].message.lower()

    @pytest.mark.asyncio
    async def test_invalid_zip_returns_invalid(self):
        """Test that invalid ZIP returns invalid result."""
        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        mock_file.read = AsyncMock(return_value=b"not a zip file")

        result = await sequence_upload.validate_sequence(file=mock_file)

        assert result.data.valid is False
        # errors is a list of ValidationErrorDetail objects
        assert any("Invalid ZIP" in err.message for err in result.data.errors)


class TestUploadSequence:
    """Tests for POST /api/sequences/upload endpoint."""

    @pytest.mark.asyncio
    async def test_non_zip_file_rejected(self):
        """Test that non-ZIP files are rejected."""
        mock_file = MagicMock()
        mock_file.filename = "test.txt"

        mock_loader = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await sequence_upload.upload_sequence(
                file=mock_file,
                force=False,
                sequence_loader=mock_loader,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_empty_file_rejected(self):
        """Test that empty file is rejected."""
        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        mock_file.read = AsyncMock(return_value=b"")

        mock_loader = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await sequence_upload.upload_sequence(
                file=mock_file,
                force=False,
                sequence_loader=mock_loader,
            )

        assert exc_info.value.status_code == 400
        assert "empty" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_zip_rejected(self):
        """Test that invalid ZIP is rejected."""
        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        mock_file.read = AsyncMock(return_value=b"not a zip")

        mock_loader = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await sequence_upload.upload_sequence(
                file=mock_file,
                force=False,
                sequence_loader=mock_loader,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_existing_package_requires_force(self):
        """Test that existing package requires force flag."""
        manifest = {
            "name": "test_sequence",
            "version": "1.0.0",
            "display_name": "Test Sequence",
            "description": "A test sequence",
            "entry_point": {
                "module": "sequence",
                "class_name": "TestSequence",
            },
            "hardware": {},
            "parameters": {},
        }

        # Create valid ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("test_sequence/manifest.yaml", yaml.dump(manifest))
            zf.writestr("test_sequence/sequence.py", "# Test")
        zip_content = zip_buffer.getvalue()

        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        mock_file.read = AsyncMock(return_value=zip_content)

        # Mock loader with existing package
        with tempfile.TemporaryDirectory() as tmpdir:
            packages_path = Path(tmpdir)
            (packages_path / "test_sequence").mkdir()
            (packages_path / "test_sequence" / "manifest.yaml").touch()

            mock_loader = MagicMock()
            mock_loader.packages_path = packages_path

            with pytest.raises(HTTPException) as exc_info:
                await sequence_upload.upload_sequence(
                    file=mock_file,
                    force=False,
                    sequence_loader=mock_loader,
                )

            assert exc_info.value.status_code == 409
            assert "already exists" in str(exc_info.value.detail)


class TestDeleteSequence:
    """Tests for DELETE /api/sequences/{name} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_nonexistent_raises_404(self):
        """Test that deleting nonexistent package raises 404."""
        mock_loader = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            packages_path = Path(tmpdir)
            mock_loader.packages_path = packages_path
            mock_loader.get_package_path = MagicMock(
                return_value=packages_path / "nonexistent"
            )

            with pytest.raises(HTTPException) as exc_info:
                await sequence_upload.delete_sequence(
                    sequence_name="nonexistent",
                    sequence_loader=mock_loader,
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_existing_package(self):
        """Test successful deletion of existing package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            packages_path = Path(tmpdir)
            package_path = packages_path / "test_sequence"
            package_path.mkdir()
            (package_path / "manifest.yaml").touch()

            mock_loader = MagicMock()
            mock_loader.packages_path = packages_path
            mock_loader.get_package_path = MagicMock(return_value=package_path)
            mock_loader.clear_cache = MagicMock()

            result = await sequence_upload.delete_sequence(
                sequence_name="test_sequence",
                sequence_loader=mock_loader,
            )

            assert result.success is True
            assert result.data.deleted is True
            assert result.data.name == "test_sequence"
            assert not package_path.exists()
            mock_loader.clear_cache.assert_called_once()


class TestDownloadSequence:
    """Tests for GET /api/sequences/{name}/download endpoint."""

    @pytest.mark.asyncio
    async def test_download_nonexistent_raises_404(self):
        """Test that downloading nonexistent package raises 404."""
        mock_loader = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            packages_path = Path(tmpdir)
            mock_loader.get_package_path = MagicMock(
                return_value=packages_path / "nonexistent"
            )

            with pytest.raises(HTTPException) as exc_info:
                await sequence_upload.download_sequence(
                    sequence_name="nonexistent",
                    sequence_loader=mock_loader,
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_download_existing_package(self):
        """Test successful download of existing package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            packages_path = Path(tmpdir)
            package_path = packages_path / "test_sequence"
            package_path.mkdir()
            (package_path / "manifest.yaml").write_text("name: test_sequence")
            (package_path / "sequence.py").write_text("# Test")

            mock_loader = MagicMock()
            mock_loader.get_package_path = MagicMock(return_value=package_path)

            response = await sequence_upload.download_sequence(
                sequence_name="test_sequence",
                sequence_loader=mock_loader,
            )

            assert response.media_type == "application/zip"
            assert "test_sequence.zip" in response.headers["Content-Disposition"]

            # Verify ZIP contents
            zip_buffer = io.BytesIO(response.body)
            with zipfile.ZipFile(zip_buffer, "r") as zf:
                names = zf.namelist()
                assert "test_sequence/manifest.yaml" in names
                assert "test_sequence/sequence.py" in names

    @pytest.mark.asyncio
    async def test_download_excludes_pycache(self):
        """Test that __pycache__ is excluded from download."""
        with tempfile.TemporaryDirectory() as tmpdir:
            packages_path = Path(tmpdir)
            package_path = packages_path / "test_sequence"
            package_path.mkdir()
            (package_path / "manifest.yaml").write_text("name: test_sequence")
            (package_path / "__pycache__").mkdir()
            (package_path / "__pycache__" / "test.pyc").write_bytes(b"compiled")

            mock_loader = MagicMock()
            mock_loader.get_package_path = MagicMock(return_value=package_path)

            response = await sequence_upload.download_sequence(
                sequence_name="test_sequence",
                sequence_loader=mock_loader,
            )

            # Verify __pycache__ is excluded
            zip_buffer = io.BytesIO(response.body)
            with zipfile.ZipFile(zip_buffer, "r") as zf:
                names = zf.namelist()
                assert not any("__pycache__" in n for n in names)
                assert not any(".pyc" in n for n in names)
