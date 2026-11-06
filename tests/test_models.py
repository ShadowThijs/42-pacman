"""Unit tests for configuration and shared models."""

from pathlib import Path

import pytest

from src.models import (
    DEFAULT_LEVEL_MAX_TIME,
    MAX_NAME_LENGTH,
    Config,
    clean_json,
    sanitize_name,
)


def test_clean_json_removes_all_supported_comments() -> None:
    """Hash, slash and block comments are stripped."""
    text: str = """
    {
        # hash comment
        // slash comment
        /* block
           comment */
        "value": 42
    }
    """
    cleaned: str = clean_json(text)
    assert "comment" not in cleaned
    assert '"value": 42' in cleaned


def test_clean_json_keeps_comment_markers_inside_strings() -> None:
    """URLs and hash characters inside JSON strings survive."""
    text: str = '{"url": "https://example.com/#section"}'
    assert clean_json(text) == text


def test_sanitize_name_uppercases_and_filters() -> None:
    """Names allow only letters, digits and spaces."""
    assert sanitize_name("hello!") == "HELLO"
    assert sanitize_name("  a   b  ") == "A B"
    assert sanitize_name("abc_123") == "ABC 123"


def test_sanitize_name_truncates_to_ten_characters() -> None:
    """The leaderboard never stores more than ten characters."""
    assert len(sanitize_name("abcdefghijklmnop")) == MAX_NAME_LENGTH


def test_config_defaults_when_file_is_missing(tmp_path: Path) -> None:
    """A missing file falls back to every documented default."""
    cfg = Config(str(tmp_path / "does-not-exist.json"))
    assert cfg.level == 1
    assert cfg.level_max_time == DEFAULT_LEVEL_MAX_TIME
    assert cfg.max_levels == 10
    assert cfg.lives == 3


def test_config_uses_configured_level(tmp_path: Path) -> None:
    """The configured starting level is used instead of always level 1."""
    path: Path = tmp_path / "config.json"
    path.write_text(
        '{"level": 4, "max_levels": 6, "width": 10, "height": 10}',
        encoding="utf-8",
    )
    cfg = Config(str(path))
    assert cfg.level == 4
    assert cfg.max_levels == 6


def test_config_level_is_clamped_to_max_levels(tmp_path: Path) -> None:
    """A starting level beyond the final level is clamped."""
    path: Path = tmp_path / "config.json"
    path.write_text(
        '{"level": 99, "max_levels": 3}', encoding="utf-8"
    )
    cfg = Config(str(path))
    assert cfg.level == 3
    assert cfg.max_levels == 3


def test_config_invalid_types_and_values_are_safe(tmp_path: Path) -> None:
    """Wrong types fall back to defaults and numbers are clamped."""
    path: Path = tmp_path / "config.json"
    path.write_text(
        """
        {
            "lives": true,
            "width": 999,
            "height": -4,
            "pacgum": -2,
            "pp_ghost": -50,
            "seed": 0,
            "level_max_time": 0,
            "highscore_db": ""
        }
        """,
        encoding="utf-8",
    )
    cfg = Config(str(path))
    assert cfg.lives == 3
    assert cfg.width == 50
    assert cfg.height == 5
    assert cfg.pacgum == 0
    assert cfg.pp_ghost == 0
    assert cfg.seed == 1
    assert cfg.level_max_time == 1
    assert cfg.highscore_db == "database.db"


def test_config_unknown_keys_are_ignored(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Unknown keys are reported and otherwise ignored."""
    path: Path = tmp_path / "config.json"
    path.write_text(
        '{"unknown_key": 123, "lives": 5}', encoding="utf-8"
    )
    cfg = Config(str(path))
    assert cfg.lives == 5
    assert "unknown_key" in capsys.readouterr().out


def test_config_invalid_json_uses_defaults(tmp_path: Path) -> None:
    """Broken JSON never raises; defaults keep the game running."""
    path: Path = tmp_path / "config.json"
    path.write_text("this is not json", encoding="utf-8")
    cfg = Config(str(path))
    assert cfg.level == 1
    assert cfg.width == 20


def test_config_root_must_be_an_object(tmp_path: Path) -> None:
    """A JSON array is rejected without an exception."""
    path: Path = tmp_path / "config.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    cfg = Config(str(path))
    assert cfg.max_levels == 10
