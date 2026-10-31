"""Session-wide cheat state."""

from __future__ import annotations


class Cheats:
    """Cheat flags for one program session.

    The object lives on ``Game`` for the whole run. Starting a new game
    or a new level does not reset it, and ``enabled`` is read-only: once
    activated, cheats stay on until the process exits.

    Add future cheat flags here as attributes in ``__init__``, for
    example ``self.invincible = False``, and set them when the
    corresponding cheat is enabled.
    """

    def __init__(self) -> None:
        """Start a session with every cheat disabled."""
        self._enabled: bool = False

    @property
    def enabled(self) -> bool:
        """Return whether cheats have been unlocked this session."""
        return self._enabled

    def activate(self) -> bool:
        """Enable cheats and report whether this call changed the state."""
        newly_activated = not self._enabled
        self._enabled = True
        return newly_activated
