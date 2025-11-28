"""Slot machine application - composition root."""

import tkinter as tk
from typing import Optional

from config import DEFAULT_BALANCE, SYMBOL_DISPLAY
from application.game_engine import GameEngine
from infrastructure.persistence import JsonPlayerRepository
from infrastructure.sounds import SoundPlayer
from .views import MainView


class SlotMachineApp:
    """Main application class - wires all dependencies together."""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title("5-Reel Slot Machine")
        self._root.configure(bg="#2c3e50")
        self._root.resizable(False, False)

        # Wire dependencies
        self._repository = JsonPlayerRepository()
        self._engine = GameEngine(repository=self._repository)
        self._sounds = SoundPlayer(enabled=True)

        # Create main view
        self._view = MainView(self._root)
        self._view.pack(fill=tk.BOTH, expand=True)

        # Connect events
        self._view.on_spin = self._handle_spin

        # Load player and initialize display
        self._engine.load_player("default")
        self._view.set_balance(self._engine.current_balance)

        # Check if player is bankrupt on start
        if self._engine.current_balance == 0:
            self._handle_bankrupt()

    def _handle_spin(self) -> None:
        """Handle spin button click."""
        # Disable controls during spin
        self._view.set_enabled(False)
        self._view.clear_highlights()
        self._view.set_message("Spinning...", is_win=False)

        # Play spin sound
        self._sounds.play("spin")

        try:
            # Execute spin (get result immediately, but animate display)
            result = self._engine.spin(
                bet_per_line=self._view.bet_per_line,
                num_lines=self._view.num_lines,
            )

            # Animate reels, then show result after animation completes
            def on_spin_complete():
                # Update balance and last win after wheels stop
                self._view.set_balance(self._engine.current_balance)
                self._view.set_last_win(result.total_payout)

                # Show result message and play sound
                if result.is_win:
                    win_details = self._format_win_details(result.winning_lines)
                    self._view.set_message(f"WIN ${result.total_payout}! {win_details}", is_win=True)
                    self._view.highlight_winning_lines(result.winning_lines)
                    self._sounds.play_win(result.total_payout, result.bet_amount)
                else:
                    self._view.set_message("No win. Try again!", is_win=False)
                    self._sounds.play("lose")

                # Re-enable controls
                self._view.set_enabled(True)

                # Check for bankrupt
                if self._engine.current_balance == 0:
                    self._root.after(1000, self._handle_bankrupt)

            self._view.spin_reels_animated(
                result.grid,
                on_spin_complete,
                on_reel_stop=lambda: self._sounds.play("reel_stop"),
            )

        except ValueError as e:
            self._view.set_message(str(e), is_error=True)
            self._view.set_enabled(True)

    def _format_win_details(self, winning_lines) -> str:
        """Format winning line details for display."""
        if not winning_lines:
            return ""

        details = []
        for win in winning_lines:
            symbol_display = SYMBOL_DISPLAY.get(win.symbol_type, "?")
            details.append(f"Line {win.payline_id}: {win.match_count}x {symbol_display}")

        return " | ".join(details)

    def _handle_bankrupt(self) -> None:
        """Handle when player runs out of credits."""
        # Show bankrupt dialog
        dialog = tk.Toplevel(self._root)
        dialog.title("Out of Credits!")
        dialog.configure(bg="#2c3e50")
        dialog.transient(self._root)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("300x150")
        dialog.resizable(False, False)

        tk.Label(
            dialog,
            text="You're out of credits!",
            font=("Helvetica", 14, "bold"),
            bg="#2c3e50",
            fg="#e74c3c",
        ).pack(pady=20)

        tk.Label(
            dialog,
            text=f"Add ${DEFAULT_BALANCE} free credits?",
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg="#ecf0f1",
        ).pack(pady=5)

        btn_frame = tk.Frame(dialog, bg="#2c3e50")
        btn_frame.pack(pady=15)

        def add_credits():
            self._engine.add_credits(DEFAULT_BALANCE)
            self._view.set_balance(self._engine.current_balance)
            self._view.set_message(f"Added ${DEFAULT_BALANCE} credits. Good luck!")
            dialog.destroy()

        def quit_game():
            dialog.destroy()
            self._root.quit()

        tk.Button(
            btn_frame,
            text="Add Credits",
            font=("Helvetica", 12),
            command=add_credits,
            bg="#27ae60",
            fg="white",
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Quit",
            font=("Helvetica", 12),
            command=quit_game,
            bg="#e74c3c",
            fg="white",
        ).pack(side=tk.LEFT, padx=10)

    def run(self) -> None:
        """Start the application main loop."""
        self._root.mainloop()
