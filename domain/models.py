"""Domain models for the slot machine game."""

from dataclasses import dataclass, field
from typing import List, Tuple

from config import SymbolType


@dataclass(frozen=True)
class Symbol:
    """Represents a slot machine symbol."""

    type: SymbolType

    @property
    def is_wild(self) -> bool:
        return self.type == SymbolType.WILD


@dataclass(frozen=True)
class Payline:
    """Defines a payline pattern across 5 reels."""

    id: int
    positions: Tuple[int, ...]  # Row index for each reel (0=top, 1=middle, 2=bottom)

    def get_symbols_from_grid(self, grid: List[List[Symbol]]) -> List[Symbol]:
        """Extract symbols along this payline from a reel grid.

        Grid is indexed as grid[reel_index][row_index].
        """
        return [grid[reel_idx][row_idx] for reel_idx, row_idx in enumerate(self.positions)]


@dataclass(frozen=True)
class WinLine:
    """Represents a winning payline result."""

    payline_id: int
    symbol_type: SymbolType
    match_count: int
    payout: int


@dataclass(frozen=True)
class SpinResult:
    """Immutable result of a spin."""

    grid: Tuple[Tuple[Symbol, ...], ...]  # 5 reels x 3 visible symbols
    winning_lines: Tuple[WinLine, ...]
    total_payout: int
    bet_amount: int

    @property
    def is_win(self) -> bool:
        return self.total_payout > 0

    @property
    def net_result(self) -> int:
        return self.total_payout - self.bet_amount


@dataclass
class Player:
    """Player state with balance and statistics."""

    id: str
    balance: int
    total_spins: int = 0
    total_wins: int = 0
    biggest_win: int = 0

    def deduct(self, amount: int) -> "Player":
        """Return a new Player with deducted balance."""
        return Player(
            id=self.id,
            balance=self.balance - amount,
            total_spins=self.total_spins,
            total_wins=self.total_wins,
            biggest_win=self.biggest_win,
        )

    def add_winnings(self, amount: int) -> "Player":
        """Return a new Player with added winnings."""
        return Player(
            id=self.id,
            balance=self.balance + amount,
            total_spins=self.total_spins,
            total_wins=self.total_wins + (1 if amount > 0 else 0),
            biggest_win=max(self.biggest_win, amount),
        )

    def record_spin(self) -> "Player":
        """Return a new Player with incremented spin count."""
        return Player(
            id=self.id,
            balance=self.balance,
            total_spins=self.total_spins + 1,
            total_wins=self.total_wins,
            biggest_win=self.biggest_win,
        )
