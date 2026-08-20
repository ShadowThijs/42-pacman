"""Game states + mouse interaction: clickable, hover-highlighted buttons.

Run:  python examples/game_states_mouse.py

This extends examples/game_states.py with a mouse-driven menu: PLAY,
LEADERBOARD, and QUIT buttons that highlight when hovered and fire when
clicked. The same state-machine + stack from game_states.py is reused --
the only change is that states now also handle mouse events.

Why mouse "just works" here:
    The Game loop already routes EVERY event to the top state via
        self.current.handle_event(event)
    Mouse events (MOUSEMOTION, MOUSEBUTTONUP) are ordinary events, so a
    state opts into the mouse simply by handling them in handle_event().

The Button class:
    * Hover is updated on MOUSEMOTION (and re-checked at click time).
    * The click fires on MOUSEBUTTONUP while the cursor is over the button.
      This means you can press the button, drag the pointer away, and
      release to CANCEL -- a small but nice UX detail, for free.
    * draw() swaps the fill/border colour when hovered -> the highlight.

Controls: mouse to click | ESC/Q quits
"""

import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
BASE = (30, 30, 60)        # button fill, normal
HOVER = (70, 70, 140)      # button fill, hovered
BORDER = (90, 90, 120)     # button border, normal


class Button:
    """A clickable, hover-highlighting button.

    A click is MOUSEBUTTONUP (left button) while the pointer is over the
    rect. Call handle_event() per event and draw() per frame.
    """

    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        center: tuple[int, int],
        on_click=None,
        size: tuple[int, int] = (240, 56),
    ) -> None:
        self.text = text
        self.font = font
        self.on_click = on_click
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center          # anchor by center -> easy to lay out
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
            self.hovered = self.rect.collidepoint(event.pos)
            if self.hovered and self.on_click is not None:
                self.on_click()

    def draw(self, screen: pygame.Surface) -> None:
        fill = HOVER if self.hovered else BASE
        edge = WHITE if self.hovered else BORDER
        pygame.draw.rect(screen, fill, self.rect, border_radius=10)
        pygame.draw.rect(screen, edge, self.rect, width=2, border_radius=10)
        label = self.font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))


def _column_starts(
    n: int, item_h: int, gap: int
) -> list[int]:
    """Y-centers for n buttons stacked and vertically centered on screen."""
    total = n * item_h + (n - 1) * gap
    y = (HEIGHT - total) // 2 + item_h // 2
    return [y + i * (item_h + gap) for i in range(n)]


# --------------------------------------------------------------------------- #
#  States                                                                      #
# --------------------------------------------------------------------------- #
class State:
    """Base state. Override handle_event / update / draw in subclasses."""

    def __init__(self, game: "Game") -> None:
        self.game = game

    def handle_event(self, event: pygame.event.Event) -> None: ...
    def update(self, dt: float) -> None: ...
    def draw(self, screen: pygame.Surface) -> None: ...


class MenuState(State):
    """Main menu: PLAY, LEADERBOARD, QUIT buttons."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        cx = WIDTH // 2
        labels = ["PLAY", "LEADERBOARD", "QUIT"]
        actions = [
            lambda: game.replace(PlayingState(game)),
            lambda: game.replace(LeaderboardState(game)),
            game.quit,
        ]
        ys = _column_starts(len(labels), 56, 20)
        self.buttons = [
            Button(text, game.font_btn, (cx, y), on_click=act)
            for text, act, y in zip(labels, actions, ys)
        ]

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK)
        title = self.game.font_title.render("42PacMan", True, YELLOW)
        screen.blit(
            title, title.get_rect(midtop=(WIDTH // 2, HEIGHT // 5))
        )
        for btn in self.buttons:
            btn.draw(screen)


class PlayingState(State):
    """A stub game: the dot follows the mouse; BACK returns to the menu."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.mx, self.my = WIDTH // 2, HEIGHT // 2
        self.back = Button(
            "BACK", game.font_btn,
            (WIDTH // 2, HEIGHT - 60),
            on_click=lambda: game.replace(MenuState(game)),
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.mx, self.my = event.pos
        self.back.handle_event(event)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((10, 10, 20))
        hint = self.game.font_title.render(
            "PLAYING -- move the mouse", True, WHITE
        )
        screen.blit(hint, hint.get_rect(midtop=(WIDTH // 2, 60)))
        pygame.draw.circle(screen, YELLOW, (self.mx, self.my), 20)
        self.back.draw(screen)


class LeaderboardState(State):
    """Fake leaderboard + a BACK button."""

    SCORES: list[tuple[str, int]] = [
        ("AAA", 4200), ("BOB", 3900), ("CLI", 2100),
    ]

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.back = Button(
            "BACK", game.font_btn,
            (WIDTH // 2, HEIGHT - 60),
            on_click=lambda: game.replace(MenuState(game)),
        )

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK)
        title = self.game.font_title.render("LEADERBOARD", True, CYAN)
        screen.blit(title, title.get_rect(midtop=(WIDTH // 2, 60)))

        # Stack the score lines, vertically centered as a block.
        lines = [f"{name} ........ {score}" for name, score in self.SCORES]
        lh = self.game.font_body.get_height()
        y = HEIGHT // 2 - (len(lines) * (lh + 6)) // 2
        for line in lines:
            surf = self.game.font_body.render(line, True, WHITE)
            screen.blit(surf, surf.get_rect(midtop=(WIDTH // 2, y)))
            y += lh + 6

        self.back.draw(screen)


# --------------------------------------------------------------------------- #
#  Game                                                                        #
# --------------------------------------------------------------------------- #
class Game:
    """Owns the window, fonts, clock, and the state stack."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game States + Mouse Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        # Fonts live on the Game so every state shares them.
        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_btn = pygame.font.SysFont("arial", 28, bold=True)
        self.font_body = pygame.font.SysFont("arial", 26)
        self.stack: list[State] = [MenuState(self)]

    @property
    def current(self) -> State:
        return self.stack[-1]

    def replace(self, state: State) -> None:
        self.stack[-1] = state

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif (event.type == pygame.KEYDOWN
                        and event.key in (pygame.K_q, pygame.K_ESCAPE)):
                    self.running = False
                else:
                    self.current.handle_event(event)   # mouse + keyboard both land here
            self.current.update(dt)
            for state in self.stack:
                state.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
