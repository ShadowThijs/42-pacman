"""Main module."""

import os
import sys
from pathlib import Path

from src import Config, Database, Game, db_init
from src.models import CELL_SIZE
from src.ui.app import App

USAGE: str = "Usage: python3 pac-man.py config.json"


def _packaged_config() -> str:
    """Return a config bundled inside a PyInstaller executable, if any."""
    bundle_root: str | None = getattr(sys, "_MEIPASS", None)
    if bundle_root is None:
        return ""
    candidate: Path = Path(bundle_root) / "config.json"
    return str(candidate) if candidate.is_file() else ""


def config_file(argv: list[str]) -> str | None:
    """Return the config path, or ``None`` when the CLI usage is wrong.

    A source checkout must receive exactly one argument.  A packaged
    build accepts zero arguments and looks beside the executable (or in
    the PyInstaller bundle) so it can be launched with a double click.
    """
    frozen: bool = bool(getattr(sys, "frozen", False))
    args: list[str] = argv[1:]

    if len(args) == 1:
        return args[0]

    if not args and frozen:
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
        return _packaged_config()

    if not args:
        print("Error: missing configuration file.")
    else:
        print("Error: too many arguments.")
    print(USAGE)
    return None


def run_game(cfg_file: str) -> None:
    """Load the configuration and run the application."""
    config: Config = Config(cfg_json=cfg_file)
    db: Database = db_init(config)
    try:
        game: Game = Game()
        width: int = config.width * CELL_SIZE + 100
        height: int = config.height * CELL_SIZE + 80
        game.init_game(width, height, config, db)
        App(game).run()
    finally:
        db.close()


def main() -> int:
    """Program entry point: always return an exit code, never a traceback."""
    cfg_file: str | None = config_file(sys.argv)
    if cfg_file is None:
        return 1

    try:
        run_game(cfg_file)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as exc:
        if os.environ.get("PACMAN_DEBUG") == "1":
            raise
        message: str = str(exc) or type(exc).__name__
        print(f"Error: {message}")
        print("The game could not continue. Check the configuration file.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
