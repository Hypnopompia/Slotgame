"""GUI views for the slot machine game."""

import tkinter as tk
import random
from tkinter import ttk
from typing import Callable, Optional, List, Tuple

from config import (
    SymbolType,
    SYMBOL_DISPLAY,
    PAYTABLE,
    NUM_REELS,
    NUM_ROWS,
    MIN_BET,
    MAX_BET,
    BET_INCREMENT,
    PAYLINES,
    PAYLINE_INFO,
)
from domain.models import Symbol, WinLine


def _random_symbol_display() -> str:
    """Get a random symbol display for initialization."""
    return random.choice(list(SYMBOL_DISPLAY.values()))


class InfoPanel(tk.Frame):
    """Displays balance and last win information."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.configure(bg="#2c3e50")

        # Balance display
        self._balance_var = tk.StringVar(value="Balance: $1000")
        self._balance_label = tk.Label(
            self,
            textvariable=self._balance_var,
            font=("Helvetica", 16, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
        )
        self._balance_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Last win display
        self._win_var = tk.StringVar(value="Last Win: $0")
        self._win_label = tk.Label(
            self,
            textvariable=self._win_var,
            font=("Helvetica", 16, "bold"),
            bg="#2c3e50",
            fg="#f1c40f",
        )
        self._win_label.pack(side=tk.RIGHT, padx=20, pady=10)

    def set_balance(self, amount: int) -> None:
        self._balance_var.set(f"Balance: ${amount}")

    def set_last_win(self, amount: int) -> None:
        self._win_var.set(f"Last Win: ${amount}")
        if amount > 0:
            self._win_label.configure(fg="#2ecc71")
        else:
            self._win_label.configure(fg="#f1c40f")


class PaytablePanel(tk.Frame):
    """Displays the paytable showing symbol payouts."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.configure(bg="#1a1a2e", relief=tk.RIDGE, bd=2)

        # Title
        title = tk.Label(
            self,
            text="PAYTABLE (multipliers per bet/line)",
            font=("Helvetica", 10, "bold"),
            bg="#1a1a2e",
            fg="#f1c40f",
        )
        title.pack(pady=(5, 2))

        # Header row
        header_frame = tk.Frame(self, bg="#1a1a2e")
        header_frame.pack(fill=tk.X, padx=5)

        tk.Label(
            header_frame, text="Symbol", font=("Helvetica", 9, "bold"),
            bg="#1a1a2e", fg="#ecf0f1", width=8
        ).pack(side=tk.LEFT, padx=2)

        for count in [3, 4, 5]:
            tk.Label(
                header_frame, text=f"×{count}", font=("Helvetica", 9, "bold"),
                bg="#1a1a2e", fg="#ecf0f1", width=5
            ).pack(side=tk.LEFT, padx=2)

        # Symbol rows - order from highest to lowest value
        symbol_order = [
            SymbolType.WILD,
            SymbolType.SEVEN,
            SymbolType.BAR,
            SymbolType.BELL,
            SymbolType.PLUM,
            SymbolType.ORANGE,
            SymbolType.LEMON,
            SymbolType.CHERRY,
        ]

        for symbol_type in symbol_order:
            row_frame = tk.Frame(self, bg="#1a1a2e")
            row_frame.pack(fill=tk.X, padx=5, pady=1)

            # Symbol display
            display = SYMBOL_DISPLAY.get(symbol_type, "?")
            tk.Label(
                row_frame, text=display, font=("Helvetica", 12),
                bg="#1a1a2e", fg="#ecf0f1", width=6
            ).pack(side=tk.LEFT, padx=2)

            # Payouts for 3, 4, 5 matches
            payouts = PAYTABLE.get(symbol_type, {})
            for count in [3, 4, 5]:
                payout = payouts.get(count, 0)
                color = "#2ecc71" if payout >= 100 else "#ecf0f1"
                tk.Label(
                    row_frame, text=str(payout), font=("Helvetica", 9),
                    bg="#1a1a2e", fg=color, width=5
                ).pack(side=tk.LEFT, padx=2)

        # Help text
        help_text = tk.Label(
            self,
            text="Win = Bet/Line × Multiplier | ⭐ = Wild (substitutes any)",
            font=("Helvetica", 8),
            bg="#1a1a2e",
            fg="#888",
        )
        help_text.pack(pady=(2, 5))


class ReelView(tk.Frame):
    """Displays a single reel with 3 visible symbols."""

    def __init__(self, parent: tk.Widget, reel_index: int):
        super().__init__(parent)
        self._reel_index = reel_index
        self._is_spinning = False
        self._final_symbols: Optional[Tuple[Symbol, ...]] = None
        self._spin_count = 0
        self._on_stop_callback: Optional[Callable[[], None]] = None
        self.configure(bg="#34495e", relief=tk.RIDGE, bd=2)

        self._symbol_labels: List[tk.Label] = []

        for row in range(NUM_ROWS):
            label = tk.Label(
                self,
                text=_random_symbol_display(),
                font=("Helvetica", 28),
                width=4,
                height=2,
                bg="#1a1a2e",
                fg="#eee",
                relief=tk.SUNKEN,
                bd=1,
            )
            label.pack(pady=2, padx=4)
            self._symbol_labels.append(label)

    def set_symbols(self, symbols: Tuple[Symbol, ...]) -> None:
        """Update the displayed symbols."""
        for i, symbol in enumerate(symbols):
            display = SYMBOL_DISPLAY.get(symbol.type, "?")
            self._symbol_labels[i].configure(text=display)

    def start_spinning(self, final_symbols: Tuple[Symbol, ...], duration_ms: int, on_stop: Optional[Callable[[], None]] = None) -> None:
        """Start the spinning animation."""
        self._is_spinning = True
        self._final_symbols = final_symbols
        self._spin_count = duration_ms // 50  # Number of animation frames
        self._on_stop_callback = on_stop
        self._animate_spin()

    def _animate_spin(self) -> None:
        """Animate one frame of the spin."""
        if not self._is_spinning:
            return

        if self._spin_count > 0:
            # Show random symbols during spin
            for label in self._symbol_labels:
                label.configure(text=_random_symbol_display())
            self._spin_count -= 1
            # Schedule next frame (faster at start, slower near end)
            delay = 50 if self._spin_count > 5 else 100
            self.after(delay, self._animate_spin)
        else:
            # Show final symbols
            self._is_spinning = False
            if self._final_symbols:
                self.set_symbols(self._final_symbols)
            if self._on_stop_callback:
                self._on_stop_callback()

    def highlight_row(self, row: int, highlight: bool = True) -> None:
        """Highlight a specific row (for winning lines)."""
        if 0 <= row < len(self._symbol_labels):
            bg_color = "#2ecc71" if highlight else "#1a1a2e"
            self._symbol_labels[row].configure(bg=bg_color)

    def highlight_row_color(self, row: int, color: str) -> None:
        """Highlight a specific row with a custom color."""
        if 0 <= row < len(self._symbol_labels):
            self._symbol_labels[row].configure(bg=color)

    def clear_highlights(self) -> None:
        """Clear all row highlights."""
        for label in self._symbol_labels:
            label.configure(bg="#1a1a2e")


class ControlPanel(tk.Frame):
    """Bet controls and spin button."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.configure(bg="#2c3e50")

        self._on_spin: Optional[Callable[[], None]] = None
        self._on_lines_changed: Optional[Callable[[int], None]] = None
        self._bet_per_line = MIN_BET
        self._num_lines = len(PAYLINES)

        # Bet per line controls
        bet_frame = tk.Frame(self, bg="#2c3e50")
        bet_frame.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            bet_frame, text="Bet/Line:", font=("Helvetica", 12), bg="#2c3e50", fg="#ecf0f1"
        ).pack(side=tk.LEFT)

        tk.Button(
            bet_frame,
            text="-",
            font=("Helvetica", 14, "bold"),
            width=2,
            command=self._decrease_bet,
            bg="#e74c3c",
            fg="black",
        ).pack(side=tk.LEFT, padx=5)

        self._bet_var = tk.StringVar(value=str(self._bet_per_line))
        self._bet_entry = tk.Entry(
            bet_frame,
            textvariable=self._bet_var,
            font=("Helvetica", 14, "bold"),
            width=5,
            bg="#ecf0f1",
            fg="black",
            justify=tk.CENTER,
            relief=tk.SUNKEN,
        )
        self._bet_entry.pack(side=tk.LEFT, padx=5)
        self._bet_entry.bind("<Return>", self._on_bet_entry)
        self._bet_entry.bind("<FocusOut>", self._on_bet_entry)

        tk.Button(
            bet_frame,
            text="+",
            font=("Helvetica", 14, "bold"),
            width=2,
            command=self._increase_bet,
            bg="#27ae60",
            fg="black",
        ).pack(side=tk.LEFT, padx=5)

        # Lines controls
        lines_frame = tk.Frame(self, bg="#2c3e50")
        lines_frame.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            lines_frame, text="Lines:", font=("Helvetica", 12), bg="#2c3e50", fg="#ecf0f1"
        ).pack(side=tk.LEFT)

        tk.Button(
            lines_frame,
            text="-",
            font=("Helvetica", 14, "bold"),
            width=2,
            command=self._decrease_lines,
            bg="#e74c3c",
            fg="black",
        ).pack(side=tk.LEFT, padx=5)

        self._lines_var = tk.StringVar(value=str(self._num_lines))
        tk.Label(
            lines_frame,
            textvariable=self._lines_var,
            font=("Helvetica", 14, "bold"),
            width=3,
            bg="#ecf0f1",
            fg="black",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            lines_frame,
            text="+",
            font=("Helvetica", 14, "bold"),
            width=2,
            command=self._increase_lines,
            bg="#27ae60",
            fg="black",
        ).pack(side=tk.LEFT, padx=5)

        # Total bet display
        self._total_bet_var = tk.StringVar()
        self._update_total_bet()
        tk.Label(
            self,
            textvariable=self._total_bet_var,
            font=("Helvetica", 12),
            bg="#2c3e50",
            fg="#f39c12",
        ).pack(side=tk.LEFT, padx=20)

        # Spin button
        self._spin_btn = tk.Button(
            self,
            text="SPIN",
            font=("Helvetica", 20, "bold"),
            width=10,
            height=2,
            command=self._handle_spin,
            bg="#e74c3c",
            fg="black",
            activebackground="#c0392b",
        )
        self._spin_btn.pack(side=tk.RIGHT, padx=20, pady=10)

    def _decrease_bet(self) -> None:
        if self._bet_per_line > MIN_BET:
            self._bet_per_line -= BET_INCREMENT
            self._bet_var.set(str(self._bet_per_line))
            self._update_total_bet()

    def _increase_bet(self) -> None:
        if self._bet_per_line < MAX_BET:
            self._bet_per_line += BET_INCREMENT
            self._bet_var.set(str(self._bet_per_line))
            self._update_total_bet()

    def _on_bet_entry(self, event=None) -> None:
        """Handle manual bet entry."""
        try:
            # Remove $ if present and parse
            value = self._bet_var.get().replace("$", "").strip()
            new_bet = int(value)
            # Clamp to valid range
            new_bet = max(MIN_BET, min(MAX_BET, new_bet))
            self._bet_per_line = new_bet
            print(f"[DEBUG] Bet changed to: ${self._bet_per_line}")
        except ValueError:
            # Invalid input, revert to current value
            print(f"[DEBUG] Invalid bet input: '{self._bet_var.get()}', keeping ${self._bet_per_line}")
        # Update display to normalized value
        self._bet_var.set(str(self._bet_per_line))
        self._update_total_bet()
        print(f"[DEBUG] Total bet updated: ${self._bet_per_line} × {self._num_lines} lines = ${self._bet_per_line * self._num_lines}")

    def _decrease_lines(self) -> None:
        if self._num_lines > 1:
            self._num_lines -= 1
            self._lines_var.set(str(self._num_lines))
            self._update_total_bet()
            if self._on_lines_changed:
                self._on_lines_changed(self._num_lines)

    def _increase_lines(self) -> None:
        if self._num_lines < len(PAYLINES):
            self._num_lines += 1
            self._lines_var.set(str(self._num_lines))
            self._update_total_bet()
            if self._on_lines_changed:
                self._on_lines_changed(self._num_lines)

    def _update_total_bet(self) -> None:
        total = self._bet_per_line * self._num_lines
        self._total_bet_var.set(f"Total Bet: ${total}")

    def _handle_spin(self) -> None:
        if self._on_spin:
            self._on_spin()

    @property
    def bet_per_line(self) -> int:
        return self._bet_per_line

    @property
    def num_lines(self) -> int:
        return self._num_lines

    @property
    def on_spin(self) -> Optional[Callable[[], None]]:
        return self._on_spin

    @on_spin.setter
    def on_spin(self, callback: Callable[[], None]) -> None:
        self._on_spin = callback

    @property
    def on_lines_changed(self) -> Optional[Callable[[int], None]]:
        return self._on_lines_changed

    @on_lines_changed.setter
    def on_lines_changed(self, callback: Callable[[int], None]) -> None:
        self._on_lines_changed = callback

    def set_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self._spin_btn.configure(state=state)


class MessagePanel(tk.Frame):
    """Displays game messages (wins, errors)."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.configure(bg="#2c3e50")

        self._message_var = tk.StringVar(value="Good luck!")
        self._message_label = tk.Label(
            self,
            textvariable=self._message_var,
            font=("Helvetica", 14),
            bg="#2c3e50",
            fg="#ecf0f1",
        )
        self._message_label.pack(pady=10)

    def set_message(self, message: str, is_win: bool = False, is_error: bool = False) -> None:
        self._message_var.set(message)
        if is_error:
            self._message_label.configure(fg="#e74c3c")
        elif is_win:
            self._message_label.configure(fg="#2ecc71")
        else:
            self._message_label.configure(fg="#ecf0f1")


class PaylineLegend(tk.Frame):
    """Shows payline legend with clickable buttons to highlight lines."""

    def __init__(self, parent: tk.Widget, on_highlight: Callable[[int], None], on_clear: Callable[[], None]):
        super().__init__(parent)
        self.configure(bg="#2c3e50")
        self._on_highlight = on_highlight
        self._on_clear = on_clear
        self._num_active = len(PAYLINES)

        tk.Label(
            self,
            text="Paylines:",
            font=("Helvetica", 10),
            bg="#2c3e50",
            fg="#ecf0f1",
        ).pack(side=tk.LEFT, padx=(0, 5))

        self._buttons: List[tk.Label] = []
        for i, info in enumerate(PAYLINE_INFO):
            btn = tk.Label(
                self,
                text=f" {i+1} ",
                font=("Helvetica", 10, "bold"),
                bg=info["color"],
                fg="white",
                relief=tk.RAISED,
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Enter>", lambda e, idx=i: self._on_hover(idx))
            btn.bind("<Leave>", lambda e: self._on_leave())
            self._buttons.append(btn)

    def _on_hover(self, line_idx: int) -> None:
        """Highlight the hovered payline."""
        if line_idx < self._num_active:
            self._on_highlight(line_idx)

    def _on_leave(self) -> None:
        """Clear payline highlight."""
        self._on_clear()

    def set_active_lines(self, num_lines: int) -> None:
        """Update which lines are shown as active."""
        self._num_active = num_lines
        for i, btn in enumerate(self._buttons):
            if i < num_lines:
                btn.configure(bg=PAYLINE_INFO[i]["color"], relief=tk.RAISED)
            else:
                btn.configure(bg="#555", relief=tk.FLAT)


class MainView(tk.Frame):
    """Main game view - composes all sub-views."""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.configure(bg="#2c3e50")

        self._on_spin: Optional[Callable[[], None]] = None
        self._showing_payline: bool = False
        self._reel_container: Optional[tk.Frame] = None
        self._line_canvas: Optional[tk.Canvas] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Info panel (balance, last win)
        self._info_panel = InfoPanel(self)
        self._info_panel.pack(fill=tk.X, padx=10, pady=5)

        # Payline legend
        self._payline_legend = PaylineLegend(
            self,
            on_highlight=self._highlight_payline,
            on_clear=self._clear_payline_preview,
        )
        self._payline_legend.pack(pady=5)

        # Main content area - reels on left, paytable on right
        content_frame = tk.Frame(self, bg="#2c3e50")
        content_frame.pack(padx=10, pady=10)

        # Container for reels and line overlay - using place geometry for canvas overlay
        self._reel_container = tk.Frame(content_frame, bg="#2c3e50")
        self._reel_container.pack(side=tk.LEFT, padx=(0, 15))

        # Reel display area
        self._reel_frame = tk.Frame(self._reel_container, bg="#34495e", relief=tk.GROOVE, bd=3)
        self._reel_frame.pack()

        self._reel_views: List[ReelView] = []
        for i in range(NUM_REELS):
            reel = ReelView(self._reel_frame, reel_index=i)
            reel.pack(side=tk.LEFT, padx=5, pady=10)
            self._reel_views.append(reel)

        # Paytable panel on right side
        self._paytable_panel = PaytablePanel(content_frame)
        self._paytable_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Message panel
        self._message_panel = MessagePanel(self)
        self._message_panel.pack(fill=tk.X, padx=10)

        # Control panel (bet/spin controls)
        self._control_panel = ControlPanel(self)
        self._control_panel.pack(fill=tk.X, padx=10, pady=10)
        self._control_panel.on_spin = self._handle_spin
        self._control_panel.on_lines_changed = self._on_lines_changed

    def _get_cell_center_in_frame(self, reel_idx: int, row_idx: int) -> Tuple[int, int]:
        """Get the center coordinates of a reel cell relative to the reel frame."""
        reel_view = self._reel_views[reel_idx]
        label = reel_view._symbol_labels[row_idx]

        # Get label position relative to its parent (reel_view), and reel_view relative to reel_frame
        reel_x = reel_view.winfo_x()
        reel_y = reel_view.winfo_y()
        label_x = label.winfo_x()
        label_y = label.winfo_y()

        x = reel_x + label_x + label.winfo_width() // 2
        y = reel_y + label_y + label.winfo_height() // 2
        return (x, y)

    def _draw_payline(self, line_idx: int) -> None:
        """Draw a payline using a canvas overlay that redraws the reel symbols."""
        # Clear any existing overlay
        self._clear_payline_drawing()

        # Make sure geometry is calculated
        self.update_idletasks()

        # Get payline positions and color
        positions = PAYLINES[line_idx]
        color = PAYLINE_INFO[line_idx]["color"]

        # Get container dimensions
        container_width = self._reel_container.winfo_width()
        container_height = self._reel_container.winfo_height()

        if container_width <= 1 or container_height <= 1:
            return

        # Get reel_frame position and size
        frame_x = self._reel_frame.winfo_x()
        frame_y = self._reel_frame.winfo_y()
        frame_width = self._reel_frame.winfo_width()
        frame_height = self._reel_frame.winfo_height()

        # Create canvas overlay
        self._line_canvas = tk.Canvas(
            self._reel_container,
            width=frame_width,
            height=frame_height,
            highlightthickness=0,
            bg="#34495e"  # Match the reel frame background
        )
        self._line_canvas.place(x=frame_x, y=frame_y)

        # Draw all the reel cells on the canvas
        for reel_idx, reel_view in enumerate(self._reel_views):
            for row_idx, label in enumerate(reel_view._symbol_labels):
                # Get cell position and size
                reel_x = reel_view.winfo_x()
                reel_y = reel_view.winfo_y()
                label_x = label.winfo_x()
                label_y = label.winfo_y()
                label_w = label.winfo_width()
                label_h = label.winfo_height()

                x1 = reel_x + label_x
                y1 = reel_y + label_y
                x2 = x1 + label_w
                y2 = y1 + label_h

                # Check if this cell is on the payline
                is_on_payline = positions[reel_idx] == row_idx

                # Draw cell background
                bg_color = color if is_on_payline else "#1a1a2e"
                self._line_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg_color,
                    outline="#555",
                    width=1
                )

                # Draw the symbol text
                symbol_text = label.cget("text")
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                self._line_canvas.create_text(
                    cx, cy,
                    text=symbol_text,
                    font=("Helvetica", 28),
                    fill="#eee"
                )

        # Get coordinates for payline points
        points = []
        for reel_idx, row_idx in enumerate(positions):
            x, y = self._get_cell_center_in_frame(reel_idx, row_idx)
            points.append((x, y))

        if not points or points[0][0] == 0:
            return

        # Flatten points for create_line
        flat_points = []
        for px, py in points:
            flat_points.extend([px, py])

        # Draw the line with white outline (thicker, drawn first)
        self._line_canvas.create_line(
            flat_points,
            fill="white",
            width=8,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )
        # Draw colored line on top
        self._line_canvas.create_line(
            flat_points,
            fill=color,
            width=4,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )

        # Draw circles at each point
        for px, py in points:
            self._line_canvas.create_oval(
                px - 10, py - 10, px + 10, py + 10,
                fill=color,
                outline="white",
                width=2
            )

    def _clear_payline_drawing(self) -> None:
        """Clear the payline canvas overlay."""
        if self._line_canvas is not None:
            try:
                self._line_canvas.destroy()
            except tk.TclError:
                pass
            self._line_canvas = None

    def _highlight_payline(self, line_idx: int) -> None:
        """Highlight a specific payline on the reels."""
        self._showing_payline = True
        self.clear_highlights()
        positions = PAYLINES[line_idx]
        color = PAYLINE_INFO[line_idx]["color"]
        for reel_idx, row_idx in enumerate(positions):
            self._reel_views[reel_idx].highlight_row_color(row_idx, color)
        # Draw the connecting line
        self._draw_payline(line_idx)

    def _clear_payline_preview(self) -> None:
        """Clear the payline preview highlight."""
        self._showing_payline = False
        self.clear_highlights()
        self._clear_payline_drawing()

    def _on_lines_changed(self, num_lines: int) -> None:
        """Called when number of active lines changes."""
        self._payline_legend.set_active_lines(num_lines)

    def _handle_spin(self) -> None:
        if self._on_spin:
            self._on_spin()

    @property
    def on_spin(self) -> Optional[Callable[[], None]]:
        return self._on_spin

    @on_spin.setter
    def on_spin(self, callback: Callable[[], None]) -> None:
        self._on_spin = callback

    @property
    def bet_per_line(self) -> int:
        return self._control_panel.bet_per_line

    @property
    def num_lines(self) -> int:
        return self._control_panel.num_lines

    def set_balance(self, amount: int) -> None:
        self._info_panel.set_balance(amount)

    def set_last_win(self, amount: int) -> None:
        self._info_panel.set_last_win(amount)

    def set_message(self, message: str, is_win: bool = False, is_error: bool = False) -> None:
        self._message_panel.set_message(message, is_win, is_error)

    def set_enabled(self, enabled: bool) -> None:
        self._control_panel.set_enabled(enabled)

    def update_reels(self, grid: Tuple[Tuple[Symbol, ...], ...]) -> None:
        """Update all reels with new symbols."""
        for i, reel_view in enumerate(self._reel_views):
            reel_view.set_symbols(grid[i])

    def spin_reels_animated(
        self,
        grid: Tuple[Tuple[Symbol, ...], ...],
        on_complete: Callable[[], None],
        on_reel_stop: Optional[Callable[[], None]] = None,
    ) -> None:
        """Spin all reels with animation, calling on_complete when done."""
        self._reels_stopped = 0

        def handle_reel_stop():
            self._reels_stopped += 1
            # Call the per-reel callback if provided
            if on_reel_stop:
                on_reel_stop()
            # Call the complete callback when all reels have stopped
            if self._reels_stopped >= NUM_REELS:
                on_complete()

        # Start each reel with staggered stop times (each reel spins longer)
        base_duration = 500  # ms
        for i, reel_view in enumerate(self._reel_views):
            duration = base_duration + (i * 300)  # Each reel spins 300ms longer
            reel_view.start_spinning(grid[i], duration, handle_reel_stop)

    def highlight_winning_lines(self, winning_lines: Tuple[WinLine, ...]) -> None:
        """Highlight rows that are part of winning lines."""
        # Clear previous highlights
        for reel_view in self._reel_views:
            reel_view.clear_highlights()

        # Highlight winning positions
        for win_line in winning_lines:
            payline_positions = PAYLINES[win_line.payline_id - 1]
            for reel_idx, row_idx in enumerate(payline_positions):
                if reel_idx < win_line.match_count:
                    self._reel_views[reel_idx].highlight_row(row_idx, True)

    def clear_highlights(self) -> None:
        """Clear all winning line highlights."""
        for reel_view in self._reel_views:
            reel_view.clear_highlights()
