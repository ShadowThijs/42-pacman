"""Player class."""

import pygame

from .models import CELL_SIZE, OFFSET, Direction
from .sprites import Sprites

VECTORS: dict[int, tuple[int, int]] = {
    Direction.North: (0, -1),
    Direction.South: (0, 1),
    Direction.East: (1, 0),
    Direction.West: (-1, 0),
}

REVERSE: dict[int, int] = {
    Direction.North: Direction.South,
    Direction.South: Direction.North,
    Direction.East: Direction.West,
    Direction.West: Direction.East,
}

SWITCH_DT: float = 0.2


class PacMan:
    """Pacman player class."""

    def __init__(self, x: float, y: float, speed: int = 100) -> None:
        """Initialize Pacman in the tile containing pixel (x, y)."""
        self.speed: int = speed
        self.row: int
        self.col: int
        self.row, self.col = self._tile_at(x, y)
        self.progress: float = 0.0
        self.direction: int | None = None
        self.next_direction: int | None = None
        self.facing: int = Direction.East
        self.frame: int = 1
        self.anim_t: float = 0.0
        self.anim_frame: int = 0

    def queue(self, direction: int) -> None:
        """Buffer a direction change, applied at the next tile center."""
        self.next_direction = direction

    def update(
        self,
        dt: float,
        maze: list[list[int]],
        pacgums: list[tuple[int, int]],
    ) -> int:
        """Advance the player one frame."""
        eaten: int = 0
        rev_dir = self.direction
        rev_next = self.next_direction
        if (
            self.progress > 0.0
            and rev_dir is not None
            and rev_next is not None
            and rev_next == REVERSE[rev_dir]
        ):
            dx, dy = VECTORS[rev_dir]
            self.col += dx
            self.row += dy
            self.direction = rev_next
            self.facing = rev_next
            self.progress = 1.0 - self.progress
            self.next_direction = None

        for p in list(pacgums):
            if self.row == p[0] and self.col == p[1]:
                pacgums.remove(p)
                eaten += 1

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
        if self.anim_t >= SWITCH_DT:
            self.anim_t = 0.0
            self.anim_frame = 1 - self.anim_frame
        self.frame = self.anim_frame + 1
        return eaten

    def _decide(self, maze: list[list[int]]) -> None:
        """Resolve buffered input; stop if the facing direction is walled."""
        nxt = self.next_direction
        if nxt is not None and self._open(maze, self.row, self.col, nxt):
            self.direction = nxt
            self.facing = nxt
            self.next_direction = None
        if self.direction is not None and not self._open(
            maze, self.row, self.col, self.direction
        ):
            self.direction = None

    def draw(self, screen: pygame.Surface, sp: Sprites) -> None:
        """Draw the player."""
        spr: pygame.Surface = sp.pacman(self.facing, self.frame)
        screen.blit(spr, (self.x - 16, self.y - 16))

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

    @staticmethod
    def _open(
        maze: list[list[int]], row: int, col: int, direction: int
    ) -> bool:
        """No wall on `direction`'s side of cell (row, col)."""
        return maze[row][col] & direction == 0
