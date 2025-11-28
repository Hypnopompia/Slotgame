# 5-Reel Slot Machine Game

A Python slot machine game with animated reels, multiple paylines, wild symbols, and sound effects.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Features

- 5-reel slot machine with 3 rows
- 9 configurable paylines
- Wild symbol substitution
- Animated spinning reels
- Sound effects on spin, win, and reel stop
- Paytable display with multipliers
- Hover over payline numbers to visualize each line
- Persistent player balance (saved to JSON)

## Installation

### Prerequisites

- Python 3.10 or higher
- Tkinter (usually included with Python)

### macOS

```bash
# Install Python with Tkinter support via Homebrew
brew install python-tk@3.13

# Clone the repository
git clone git@github.com:Hypnopompia/Slotgame.git
cd Slotgame

# Run the game
/opt/homebrew/bin/python3.13 main.py
```

If you have Python installed via other means, ensure Tkinter is available:
```bash
python3 -c "import tkinter; print('Tkinter OK')"
```

### Windows

1. Download and install Python from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Tkinter is included by default with the Windows installer

2. Clone or download the repository:
```cmd
git clone git@github.com:Hypnopompia/Slotgame.git
cd Slotgame
```

3. Run the game:
```cmd
python main.py
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and Tkinter
sudo apt update
sudo apt install python3 python3-tk

# Optional: Install PulseAudio for sound support
sudo apt install pulseaudio-utils

# Clone the repository
git clone git@github.com:Hypnopompia/Slotgame.git
cd Slotgame

# Run the game
python3 main.py
```

### Linux (Fedora)

```bash
# Install Python and Tkinter
sudo dnf install python3 python3-tkinter

# Clone the repository
git clone git@github.com:Hypnopompia/Slotgame.git
cd Slotgame

# Run the game
python3 main.py
```

### Linux (Arch)

```bash
# Install Python and Tkinter
sudo pacman -S python tk

# Clone the repository
git clone git@github.com:Hypnopompia/Slotgame.git
cd Slotgame

# Run the game
python main.py
```

## How to Play

1. **Set your bet**: Use the +/- buttons or click the bet field to type an amount
2. **Choose paylines**: Select how many lines to bet on (1-9)
3. **Spin**: Click the SPIN button
4. **Win**: Match 3 or more symbols from left to right on active paylines

### Symbols (highest to lowest value)

| Symbol | Name |
|--------|------|
| ⭐ | Wild (substitutes for any symbol) |
| 7️⃣ | Seven |
| 📊 | Bar |
| 🔔 | Bell |
| 🍇 | Plum |
| 🍊 | Orange |
| 🍋 | Lemon |
| 🍒 | Cherry |

### Viewing Paylines

Hover over the numbered payline buttons to see exactly where each line runs across the reels.

## Project Structure

```
slotgame/
├── main.py                 # Entry point
├── config.py               # Game configuration (symbols, payouts, paylines)
├── domain/                 # Core game logic
│   ├── models.py           # Data models (Symbol, Player, SpinResult)
│   └── services.py         # Game services (ReelGenerator, PayoutCalculator)
├── application/            # Application layer
│   └── game_engine.py      # Game orchestration
├── infrastructure/         # External concerns
│   ├── persistence.py      # JSON file storage
│   └── sounds.py           # Cross-platform sound effects
└── presentation/           # UI layer
    ├── views.py            # Tkinter UI components
    └── app.py              # Application composition root
```

## Building Executables

### Download Pre-built Executables

Check the [Releases](https://github.com/Hypnopompia/Slotgame/releases) page for pre-built executables for Windows, macOS, and Linux.

### Build Locally with PyInstaller

You can build a standalone executable for your platform:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "SlotMachine" main.py
```

The executable will be in the `dist/` folder.

#### Platform-specific notes:

**macOS:**
```bash
pyinstaller --onefile --windowed --name "SlotMachine" main.py
# Creates dist/SlotMachine.app
```

**Windows:**
```cmd
pyinstaller --onefile --windowed --name "SlotMachine" main.py
# Creates dist\SlotMachine.exe
```

**Linux:**
```bash
pyinstaller --onefile --name "SlotMachine" main.py
# Creates dist/SlotMachine
chmod +x dist/SlotMachine
```

### Automated Builds (GitHub Actions)

This repository includes a GitHub Actions workflow that automatically builds executables for all platforms when you create a release tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers the build workflow and creates a GitHub Release with downloadable executables for:
- macOS (`.zip` containing `.app` bundle)
- Windows (`.exe`)
- Linux (binary)

You can also manually trigger a build from the Actions tab using "workflow_dispatch".

## Configuration

Game settings can be modified in `config.py`:
- `DEFAULT_BALANCE`: Starting credits (default: 1000)
- `SYMBOL_WEIGHTS`: Probability of each symbol appearing
- `PAYTABLE`: Payout multipliers for symbol matches
- `PAYLINES`: Payline patterns across the reels

## License

MIT License
