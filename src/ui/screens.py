"""Screens."""

from collections.abc import Callable
from typing import Any

import pygame as pg

from src import Game
from src.state import State
from src.ui.components import Button
from src.ui.theme import Theme

SELECT_HINT: str = "↑/↓ select | Enter confirm"


class MenuScreen(State):
    """Shared class for menus."""

    fills_background: bool = True

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        game: Game,
        theme: Theme,
        title: str,
        items: list[tuple[str, Callable[[], None]]],
        body_lines: str | None = None,
        footer: str | None = None
    ) -> None:
        """Init."""
        super().__init__(title, game)
        self.theme: Theme = theme
        self.title: str = title
        self.items: list[tuple[str, Callable[[], None]]] = items
        self.body_lines: str | None = body_lines
        self.footer: str = SELECT_HINT if footer is None else footer
        self.selected_index: int = 0
        self.buttons: list[Button] = self._build_buttons()
        self._layout_size: tuple[int, int] | None = None
        self._layout(self.game.screen.get_size())

    def _build_buttons(self) -> list[Button]:
        """Build one button per item; _layout positions them."""
        return [
            Button(
                text,
                self.theme.button_font,
                (0, 0),
                on_click=on_click,
                size=self.theme.button_size,
            )
            for text, on_click in self.items
        ]

    def _layout(self, size: tuple[int, int]) -> None:
        """Re-center the buttons for the current window size."""
        if size == self._layout_size:
            return
        self._layout_size = size
        ys: list[int] = self.theme.centered_column(
            len(self.items),
            self.theme.button_size[1],
            self.theme.button_gap,
            size[1],
        )
        for button, y in zip(self.buttons, ys, strict=True):
            button.rect.center = (size[0] // 2, y)

    def _move(self, step: int) -> None:
        """Move the selection, wrapping around."""
        if not self.items:
            return
        self.selected_index = (
            self.selected_index + step
        ) % len(self.items)
        for button in self.buttons:
            button.hovered = False

    def _activate(self) -> None:
        """Run the selected item's callback."""
        if self.items:
            self.items[self.selected_index][1]()

    def handle_event(self, event: Any) -> None:
        """Handle keyboard and mouse input."""
        self._layout(self.game.screen.get_size())
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_DOWN, pg.K_s):
                self._move(1)
            elif event.key in (pg.K_UP, pg.K_w):
                self._move(-1)
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
                self._activate()
        elif event.type == pg.MOUSEMOTION:
            for index, button in enumerate(self.buttons):
                button.handle_event(event)
                if button.hovered:
                    self.selected_index = index
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt: float) -> None:
        """Menus have no state to update."""

    def _draw_body(self, screen: pg.Surface) -> None:
        """Draw the optional body lines under the title."""
        if not self.body_lines:
            return
        y: int = (
            self.theme.title_top
            + self.theme.title_font.get_height()
            + 16
        )
        for line in self.body_lines.splitlines():
            surface: pg.Surface = self.theme.body_font.render(
                line, True, self.theme.text_color
            )
            screen.blit(
                surface,
                surface.get_rect(
                    midtop=(screen.get_width() // 2, y)
                ),
            )
            y += self.theme.body_font.get_height() + 6

    def draw(self, screen: pg.Surface) -> None:
        """Draw the menu."""
        self._layout(screen.get_size())
        if self.fills_background:
            screen.fill(self.theme.background)
        else:
            self.theme.draw_dim_overlay(screen)
        self.theme.draw_title(screen, self.title)
        self._draw_body(screen)
        for index, button in enumerate(self.buttons):
            button.selected = index == self.selected_index
            button.draw(screen)
        if self.footer:
            self.theme.draw_footer(screen, self.footer)


class StartMenuScreen(MenuScreen):
    """Start menu screen."""

    def __init__(
        self,
        game: Game,
        theme: Theme,
        on_play: Callable[[], None]
    ) -> None:
        """Init."""
        super().__init__(
            game,
            theme,
            "42PACMAN",
            [("PLAY", on_play), ("QUIT", game.quit)],
        )


class PauseMenuScreen(MenuScreen):
    """Pause overlay drawn on top of the frozen game."""

    fills_background = False

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        game: Game,
        theme: Theme,
        on_resume: Callable[[], None],
        on_restart: Callable[[], None],
        on_quit: Callable[[], None],
        background: pg.Surface | None = None
    ) -> None:
        """Init."""
        self._on_resume: Callable[[], None] = on_resume
        self.background: pg.Surface | None = background
        super().__init__(
            game,
            theme,
            "PAUSED",
            [
                ("RESUME", on_resume),
                ("RESTART", on_restart),
                ("QUIT", on_quit),
            ],
            footer="Esc / P resume",
        )

    def handle_event(self, event: Any) -> None:
        """Handle pause shortcuts before ordinary menu input."""
        if event.type == pg.KEYDOWN and event.key in (pg.K_ESCAPE, pg.K_p):
            self._on_resume()
            return
        super().handle_event(event)

    def draw(self, screen: pg.Surface) -> None:
        """Draw the frozen frame, then the pause menu over it."""
        if self.background is not None:
            if self.background.get_size() != screen.get_size():
                self.background = pg.transform.smoothscale(
                    self.background, screen.get_size()
                )
            screen.blit(self.background, (0, 0))
        super().draw(screen)


class DeathScreen(MenuScreen):
    """Death screen."""

    def __init__(
        self,
        game: Game,
        theme: Theme,
        score: int,
        on_retry: Callable[[], None],
        on_menu: Callable[[], None]
    ) -> None:
        """Init."""
        super().__init__(
            game,
            theme,
            "GAME OVER",
            [
                ("RETRY", on_retry),
                ("MAIN MENU", on_menu),
                ("QUIT", game.quit),
            ],
            body_lines=f"Score: {score}",
        )
