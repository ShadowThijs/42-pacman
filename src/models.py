"""Contains all general models."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

CELL_SIZE: int = 36
WALL_THICKNESS: int = 2
OFFSET: tuple[int, int] = (50, 50)

# Seconds after Pac-Man's first input at which each ghost is released:
# Blinky (red), Pinky (pink), Inky (cyan), Clyde (orange).
DEFAULT_GHOST_RELEASE_DELAYS: list[float] = [0.0, 2.0, 4.0, 6.0]


def clean_json(text: str) -> str:
    """Strip #, // and /* */ comments from JSON text."""
    pattern = r"""
        (?P<comment>
            /\*[\s\S]*?\*/
          | //[^\n\r]*
          | \#[^\n\r]*
        )
      | (?P<string>
            "(?:\\.|[^"\\])*"
        )
    """
    return re.sub(
        pattern, lambda m: m.group("string") or "", text, flags=re.VERBOSE
    )


class Config:
    """Config class.

    Holds all config file values.
    """

    highscore_db: str
    level: int
    width: int
    height: int
    lives: int
    pacgum: int
    pp_pacgum: int
    pp_super_pacgum: int
    pp_ghost: int
    seed: int
    level_max_time: int
    ghost_release_delays: list[float]

    DEFAULTS: ClassVar[dict[str, Any]] = {
        "highscore_db": "database.db",
        "level": 1,
        "width": 20,
        "height": 20,
        "lives": 3,
        "pacgum": 42,
        "pp_pacgum": 10,
        "pp_super_pacgum": 50,
        "pp_ghost": 200,
        "seed": 42,
        "level_max_time": 90,
        "ghost_release_delays": DEFAULT_GHOST_RELEASE_DELAYS,
    }

    def __init__(self, cfg_json: str) -> None:
        """Init Config."""
        data: dict[str, Any] = {}
        loaded: bool = False

        if cfg_json == "":
            print("No config file provided, using defaults")
        elif not Path(cfg_json).is_file():
            print(
                f"Config file not found: {cfg_json}, using defaults"
            )
        else:
            with open(cfg_json) as f:
                data = json.loads(clean_json(f.read()))
            loaded = True

        for key, default in self.DEFAULTS.items():
            value = data.get(key, default)
            if loaded and key not in data:
                print(f"Missing '{key}' in config, using default: {default!r}")
            elif loaded and not isinstance(value, type(default)):
                print(f"Invalid type for '{key}', using default: {default!r}")
                value = default
            setattr(self, key, value)

        self.ghost_release_delays = self._release_delays()

    def _release_delays(self) -> list[float]:
        """Return a validated four-ghost release schedule."""
        delays = self.ghost_release_delays
        valid: bool = (
            isinstance(delays, list)
            and len(delays) == 4
            and all(
                isinstance(d, (int, float))
                and not isinstance(d, bool)
                and d >= 0
                for d in delays
            )
            and all(
                earlier <= later
                for earlier, later in zip(delays, delays[1:])
            )
        )
        if not valid:
            print(
                "Invalid 'ghost_release_delays', using default: "
                f"{DEFAULT_GHOST_RELEASE_DELAYS!r}"
            )
            return list(DEFAULT_GHOST_RELEASE_DELAYS)
        return [float(d) for d in delays]


class Colors:
    """Color transformation."""

    red = (255, 0, 0)
    orange = (255, 128, 0)
    yellow = (255, 255, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    indigo = (75, 0, 130)
    violet = (148, 0, 211)
    white = (255, 255, 255)
    black = (0, 0, 0)
    purple = (128, 0, 128)
    cyan = (0, 255, 255)
    lime = (137, 243, 54)
    magenta = (139, 0, 139)
    brown = (64, 32, 0)
    gold = (255, 215, 0)
    maroon = (128, 0, 0)
    darkred = (139, 0, 0)
    crimson = (220, 20, 60)

    muted = (170, 170, 190)

    base_button = (30, 30, 60)
    hover_button = (70, 70, 140)
    border_button = (90, 90, 120)


class Direction:
    """Directions for ghosts and player."""

    North: int = 0x1
    East: int = 0x2
    South: int = 0x4
    West: int = 0x8
    All: int = 0xF


@dataclass(frozen=True)
class Position:
    """2D grid coordinate (row, col) with pixel x/y accessors.

    The maze is indexed as ``maze[row][col]``, so a Position's ``row``
    is the y-axis and its ``col`` is the x-axis. Use ``.x``/``.y`` or
    :meth:`from_xy` when working with pixel-style (x, y) coordinates.
    """

    row: int = 0
    col: int = 0

    @property
    def x(self) -> int:
        """Pixel x coordinate (the column)."""
        return self.col

    @property
    def y(self) -> int:
        """Pixel y coordinate (the row)."""
        return self.row

    @classmethod
    def from_xy(cls, x: int, y: int) -> Position:
        """Build a Position from (x, y) coordinates (column, row)."""
        return cls(y, x)

    def __repr__(self) -> str:
        """Return representation."""
        return f"Position(row={self.row}, col={self.col})"
