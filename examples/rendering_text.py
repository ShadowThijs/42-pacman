"""Rendering text: fonts, live stats, and positioning.

Run:  python examples/rendering_text.py

Core API:

    font = pygame.font.SysFont("arial", 36)   # named system font (best effort)
    font = pygame.font.Font(None, 36)         # pygame's built-in default font
    surface = font.render("Hello", True, WHITE)   # True = antialiased
    screen.blit(surface, (x, y))

Things to know:
  * render() returns a *Surface*. You place text by blitting that surface,
    exactly like a sprite -- so all the centering/anchoring tricks from
    centering_layout.py apply to text too.
  * For a value that changes every frame (score, timer, FPS), just call
    render() again each frame; it is cheap for short strings. For static
    text, render once, store the surface, reuse it.
  * get_rect(center=...) is the easiest way to center text of any size on
    a screen of any size (see the title below).
  * pygame.freetype (import pygame.freetype) is a more capable alternative
    with better Unicode support, rotation, and outlines. For a typical HUD
    the basic font module above is enough.

Controls: SPACE adds points | Q quits
"""

import pygame

WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Text Rendering Demo")
    clock = pygame.time.Clock()

    # Load fonts ONCE, outside the loop. Reuse the font objects; only the
    # *rendered surface* is remade when the text changes.
    title_font = pygame.font.SysFont("arial", 44, bold=True)
    body_font = pygame.font.SysFont("arial", 24)
    mono = pygame.font.Font(None, 22)  # always available, even w/o named font

    score = 0
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    score += 10

        screen.fill(BLACK)

        # --- Centered title: get_rect + center handles any text size ---
        title = title_font.render("SCORE TRACKER", True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

        # --- Top-left label (absolute position) + live stat beside it ---
        screen.blit(body_font.render("Score:", True, WHITE), (20, 20))
        # Re-rendered every frame because the value changes:
        screen.blit(body_font.render(str(score), True, GREEN), (110, 20))

        # --- FPS, anchored to bottom-left of the window ---
        fps = mono.render(f"{clock.get_fps():.0f} fps", True, WHITE)
        screen.blit(fps, fps.get_rect(bottomleft=(20, HEIGHT - 20)))

        # --- Multiline block: render each line, stack by line height ---
        lines = ["Controls:", "  SPACE +10", "  Q quit"]
        y = HEIGHT // 2 - 30
        for line in lines:
            surf = body_font.render(line, True, WHITE)
            screen.blit(surf, (WIDTH // 2 - 80, y))
            y += surf.get_height() + 4  # advance by height + spacing

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
