#!/usr/bin/env python3
"""
PSA Sensor Test Sequence - CLI Entry Point.

This module provides the CLI entry point for running the sequence
as a subprocess from Station Service.
"""

from sequence import PSASensorTestSequence

if __name__ == "__main__":
    exit(PSASensorTestSequence.run_from_cli())
