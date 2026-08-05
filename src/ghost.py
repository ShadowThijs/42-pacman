"""Ghost class."""

from .models import Direction


class Ghost:
    """Ghost player class."""

    def __init__(self) -> None:
        """Initialize."""
        self.x: int
        self.y: int
        self.direction: Direction


class Blinky(Ghost):
    """Blinky (red) ghost.

    Follows Pac-Man directly (shortest path)
    Goes to the upper-right corner in Scatter mode
    """


class Inky(Ghost):
    """Inky (cyan) ghost.

    Target is relative to both Blinky and Pac-Man,
        where the distance Blinky is from Pinky's target
        is doubled to get Inky's target
    Goes to the lower-right corner in Scatter mode
    """


class Pinky(Ghost):
    """Pinky (pink) ghost.

    Target spot 2 cells in front of Pac-Man
        * Will target 2 to the left when Pac-Man faces up
    Goes to upper-left corner in Scatter mode
    """


class Clyde(Ghost):
    """Clyde (orange) ghost.

    Target is Pac-Man directly, but tries to target,
        Scatter corner when within 8 cell radius of Pac-Man
    Goes to lower-left in Scatter mode
    """
