"""Main module."""

import sys

from src import Config, Database, Game, db_init
from src.models import CELL_SIZE
from src.ui.app import App


def main() -> None:
    """Main function."""
    cfg_file: str = sys.argv[1] if len(sys.argv) > 1 else ""
    config: Config = Config(cfg_json=cfg_file)
    db: Database = db_init(config)
    game: Game = Game()
    width: int = config.width * CELL_SIZE + 100
    height: int = config.height * CELL_SIZE + 80
    game.init_game(width, height, config, db)
    App(game).run()


if __name__ == "__main__":
    main()
