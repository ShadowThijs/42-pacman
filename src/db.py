"""Database manager."""

import os
import sqlite3 as sq
import sys
from pathlib import Path

from .models import Config, sanitize_name


class Database:
    """Database class."""

    def __init__(self) -> None:
        """Init db."""
        self.name: str
        self.conn: sq.Connection
        self.cursor: sq.Cursor

    def connect_db(self, name: str) -> sq.Cursor:
        """Connect to a database."""
        self.name = name
        self.conn = sq.connect(name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def setup_db(self) -> None:
        """Setup the database."""
        if not hasattr(self, "cursor"):
            return
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscores
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )""")

    def get_leaderboard(self, limit: int = 10) -> list[tuple[str, int]]:
        """Return the best ``limit`` scores, sanitised for display."""
        if not hasattr(self, "cursor"):
            return []
        try:
            self.cursor.execute(
                """
                SELECT name, score
                FROM highscores
                ORDER BY score DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = self.cursor.fetchall() or []
        except sq.Error:
            return []
        return [
            (sanitize_name(name) or "PLAYER", max(0, int(score)))
            for name, score in rows
        ]

    def add_leaderboard_entry(self, name: str, score: int) -> None:
        """Add a leaderboard entry, enforcing the name and score rules."""
        if not hasattr(self, "cursor"):
            return
        safe_name: str = sanitize_name(name) or "PLAYER"
        safe_score: int = max(0, int(score))
        try:
            self.cursor.execute(
                """
                INSERT INTO highscores
                    (name, score)
                VALUES
                    (?, ?)
            """,
                (safe_name, safe_score),
            )
            self.conn.commit()
        except sq.Error:
            print(sq.Error)
            return


def _is_frozen() -> bool:
    """Return whether the game runs from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def _user_data_dir() -> Path:
    """Return the per-user directory used by packaged builds."""
    app_name: str = "42-pacman"
    if sys.platform == "win32":
        base: str | None = os.environ.get("APPDATA")
        if base is not None:
            return Path(base) / app_name
        return Path.home() / "AppData" / "Roaming" / app_name
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name
    base = os.environ.get("XDG_DATA_HOME")
    if base is not None:
        return Path(base) / app_name
    return Path.home() / ".local" / "share" / app_name


def _database_path(cfg: Config) -> Path:
    """Resolve the highscore path for source runs and packaged builds."""
    configured: Path = Path(cfg.highscore_db)
    if not _is_frozen() or configured.is_absolute():
        return configured
    return _user_data_dir() / configured.name


def db_init(cfg: Config) -> Database:
    """Open the highscore database, disabling it cleanly on failure."""
    db: Database = Database()
    try:
        path: Path = _database_path(cfg)
        path.parent.mkdir(parents=True, exist_ok=True)
        db.connect_db(str(path))
        db.setup_db()
    except (OSError, sq.Error) as exc:
        print(f"Could not open highscore database: {exc}")
    return db
