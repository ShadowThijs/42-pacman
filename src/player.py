"""Player class."""

from typing import Optional

import pygame

from .models import Colors, Direction
from .sprites import Sprites

VECTORS: dict[int, tuple[int, int]] = {
    Direction.North: (0, -1),
    Direction.South: (0, 1),
    Direction.East: (1, 0),
    Direction.West: (-1, 0)
}

SWITCH_DT: float = 0.2

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
        self.direction: int = Direction.North
        self.is_moving: bool = False
        self.frame: int = 1
        self.anim_t: float = 0.0
        self.anim_frame: int = 0

    def set_direction(self, direction: int) -> None:
        """Set the direction the player wants to move in."""
        self.direction = direction

    def update(self, dt: float) -> None:
        """Advance the player in current direction."""
        if self.direction is None or self.direction not in VECTORS:
            self.is_moving = False
            return

        self.anim_t += dt
        if self.anim_t >= SWITCH_DT:
            self.anim_t = 0.0
            self.anim_frame = 1 - self.anim_frame
        self.frame = self.anim_frame + 1
        dx, dy = VECTORS[self.direction]
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.is_moving = True

    def draw(self, screen: pygame.Surface, sp: Sprites) -> None:
        """Draw the player."""
        spr: pygame.Surface = sp.pacman(self.direction, self.frame)
        screen.blit(spr, (self.x - 16, self.y - 16))
