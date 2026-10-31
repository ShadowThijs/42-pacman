"""Arcade screens shown by the state manager."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame as pg

from src.models import CELL_SIZE, OFFSET, Colors, Direction
from src.state import State
from src.ui.components import Button
from src.ui.theme import Theme

if TYPE_CHECKING:
    from src.game import Game
    from src.ui.app import App

MAX_NAME_LENGTH: int = 12
ALLOWED_NAME_CHARS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
DEATH_FRAME_TIME: float = 0.075
DEATH_HOLD: float = 0.45
GHOST_COLORS: tuple[str, ...] = ("red", "pink", "cyan", "orange")
KONAMI_CODE: tuple[int, ...] = (
    pg.K_UP,
    pg.K_UP,
    pg.K_DOWN,
    pg.K_DOWN,
    pg.K_LEFT,
    pg.K_RIGHT,
    pg.K_LEFT,
    pg.K_RIGHT,
    pg.K_a,
    pg.K_b,
)
FLICKER_DURATION: float = 0.75
FLICKER_INTERVAL: float = 0.15
FLICKER_TINTS: tuple[tuple[int, int, int], ...] = (
    (80, 0, 0),
    (0, 70, 0),
    (0, 0, 90),
    (80, 70, 0),
    (70, 0, 90),
    (0, 70, 90),
)
CHEAT_TITLE_COLORS: tuple[tuple[int, int, int], ...] = (
    Colors.red,
    Colors.orange,
    Colors.yellow,
    Colors.lime,
    Colors.cyan,
    Colors.magenta,
    Colors.violet,
)
MOVE_KEYS: dict[int, int] = {
    pg.K_UP: Direction.North,
    pg.K_w: Direction.North,
    pg.K_DOWN: Direction.South,
    pg.K_s: Direction.South,
    pg.K_LEFT: Direction.West,
    pg.K_a: Direction.West,
    pg.K_RIGHT: Direction.East,
    pg.K_d: Direction.East,
}


def _safe_name(name: str) -> str:
    """Return a name that the arcade font can render."""
    cleaned: str = "".join(
        char if char in ALLOWED_NAME_CHARS else " " for char in name.upper()
    )
    cleaned = " ".join(cleaned.split())
    return cleaned[:MAX_NAME_LENGTH] or "PLAYER"


def _rank_label(index: int) -> str:
    """Return 1ST, 2ND, 3RD, 4TH ... for a zero-based row index."""
    number: int = index + 1
    suffix: str = "TH"
    if number % 100 not in (11, 12, 13):
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(number % 10, "TH")
    return f"{number}{suffix}"


class MenuScreen(State):
    """Shared base for keyboard and mouse driven text menus."""

    fills_background: bool = True

    def __init__(  # noqa: PLR0913
        self,
        game: Game,
        theme: Theme,
        title: str,
        items: list[tuple[str, Callable[[], None]]],
        *,
        footer: str | None = None,
        title_top: int | None = None,
        button_size: tuple[int, int] | None = None,
    ) -> None:
        """Create a menu from labels and callbacks."""
        super().__init__(game)
        self.theme: Theme = theme
        self.title: str = title
        self.items: list[tuple[str, Callable[[], None]]] = items
        self.footer: str = theme.select_hint if footer is None else footer
        self.title_top: int = (
            theme.title_top if title_top is None else title_top
        )
        self.button_size: tuple[int, int] = (
            theme.button_size if button_size is None else button_size
        )
        self.selected_index: int = 0
        self.buttons: list[Button] = self._build_buttons()
        self._layout_size: tuple[int, int] | None = None
        self._layout(self.game.screen.get_size())

    def _build_buttons(self) -> list[Button]:
        """Create one text item per menu entry."""
        return [
            Button(
                text,
                self.theme.button_font,
                (0, 0),
                on_click=callback,
                size=self.button_size,
            )
            for text, callback in self.items
        ]

    def _layout(self, size: tuple[int, int]) -> None:
        """Centre the menu items for the current window size."""
        if size == self._layout_size:
            return
        self._layout_size = size
        width, height = size
        ys: list[int] = self.theme.centered_column(
            len(self.items),
            self.button_size[1],
            self.theme.button_gap,
            height,
        )
        for button, y in zip(self.buttons, ys, strict=True):
            button.rect.center = (width // 2, y)

    def _move(self, step: int) -> None:
        """Move keyboard selection, wrapping around."""
        if not self.items:
            return
        self.selected_index = (self.selected_index + step) % len(self.items)
        for button in self.buttons:
            button.hovered = False

    def _activate(self) -> None:
        """Run the selected callback."""
        if self.items:
            self.items[self.selected_index][1]()

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle keyboard navigation and mouse clicks."""
        self._layout(self.game.screen.get_size())
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_DOWN, pg.K_s):
                self._move(1)
            elif event.key in (pg.K_UP, pg.K_w):
                self._move(-1)
            elif event.key in (
                pg.K_RETURN,
                pg.K_KP_ENTER,
                pg.K_SPACE,
            ):
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
        """Menus have no per-frame state to update."""

    def draw_decor(self, screen: pg.Surface) -> None:
        """Hook for menus that want a little decoration."""

    def draw_title(self, screen: pg.Surface) -> None:
        """Draw the screen title, overridable for special visuals."""
        self.theme.draw_title(
            screen,
            self.title,
            self.title_top,
            shadow_color=Colors.red,
        )

    def draw(self, screen: pg.Surface) -> None:
        """Draw the background, title, items and footer."""
        self._layout(screen.get_size())
        if self.fills_background:
            self.theme.draw_background(screen)
        else:
            self.theme.draw_dim_overlay(screen)
        self.draw_title(screen)
        self.draw_decor(screen)
        for index, button in enumerate(self.buttons):
            button.selected = index == self.selected_index
            button.draw(screen)
        if self.footer:
            self.theme.draw_footer(screen, self.footer)


class StartMenuScreen(MenuScreen):
    """Opening attract screen."""

    def __init__(self, game: Game, theme: Theme, app: App) -> None:
        """Build the attract screen."""
        self.app: App = app
        self._elapsed: float = 0.0
        self._konami_progress: int = 0
        self._flicker_remaining: float = 0.0
        self._high_score: int = game.best_score()
        self._pac: pg.Surface = pg.transform.smoothscale(
            game.sprites.pacman(Direction.East, 1), (48, 48)
        )
        self._ghosts: list[pg.Surface] = [
            pg.transform.smoothscale(
                game.sprites.ghost(color, Direction.East, 1), (44, 44)
            )
            for color in GHOST_COLORS
        ]
        super().__init__(
            game,
            theme,
            "42 PACMAN",
            [
                ("PUSH ENTER TO START", lambda: app.start_game()),
                ("LEADERBOARD", lambda: app.show_leaderboard()),
                ("QUIT", lambda: app.quit()),
            ],
            footer="ARROWS SELECT  ENTER CONFIRM",
            title_top=70,
        )

    def handle_event(self, event: pg.event.Event) -> None:
        """Track the Konami code, then run ordinary menu input."""
        if event.type == pg.KEYDOWN:
            self._advance_konami(event.key)
        super().handle_event(event)

    def _advance_konami(self, key: int) -> None:
        """Advance the home-screen-only Konami code sequence."""
        if key == KONAMI_CODE[self._konami_progress]:
            self._konami_progress += 1
        elif key == KONAMI_CODE[0]:
            self._konami_progress = 1
        else:
            self._konami_progress = 0

        if self._konami_progress >= len(KONAMI_CODE):
            self._konami_progress = 0
            self.game.cheats.activate()
            self._flicker_remaining = FLICKER_DURATION

    def draw_title(self, screen: pg.Surface) -> None:
        """Use a rainbow logo whenever cheats are active."""
        if not self.game.cheats.enabled:
            super().draw_title(screen)
            return
        self.theme.draw_multicolor_title(
            screen,
            self.title,
            self.title_top,
            CHEAT_TITLE_COLORS,
            shadow_color=Colors.violet,
        )

    def update(self, dt: float) -> None:
        """Advance the small character bob."""
        self._elapsed += dt
        if self._flicker_remaining > 0.0:
            self._flicker_remaining = max(
                0.0, self._flicker_remaining - dt
            )

    def draw(self, screen: pg.Surface) -> None:
        """Draw the attract screen and its cheat activation flash."""
        super().draw(screen)
        self._draw_flicker(screen)

    def _draw_flicker(self, screen: pg.Surface) -> None:
        """Flash a colored tint over the home screen after activation."""
        if self._flicker_remaining <= 0.0:
            return
        elapsed: float = FLICKER_DURATION - self._flicker_remaining
        phase: int = int(elapsed / FLICKER_INTERVAL) % len(FLICKER_TINTS)
        screen.fill(
            FLICKER_TINTS[phase],
            special_flags=pg.BLEND_RGB_ADD,
        )

    def draw_decor(self, screen: pg.Surface) -> None:
        """Draw the high score line and the arcade cast."""
        center: int = screen.get_width() // 2
        label: pg.Surface = self.theme.render_text(
            "HIGH SCORE",
            self.theme.small_font,
            self.theme.text_color,
        )
        score: pg.Surface = self.theme.render_text(
            f"{self._high_score:06d}",
            self.theme.score_font,
            Colors.yellow,
        )
        gap: int = 16
        total: int = label.get_width() + gap + score.get_width()
        x: int = center - total // 2
        y: int = 210
        screen.blit(label, (x, y - label.get_height() // 2))
        screen.blit(
            score,
            (
                x + label.get_width() + gap,
                y - score.get_height() // 2,
            ),
        )

        baseline: int = screen.get_height() - 150
        pac_x: int = center - 190 + int(math.sin(self._elapsed * 1.4) * 6)
        screen.blit(self._pac, self._pac.get_rect(center=(pac_x, baseline)))
        for index, ghost in enumerate(self._ghosts):
            ghost_x: int = center - 90 + index * 75
            ghost_y: int = baseline + int(
                math.sin(self._elapsed * 2.0 + index * 0.6) * 5
            )
            screen.blit(ghost, ghost.get_rect(center=(ghost_x, ghost_y)))
        # Every State can draw cheat-only content from self.game.cheats.
        if self.game.cheats.enabled:
            self.theme.draw_text(
                screen,
                "CHEATS ACTIVE",
                self.theme.small_font,
                Colors.lime,
                topleft=(20, 20),
            )


class PauseMenuScreen(MenuScreen):
    """Pause overlay over the frozen maze."""

    fills_background = False

    def __init__(self, game: Game, theme: Theme, app: App) -> None:
        """Build the pause menu."""
        self.app: App = app
        super().__init__(
            game,
            theme,
            "PAUSED",
            [
                ("RESUME", lambda: app.resume()),
                ("RESTART", lambda: app.start_game()),
                ("MAIN MENU", lambda: app.show_start_menu()),
                ("QUIT", lambda: app.quit()),
            ],
            footer="ESC RESUME",
            title_top=150,
        )

    def handle_event(self, event: pg.event.Event) -> None:
        """Resume with Escape or P before ordinary menu input."""
        if event.type == pg.KEYDOWN and event.key in (
            pg.K_ESCAPE,
            pg.K_p,
        ):
            self.app.resume()
            return
        super().handle_event(event)


class GameScreen(State):
    """The playable maze with a classic score row and lives row."""

    def __init__(self, game: Game, theme: Theme, app: App) -> None:
        """Build the gameplay screen for an existing level."""
        super().__init__(game)
        self.theme: Theme = theme
        self.app: App = app
        self.high_score: int = game.best_score()
        self._life_icon: pg.Surface = pg.transform.smoothscale(
            game.sprites.pacman(Direction.East, 1), (20, 20)
        )
        self._frame_without_pacman: pg.Surface | None = None
        self._last_move_key: int | None = None

    def handle_event(self, event: pg.event.Event) -> None:
        """Translate input into movement, pause, or quit."""
        if event.type != pg.KEYDOWN:
            return
        key: int = event.key
        direction: int | None = MOVE_KEYS.get(key)
        if direction is not None:
            self._last_move_key = key
            self.game.queue_direction(direction)
        elif key in (pg.K_p, pg.K_ESCAPE):
            self.game.states.push(
                PauseMenuScreen(self.game, self.theme, self.app)
            )
        elif key == pg.K_q:
            self.app.quit()

    def _poll_held_direction(self) -> None:
        """Keep a held key moving Pac-Man after a stop or a respawn.

        ``KEYDOWN`` alone is not enough: holding a direction against a
        wall, through a death animation, or across a menu produces no
        new event when play resumes. Polling the key state fixes that.
        """
        if self.game.pac.direction is not None:
            return
        keys = pg.key.get_pressed()
        if self._last_move_key is not None and keys[self._last_move_key]:
            self.game.queue_direction(MOVE_KEYS[self._last_move_key])
            return
        for key, direction in MOVE_KEYS.items():
            if keys[key]:
                self._last_move_key = key
                self.game.queue_direction(direction)
                return

    def _start_death(self, position: tuple[float, float]) -> None:
        """Freeze the last frame and play the death animation."""
        source: pg.Surface = (
            self._frame_without_pacman
            if self._frame_without_pacman is not None
            else self.game.screen
        )
        background: pg.Surface = source.copy()
        self.app.last_game_frame = background
        on_done: Callable[[], None] = (
            self.app.game_over
            if self.game.game_over
            else self.app.finish_death
        )
        self.game.states.push(
            DyingState(
                self.game,
                self.theme,
                background,
                position,
                on_done,
            )
        )

    def update(self, dt: float) -> None:
        """Advance gameplay and react to a death."""
        self._poll_held_direction()
        lives_before: int = self.game.pac.lives
        pac_x: float = self.game.pac.x
        pac_y: float = self.game.pac.y
        self.game.update(dt)
        self.high_score = max(self.high_score, self.game.score)
        if self.game.pac.lives < lives_before:
            self._start_death((pac_x, pac_y))

    def _maze_bounds(self) -> tuple[int, int, int, int]:
        """Return the left, top, right and bottom of the maze."""
        left: int = OFFSET[0]
        top: int = OFFSET[1]
        right: int = left + self.game.config.width * CELL_SIZE
        bottom: int = top + self.game.config.height * CELL_SIZE
        return left, top, right, bottom

    def _draw_top_hud(self, screen: pg.Surface) -> None:
        """Draw 1UP, high score and level above the maze."""
        theme = self.theme
        game = self.game
        left, _, right, _ = self._maze_bounds()
        center: int = (left + right) // 2
        theme.draw_text(
            screen,
            "1UP",
            theme.small_font,
            Colors.red,
            topleft=(left, 2),
        )
        theme.draw_text(
            screen,
            f"{game.score:06d}",
            theme.score_font,
            theme.text_color,
            topleft=(left, 18),
        )
        theme.draw_text(
            screen,
            "HIGH SCORE",
            theme.small_font,
            theme.text_color,
            midtop=(center, 2),
        )
        theme.draw_text(
            screen,
            f"{self.high_score:06d}",
            theme.score_font,
            theme.text_color,
            midtop=(center, 18),
        )
        theme.draw_text(
            screen,
            "LEVEL",
            theme.small_font,
            theme.text_color,
            topright=(right, 2),
        )
        theme.draw_text(
            screen,
            f"{game.level:02d}",
            theme.score_font,
            theme.accent,
            topright=(right, 18),
        )

    def _draw_bottom_hud(self, screen: pg.Surface) -> None:
        """Draw remaining lives below the maze."""
        left, _, right, bottom = self._maze_bounds()
        center: int = (left + right) // 2
        y: int = bottom + 6
        theme = self.theme
        lives: int = max(self.game.pac.lives, 0)
        for index in range(min(lives, 5)):
            screen.blit(
                self._life_icon,
                self._life_icon.get_rect(topleft=(left + index * 26, y)),
            )
        theme.draw_text(
            screen,
            "1 Invincible",
            theme.small_font,
            theme.accent,
            midbottom=(center - 210, y + 19),
        )
        theme.draw_text(
            screen,
            "2 Speedhack",
            theme.small_font,
            theme.accent,
            midbottom=(center - 90, y + 19),
        )
        theme.draw_text(
            screen,
            "3 Add live",
            theme.small_font,
            theme.accent,
            midbottom=(center + 20, y + 19),
        )
        theme.draw_text(
            screen,
            "4 Skip level",
            theme.small_font,
            theme.accent,
            midbottom=(center + 135, y + 19),
        )
        theme.draw_text(
            screen,
            "5 Ghost freeze",
            theme.small_font,
            theme.accent,
            midbottom=(center + 265, y + 19),
        )

    def draw(self, screen: pg.Surface) -> None:
        """Draw the maze, actors and the two arcade HUD rows."""
        screen.fill(Colors.black)
        self._draw_top_hud(screen)
        self.game.render_level()
        self.game.draw_actors(screen, include_pacman=False)
        self._draw_bottom_hud(screen)
        if (
            self._frame_without_pacman is None
            or self._frame_without_pacman.get_size() != screen.get_size()
        ):
            self._frame_without_pacman = pg.Surface(screen.get_size())
        self._frame_without_pacman.blit(screen, (0, 0))
        self.game.pac.draw(screen, self.game.sprites)
        if not self.game.first_input:
            left, top, right, bottom = self._maze_bounds()
            self.theme.draw_text(
                screen,
                "READY!",
                self.theme.heading_font,
                Colors.yellow,
                center=(
                    (left + right) // 2,
                    (top + bottom) // 2,
                ),
            )


class DyingState(State):
    """Pac-Man's death animation over the frozen maze."""

    fills_background = False

    def __init__(
        self,
        game: Game,
        theme: Theme,
        background: pg.Surface,
        position: tuple[float, float],
        on_done: Callable[[], None],
    ) -> None:
        """Prepare the animation from the last rendered frame."""
        super().__init__(game)
        self.theme: Theme = theme
        self.background: pg.Surface = background
        self.position: tuple[int, int] = (
            int(position[0]),
            int(position[1]),
        )
        self.on_done: Callable[[], None] = on_done
        self.elapsed: float = 0.0
        self._done: bool = False
        self._frames: list[pg.Surface] = [
            game.sprites.death(frame) for frame in range(10)
        ]
        self._duration: float = 10 * DEATH_FRAME_TIME + DEATH_HOLD

    def _finish(self) -> None:
        """Run the transition callback once."""
        if self._done:
            return
        self._done = True
        self.on_done()

    def handle_event(self, event: pg.event.Event) -> None:
        """Allow the short animation to be skipped."""
        if event.type == pg.KEYDOWN and self.elapsed > 0.3:
            self._finish()

    def update(self, dt: float) -> None:
        """Advance the animation and finish when it is over."""
        self.elapsed += dt
        if self.elapsed >= self._duration:
            self._finish()

    def draw(self, screen: pg.Surface) -> None:
        """Draw the frozen frame and the current death frame."""
        if self.background.get_size() == screen.get_size():
            screen.blit(self.background, (0, 0))
        else:
            screen.blit(
                pg.transform.smoothscale(self.background, screen.get_size()),
                (0, 0),
            )
        frame: int = min(
            int(self.elapsed / DEATH_FRAME_TIME),
            len(self._frames) - 1,
        )
        sprite: pg.Surface = self._frames[frame]
        screen.blit(sprite, sprite.get_rect(center=self.position))


class NameEntryScreen(State):
    """Arcade high-score name entry after game over."""

    def __init__(
        self,
        game: Game,
        theme: Theme,
        app: App,
        score: int,
        background: pg.Surface | None = None,
    ) -> None:
        """Create the game-over prompt for ``score``."""
        super().__init__(game)
        self.theme: Theme = theme
        self.app: App = app
        self.score: int = score
        self.background: pg.Surface | None = background
        self.name: str = ""
        self.cursor_time: float = 0.0
        self.selected_index: int = 0
        self.buttons: list[Button] = [
            Button(
                "SAVE SCORE",
                theme.button_font,
                (0, 0),
                on_click=self._submit,
                size=(230, 44),
            ),
            Button(
                "SKIP",
                theme.button_font,
                (0, 0),
                on_click=lambda: app.skip_score(),
                size=(150, 44),
            ),
        ]
        self._layout_buttons(self.game.screen.get_size())

    def _layout_buttons(self, size: tuple[int, int]) -> None:
        """Place the two text actions under the input."""
        width, height = size
        y: int = height - 240
        self.buttons[0].rect.center = (width // 2 - 130, y)
        self.buttons[1].rect.center = (width // 2 + 130, y)

    def _submit(self) -> None:
        """Save the entered name, falling back to PLAYER."""
        name: str = " ".join(self.name.split()) or "PLAYER"
        self.app.submit_score(name, self.score)

    def _activate(self) -> None:
        """Run the selected action."""
        selected = self.buttons[self.selected_index]
        if selected.on_click is not None:
            selected.on_click()

    def _move(self, step: int) -> None:
        """Move the action selection, wrapping around."""
        self.selected_index = (self.selected_index + step) % len(self.buttons)
        for button in self.buttons:
            button.hovered = False

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle text entry, keyboard actions and mouse clicks."""
        size: tuple[int, int] = self.game.screen.get_size()
        self._layout_buttons(size)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.app.skip_score()
            elif event.key == pg.K_UP:
                self._move(-1)
            elif event.key == pg.K_DOWN:
                self._move(1)
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self._activate()
            elif event.key == pg.K_BACKSPACE:
                self.name = self.name[:-1]
            else:
                char: str = event.unicode.upper()
                if (
                    char in ALLOWED_NAME_CHARS
                    and len(self.name) < MAX_NAME_LENGTH
                ):
                    self.name += char
        elif event.type == pg.MOUSEMOTION:
            for index, button in enumerate(self.buttons):
                button.handle_event(event)
                if button.hovered:
                    self.selected_index = index
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt: float) -> None:
        """Blink the input cursor."""
        self.cursor_time += dt

    def draw(self, screen: pg.Surface) -> None:
        """Draw the game-over high-score entry."""
        if self.background is not None:
            if self.background.get_size() == screen.get_size():
                screen.blit(self.background, (0, 0))
            else:
                screen.blit(
                    pg.transform.smoothscale(
                        self.background, screen.get_size()
                    ),
                    (0, 0),
                )
            self.theme.draw_dim_overlay(screen, 205)
        else:
            screen.fill(Colors.black)
        self._layout_buttons(screen.get_size())
        center: int = screen.get_width() // 2
        self.theme.draw_title(
            screen,
            "GAME OVER",
            120,
            color=Colors.red,
            shadow_color=(84, 0, 0),
        )
        self.theme.draw_text(
            screen,
            f"SCORE {self.score:06d}",
            self.theme.score_font,
            Colors.white,
            center=(center, 250),
        )
        self.theme.draw_text(
            screen,
            "ENTER YOUR NAME",
            self.theme.body_font,
            Colors.yellow,
            center=(center, 330),
        )
        input_y: int = 372
        text_surface: pg.Surface = self.theme.render_text(
            self.name,
            self.theme.input_font,
            Colors.yellow,
        )
        cursor_width: int = 18
        gap: int = 6 if self.name else 0
        total: int = text_surface.get_width() + gap + cursor_width
        start_x: int = center - total // 2
        screen.blit(text_surface, (start_x, input_y))
        cursor_x: int = start_x + text_surface.get_width() + gap
        if int(self.cursor_time * 2) % 2 == 0:
            pg.draw.rect(
                screen,
                Colors.yellow,
                pg.Rect(
                    cursor_x,
                    input_y + 4,
                    cursor_width,
                    self.theme.input_font.get_height() - 6,
                ),
            )
        line_y: int = input_y + self.theme.input_font.get_height() + 8
        pg.draw.line(
            screen,
            Colors.blue,
            (center - 220, line_y),
            (center + 220, line_y),
            1,
        )
        for index, button in enumerate(self.buttons):
            button.selected = index == self.selected_index
            button.draw(screen)
        self.theme.draw_footer(screen, "ENTER CONFIRM  ESC SKIP")


class LeaderboardScreen(State):
    """Classic arcade high-score table backed by db.py."""

    def __init__(
        self,
        game: Game,
        theme: Theme,
        app: App,
        highlight: tuple[str, int] | None = None,
        new_score: int | None = None,
    ) -> None:
        """Load the top ten and build the actions."""
        super().__init__(game)
        self.theme: Theme = theme
        self.app: App = app
        self.highlight: tuple[str, int] | None = highlight
        self.new_score: int | None = new_score
        self.entries: list[tuple[str, int]] = game.leaderboard(10)
        self.selected_index: int = 0
        self.buttons: list[Button] = [
            Button(
                "PLAY AGAIN",
                theme.button_font,
                (0, 0),
                on_click=lambda: app.start_game(),
                size=(230, 44),
            ),
            Button(
                "MAIN MENU",
                theme.button_font,
                (0, 0),
                on_click=lambda: app.show_start_menu(),
                size=(230, 44),
            ),
        ]
        self._layout_size: tuple[int, int] | None = None
        self._layout(self.game.screen.get_size())

    def _layout(self, size: tuple[int, int]) -> None:
        """Place the two text actions under the table."""
        if size == self._layout_size:
            return
        self._layout_size = size
        width, height = size
        y: int = min(640, height - 120)
        self.buttons[0].rect.center = (width // 2 - 130, y)
        self.buttons[1].rect.center = (width // 2 + 130, y)

    def _subtitle(self) -> str:
        """Return the one-line status shown under the title."""
        if self.new_score is None:
            return ""
        if self.entries and self.entries[0] == self.highlight:
            return f"NEW HIGH SCORE {self.new_score:06d}"
        return f"SCORE SAVED {self.new_score:06d}"

    def _move(self, step: int) -> None:
        """Change the selected action, wrapping around."""
        self.selected_index = (self.selected_index + step) % len(self.buttons)
        for button in self.buttons:
            button.hovered = False

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle keyboard and mouse navigation."""
        self._layout(self.game.screen.get_size())
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.app.show_start_menu()
            elif event.key in (
                pg.K_LEFT,
                pg.K_UP,
                pg.K_a,
                pg.K_w,
            ):
                self._move(-1)
            elif event.key in (
                pg.K_RIGHT,
                pg.K_DOWN,
                pg.K_d,
                pg.K_s,
            ):
                self._move(1)
            elif event.key in (
                pg.K_RETURN,
                pg.K_KP_ENTER,
                pg.K_SPACE,
            ):
                selected = self.buttons[self.selected_index]
                if selected.on_click is not None:
                    selected.on_click()
        elif event.type == pg.MOUSEMOTION:
            for index, button in enumerate(self.buttons):
                button.handle_event(event)
                if button.hovered:
                    self.selected_index = index
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt: float) -> None:
        """Nothing changes while the table is open."""

    def _draw_table(self, screen: pg.Surface) -> None:
        """Draw the ranked score table."""
        theme = self.theme
        center: int = screen.get_width() // 2
        left: int = center - 280
        score_right: int = center
        name_left: int = center + 30
        right: int = center + 280
        if not self.entries:
            theme.draw_text(
                screen,
                "NO HIGH SCORES YET",
                theme.heading_font,
                Colors.white,
                center=(center, 300),
            )
            theme.draw_text(
                screen,
                "PLAY A GAME",
                theme.body_font,
                theme.text_muted,
                center=(center, 360),
            )
            return
        header_y: int = 180
        theme.draw_text(
            screen,
            "RANK",
            theme.small_font,
            theme.text_dim,
            topleft=(left, header_y),
        )
        theme.draw_text(
            screen,
            "SCORE",
            theme.small_font,
            theme.text_dim,
            topright=(score_right, header_y),
        )
        theme.draw_text(
            screen,
            "NAME",
            theme.small_font,
            theme.text_dim,
            topleft=(name_left, header_y),
        )
        pg.draw.line(
            screen,
            Colors.blue,
            (left, header_y + 22),
            (right, header_y + 22),
            1,
        )
        row_y: int = header_y + 34
        for index in range(10):
            if index >= len(self.entries):
                theme.draw_text(
                    screen,
                    _rank_label(index),
                    theme.body_font,
                    theme.text_dim,
                    topleft=(left, row_y),
                )
                row_y += 34
                continue
            name, score = self.entries[index]
            highlighted: bool = (name, score) == self.highlight
            color: tuple[int, int, int] = (
                Colors.yellow if highlighted else Colors.white
            )
            theme.draw_text(
                screen,
                _rank_label(index),
                theme.body_font,
                color,
                topleft=(left, row_y),
            )
            theme.draw_text(
                screen,
                f"{score:06d}",
                theme.body_font,
                color,
                topright=(score_right, row_y),
            )
            theme.draw_text(
                screen,
                _safe_name(name),
                theme.body_font,
                color,
                topleft=(name_left, row_y),
            )
            if highlighted:
                theme.draw_text(
                    screen,
                    "NEW",
                    theme.small_font,
                    Colors.yellow,
                    topright=(right, row_y + 2),
                )
            row_y += 34

    def draw(self, screen: pg.Surface) -> None:
        """Draw the title, table and actions."""
        self._layout(screen.get_size())
        self.theme.draw_background(screen)
        self.theme.draw_title(
            screen,
            "HIGH SCORES",
            50,
            shadow_color=Colors.red,
        )
        subtitle: str = self._subtitle()
        if subtitle:
            self.theme.draw_text(
                screen,
                subtitle,
                self.theme.body_font,
                Colors.yellow,
                center=(screen.get_width() // 2, 138),
            )
        self._draw_table(screen)
        for index, button in enumerate(self.buttons):
            button.selected = index == self.selected_index
            button.draw(screen)
        self.theme.draw_footer(screen, "ARROWS SELECT  ESC MAIN MENU")
