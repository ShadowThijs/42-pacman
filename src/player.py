"""Player class."""

from collections import deque

import pygame

from .models import (
    ANIMATION_FRAME_TIME,
    CELL_SIZE,
    OFFSET,
    REVERSE,
    VECTORS,
    Direction,
    can_move,
)
from .sprites import Sprites

# How many recent direction presses to keep. Two is enough to chain a
# turn into the next junction without letting stale input pile up.
INPUT_BUFFER: int = 2


class PacMan:
    """Pacman player class."""

    def __init__(
        self, x: float, y: float, speed: int = 85, lives: int = 3
    ) -> None:
        """Initialize Pacman in the tile containing pixel (x, y)."""
        self.speed: int = speed
        self.row: int
        self.col: int
        self.row, self.col = self._tile_at(x, y)
        self.progress: float = 0.0
        self.direction: int | None = None
        self.pending: deque[int] = deque(maxlen=INPUT_BUFFER)
        self.facing: int = Direction.East
        self.frame: int = 1
        self.anim_t: float = 0.0
        self.anim_frame: int = 0
        self.lives: int = lives

    def queue(self, direction: int) -> None:
        """Remember a direction press for the next tile centre.

        Repeating the most recent press is ignored, so held keys can be
        polled every frame without filling the buffer.
        """
        if not self.pending or self.pending[-1] != direction:
            self.pending.append(direction)

    def respawn(self, x: float, y: float) -> None:
        """Place Pac-Man back at pixel (x, y), motionless.

        Clearing ``progress`` is essential: a collision usually happens
        mid-tile, and a non-zero progress with no direction would stop
        ``update`` from ever calling ``_decide`` again.
        """
        self.row, self.col = self._tile_at(x, y)
        self.progress = 0.0
        self.direction = None
        self.pending.clear()
        self.facing = Direction.East
        self.anim_t = 0.0
        self.anim_frame = 0
        self.frame = 1

    def update(
        self,
        dt: float,
        maze: list[list[int]],
        pacgums: set[tuple[int, int]],
    ) -> int:
        """Advance the player one frame and return how many gums it ate."""
        eaten: int = 0
        if self.direction is None:
            # A stopped Pac-Man belongs on a tile centre, otherwise
            # buffered input would never be resolved by ``_decide``.
            self.progress = 0.0

        tile: tuple[int, int] = (self.row, self.col)
        if tile in pacgums:
            pacgums.discard(tile)
            eaten += 1

        self._reverse_now()

        if self.progress == 0.0:
            self._decide(maze)

        if self.direction is None:
            return eaten

        step: float = self.speed * dt / CELL_SIZE
        self.progress += step
        while self.progress >= 1.0:
            self.progress -= 1.0
            dx, dy = VECTORS[self.direction]
            self.col += dx
            self.row += dy
            self._decide(maze)
            if self.direction is None:
                self.progress = 0.0
                return eaten

        self.anim_t += dt
        if self.anim_t >= ANIMATION_FRAME_TIME:
            self.anim_t = 0.0
            self.anim_frame = 1 - self.anim_frame
        self.frame = self.anim_frame + 1
        return eaten

    def _reverse_now(self) -> None:
        """Apply a reverse input immediately, even mid-tile."""
        if (
            self.direction is None
            or self.progress <= 0.0
            or not self.pending
        ):
            return
        requested: int = self.pending[-1]
        if requested != REVERSE[self.direction]:
            return

        # The logical tile becomes the one we were moving towards, so
        # the pixel position stays put while the visual direction flips.
        dx, dy = VECTORS[self.direction]
        self.col += dx
        self.row += dy
        self.direction = requested
        self.facing = requested
        self.progress = 1.0 - self.progress
        self.pending.clear()

    def _decide(self, maze: list[list[int]]) -> None:
        """Resolve buffered input; stop if the current direction is walled.

        The newest open request wins, so a blocked press never masks a
        directional change the player made right after it.
        """
        for requested in reversed(self.pending):
            if can_move(maze, self.row, self.col, requested):
                self.direction = requested
                self.facing = requested
                self.pending.clear()
                return

        if self.direction is not None and not can_move(
            maze, self.row, self.col, self.direction
        ):
            self.direction = None

    def draw(self, screen: pygame.Surface, sp: Sprites) -> None:
        """Draw the player."""
        spr: pygame.Surface = sp.pacman(self.facing, self.frame)
        screen.blit(spr, spr.get_rect(center=(round(self.x), round(self.y))))

    @property
    def x(self) -> float:
        """Pixel x, interpolated between current tile and the next."""
        ox, _ = OFFSET
        base: float = ox + self.col * CELL_SIZE + CELL_SIZE / 2
        if self.direction is None:
            return base
        return base + VECTORS[self.direction][0] * CELL_SIZE * self.progress

    @property
    def y(self) -> float:
        """Pixel y, interpolated between current tile and the next."""
        _, oy = OFFSET
        base: float = oy + self.row * CELL_SIZE + CELL_SIZE / 2
        if self.direction is None:
            return base
        return base + VECTORS[self.direction][1] * CELL_SIZE * self.progress

    @staticmethod
    def _tile_at(x: float, y: float) -> tuple[int, int]:
        """Return (row, col) of the tile containing pixel (x, y)."""
        ox, oy = OFFSET
        col: int = round((x - ox - CELL_SIZE / 2) / CELL_SIZE)
        row: int = round((y - oy - CELL_SIZE / 2) / CELL_SIZE)
        return row, col
