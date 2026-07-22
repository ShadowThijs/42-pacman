"""Contains all general models."""

import json
import re
from pathlib import Path


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
    return re.sub(pattern, lambda m: m.group("string") or "", text, flags=re.VERBOSE)

class Config:
    """Config class.

    Holds all config file values.
    """

    def __init__(self, cfg_json: str) -> None:
        """Init Config."""
        file_dir: Path = Path(__file__).parent.parent
        if cfg_json == "":
            print("Missing config.json")
            self.highscore_db:      str = "database.db"
            self.level:             int = 1
            self.width:             int = 20
            self.height:            int = 20
            self.lives:             int = 3
            self.pacgum:            int = 42
            self.pp_pacgum:         int = 10
            self.pp_super_pacgum:   int = 50
            self.pp_ghost:          int = 200
            self.seed:              int = 42
            self.leve_max_time:     int = 90
        else:
            with open(cfg_json) as f:
                d = json.loads(clean_json(f.read()))
                print(d)
