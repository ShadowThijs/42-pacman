"""Shared helpers for the test suite."""

from __future__ import annotations

import json
from pathlib import Path

from src import Config, Game, db_init
from src.models import CELL_SIZE
from src.ui.app import App

DEFAULT_CONFIG: dict[str, object] = {
    "highscore_db": "scores.db",
    "level": 1,
    "width": 15,
    "height": 15,
    "lives": 3,
    "pacgum": 20,
    "pp_pacgum": 10,
    "pp_super_pacgum": 50,
    "pp_ghost": 200,
    "seed": 42,
    "level_max_time": 60,
    "max_levels": 10,
}


def make_config(tmp_path: Path, **overrides: object) -> Config:
    """Write a complete config file in ``tmp_path`` and load it."""
    data: dict[str, object] = dict(DEFAULT_CONFIG)
    data["highscore_db"] = str(tmp_path / "scores.db")
    data.update(overrides)
    path: Path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return Config(str(path))


def make_game(config: Config) -> tuple[Game, App]:
    """Initialise a game and start a fresh session in it."""
    db = db_init(config)
    game = Game()
    game.init_game(
        config.width * CELL_SIZE + 100,
        config.height * CELL_SIZE + 80,
        config,
        db,
    )
    app = App(game)
    app.show_start_menu()
    app.start_game()
    return game, app
