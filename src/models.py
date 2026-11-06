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
ANIMATION_FRAME_TIME: float = 0.2
MAX_NAME_LENGTH: int = 10
ALLOWED_NAME_CHARS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

DEFAULT_HIGHSCORE_DB: str = "database.db"
DEFAULT_LEVEL: int = 1
DEFAULT_WIDTH: int = 20
DEFAULT_HEIGHT: int = 20
DEFAULT_LIVES: int = 3
DEFAULT_PACGUM: int = 42
DEFAULT_POINTS_PER_PACGUM: int = 10
DEFAULT_POINTS_PER_SUPER_PACGUM: int = 50
DEFAULT_POINTS_PER_GHOST: int = 200
DEFAULT_SEED: int = 42
DEFAULT_LEVEL_MAX_TIME: int = 300
DEFAULT_MAX_LEVELS: int = 10

MIN_MAZE_SIZE: int = 5
MAX_MAZE_SIZE: int = 35
MIN_LIVES: int = 1
MAX_LIVES: int = 99
MIN_LEVEL_MAX_TIME: int = 1
MAX_LEVEL_MAX_TIME: int = 3600
MAX_LEVELS_LIMIT: int = 100
MAX_POINTS: int = 1_000_000
MAX_PACGUM: int = 1_000_000
MIN_SEED: int = 1
MAX_SEED: int = 2_147_483_647


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


def sanitize_name(name: str) -> str:
    """Return a leaderboard-safe version of ``name``.

    Names are uppercased and limited to :data:`MAX_NAME_LENGTH`
    characters.  Only characters in :data:`ALLOWED_NAME_CHARS` are kept;
    anything else becomes a separator.  Repeated and leading/trailing
    spaces are collapsed away.  An empty result means the name should be
    treated as missing.
    """
    cleaned: str = "".join(
        char if char in ALLOWED_NAME_CHARS else " " for char in name.upper()
    )
    return " ".join(cleaned.split())[:MAX_NAME_LENGTH]


class Config:
    """Config class.

    Holds all config file values.  Values are validated and clamped so a
    malformed file never stops the game from starting.
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
    max_levels: int

    DEFAULTS: ClassVar[dict[str, Any]] = {
        "highscore_db": DEFAULT_HIGHSCORE_DB,
        "level": DEFAULT_LEVEL,
        "width": DEFAULT_WIDTH,
        "height": DEFAULT_HEIGHT,
        "lives": DEFAULT_LIVES,
        "pacgum": DEFAULT_PACGUM,
        "pp_pacgum": DEFAULT_POINTS_PER_PACGUM,
        "pp_super_pacgum": DEFAULT_POINTS_PER_SUPER_PACGUM,
        "pp_ghost": DEFAULT_POINTS_PER_GHOST,
        "seed": DEFAULT_SEED,
        "level_max_time": DEFAULT_LEVEL_MAX_TIME,
        "max_levels": DEFAULT_MAX_LEVELS,
    }
    LIMITS: ClassVar[dict[str, tuple[int, int]]] = {
        "level": (1, MAX_LEVELS_LIMIT),
        "width": (MIN_MAZE_SIZE, MAX_MAZE_SIZE),
        "height": (MIN_MAZE_SIZE, MAX_MAZE_SIZE),
        "lives": (MIN_LIVES, MAX_LIVES),
        "pacgum": (0, MAX_PACGUM),
        "pp_pacgum": (0, MAX_POINTS),
        "pp_super_pacgum": (0, MAX_POINTS),
        "pp_ghost": (0, MAX_POINTS),
        "seed": (MIN_SEED, MAX_SEED),
        "level_max_time": (MIN_LEVEL_MAX_TIME, MAX_LEVEL_MAX_TIME),
        "max_levels": (1, MAX_LEVELS_LIMIT),
    }

    def __init__(self, cfg_json: str) -> None:
        """Init Config."""
        data, loaded = self._read(cfg_json)

        for key in sorted(set(data) - set(self.DEFAULTS)):
            print(f"Ignoring unknown config key: {key!r}")

        values: dict[str, Any] = {}
        for key, default in self.DEFAULTS.items():
            if key not in data:
                if loaded:
                    print(
                        f"Missing '{key}' in config, "
                        f"using default: {default!r}"
                    )
                values[key] = default
                continue
            values[key] = self._validated(key, data[key], default)

        max_levels: int = int(values["max_levels"])
        level: int = int(values["level"])
        if level > max_levels:
            print(
                f"Clamped 'level' from {level} to {max_levels} "
                "(cannot exceed 'max_levels')"
            )
            level = max_levels

        self.highscore_db = str(values["highscore_db"])
        self.level = level
        self.width = int(values["width"])
        self.height = int(values["height"])
        self.lives = int(values["lives"])
        self.pacgum = int(values["pacgum"])
        self.pp_pacgum = int(values["pp_pacgum"])
        self.pp_super_pacgum = int(values["pp_super_pacgum"])
        self.pp_ghost = int(values["pp_ghost"])
        self.seed = int(values["seed"])
        self.level_max_time = int(values["level_max_time"])
        self.max_levels = max_levels

    @staticmethod
    def _read(cfg_json: str) -> tuple[dict[str, Any], bool]:
        """Read and parse ``cfg_json``, reporting every failure clearly."""
        if cfg_json == "":
            print(
                "Warning: no config file provided; using built-in defaults",
                flush=True,
            )
            return {}, False

        path: Path = Path(cfg_json)
        if not path.is_file():
            print(
                f"Warning: config file not found: {cfg_json}; "
                "using built-in defaults",
                flush=True,
            )
            return {}, False

        try:
            with open(path, encoding="utf-8-sig") as handle:
                parsed: Any = json.loads(clean_json(handle.read()))
        except (OSError, ValueError) as exc:
            print(
                f"Warning: could not read config {cfg_json}: {exc}; "
                "using built-in defaults",
                flush=True,
            )
            return {}, False

        if not isinstance(parsed, dict):
            print(
                f"Warning: invalid config {cfg_json}: root must be a "
                "JSON object; using built-in defaults",
                flush=True,
            )
            return {}, False
        return {str(key): value for key, value in parsed.items()}, True

    @classmethod
    def _validated(cls, key: str, value: Any, default: Any) -> Any:
        """Return a safe value for ``key``, or ``default`` if unusable."""
        if key == "highscore_db":
            if not isinstance(value, str) or not value.strip():
                print(
                    f"Invalid value for '{key}', using default: {default!r}"
                )
                return default
            return value.strip()

        if isinstance(value, bool) or not isinstance(value, int):
            print(f"Invalid type for '{key}', using default: {default!r}")
            return default

        limits: tuple[int, int] | None = cls.LIMITS.get(key)
        if limits is not None:
            low, high = limits
            if not low <= value <= high:
                clamped: int = max(low, min(high, value))
                print(
                    f"Invalid value for '{key}': {value!r}; "
                    f"clamped to {clamped}"
                )
                return clamped
        return value


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


# (column, row) deltas for each direction bit.
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

# Classic Pac-Man tie-break order when several routes are equally short.
DIRECTION_ORDER: tuple[int, ...] = (
    Direction.North,
    Direction.West,
    Direction.South,
    Direction.East,
)


def can_move(
    maze: list[list[int]],
    row: int,
    col: int,
    direction: int,
) -> bool:
    """Return whether (row, col) has no wall on ``direction``'s side."""
    if not (0 <= row < len(maze) and 0 <= col < len(maze[0])):
        return False
    return (maze[row][col] & direction) == 0


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
