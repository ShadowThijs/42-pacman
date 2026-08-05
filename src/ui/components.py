"""Components for pygame."""

from typing import Any

import pygame as pg

from ..models import Colors


class Button:
    """Button component.

    Has built-in keyboard support.
    Has support for mouse interaction."""

    def __init__(
        self,
        text: str,
        font: pg.font.Font,
        center: tuple[int, int],
        on_click: Any = None,
        size: tuple[int, int] = (240, 56)
    ) -> None:
        """Init button."""
        self.text: str = text
        self.font: pg.font.Font = font
        self.on_click: Any = on_click
        self.rect: pg.Rect = pg.Rect(0, 0, *size)
        self.rect.center = center
        self.hovered = False

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle event on button."""
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif (event.type == pg.MOUSEBUTTONUP and event.button == 1):
            self.hovered = self.rect.collidepoint(event.pos)
            if self.hovered and self.on_click is not None:
                self.on_click()

    def draw(self, screen: pg.Surface) -> None:
        fill = Colors.hover_button if self.hovered else Colors.base_button
        edge = Colors.white if self.hovered else Colors.border_button
        pg.draw.rect(screen, fill, self.rect, border_radius=10)
        pg.draw.rect(screen, edge, self.rect, width=2, border_radius=10)
        label = self.font.render(self.text, True, Colors.white)
        screen.blit(label, label.get_rect(center=self.rect.center))
