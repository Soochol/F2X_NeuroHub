"""
Unit tests for SDK CLI argument parsing.
"""

import json
import tempfile
from pathlib import Path

import pytest

from station_service.sdk.cli import CLIArgs, create_parser, parse_args


# ============================================================================
# Tests for parse_args
# ============================================================================


class TestParseArgs:
    """Tests for parse_args function."""

    def test_start_action(self):
        """Test --start action parsing."""
        args = parse_args(["--start"])
        assert args.action == "start"

    def test_stop_action(self):
        """Test --stop action parsing."""
        args = parse_args(["--stop"])
        assert args.action == "stop"

    def test_status_action(self):
        """Test --status action parsing."""
        args = parse_args(["--status"])
        assert args.action == "status"

    def test_inline_config(self):
        """Test --config with inline JSON."""
        config = {"wip_id": "WIP-001", "parameters": {"timeout": 30}}
        args = parse_args(["--start", "--config", json.dumps(config)])

        assert args.action == "start"
        assert args.config == config
        assert args.wip_id == "WIP-001"
        assert args.parameters == {"timeout": 30}

    def test_config_file(self):
        """Test --config-file option."""
        config = {
            "execution_id": "exec-123",
            "wip_id": "WIP-002",
            "hardware": {"device": {"port": "COM1"}},
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            f.flush()

            args = parse_args(["--start", "--config-file", f.name])

        assert args.config == config
        assert args.execution_id == "exec-123"
        assert args.wip_id == "WIP-002"
        assert args.hardware_config == {"device": {"port": "COM1"}}

        # Cleanup
        Path(f.name).unlink()

    def test_invalid_json_config(self):
        """Test error on invalid JSON config."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_args(["--start", "--config", "not valid json"])

    def test_missing_config_file(self):
        """Test error on missing config file."""
        with pytest.raises(FileNotFoundError):
            parse_args(["--start", "--config-file", "/nonexistent/config.json"])

    def test_dry_run_option(self):
        """Test --dry-run option."""
        args = parse_args(["--start", "--dry-run"])
        assert args.dry_run is True

    def test_verbose_option(self):
        """Test --verbose option."""
        args = parse_args(["--start", "--verbose"])
        assert args.verbose is True

    def test_verbose_short_option(self):
        """Test -v verbose option."""
        args = parse_args(["--start", "-v"])
        assert args.verbose is True

    def test_timeout_option(self):
        """Test --timeout option."""
        args = parse_args(["--start", "--timeout", "120.5"])
        assert args.timeout == 120.5

    def test_combined_options(self):
        """Test multiple options combined."""
        config = {"wip_id": "WIP-123"}
        args = parse_args([
            "--start",
            "--config", json.dumps(config),
            "--verbose",
            "--dry-run",
            "--timeout", "60",
        ])

        assert args.action == "start"
        assert args.wip_id == "WIP-123"
        assert args.verbose is True
        assert args.dry_run is True
        assert args.timeout == 60.0

    def test_config_short_option(self):
        """Test -c config option."""
        config = {"wip_id": "WIP-001"}
        args = parse_args(["--start", "-c", json.dumps(config)])
        assert args.wip_id == "WIP-001"

    def test_config_file_short_option(self):
        """Test -f config-file option."""
        config = {"wip_id": "WIP-002"}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            f.flush()

            args = parse_args(["--start", "-f", f.name])

        assert args.wip_id == "WIP-002"
        Path(f.name).unlink()


# ============================================================================
# Tests for CLIArgs
# ============================================================================


class TestCLIArgs:
    """Tests for CLIArgs class."""

    def test_default_values(self):
        """Test default CLIArgs values."""
        args = CLIArgs(action="start")

        assert args.action == "start"
        assert args.config == {}
        assert args.execution_id is None
        assert args.wip_id is None
        assert args.batch_id is None
        assert args.process_id is None
        assert args.operator_id is None
        assert args.lot_id is None
        assert args.serial_number is None
        assert args.hardware_config == {}
        assert args.parameters == {}
        assert args.dry_run is False
        assert args.verbose is False
        assert args.timeout is None

    def test_full_config_extraction(self):
        """Test full configuration extraction."""
        config = {
            "execution_id": "exec-001",
            "wip_id": "WIP-001",
            "batch_id": "BATCH-001",
            "process_id": 1,
            "operator_id": 42,
            "lot_id": "LOT-001",
            "serial_number": "SN-001",
            "hardware": {"power": {"port": "COM1"}},
            "parameters": {"timeout": 30},
        }

        args = parse_args(["--start", "--config", json.dumps(config)])

        assert args.execution_id == "exec-001"
        assert args.wip_id == "WIP-001"
        assert args.batch_id == "BATCH-001"
        assert args.process_id == 1
        assert args.operator_id == 42
        assert args.lot_id == "LOT-001"
        assert args.serial_number == "SN-001"
        assert args.hardware_config == {"power": {"port": "COM1"}}
        assert args.parameters == {"timeout": 30}


# ============================================================================
# Tests for create_parser
# ============================================================================


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_creation(self):
        """Test parser is created correctly."""
        parser = create_parser("test_sequence")
        assert parser.prog == "test_sequence"

    def test_mutually_exclusive_actions(self):
        """Test actions are mutually exclusive."""
        parser = create_parser()

        # Should fail with multiple actions
        with pytest.raises(SystemExit):
            parser.parse_args(["--start", "--stop"])

    def test_required_action(self):
        """Test action is required."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_mutually_exclusive_config(self):
        """Test config and config-file are mutually exclusive."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([
                "--start",
                "--config", "{}",
                "--config-file", "/path/to/file",
            ])

    def test_help_available(self):
        """Test help option is available."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])

        # Help exits with 0
        assert exc_info.value.code == 0


# ============================================================================
# Tests for edge cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_config(self):
        """Test empty config object."""
        args = parse_args(["--start", "--config", "{}"])
        assert args.config == {}
        assert args.wip_id is None

    def test_nested_config(self):
        """Test deeply nested config."""
        config = {
            "hardware": {
                "device": {
                    "settings": {
                        "advanced": {
                            "value": 123
                        }
                    }
                }
            }
        }
        args = parse_args(["--start", "--config", json.dumps(config)])
        assert args.hardware_config["device"]["settings"]["advanced"]["value"] == 123

    def test_unicode_in_config(self):
        """Test unicode characters in config."""
        config = {
            "wip_id": "WIP-한글-001",
            "parameters": {"name": "테스트 시퀀스"}
        }
        args = parse_args(["--start", "--config", json.dumps(config)])
        assert args.wip_id == "WIP-한글-001"
        assert args.parameters["name"] == "테스트 시퀀스"

    def test_large_config(self):
        """Test handling of large config."""
        config = {
            "parameters": {f"param_{i}": i for i in range(100)}
        }
        args = parse_args(["--start", "--config", json.dumps(config)])
        assert len(args.parameters) == 100
        assert args.parameters["param_50"] == 50
