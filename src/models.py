"""Contains all general models."""

import json
import re
from pathlib import Path
from typing import Any, ClassVar


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
        pattern,
        lambda m: m.group("string") or "",
        text, flags=re.VERBOSE
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
    }

    def __init__(self, cfg_json: str) -> None:
        """Init Config."""
        data: dict[str, Any] = {}

        if cfg_json == "":
            print("Missing config.json")
        elif not Path(cfg_json).is_file():
            print(f"Config file not found: {cfg_json}")
        else:
            with open(cfg_json) as f:
                data = json.loads(clean_json(f.read()))

        for key, default in self.DEFAULTS.items():
            value = data.get(key, default)
            if key not in data:
                print(f"Missing '{key}' in config, using default: {default!r}")
            elif not isinstance(value, type(default)):
                print(f"Invalid type for '{key}', using default: {default!r}")
                value = default
            setattr(self, key, value)


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


class Direction:
    """Directions for ghosts and player."""
    North: int = 0x1
    East:  int = 0x2
    South: int = 0x4
    West:  int = 0x8
    All:   int = 0xf
