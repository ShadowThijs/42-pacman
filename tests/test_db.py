"""Tests for the persistent SQLite highscore system."""

from pathlib import Path

from src import db_init
from src.db import Database
from tests.helpers import make_config


def test_database_persists_scores_across_connections(
    tmp_path: Path,
) -> None:
    """Scores survive closing and reopening the database."""
    path: Path = tmp_path / "scores.db"
    first = Database()
    first.connect_db(str(path))
    first.setup_db()
    assert first.add_leaderboard_entry("ALICE", 123)
    first.close()

    second = Database()
    second.connect_db(str(path))
    second.setup_db()
    assert second.get_leaderboard() == [("ALICE", 123)]
    second.close()


def test_database_keeps_only_top_ten(tmp_path: Path) -> None:
    """Inserting more than ten scores prunes the lowest entries."""
    db = Database()
    db.connect_db(str(tmp_path / "scores.db"))
    db.setup_db()
    for value in range(15):
        assert db.add_leaderboard_entry(f"P{value}", value)
    entries = db.get_leaderboard(20)
    assert len(entries) == 10
    assert entries[0] == ("P14", 14)
    assert entries[-1] == ("P5", 5)
    db.close()


def test_database_sanitizes_names_and_scores(tmp_path: Path) -> None:
    """Invalid name characters are removed and scores never go negative."""
    db = Database()
    db.connect_db(str(tmp_path / "scores.db"))
    db.setup_db()
    assert db.add_leaderboard_entry("a!very-long-name", -25)
    entries = db.get_leaderboard()
    assert len(entries) == 1
    name, score = entries[0]
    assert name == "A VERY LON"
    assert score == 0
    db.close()


def test_database_handles_corrupt_file(tmp_path: Path) -> None:
    """A corrupt file disables the leaderboard without crashing."""
    path: Path = tmp_path / "broken.db"
    path.write_text("not a sqlite database", encoding="utf-8")
    db = Database()
    db.connect_db(str(path))
    db.setup_db()
    assert not db.connected
    assert db.get_leaderboard() == []
    assert not db.add_leaderboard_entry("PLAYER", 10)
    db.close()


def test_db_init_creates_configured_database(tmp_path: Path) -> None:
    """db_init creates the database at the configured path."""
    cfg = make_config(tmp_path)
    db = db_init(cfg)
    assert db.connected
    assert (tmp_path / "scores.db").is_file()
    db.close()


def test_db_init_handles_unwritable_path(tmp_path: Path) -> None:
    """A parent path that is a file disables storage cleanly."""
    blocker: Path = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    cfg = make_config(tmp_path, highscore_db=str(blocker / "scores.db"))
    db = db_init(cfg)
    assert not db.connected
    db.close()
