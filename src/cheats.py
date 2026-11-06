"""Session-wide cheat state."""

from __future__ import annotations


class Cheats:
    """Cheat flags for one program session."""

    def __init__(self) -> None:
        """Start a session with every cheat disabled."""
        self._enabled: bool = False
        self._invincible: bool = False
        self._speedhack: bool = False
        self._ghostfreeze: bool = False

    @property
    def enabled(self) -> bool:
        """Return whether cheats have been unlocked this session."""
        return self._enabled

    def activate(self) -> bool:
        """Enable cheats and report whether this call changed the state."""
        newly_activated = not self._enabled
        self._enabled = True
        return newly_activated

    def invincible(self, change: bool | None = None) -> bool:
        """Change or retrieve cheat."""
        if change not in (None, self._invincible):
            self._invincible = change
        return self._invincible

    def speedhack(self, change: bool | None = None) -> bool:
        """Change or retrieve cheat."""
        if change not in (None, self._speedhack):
            self._speedhack = change
        return self._speedhack

    def ghostfreeze(self, change: bool | None = None) -> bool:
        """Change or retrieve cheat."""
        if change not in (None, self._ghostfreeze):
            self._ghostfreeze = change
        return self._ghostfreeze
