"""Database manager."""

import sqlite3 as sq

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


def db_init(cfg: Config) -> Database:
    """Helper for initializing database."""
    db: Database = Database()
    db.connect_db(cfg.highscore_db)
    db.setup_db()
    return db
