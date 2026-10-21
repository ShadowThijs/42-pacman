"""Theme manager."""

from collections.abc import Callable

import pygame as pg
from pygame import font

from src.models import Colors


class Theme:
    """Theme class."""

    background: tuple[int, int, int] = Colors.black
    title_color: tuple[int, int, int] = Colors.yellow
    text_color: tuple[int, int, int] = Colors.white
    text_muted: tuple[int, int, int] = Colors.muted
    overlay_color: tuple[int, int, int, int] = (0, 0, 0, 160)

    def __init__(self) -> None:
        """Init theme."""
        if not font.get_init():
            font.init()
        self.title_font: font.Font = font.SysFont("dejavusans", 52, bold=True)
        self.button_font: font.Font = font.SysFont("dejavusans", 28, bold=True)
        self.body_font: font.Font = font.SysFont("dejavusans", 22, bold=False)
        self.button_size: tuple[int, int] = (260, 56)
        self.button_gap: int = 18
        self.title_top: int = 96
        self.footer_margin: int = 32
        self.max_content_width: int = 640
        self._overlay: pg.Surface | None = None
        self._overlay_size: tuple[int, int] | None = None

    def centered_column(
        self,
        n: int,
        item_h: int,
        gap: int,
        screen_h: int
    ) -> list[int]:
        """Centered column."""
        if n == 0:
            return []
        result: list[int] = []
        total: int = n * item_h + max(n - 1, 0) * gap
        top: int = (screen_h - total) // 2
        for i in range(n):
            result.append(top + item_h // 2 + i * (item_h + gap))
        return result

    def draw_dim_overlay(
        self,
        screen: pg.Surface
    ) -> None:
        """Draw dim overlay."""
        size: tuple[int, int] = screen.get_size()
        if self._overlay is None or self._overlay_size != size:
            self._overlay = pg.Surface(size, pg.SRCALPHA)
            self._overlay.fill(self.overlay_color)
            self._overlay_size = size
        screen.blit(self._overlay, (0, 0))

    def draw_title(
        self,
        screen: pg.Surface,
        text: str
    ) -> None:
        """Draw the title."""
        title_surface: pg.Surface = self.title_font.render(
            text,
            True,
            self.title_color
        )
        title_rect: pg.Rect = title_surface.get_rect(
            midtop=(screen.get_width() // 2, self.title_top)
        )
        screen.blit(title_surface, title_rect)

    def draw_footer(
        self,
        screen: pg.Surface,
        text: str
    ) -> None:
        """Draw footer."""
        footer_surface: pg.Surface = self.body_font.render(
            text,
            True,
            self.text_muted
        )
        footer_rect: pg.Rect = footer_surface.get_rect(
            midbottom=(
                screen.get_width() // 2,
                screen.get_height() - self.footer_margin,
            )
        )
        screen.blit(footer_surface, footer_rect)


if __name__ == "__main__":
    """Run a visual preview of the theme."""
    from .components import Button

    pg.init()
    screen: pg.Surface = pg.display.set_mode((1200, 800), pg.RESIZABLE)
    pg.display.set_caption("Theme preview")
    clock: pg.time.Clock = pg.time.Clock()
    theme: Theme = Theme()
    running: bool = True
    dimmed: bool = False

    rect: pg.Rect = screen.get_rect()
    labels: list[str] = ["PLAY", "OPTIONS", "QUIT"]
    callbacks: list[Callable[[], None]] = [
        lambda: print("PLAY"),
        lambda: print("OPTIONS"),
        lambda: print("QUIT"),
    ]
    ys: list[int] = theme.centered_column(
        len(labels),
        theme.button_size[1],
        theme.button_gap,
        rect.height,
    )
    buttons: list[Button] = [
        Button(
            label,
            theme.button_font,
            (rect.centerx, y),
            on_click=callback,
            size=theme.button_size,
        )
        for label, y, callback in zip(labels, ys, callbacks, strict=False)
    ]

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (
                    event.type == pg.KEYDOWN and event.key in (
                        pg.K_ESCAPE,
                        pg.K_q,
                    )):
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                dimmed = not dimmed
            else:
                for button in buttons:
                    button.handle_event(event)

        screen.fill(theme.background)
        pg.draw.rect(
            screen,
            Colors.blue,
            screen.get_rect().inflate(-80, -80),
            width=2,
        )
        for x in (rect.centerx - 320, rect.centerx + 320):
            for y in (260, 400, 540):
                pg.draw.circle(screen, Colors.orange, (x, y), 8)
        pg.draw.circle(screen, Colors.yellow, (rect.centerx, 660), 20)
        if dimmed:
            theme.draw_dim_overlay(screen)
        theme.draw_title(screen, "42PACMAN")
        body: pg.Surface = theme.body_font.render(
            "Score: 4200",
            True,
            theme.text_color,
        )
        body_rect: pg.Rect = body.get_rect(
            midtop=(
                rect.centerx,
                theme.title_top + theme.title_font.get_height() + 8,
            )
        )
        screen.blit(body, body_rect)
        for button in buttons:
            button.draw(screen)
        theme.draw_footer(
            screen,
            "Mouse hover + click | Space: dim | Esc: quit",
        )
        pg.display.flip()
        clock.tick(60)

    pg.quit()
