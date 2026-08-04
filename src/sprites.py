"""Sprite helpers."""

from pathlib import Path

import pygame

from .models import Direction

# Direction bitmask -> sprite filename letter.
_DIR_LETTER: dict[int, str] = {
    Direction.North: "N",
    Direction.East: "E",
    Direction.South: "S",
    Direction.West: "W",
}


class Sprites:
    """Sprites class.

    Loads and selects renderable sprites from the resources folder.
    """

    def __init__(self, base: str = "resources") -> None:
        """Init sprite loader with base resources directory."""
        self.base: Path = Path(base)
        self._cache: dict[Path, pygame.Surface] = {}

    def _load(self, rel: str) -> pygame.Surface:
        """Load and cache a sprite surface by relative path."""
        path: Path = self.base / rel
        if path not in self._cache:
            self._cache[path] = pygame.image.load(str(path))
        return self._cache[path]

    def pacman(self, direction: int, frame: int = 1) -> pygame.Surface:
        """Get pacman sprite for a direction and animation frame (1-2)."""
        return self._load(f"pacman/{_DIR_LETTER[direction]}-{frame}.svg")

    def ghost(
        self,
        color: str,
        direction: int,
        frame: int = 1
    ) -> pygame.Surface:
        """Ghost sprite (red/pink/cyan/orange), direction + frame (1-2)."""
        return self._load(
            f"{color}-ghost/{_DIR_LETTER[direction]}-{frame}.svg"
        )

    def vulnerable(
        self,
        white: bool = False,
        frame: int = 1
    ) -> pygame.Surface:
        """Frightened ghost sprite; white flashes near fright end (1-2)."""
        tone: str = "white" if white else "blue"
        return self._load(f"vulnerable-ghost/{tone}-{frame}.svg")

    def eyes(self, direction: int) -> pygame.Surface:
        """Get dead-ghost eyes sprite for a direction."""
        return self._load(f"dead-ghost-eyes/{_DIR_LETTER[direction]}.svg")

    def death(self, frame: int = 0) -> pygame.Surface:
        """Get pacman death animation sprite (0-9)."""
        return self._load(f"dead/dying-{frame}.svg")
