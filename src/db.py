"""Database manager."""

import sqlite3 as sq


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

    def setup_db(self):
        """Setup the database."""
        if not hasattr(self, 'cursor'):
            return
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS highscores
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )''')

    def get_leaderboard(self, limit: int = 5) -> list[tuple[str, int]]:
        """Return leaderboard sorted from database."""
        if not hasattr(self, 'cursor'):
            return []
        try:
            self.cursor.execute('''
                SELECT name, score
                FROM highscores
                ORDER BY score DESC
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall() or []
        except sq.Error:
            return []

    def add_leaderboard_entry(self, name: str, score: int) -> None:
        """Add a leaderboard entry to database."""
        if not hasattr(self, 'cursor') and not hasattr(self, 'conn'):
            return
        try:
            self.cursor.execute('''
                INSERT INTO highscores
                    (name, score)
                VALUES
                    (?, ?)
            ''', (name, score))
            self.conn.commit()
        except sq.Error:
            print(sq.Error)
            return


def db_init() -> Database:
    """Helper for initializing database."""
    db: Database = Database()
    db.connect_db("database.db")
    db.setup_db()
    return db
