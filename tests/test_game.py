"""Gameplay, progression, cheats and UI-flow tests."""

from collections.abc import Iterator
from pathlib import Path

import pygame
import pytest

from src import Config, Game
from src.cheats import Cheats
from src.ghost import GhostState
from src.models import Direction, VECTORS, can_move
from src.ui.app import App
from src.ui.screens import (
    GameScreen,
    InstructionsScreen,
    NameEntryScreen,
    PauseMenuScreen,
    StartMenuScreen,
    VictoryScreen,
)
from tests.helpers import make_config, make_game


@pytest.fixture
def session(tmp_path: Path) -> Iterator[tuple[Game, App]]:
    """Start a headless game session and clean up afterwards."""
    config: Config = make_config(tmp_path)
    game, app = make_game(config)
    yield game, app
    if game.db is not None:
        game.db.close()
    game.quit()
    pygame.quit()


def _frame(game: Game) -> None:
    """Advance and draw one frame."""
    game.states.update(0.016)
    game.states.draw(game.screen)


def _key(key: int, unicode: str = "") -> pygame.event.Event:
    """Build a KEYDOWN event."""
    return pygame.event.Event(
        pygame.KEYDOWN, key=key, unicode=unicode, mod=0
    )


def _snapshot(game: Game) -> tuple[object, ...]:
    """Capture everything that identifies the first generated level."""
    return (
        game.current_maze.maze,
        set(game.pacgums),
        set(game.supergums),
        game.player_spawn,
    )


def _start(tmp_path: Path, **overrides: object) -> tuple[Game, App]:
    """Start a game with a custom config for a single test."""
    config: Config = make_config(tmp_path, **overrides)
    return make_game(config)


def _teardown(game: Game) -> None:
    """Release pygame resources for a manually built game."""
    if game.db is not None:
        game.db.close()
    game.quit()
    pygame.quit()


def test_start_uses_configured_level(tmp_path: Path) -> None:
    """The config level value is the first played level."""
    game, _ = _start(tmp_path, level=4, max_levels=6)
    try:
        assert game.level == 4
        assert game.config.max_levels == 6
        assert game.current_maze is not None
    finally:
        _teardown(game)


def test_clamped_maximum_maze_size_starts(tmp_path: Path) -> None:
    """Oversized width and height clamp to a maze the generator can build."""
    game, _ = _start(tmp_path, width=999, height=999)
    try:
        assert len(game.current_maze.maze) == 35
        assert len(game.current_maze.maze[0]) == 35
        assert game.level_error is None
    finally:
        _teardown(game)


def test_first_level_is_deterministic(tmp_path: Path) -> None:
    """The fixed seed produces the same maze and pellets every session."""
    first, _ = _start(tmp_path)
    snapshot = _snapshot(first)
    _teardown(first)

    second, _ = _start(tmp_path)
    try:
        assert _snapshot(second) == snapshot
    finally:
        _teardown(second)


def test_initial_level_contents(session: tuple[Game, App]) -> None:
    """A level starts with pellets, four power pellets and four ghosts."""
    game, _ = session
    assert len(game.pacgums) == game.config.pacgum
    assert len(game.supergums) == 4
    assert (0, 0) in game.supergums
    assert (0, game.config.width - 1) in game.supergums
    assert (game.config.height - 1, 0) in game.supergums
    assert len(game.to_spawn) == 4
    assert game.pac.lives == game.config.lives


def test_eating_pacgum_increases_score(session: tuple[Game, App]) -> None:
    """Eating a normal pellet awards the configured points."""
    game, _ = session
    tile = next(iter(game.pacgums))
    game.pac.respawn(*game._tile_center(*tile))
    game.update(0.016)
    assert (game.pac.row, game.pac.col) == tile
    assert game.score == game.config.pp_pacgum
    assert tile not in game.pacgums


def test_player_cannot_cross_walls(session: tuple[Game, App]) -> None:
    """A blocked direction leaves Pac-Man on its tile."""
    game, _ = session
    row, col = game.player_spawn
    game.pac.respawn(*game._tile_center(row, col))
    blocked: int = next(
        direction
        for direction in (
            Direction.North,
            Direction.East,
            Direction.South,
            Direction.West,
        )
        if not can_move(game.current_maze.maze, row, col, direction)
    )
    game.queue_direction(blocked)
    for _ in range(30):
        game.update(0.016)
    assert (game.pac.row, game.pac.col) == (row, col)


def test_player_moves_through_open_corridor(
    session: tuple[Game, App],
) -> None:
    """An open direction moves Pac-Man out of the starting tile."""
    game, _ = session
    row, col = game.player_spawn
    game.pac.respawn(*game._tile_center(row, col))
    opened: int = next(
        direction
        for direction in (
            Direction.North,
            Direction.East,
            Direction.South,
            Direction.West,
        )
        if can_move(game.current_maze.maze, row, col, direction)
    )
    dc, dr = VECTORS[opened]
    game.queue_direction(opened)
    for _ in range(30):
        game.update(0.016)
    assert (game.pac.row, game.pac.col) != (row, col)
    assert (game.pac.row, game.pac.col) != (row - dr, col - dc)


def test_eating_supergum_increases_score(session: tuple[Game, App]) -> None:
    """Eating a power pellet awards its configured points."""
    game, _ = session
    tile = game.supergums[0]
    game.pac.respawn(*game._tile_center(*tile))
    game.update(0.016)
    assert game.score == game.config.pp_super_pacgum
    assert tile not in game.supergums


def test_frightened_ghost_becomes_edible(session: tuple[Game, App]) -> None:
    """A frighten call marks released ghosts edible and it wears off."""
    game, _ = session
    game.first_input = True
    game.release_ghosts(10.0)
    assert len(game.ghosts) == 4
    ghost = game.ghosts[0]
    ghost.frighten()
    assert ghost.is_frightened()
    ghost.timer = 0.01
    ghost.update(0.02, game.pac, game.ghosts[0])
    assert ghost.state == GhostState.CHASE


def test_frightened_ghost_flees_to_far_corner(
    session: tuple[Game, App],
) -> None:
    """A frightened ghost targets the corner farthest from Pac-Man."""
    game, _ = session
    game.first_input = True
    game.release_ghosts(10.0)
    ghost = game.ghosts[0]
    ghost.frighten()
    target = ghost.target_tile(game.pac, None)
    corners = (
        (0, 0),
        (0, game.config.width - 1),
        (game.config.height - 1, game.config.width - 1),
        (game.config.height - 1, 0),
    )
    farthest: int = max(
        (row - game.pac.row) ** 2 + (col - game.pac.col) ** 2
        for row, col in corners
    )
    target_distance: int = (
        (target.row - game.pac.row) ** 2
        + (target.col - game.pac.col) ** 2
    )
    assert target_distance == farthest


def test_eating_frightened_ghost_scores(session: tuple[Game, App]) -> None:
    """Touching an edible ghost awards points and sends it home."""
    game, _ = session
    game.first_input = True
    game.release_ghosts(10.0)
    ghost = game.ghosts[0]
    ghost.frighten()
    ghost.row = game.pac.row
    ghost.col = game.pac.col
    ghost.progress = 0.0
    ghost.direction = None
    ghost._sync_geometry()
    game.update(0.016)
    assert game.score >= game.config.pp_ghost
    assert ghost.state == GhostState.DEAD_PATHING


def test_ghost_collision_costs_life_and_respawns(
    session: tuple[Game, App],
) -> None:
    """A normal ghost takes a life and Pac-Man returns to the centre."""
    game, _ = session
    game.first_input = True
    game.release_ghosts(10.0)
    ghost = game.ghosts[0]
    ghost.state = GhostState.CHASE
    ghost.resume_state = GhostState.CHASE
    ghost.timer = 0.0
    ghost.row = game.pac.row
    ghost.col = game.pac.col
    ghost.progress = 0.0
    ghost.direction = None
    ghost._sync_geometry()
    lives: int = game.pac.lives
    game.update(0.016)
    assert game.pac.lives == lives - 1
    assert (game.pac.row, game.pac.col) == game.player_spawn
    assert not game.game_over


def test_eaten_ghost_respawns(session: tuple[Game, App]) -> None:
    """Eyes reach their corner, wait, and return to the chase."""
    game, _ = session
    game.first_input = True
    game.release_ghosts(10.0)
    ghost = game.ghosts[0]
    ghost.state = GhostState.DEAD_PATHING
    ghost.row = ghost.spawn_pos.row
    ghost.col = ghost.spawn_pos.col
    ghost.progress = 0.0
    ghost.direction = None
    ghost._sync_geometry()
    ghost.update(0.016, game.pac, game.ghosts[0])
    assert ghost.state == GhostState.DEAD_WAITING
    for _ in range(400):
        ghost.update(0.016, game.pac, game.ghosts[0])
    final_state: GhostState = ghost.state
    assert final_state == GhostState.CHASE


def test_level_advance_keeps_score_and_lives(
    session: tuple[Game, App],
) -> None:
    """Completing all pellets advances the level without resetting stats."""
    game, _ = session
    game.score = 123
    lives: int = game.pac.lives
    game.pacgums.clear()
    game.supergums.clear()
    game.update(0.0)
    assert game.level == 2
    assert game.score == 123
    assert game.pac.lives == lives
    assert game.level_time_left == game.config.level_max_time


def test_victory_after_final_level(tmp_path: Path) -> None:
    """Clearing the configured last level wins the game."""
    game, _ = _start(tmp_path, level=2, max_levels=2)
    try:
        game.pacgums.clear()
        game.supergums.clear()
        game.update(0.0)
        assert game.victory
    finally:
        _teardown(game)


def test_timer_expiry_costs_a_life(session: tuple[Game, App]) -> None:
    """Running out of time respawns the player with one life fewer."""
    game, _ = session
    game.pac.lives = 2
    game.first_input = True
    game.level_time_left = 0.001
    game.update(0.02)
    assert game.pac.lives == 1
    assert not game.game_over
    assert game.level_time_left == game.config.level_max_time


def test_timer_expiry_on_last_life_ends_game(
    session: tuple[Game, App],
) -> None:
    """Running out of time with no lives left is a game over."""
    game, _ = session
    game.pac.lives = 1
    game.first_input = True
    game.level_time_left = 0.001
    game.update(0.02)
    assert game.pac.lives == 0
    assert game.game_over


def test_invincible_cheat_prevents_timer_death(
    session: tuple[Game, App],
) -> None:
    """Invincibility keeps the player alive when the timer expires."""
    game, _ = session
    game.cheats.invincible(True)
    game.pac.lives = 1
    game.first_input = True
    game.level_time_left = 0.001
    game.update(0.02)
    assert game.pac.lives == 1
    assert not game.game_over


def test_cheat_keys_enable_and_apply(session: tuple[Game, App]) -> None:
    """The in-game cheat keys activate cheats and add lives."""
    game, _ = session
    lives: int = game.pac.lives
    game.states.handle_event(_key(pygame.K_4, "4"))
    assert game.cheats.enabled
    assert game.pac.lives == lives + 1
    game.states.handle_event(_key(pygame.K_1, "1"))
    assert game.cheats.invincible()


def test_ui_screens_render(session: tuple[Game, App]) -> None:
    """Every menu and overlay draws without raising."""
    game, app = session
    app.show_start_menu()
    _frame(game)
    assert isinstance(game.states.current, StartMenuScreen)

    app.show_instructions()
    _frame(game)
    assert isinstance(game.states.current, InstructionsScreen)

    app.show_leaderboard()
    _frame(game)

    app.start_game()
    _frame(game)
    assert isinstance(game.states.current, GameScreen)

    game.states.handle_event(_key(pygame.K_p, "p"))
    _frame(game)
    assert isinstance(game.states.current, PauseMenuScreen)
    app.resume()
    assert isinstance(game.states.current, GameScreen)

    app.show_victory()
    _frame(game)
    assert isinstance(game.states.current, VictoryScreen)

    app.game_over()
    _frame(game)
    assert isinstance(game.states.current, NameEntryScreen)


def test_submitting_score_returns_to_main_menu(
    session: tuple[Game, App],
) -> None:
    """Saving a score persists it and returns to the main menu."""
    game, app = session
    app.submit_score("asylla", 321)
    assert isinstance(game.states.current, StartMenuScreen)
    assert game.db is not None
    assert game.db.get_leaderboard() == [("ASYLLA", 321)]


def test_name_entry_limits_length(session: tuple[Game, App]) -> None:
    """The name prompt accepts at most ten alphanumeric characters."""
    game, app = session
    app.game_over()
    for char in "abcdefghijklmnop":
        game.states.handle_event(_key(0, char))
    screen = game.states.current
    assert isinstance(screen, NameEntryScreen)
    assert len(screen.name) == 10
    game.states.handle_event(_key(pygame.K_RETURN, "\r"))
    assert isinstance(game.states.current, StartMenuScreen)


def test_cheats_class_toggles() -> None:
    """Cheat flags start disabled and toggle independently."""
    cheats = Cheats()
    assert not cheats.enabled
    assert cheats.activate()
    assert not cheats.activate()
    cheats.invincible(True)
    cheats.speedhack(True)
    cheats.ghostfreeze(True)
    assert cheats.invincible()
    assert cheats.speedhack()
    assert cheats.ghostfreeze()
