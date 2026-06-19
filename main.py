"""Main module."""

from src.db import Database


def main():
    """Main function."""
    db: Database = Database()
    db.connect_db("db/database.db")
    db.setup_db()
    print(db.get_leaderboard())
    db.add_leaderboard_entry("thijs", 42069)
    print(db.get_leaderboard())

    print("Hello from 42-pac-man!")


if __name__ == "__main__":
    main()
