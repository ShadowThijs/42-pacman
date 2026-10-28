"""Application flow: which screen follows which."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.ui.screens import (
    GameScreen,
    LeaderboardScreen,
    NameEntryScreen,
    StartMenuScreen,
)
from src.ui.theme import Theme

if TYPE_CHECKING:
    from src.game import Game


class App:
    """Own the shared theme and the transitions between screens."""

    def __init__(self, game: Game) -> None:
        """Create the app around an initialised :class:`Game`."""
        self.game: Game = game
        self.theme: Theme = Theme()
        self.last_game_frame: pg.Surface | None = None

    def run(self) -> None:
        """Open the main menu and start the main loop."""
        self.show_start_menu()
        self.game.run()

    def show_start_menu(self) -> None:
        """Replace the stack with the opening screen."""
        self.game.states.reset(
            StartMenuScreen(self.game, self.theme, self)
        )

    def start_game(self) -> None:
        """Start a brand new game session."""
        self.game.start_new_game()
        self.last_game_frame = None
        self.game.states.reset(
            GameScreen(self.game, self.theme, self)
        )

    def show_leaderboard(
        self,
        highlight: tuple[str, int] | None = None,
        new_score: int | None = None,
    ) -> None:
        """Show the database-backed leaderboard."""
        self.game.states.reset(
            LeaderboardScreen(
                self.game,
                self.theme,
                self,
                highlight,
                new_score,
            )
        )

    def game_over(self) -> None:
        """Show the name prompt after the death animation."""
        self.game.states.reset(
            NameEntryScreen(
                self.game,
                self.theme,
                self,
                self.game.score,
                self.last_game_frame,
            )
        )

    def finish_death(self) -> None:
        """Resume the frozen game after a non-final death."""
        self.game.states.pop()

    def submit_score(self, name: str, score: int | None = None) -> None:
        """Persist the score, then show it on the leaderboard."""
        actual: int = self.game.score if score is None else score
        self.game.record_score(name, actual)
        self.show_leaderboard((name, actual), actual)

    def skip_score(self) -> None:
        """Open the leaderboard without storing a name."""
        self.show_leaderboard()

    def resume(self) -> None:
        """Remove the pause overlay."""
        self.game.states.pop()

    def quit(self) -> None:
        """Stop the main loop."""
        self.game.quit()
