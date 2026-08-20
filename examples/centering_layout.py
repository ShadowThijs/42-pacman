"""Centering & anchoring UI regardless of window size.

Run:  python examples/centering_layout.py
Then RESIZE the window (drag a corner) -- everything stays centered,
flicker-free on Wayland and X11.

Three rules:

1.  Never hardcode pixel positions. Read them from the surface each frame:
        w, h = screen.get_size()
        cx, cy = w // 2, h // 2

2.  Use pygame.Rect anchor points. A Rect exposes named anchors:
        topleft, midtop, topright,
        midleft, center, midright,
        bottomleft, midbottom, bottomright
    Assigning an anchor moves the whole rect, so this centers a surface
    of ANY size on a screen of ANY size:
        r = text.get_rect()
        r.center = (cx, cy)
        screen.blit(text, r)

3.  To make elements move together, give the group a Rect (a "panel"),
    position that panel relative to the SCREEN, then position the children
    relative to the PANEL's anchors. Move/resize either and the children
    follow because their coordinates are recomputed every frame.

Why pygame.SCALED (and why a naive resizable window flickers):
    The obvious approach -- calling pygame.display.set_mode() again on
    every VIDEORESIZE event -- rebuilds the display surface many times
    per second while you drag, which flashes/flickers badly on Wayland
    and X11.

    pygame.SCALED fixes it: pygame keeps ONE fixed-size drawing surface
    (here 800x600) and SDL2 scales that single surface to fit the real
    window, so resizing is handled by the compositor -- no surface
    rebuild, no flicker. You draw in a stable coordinate space; the OS
    scales the whole frame to whatever size the user drags to.

    Consequences:
      * screen.get_size() always returns the fixed LOGICAL size (800x600)
        -- that is the size you center against.
      * pygame.display.get_window_size() returns the REAL window size in
        pixels if you ever need it (used below only for the readout).

For your maze specifically: replace the fixed OFFSET = (50, 50) with a
value derived from the screen so the maze is always centered:

    maze_w = cfg.width * CELL_SIZE
    maze_h = cfg.height * CELL_SIZE
    offset_x = (screen_w - maze_w) // 2
    offset_y = (screen_h - maze_h) // 2

Controls: Q quits | resize the window freely
"""

import pygame

# The one fixed drawing surface. Everything centers within this space;
# SDL2 scales it to the real window at the end. (That is why it's steady.)
LOGICAL_W, LOGICAL_H = 800, 600
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PANEL_BG = (20, 20, 40)


def draw_top_title(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Title pinned to the top-center of the drawing surface."""
    w = screen.get_width()
    title = font.render("RESIZE ME -- I STAY CENTERED", True, YELLOW)
    screen.blit(title, title.get_rect(midtop=(w // 2, 20)))


def draw_centered_box(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """A box dead-center, plus a label anchored to the box's center."""
    w, h = screen.get_size()
    rect = pygame.Rect(0, 0, 240, 160)
    rect.center = (w // 2, h // 2)            # <-- the key line
    pygame.draw.rect(screen, BLUE, rect, border_radius=12)
    label = font.render("centered box", True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_bottom_panel(
    screen: pygame.Surface,
    fonts: tuple[pygame.font.Font, pygame.font.Font]
) -> None:
    """Panel anchored to bottom-center; children anchored to the PANEL.

    Resize the window and the whole panel (with its children) slides so
    it stays bottom-centered, because everything is derived from the
    panel Rect each frame.
    """
    w, h = screen.get_size()
    title_font, body_font = fonts

    # 1) Position the PANEL relative to the surface.
    panel = pygame.Rect(0, 0, 320, 90)
    panel.midbottom = (w // 2, h - 20)
    pygame.draw.rect(screen, PANEL_BG, panel, border_radius=8)

    # 2) Position CHILDREN relative to the panel's anchors, not the surface.
    title = title_font.render("PANEL", True, YELLOW)
    screen.blit(title, title.get_rect(midtop=panel.midtop))
    body = body_font.render("children follow the panel", True, WHITE)
    screen.blit(body, body.get_rect(center=panel.center))


def main() -> None:
    pygame.init()
    # SCALED = one fixed drawing surface, scaled to the window by SDL2.
    # RESIZABLE = let the user drag the window. Together: smooth, flicker-free.
    screen = pygame.display.set_mode(
        (LOGICAL_W, LOGICAL_H), pygame.SCALED | pygame.RESIZABLE
    )
    pygame.display.set_caption("Centering & Anchoring Demo")
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arial", 22, bold=True)
    body_font = pygame.font.SysFont("arial", 16)
    size_font = pygame.font.Font(None, 26)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            # NOTE: no VIDEORESIZE handling -- SCALED handles resizing for us,
            # so we never rebuild the display surface (that was the flicker).

        screen.fill((0, 0, 0))

        # Real OS window size for the readout; the drawing surface itself
        # stays the fixed LOGICAL size, which is what we center against.
        win_w, win_h = pygame.display.get_window_size()
        size_text = size_font.render(f"window: {win_w} x {win_h}", True, WHITE)
        screen.blit(
            size_text,
            size_text.get_rect(midbottom=(LOGICAL_W // 2, LOGICAL_H // 2 - 110)),
        )

        draw_top_title(screen, title_font)
        draw_centered_box(screen, body_font)
        draw_bottom_panel(screen, (title_font, body_font))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
