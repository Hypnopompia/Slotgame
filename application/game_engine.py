"""Game engine - orchestrates game flow."""

import logging
from typing import Optional

from config import SYMBOL_DISPLAY
from domain.models import Player, SpinResult
from domain.services import ReelGenerator, PayoutCalculator
from infrastructure.persistence import JsonPlayerRepository

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class GameEngine:
    """Orchestrates game flow and coordinates domain services.

    Responsibilities:
    - Manages player state
    - Validates game rules (sufficient balance, valid bets)
    - Coordinates spin flow
    - Persists player data
    """

    def __init__(
        self,
        repository: JsonPlayerRepository,
        reel_generator: Optional[ReelGenerator] = None,
        payout_calculator: Optional[PayoutCalculator] = None,
    ):
        self._repository = repository
        self._reel_generator = reel_generator or ReelGenerator()
        self._payout_calculator = payout_calculator or PayoutCalculator()
        self._player: Optional[Player] = None

    def load_player(self, player_id: str = "default") -> Player:
        """Load or create a player."""
        self._player = self._repository.load(player_id)
        return self._player

    def spin(self, bet_per_line: int, num_lines: int) -> SpinResult:
        """Execute a spin.

        Args:
            bet_per_line: Bet amount per payline
            num_lines: Number of paylines to bet on

        Returns:
            SpinResult with grid, winning lines, and payout

        Raises:
            ValueError: If no player loaded or insufficient balance
        """
        if not self._player:
            raise ValueError("No player loaded")

        total_bet = bet_per_line * num_lines

        logger.info("=" * 50)
        logger.info(f"SPIN: bet_per_line=${bet_per_line}, num_lines={num_lines}, total_bet=${total_bet}")
        logger.info(f"Balance before: ${self._player.balance}")

        if self._player.balance < total_bet:
            raise ValueError("Insufficient balance")

        # Deduct bet
        self._player = self._player.deduct(total_bet)
        self._player = self._player.record_spin()

        # Generate reels
        grid = self._reel_generator.generate_grid()

        # Log the grid
        logger.info("Grid result:")
        for row in range(3):
            row_symbols = [SYMBOL_DISPLAY[grid[reel][row].type] for reel in range(5)]
            logger.info(f"  Row {row}: {' | '.join(row_symbols)}")

        # Calculate wins
        winning_lines, total_payout = self._payout_calculator.calculate(
            grid, bet_per_line, num_lines
        )

        # Log winning lines
        if winning_lines:
            logger.info(f"WINNING LINES ({len(winning_lines)}):")
            for win in winning_lines:
                symbol_display = SYMBOL_DISPLAY[win.symbol_type]
                logger.info(f"  Line {win.payline_id}: {win.match_count}x {symbol_display} = ${win.payout} (bet ${bet_per_line} × multiplier {win.payout // bet_per_line})")
        else:
            logger.info("No winning lines")

        logger.info(f"Total payout: ${total_payout}")

        # Add winnings
        if total_payout > 0:
            self._player = self._player.add_winnings(total_payout)

        # Persist
        self._repository.save(self._player)

        logger.info(f"Balance after: ${self._player.balance} (net: ${total_payout - total_bet})")

        return SpinResult(
            grid=grid,
            winning_lines=tuple(winning_lines),
            total_payout=total_payout,
            bet_amount=total_bet,
        )

    @property
    def current_balance(self) -> int:
        """Get current player balance."""
        return self._player.balance if self._player else 0

    @property
    def player_stats(self) -> dict:
        """Get player statistics."""
        if not self._player:
            return {}
        return {
            "total_spins": self._player.total_spins,
            "total_wins": self._player.total_wins,
            "biggest_win": self._player.biggest_win,
        }

    def add_credits(self, amount: int) -> None:
        """Add credits to player balance (for bankrupt recovery)."""
        if self._player:
            self._player = Player(
                id=self._player.id,
                balance=self._player.balance + amount,
                total_spins=self._player.total_spins,
                total_wins=self._player.total_wins,
                biggest_win=self._player.biggest_win,
            )
            self._repository.save(self._player)
