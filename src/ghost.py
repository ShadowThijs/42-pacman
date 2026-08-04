"""Ghost class."""

from .models import Direction


class Ghost:
    """Ghost player class."""

    def __init__(self) -> None:
        """Initialize."""
        self.x: int
        self.y: int
        self.direction: Direction


"""Ghost behaviour.

Blinky (red):
- Follows Pac-Man directly (shortest path to Pac-Man)
- Upper-right corner during Scatter mode (super pacgum eaten)

Inky (cyan):
- Target is relative to both Blinky and Pac-Man,
  where the distance Blinky is from Pinky's
  target is doubled to get Inky's target
- Lower-right corner during Scatter mode (super pacgum eaten)

Pinky (pink):
- Targets the spot 2 Pac-Dots in front of Pac-Man
- When Pac-Man faces up, will target spot 2 Pac-Dots in front and 2 to the left
- Upper-left during Scatter mode

Clyde (orange):
- Follows Pac-Man directly,
  tries to head to Scatter corner when within 8-dot radius of Pac-Man
- Lower-left during Scatter mode
"""
