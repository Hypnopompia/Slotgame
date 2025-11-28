"""Persistence layer for player data."""

import json
from pathlib import Path
from typing import Optional

from config import SAVE_FILE, DEFAULT_BALANCE
from domain.models import Player


class JsonPlayerRepository:
    """JSON file-based persistence for player data."""

    def __init__(self, save_path: Optional[str] = None):
        self._path = Path(save_path or SAVE_FILE)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, player_id: str) -> Player:
        """Load player data from JSON file, or create new player if not found."""
        if not self._path.exists():
            return Player(id=player_id, balance=DEFAULT_BALANCE)

        try:
            with open(self._path, "r") as f:
                data = json.load(f)

            return Player(
                id=data.get("id", player_id),
                balance=data.get("balance", DEFAULT_BALANCE),
                total_spins=data.get("total_spins", 0),
                total_wins=data.get("total_wins", 0),
                biggest_win=data.get("biggest_win", 0),
            )
        except (json.JSONDecodeError, KeyError):
            return Player(id=player_id, balance=DEFAULT_BALANCE)

    def save(self, player: Player) -> None:
        """Save player data to JSON file."""
        data = {
            "id": player.id,
            "balance": player.balance,
            "total_spins": player.total_spins,
            "total_wins": player.total_wins,
            "biggest_win": player.biggest_win,
        }

        with open(self._path, "w") as f:
            json.dump(data, f, indent=2)

    def exists(self, player_id: str) -> bool:
        """Check if player data exists."""
        return self._path.exists()
