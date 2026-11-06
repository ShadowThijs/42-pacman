"""Database manager for persistent highscores."""

import os
import sqlite3 as sq
import sys
from pathlib import Path

from .models import Config, sanitize_name

TOP_SCORES: int = 10


class Database:
    """SQLite-backed highscore storage.

    The class is deliberately tolerant: if the database cannot be
    opened or queried, the game keeps running with an empty leaderboard.
    """

    def __init__(self) -> None:
        """Create a disconnected database wrapper."""
        self.name: str = ""
        self.conn: sq.Connection | None = None
        self.cursor: sq.Cursor | None = None

    @property
    def connected(self) -> bool:
        """Return whether a usable connection is open."""
        return self.conn is not None and self.cursor is not None

    def connect_db(self, name: str) -> sq.Cursor:
        """Connect to a database, replacing any previous connection."""
        self.close()
        self.name = name
        self.conn = sq.connect(name, timeout=5.0)
        self.cursor = self.conn.cursor()
        return self.cursor

    def setup_db(self) -> None:
        """Create the highscore table if it does not exist."""
        if self.conn is None or self.cursor is None:
            return
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS highscores
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL
                )
                """
            )
            self.conn.commit()
        except sq.Error as exc:
            print(f"Could not prepare highscore database: {exc}")
            self.close()

    def get_leaderboard(
        self, limit: int = TOP_SCORES
    ) -> list[tuple[str, int]]:
        """Return the best ``limit`` scores, sanitised for display."""
        if self.conn is None or self.cursor is None:
            return []
        try:
            self.cursor.execute(
                """
                SELECT name, score
                FROM highscores
                ORDER BY score DESC, id ASC
                LIMIT ?
                """,
                (max(0, limit),),
            )
            rows: list[tuple[object, object]] = list(self.cursor.fetchall())
        except sq.Error as exc:
            print(f"Could not read highscore database: {exc}")
            return []
        return [
            (sanitize_name(str(name)) or "PLAYER", self._safe_score(score))
            for name, score in rows
        ]

    def add_leaderboard_entry(self, name: str, score: int) -> bool:
        """Store one score and keep only the top ten entries."""
        if self.conn is None or self.cursor is None:
            return False
        safe_name: str = sanitize_name(name) or "PLAYER"
        safe_score: int = self._safe_score(score)
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
            self.cursor.execute(
                """
                DELETE FROM highscores
                WHERE id NOT IN
                (
                    SELECT id
                    FROM highscores
                    ORDER BY score DESC, id ASC
                    LIMIT ?
                )
                """,
                (TOP_SCORES,),
            )
            self.conn.commit()
        except sq.Error as exc:
            print(f"Could not save highscore: {exc}")
            return False
        return True

    def close(self) -> None:
        """Close the database connection, ignoring shutdown errors."""
        if self.conn is not None:
            try:
                self.conn.close()
            except sq.Error:
                pass
        self.conn = None
        self.cursor = None

    @staticmethod
    def _safe_score(score: object) -> int:
        """Return a non-negative integer, or zero for corrupt data."""
        try:
            value: int = int(str(score))
        except (TypeError, ValueError):
            return 0
        return max(0, value)


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
    except (OSError, ValueError, sq.Error) as exc:
        print(f"Could not open highscore database: {exc}")
        db.close()
    return db
