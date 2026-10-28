"""Arcade theme shared by every screen."""

from __future__ import annotations

from pygame import font

import pygame as pg

from src.models import Colors

SPACE_GAP: int = 3


def expand_spaces(text: str) -> str:
    """Widen the very narrow space glyph of the arcade font."""
    return (" " * SPACE_GAP).join(text.split())


def _load_font(size: int) -> font.Font:
    """Load the arcade font, falling back to a bundled/system mono font."""
    for name in ("ArcadeClassic", "ByteBounce", "dejavusansmono"):
        path: str | None = font.match_font(name)
        if path is not None:
            return font.Font(path, size)
    return font.Font(None, size)


class Theme:
    """Fonts, colours and the few text helpers the screens share."""

    background: tuple[int, int, int] = Colors.black
    title_color: tuple[int, int, int] = Colors.yellow
    text_color: tuple[int, int, int] = Colors.white
    text_muted: tuple[int, int, int] = (170, 170, 170)
    text_dim: tuple[int, int, int] = (105, 105, 105)
    accent: tuple[int, int, int] = Colors.yellow
    danger: tuple[int, int, int] = Colors.red
    overlay_color: tuple[int, int, int, int] = (0, 0, 0, 165)
    select_hint: str = "ARROWS SELECT  ENTER CONFIRM"

    def __init__(self) -> None:
        """Create the shared font set and metrics."""
        if not font.get_init():
            font.init()
        self.title_font: font.Font = _load_font(64)
        self.heading_font: font.Font = _load_font(44)
        self.button_font: font.Font = _load_font(28)
        self.score_font: font.Font = _load_font(26)
        self.body_font: font.Font = _load_font(22)
        self.input_font: font.Font = _load_font(40)
        self.small_font: font.Font = _load_font(16)
        self.tiny_font: font.Font = _load_font(13)
        self.button_size: tuple[int, int] = (380, 44)
        self.button_gap: int = 14
        self.title_top: int = 80
        self.footer_margin: int = 20
        self._overlays: dict[tuple[int, int, int], pg.Surface] = {}

    def render_text(
        self,
        text: str,
        text_font: font.Font,
        color: tuple[int, int, int],
    ) -> pg.Surface:
        """Render text with readable arcade word gaps."""
        return text_font.render(expand_spaces(text), True, color)

    def centered_column(
        self,
        count: int,
        item_height: int,
        gap: int,
        screen_height: int,
    ) -> list[int]:
        """Return the y-centres of ``count`` stacked menu items."""
        if count == 0:
            return []
        total: int = count * item_height + max(count - 1, 0) * gap
        top: int = (screen_height - total) // 2
        return [
            top + item_height // 2 + index * (item_height + gap)
            for index in range(count)
        ]

    def draw_background(self, screen: pg.Surface) -> None:
        """Fill the screen with the arcade black."""
        screen.fill(self.background)

    def draw_dim_overlay(
        self,
        screen: pg.Surface,
        alpha: int | None = None,
    ) -> None:
        """Dim the frame underneath an overlay."""
        actual_alpha: int = (
            self.overlay_color[3] if alpha is None else alpha
        )
        size: tuple[int, int] = screen.get_size()
        key: tuple[int, int, int] = (size[0], size[1], actual_alpha)
        overlay: pg.Surface | None = self._overlays.get(key)
        if overlay is None:
            overlay = pg.Surface(size, pg.SRCALPHA)
            overlay.fill((0, 0, 0, actual_alpha))
            self._overlays[key] = overlay
        screen.blit(overlay, (0, 0))

    def draw_text(
        self,
        screen: pg.Surface,
        text: str,
        text_font: font.Font,
        color: tuple[int, int, int],
        *,
        center: tuple[int, int] | None = None,
        midtop: tuple[int, int] | None = None,
        midbottom: tuple[int, int] | None = None,
        midleft: tuple[int, int] | None = None,
        midright: tuple[int, int] | None = None,
        topleft: tuple[int, int] | None = None,
        topright: tuple[int, int] | None = None,
        bottomleft: tuple[int, int] | None = None,
        bottomright: tuple[int, int] | None = None,
    ) -> pg.Rect:
        """Render text at one anchor and return its rectangle."""
        surface: pg.Surface = self.render_text(
            text, text_font, color
        )
        rect: pg.Rect = surface.get_rect()
        if center is not None:
            rect.center = center
        elif midtop is not None:
            rect.midtop = midtop
        elif midbottom is not None:
            rect.midbottom = midbottom
        elif midleft is not None:
            rect.midleft = midleft
        elif midright is not None:
            rect.midright = midright
        elif topleft is not None:
            rect.topleft = topleft
        elif topright is not None:
            rect.topright = topright
        elif bottomleft is not None:
            rect.bottomleft = bottomleft
        elif bottomright is not None:
            rect.bottomright = bottomright
        screen.blit(surface, rect)
        return rect

    def draw_title(
        self,
        screen: pg.Surface,
        text: str,
        top: int | None = None,
        color: tuple[int, int, int] | None = None,
        shadow_color: tuple[int, int, int] | None = None,
        center_x: int | None = None,
    ) -> pg.Rect:
        """Draw a title with the classic offset shadow."""
        actual_top: int = self.title_top if top is None else top
        actual_color: tuple[int, int, int] = (
            self.title_color if color is None else color
        )
        actual_center: int = (
            screen.get_width() // 2 if center_x is None else center_x
        )
        main: pg.Surface = self.render_text(
            text, self.title_font, actual_color
        )
        rect: pg.Rect = main.get_rect(
            midtop=(actual_center, actual_top)
        )
        if shadow_color is not None:
            shadow: pg.Surface = self.render_text(
                text, self.title_font, shadow_color
            )
            screen.blit(shadow, rect.move(3, 3))
        screen.blit(main, rect)
        return rect

    def draw_footer(self, screen: pg.Surface, text: str) -> None:
        """Draw the shared bottom hint line."""
        self.draw_text(
            screen,
            text,
            self.small_font,
            self.text_dim,
            midbottom=(
                screen.get_width() // 2,
                screen.get_height() - self.footer_margin,
            ),
        )
