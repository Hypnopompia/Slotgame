"""Game configuration for the slot machine."""

from enum import Enum
from typing import Dict, List, Tuple

# Symbol types
class SymbolType(Enum):
    CHERRY = "cherry"
    LEMON = "lemon"
    ORANGE = "orange"
    PLUM = "plum"
    BELL = "bell"
    BAR = "bar"
    SEVEN = "seven"
    WILD = "wild"


# Symbol display characters
SYMBOL_DISPLAY: Dict[SymbolType, str] = {
    SymbolType.CHERRY: "🍒",
    SymbolType.LEMON: "🍋",
    SymbolType.ORANGE: "🍊",
    SymbolType.PLUM: "🍇",
    SymbolType.BELL: "🔔",
    SymbolType.BAR: "BAR",
    SymbolType.SEVEN: "7️⃣",
    SymbolType.WILD: "⭐",
}

# Symbol weights for random generation (higher = more common)
SYMBOL_WEIGHTS: Dict[SymbolType, int] = {
    SymbolType.CHERRY: 25,
    SymbolType.LEMON: 22,
    SymbolType.ORANGE: 20,
    SymbolType.PLUM: 15,
    SymbolType.BELL: 8,
    SymbolType.BAR: 5,
    SymbolType.SEVEN: 3,
    SymbolType.WILD: 2,
}

# Paytable: symbol -> {match_count -> multiplier}
PAYTABLE: Dict[SymbolType, Dict[int, int]] = {
    SymbolType.CHERRY: {3: 5, 4: 10, 5: 25},
    SymbolType.LEMON: {3: 5, 4: 15, 5: 30},
    SymbolType.ORANGE: {3: 10, 4: 20, 5: 40},
    SymbolType.PLUM: {3: 10, 4: 25, 5: 50},
    SymbolType.BELL: {3: 20, 4: 50, 5: 100},
    SymbolType.BAR: {3: 30, 4: 75, 5: 200},
    SymbolType.SEVEN: {3: 50, 4: 150, 5: 500},
    SymbolType.WILD: {3: 100, 4: 500, 5: 2000},
}

# Paylines: each tuple represents row indices for each of the 5 reels
# Row indices: 0 = top, 1 = middle, 2 = bottom
PAYLINES: List[Tuple[int, ...]] = [
    (1, 1, 1, 1, 1),  # Line 1: Middle row
    (0, 0, 0, 0, 0),  # Line 2: Top row
    (2, 2, 2, 2, 2),  # Line 3: Bottom row
    (0, 1, 2, 1, 0),  # Line 4: V-shape
    (2, 1, 0, 1, 2),  # Line 5: Inverted V
]

# Payline names and colors for display
PAYLINE_INFO: List[Dict] = [
    {"name": "Middle", "color": "#e74c3c"},      # Red
    {"name": "Top", "color": "#3498db"},         # Blue
    {"name": "Bottom", "color": "#2ecc71"},      # Green
    {"name": "V-Shape", "color": "#f39c12"},     # Orange
    {"name": "Inv-V", "color": "#9b59b6"},       # Purple
]

# Game settings
NUM_REELS = 5
NUM_ROWS = 3
DEFAULT_BALANCE = 1000
MIN_BET = 1
MAX_BET = 100
BET_INCREMENT = 1

# Persistence
SAVE_FILE = "data/player.json"
