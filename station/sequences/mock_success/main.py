"""Mock Success Sequence CLI entry point."""

from .sequence import MockSuccessSequence

if __name__ == "__main__":
    exit(MockSuccessSequence.run_from_cli())
