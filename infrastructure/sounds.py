"""Sound effects for the slot machine game."""

import platform
import subprocess
import threading
from pathlib import Path


class SoundPlayer:
    """Cross-platform sound player for slot machine effects."""

    # macOS system sounds
    MACOS_SOUNDS = {
        "spin": "/System/Library/Sounds/Pop.aiff",
        "win": "/System/Library/Sounds/Glass.aiff",
        "big_win": "/System/Library/Sounds/Funk.aiff",
        "lose": "/System/Library/Sounds/Basso.aiff",
        "click": "/System/Library/Sounds/Tink.aiff",
        "reel_stop": "/System/Library/Sounds/Pop.aiff",
    }

    # Windows system sounds (using winsound constants)
    # These map to sound names that we'll handle specially
    WINDOWS_SOUNDS = {
        "spin": "SystemDefault",
        "win": "SystemExclamation",
        "big_win": "SystemExclamation",
        "lose": "SystemHand",
        "click": "SystemDefault",
        "reel_stop": "SystemDefault",
    }

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._platform = platform.system()

    def play(self, sound_name: str) -> None:
        """Play a sound effect by name (non-blocking)."""
        if not self._enabled:
            return

        # Play in background thread to not block UI
        thread = threading.Thread(target=self._play_sound_for_platform, args=(sound_name,))
        thread.daemon = True
        thread.start()

    def _play_sound_for_platform(self, sound_name: str) -> None:
        """Play sound using platform-appropriate method."""
        try:
            if self._platform == "Darwin":  # macOS
                self._play_macos(sound_name)
            elif self._platform == "Windows":
                self._play_windows(sound_name)
            else:  # Linux and others
                self._play_linux(sound_name)
        except Exception:
            pass  # Silently ignore sound errors

    def _play_macos(self, sound_name: str) -> None:
        """Play sound on macOS using afplay."""
        sound_path = self.MACOS_SOUNDS.get(sound_name)
        if sound_path and Path(sound_path).exists():
            subprocess.run(
                ["afplay", sound_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _play_windows(self, sound_name: str) -> None:
        """Play sound on Windows using winsound."""
        try:
            import winsound

            sound_type = self.WINDOWS_SOUNDS.get(sound_name, "SystemDefault")

            # Map sound type names to winsound constants
            sound_map = {
                "SystemDefault": winsound.MB_OK,
                "SystemExclamation": winsound.MB_ICONEXCLAMATION,
                "SystemHand": winsound.MB_ICONHAND,
                "SystemQuestion": winsound.MB_ICONQUESTION,
                "SystemAsterisk": winsound.MB_ICONASTERISK,
            }

            flags = sound_map.get(sound_type, winsound.MB_OK)
            winsound.MessageBeep(flags)
        except ImportError:
            pass  # winsound not available

    def _play_linux(self, sound_name: str) -> None:
        """Play sound on Linux using available tools."""
        # Try paplay (PulseAudio) first, then aplay (ALSA), then bell
        sound_files = {
            "spin": "/usr/share/sounds/freedesktop/stereo/button-pressed.oga",
            "win": "/usr/share/sounds/freedesktop/stereo/complete.oga",
            "big_win": "/usr/share/sounds/freedesktop/stereo/complete.oga",
            "lose": "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga",
            "click": "/usr/share/sounds/freedesktop/stereo/button-pressed.oga",
            "reel_stop": "/usr/share/sounds/freedesktop/stereo/button-pressed.oga",
        }

        sound_path = sound_files.get(sound_name)

        if sound_path and Path(sound_path).exists():
            # Try paplay first (PulseAudio)
            try:
                subprocess.run(
                    ["paplay", sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                )
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

            # Try aplay (ALSA) - may not work with .oga files
            try:
                subprocess.run(
                    ["aplay", "-q", sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                )
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

        # Fallback: terminal bell (works in most terminals)
        print("\a", end="", flush=True)

    def play_win(self, amount: int, bet: int) -> None:
        """Play appropriate win sound based on win size."""
        if amount >= bet * 50:  # Big win (50x or more)
            self.play("big_win")
        else:
            self.play("win")

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
