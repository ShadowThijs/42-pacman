"""Application flow: which screen follows which."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.ui.screens import (
    GameScreen,
    InstructionsScreen,
    LeaderboardScreen,
    NameEntryScreen,
    StartMenuScreen,
    VictoryScreen,
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

    def show_start_menu(self, notice: str | None = None) -> None:
        """Replace the stack with the opening screen."""
        self.game.states.reset(
            StartMenuScreen(self.game, self.theme, self, notice)
        )

    def start_game(self) -> None:
        """Start a brand new game session."""
        if not self.game.start_new_game():
            self.show_start_menu(
                self.game.level_error or "COULD NOT START THE GAME"
            )
            return
        self.last_game_frame = None
        self.game.states.reset(
            GameScreen(self.game, self.theme, self)
        )

    def show_instructions(self) -> None:
        """Show the controls and rules screen."""
        self.game.states.reset(
            InstructionsScreen(self.game, self.theme, self)
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

    def show_victory(self) -> None:
        """Show the win prompt after the final level has been cleared."""
        self.game.states.reset(
            VictoryScreen(
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
        """Persist the score, then return to the main menu."""
        actual: int = self.game.score if score is None else score
        saved: bool = self.game.record_score(name, actual)
        notice: str = (
            f"SCORE SAVED {actual:06d}"
            if saved
            else "COULD NOT SAVE SCORE"
        )
        self.show_start_menu(notice)

    def skip_score(self) -> None:
        """Return to the main menu without storing a name."""
        self.show_start_menu()

    def resume(self) -> None:
        """Remove the pause overlay."""
        self.game.states.pop()

    def quit(self) -> None:
        """Stop the main loop."""
        self.game.quit()
