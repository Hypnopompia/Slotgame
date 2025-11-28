"""Domain services for slot machine game logic."""

import random
from typing import List, Tuple, Optional

from config import (
    SymbolType,
    SYMBOL_WEIGHTS,
    PAYTABLE,
    PAYLINES,
    NUM_REELS,
    NUM_ROWS,
)
from .models import Symbol, Payline, WinLine


class ReelGenerator:
    """Generates random reel results with weighted symbol selection."""

    def __init__(self):
        self._symbols = list(SymbolType)
        self._weights = [SYMBOL_WEIGHTS[s] for s in self._symbols]

    def generate_grid(self) -> Tuple[Tuple[Symbol, ...], ...]:
        """Generate a 5x3 grid of random symbols."""
        grid = []
        for _ in range(NUM_REELS):
            reel = tuple(
                Symbol(random.choices(self._symbols, weights=self._weights, k=1)[0])
                for _ in range(NUM_ROWS)
            )
            grid.append(reel)
        return tuple(grid)


class PayoutCalculator:
    """Calculates payouts for a given spin result."""

    def __init__(self):
        self._paylines = [
            Payline(id=i + 1, positions=positions) for i, positions in enumerate(PAYLINES)
        ]

    def calculate(
        self, grid: Tuple[Tuple[Symbol, ...], ...], bet_per_line: int, num_lines: int
    ) -> Tuple[List[WinLine], int]:
        """Calculate all winning lines from a grid.

        Returns:
            Tuple of (list of WinLine objects, total payout)
        """
        wins = []
        total_payout = 0

        for payline in self._paylines[:num_lines]:
            symbols = payline.get_symbols_from_grid(list(grid))
            win = self._evaluate_line(payline.id, symbols, bet_per_line)
            if win:
                wins.append(win)
                total_payout += win.payout

        return wins, total_payout

    def _evaluate_line(
        self, payline_id: int, symbols: List[Symbol], bet: int
    ) -> Optional[WinLine]:
        """Evaluate a single payline for wins.

        Matches from left-to-right. Wilds substitute for any symbol.
        """
        if not symbols:
            return None

        # Determine the matching symbol (first non-wild, or wild if all wilds)
        match_type: Optional[SymbolType] = None
        for sym in symbols:
            if not sym.is_wild:
                match_type = sym.type
                break

        # If all wilds, treat as wild match
        if match_type is None:
            match_type = SymbolType.WILD

        # Count consecutive matches from left
        count = 0
        for sym in symbols:
            if sym.type == match_type or sym.is_wild:
                count += 1
            else:
                break

        # Need at least 3 matches to win
        if count < 3:
            return None

        # Calculate payout
        multiplier = PAYTABLE.get(match_type, {}).get(count, 0)
        if multiplier == 0:
            return None

        payout = bet * multiplier

        return WinLine(
            payline_id=payline_id,
            symbol_type=match_type,
            match_count=count,
            payout=payout,
        )
