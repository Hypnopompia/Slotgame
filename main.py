#!/usr/bin/env python3
"""5-Reel Slot Machine Game - Entry Point."""

import sys
from pathlib import Path

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from presentation.app import SlotMachineApp


def main():
    """Run the slot machine game."""
    app = SlotMachineApp()
    app.run()


if __name__ == "__main__":
    main()
