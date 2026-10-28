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
        self._pacman_cache: dict[
            tuple[int, int], pygame.Surface
        ] = {}

    def _load(self, rel: str) -> pygame.Surface:
        """Load and cache a sprite surface by relative path."""
        path: Path = self.base / rel
        if path not in self._cache:
            self._cache[path] = pygame.image.load(str(path))
        return self._cache[path]

    def pacman(self, direction: int, frame: int = 1) -> pygame.Surface:
        """Get pacman sprite for a direction and animation frame (1-2)."""
        key: tuple[int, int] = (direction, frame)
        cached: pygame.Surface | None = self._pacman_cache.get(key)
        if cached is not None:
            return cached
        sprite: pygame.Surface = self._load(
            f"pacman/{_DIR_LETTER[direction]}-{frame}.svg"
        )
        if frame == 2:
            sprite = self._align_open_mouth(direction, sprite)
        self._pacman_cache[key] = sprite
        return sprite

    def _align_open_mouth(
        self,
        direction: int,
        opened: pygame.Surface,
    ) -> pygame.Surface:
        """Keep Pac-Man's trailing edge fixed while his mouth opens.

        The two source frames do not share the same bounding box: the open
        frame is wider, so drawing both centred makes the body jump
        backwards by a few pixels.  Align the trailing edge of the open
        frame with the closed frame instead, letting the mouth open
        forwards.
        """
        closed: pygame.Surface = self._load(
            f"pacman/{_DIR_LETTER[direction]}-1.svg"
        )
        closed_box: pygame.Rect = closed.get_bounding_rect(min_alpha=1)
        opened_box: pygame.Rect = opened.get_bounding_rect(min_alpha=1)
        dx: int = 0
        dy: int = 0
        if direction == Direction.East:
            dx = closed_box.left - opened_box.left
        elif direction == Direction.West:
            dx = closed_box.right - opened_box.right
        elif direction == Direction.North:
            dy = closed_box.bottom - opened_box.bottom
        else:
            dy = closed_box.top - opened_box.top
        aligned: pygame.Surface = pygame.Surface(
            opened.get_size(), pygame.SRCALPHA
        )
        aligned.blit(opened, (dx, dy))
        return aligned

    def ghost(
        self, color: str, direction: int, frame: int = 1
    ) -> pygame.Surface:
        """Ghost sprite (red/pink/cyan/orange), direction + frame (1-2)."""
        return self._load(
            f"{color}-ghost/{_DIR_LETTER[direction]}-{frame}.svg"
        )

    def vulnerable(
        self, white: bool = False, frame: int = 1
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
