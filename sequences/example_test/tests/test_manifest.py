"""Unit tests for manifest.yaml validation."""

import pytest
from pathlib import Path

import yaml
from pydantic import ValidationError

from station_service.sequence.manifest import SequenceManifest


class TestManifestValidation:
    """Tests for manifest.yaml validation against schema."""

    @pytest.fixture
    def manifest_path(self) -> Path:
        """Get path to manifest.yaml."""
        return Path(__file__).parent.parent / "manifest.yaml"

    @pytest.fixture
    def manifest_data(self, manifest_path: Path) -> dict:
        """Load manifest.yaml data."""
        with open(manifest_path, "r") as f:
            return yaml.safe_load(f)

    def test_manifest_file_exists(self, manifest_path: Path) -> None:
        """Test that manifest.yaml exists."""
        assert manifest_path.exists(), "manifest.yaml should exist"

    def test_manifest_is_valid_yaml(self, manifest_path: Path) -> None:
        """Test that manifest.yaml is valid YAML."""
        with open(manifest_path, "r") as f:
            data = yaml.safe_load(f)
        assert data is not None

    def test_manifest_validates_against_schema(self, manifest_data: dict) -> None:
        """Test that manifest validates against Pydantic schema."""
        manifest = SequenceManifest.model_validate(manifest_data)
        assert manifest.name == "example_test"
        assert manifest.version == "1.0.0"

    def test_manifest_has_entry_point(self, manifest_data: dict) -> None:
        """Test that manifest has valid entry point."""
        manifest = SequenceManifest.model_validate(manifest_data)
        assert manifest.entry_point.module == "sequence"
        assert manifest.entry_point.class_name == "ExampleTestSequence"

    def test_manifest_has_hardware_definitions(self, manifest_data: dict) -> None:
        """Test that manifest has hardware definitions."""
        manifest = SequenceManifest.model_validate(manifest_data)
        assert "dmm" in manifest.hardware
        dmm_def = manifest.hardware["dmm"]
        assert dmm_def.driver == "mock_dmm"
        assert dmm_def.class_name == "MockDMM"

    def test_manifest_has_parameters(self, manifest_data: dict) -> None:
        """Test that manifest has parameter definitions."""
        manifest = SequenceManifest.model_validate(manifest_data)
        assert "voltage_limit" in manifest.parameters
        assert "test_count" in manifest.parameters

        voltage_param = manifest.parameters["voltage_limit"]
        assert voltage_param.default == 5.0
        assert voltage_param.unit == "V"

        count_param = manifest.parameters["test_count"]
        assert count_param.default == 3

    def test_manifest_hardware_config_schema(self, manifest_data: dict) -> None:
        """Test hardware config schema validation."""
        manifest = SequenceManifest.model_validate(manifest_data)
        dmm = manifest.hardware["dmm"]
        assert dmm.config_schema is not None
        assert "port" in dmm.config_schema
        assert "measurement_delay" in dmm.config_schema


class TestManifestHelpers:
    """Tests for manifest helper methods."""

    @pytest.fixture
    def manifest(self, manifest_path: Path) -> SequenceManifest:
        """Load and validate manifest."""
        manifest_path = Path(__file__).parent.parent / "manifest.yaml"
        with open(manifest_path, "r") as f:
            data = yaml.safe_load(f)
        return SequenceManifest.model_validate(data)

    def test_get_hardware_names(self, manifest: SequenceManifest) -> None:
        """Test getting hardware names."""
        names = manifest.get_hardware_names()
        assert "dmm" in names

    def test_get_parameter_names(self, manifest: SequenceManifest) -> None:
        """Test getting parameter names."""
        names = manifest.get_parameter_names()
        assert "voltage_limit" in names
        assert "test_count" in names

    def test_get_required_packages(self, manifest: SequenceManifest) -> None:
        """Test getting required packages."""
        packages = manifest.get_required_packages()
        assert isinstance(packages, list)
