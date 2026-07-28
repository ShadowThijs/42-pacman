"""Player class."""

from .models import Direction


class PacMan:
    """Pacman player class."""

    def __init__(self) -> None:
        """Initialize."""
        self.x: int
        self.y: int
        self.super: bool
        self.round_points: int
        self.total_points: int
        self.direction: Direction
