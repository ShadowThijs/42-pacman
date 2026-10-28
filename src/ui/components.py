"""Reusable pygame components."""

from __future__ import annotations

from collections.abc import Callable

import pygame as pg

from ..models import Colors


class Button:
    """Plain arcade text item with mouse and keyboard focus support."""

    def __init__(
        self,
        text: str,
        font: pg.font.Font,
        center: tuple[int, int],
        on_click: Callable[[], None] | None = None,
        size: tuple[int, int] = (380, 44),
    ) -> None:
        """Create a text item centred on ``center``."""
        self.text: str = text
        self.font: pg.font.Font = font
        self.on_click: Callable[[], None] | None = on_click
        self.rect: pg.Rect = pg.Rect(0, 0, *size)
        self.rect.center = center
        self.hovered: bool = False
        self.selected: bool = False
        self.enabled: bool = True

    def handle_event(self, event: pg.event.Event) -> None:
        """Track the mouse and fire the callback on a left click."""
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.hovered = self.rect.collidepoint(event.pos)
            if self.hovered and self.enabled and self.on_click is not None:
                self.on_click()

    def draw(self, screen: pg.Surface) -> None:
        """Draw the label, with a yellow marker when focused."""
        active: bool = (
            self.selected or self.hovered
        ) and self.enabled
        color: tuple[int, int, int] = Colors.yellow if active else Colors.white
        if not self.enabled:
            color = (80, 80, 80)
        label: pg.Surface = self.font.render(self.text, True, color)
        label_rect: pg.Rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)
        if active:
            marker_x: int = label_rect.left - 20
            marker_y: int = label_rect.centery
            pg.draw.polygon(
                screen,
                Colors.yellow,
                [
                    (marker_x, marker_y - 7),
                    (marker_x, marker_y + 7),
                    (marker_x + 11, marker_y),
                ],
            )
