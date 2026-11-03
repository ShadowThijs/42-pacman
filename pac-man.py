"""Main module."""

import sys
from pathlib import Path

from src import Config, Database, Game, db_init
from src.models import CELL_SIZE
from src.ui.app import App


def config_file() -> str:
    """Return the CLI config, or one placed beside a packaged build."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    if not getattr(sys, "frozen", False):
        return ""

    executable_dir: Path = Path(sys.executable).resolve().parent
    candidates: list[Path] = [executable_dir / "config.json"]
    if (
        sys.platform == "darwin"
        and executable_dir.parent.name == "Contents"
        and executable_dir.parent.parent.suffix == ".app"
    ):
        candidates.append(executable_dir.parents[2] / "config.json")

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return ""


def main() -> None:
    """Main function."""
    cfg_file: str = config_file()
    config: Config = Config(cfg_json=cfg_file)
    db: Database = db_init(config)
    game: Game = Game()
    width: int = config.width * CELL_SIZE + 100
    height: int = config.height * CELL_SIZE + 80
    game.init_game(width, height, config, db)
    App(game).run()


if __name__ == "__main__":
    main()
