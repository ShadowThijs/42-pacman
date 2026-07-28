
"""Ghost class."""

from .models import Direction


class Ghost:
    """Ghost player class."""

    def __init__(self) -> None:
        """Initialize."""
        self.x: int
        self.y: int
        self.direction: Direction
