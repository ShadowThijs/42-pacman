"""Main module."""

import sys

from src import Config, Database, Game, db_init


def main():
    """Main function."""
    for s in sys.argv:
        print(s)
    cfg_file: str = sys.argv[1] if len(sys.argv) > 1 else ""
    config: Config = Config(cfg_json=cfg_file)
    db: Database = db_init()
    lb: list[tuple[str, int]] = db.get_leaderboard()
    for entry in lb:
        print(f"Name {entry[0]}: {entry[1]}")
    game: Game = Game()
    game.init_game(800,600)


if __name__ == "__main__":
    main()
