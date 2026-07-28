"""Player class."""

from typing import Optional 

import pygame

from .models import Colors, Direction


VECTORS: dict[int, tuple[int, int]] = {
    Direction.North: (0, -1),
    Direction.South: (0, 1),
    Direction.East: (1, 0),
    Direction.West: (-1, 0)
}

class PacMan:
    """Pacman player class."""

    def __init__(
        self,
        x: float,
        y: float,
        speed: int = 100
    ) -> None:
        """Initialize Pacman at (x,y) with speed."""
        self.x: float = x
        self.y: float = y
        self.speed: int = speed
        self.direction: Optional[int] = None
        self.is_moving: bool = False

    def set_direction(self, direction: int) -> None:
        """Set the direction the player wants to move in."""
        self.direction = direction
    
    def update(self, dt: float) -> None:
        """Advance the player in current direction."""
        if self.direction is None or self.direction not in VECTORS:
            self.is_moving = False
            return
        dx, dy = VECTORS[self.direction]
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.is_moving = True

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player."""
        s: int = 10
        points: list[tuple[float, float]] = [
            (self.x, self.y - s),
            (self.x + s, self.y),
            (self.x, self.y + s),
            (self.x - s, self.y)
        ]
        pygame.draw.polygon(screen, Colors.yellow, points)
