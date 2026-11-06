"""Game state machine: start menu, playing, pause overlay, game over.

Run:  python examples/game_states.py

Goal: show how to isolate input per state, so a key press in the pause
menu never reaches the player, and so the pause screen draws on top of a
frozen game.

There are two common ways to do this:

1.  Simple dispatcher (fine for small games):

        state = "menu"
        for event in pygame.event.get():
            if state == "playing":
                ...handle movement keys...      # only runs while playing
            elif state == "paused":
                ...handle pause keys...        # movement keys never get here

    Input is isolated purely because the movement keys live inside the
    ``state == "playing"`` branch. You can drop this straight into the
    single while-loop you already have in game.py.

2.  State objects + a stack (used below, scales to many screens).
    Each state owns its own event handling, update, and draw, so there is
    no shared input code that can leak between states. The STACK makes an
    overlay (pause) trivial: push the pause state on top, it draws over
    the game, and the game's update()/events are skipped while it is not
    on top.

Controls: SPACE start | arrows move | P pause | X die | R restart | Q quit
"""

import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)


class State:
    """Base state. Subclasses override the three methods below."""

    def __init__(self, game: "Game") -> None:
        self.game = game

    def handle_event(self, event: pygame.event.Event) -> None:
        """Called for every event while THIS state is on top of the stack."""

    def update(self, dt: float) -> None:
        """Called every frame while THIS state is on top."""

    def draw(self, screen: pygame.Surface) -> None:
        """Called every frame while THIS state is on top."""


class MenuState(State):
    """Start menu."""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Replace the menu with a fresh game.
            self.game.replace(PlayingState(self.game))

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK)
        font = pygame.font.SysFont("arial", 44, bold=True)
        prompt = font.render("PRESS SPACE TO START", True, WHITE)
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


class PlayingState(State):
    """Actual gameplay."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.x: int = WIDTH // 2
        self.y: int = HEIGHT // 2
        self.score: int = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_p:
            # Push pause ON TOP of this state. While it is on top, THIS
            # state gets no events/updates -> the keys below never fire.
            self.game.push(PauseState(self.game))
        elif event.key == pygame.K_x:
            self.game.replace(GameOverState(self.game, self.score))
        # Movement keys are handled ONLY here. That is the entire input
        # isolation guarantee: they do nothing in any other state.
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.x -= 6
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.x += 6
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.y -= 6
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.y += 6

    def update(self, dt: float) -> None:
        self.score += 1  # pretend the game is alive

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK)
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), 16)
        font = pygame.font.SysFont("arial", 22)
        text = font.render(
            f"Score: {self.score}   (P pause, X die)", True, WHITE
        )
        screen.blit(text, (10, 10))


class PauseState(State):
    """Pause overlay: a dimmed layer + menu drawn over the frozen game."""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_p, pygame.K_ESCAPE):
            self.game.pop()  # remove self -> back to PlayingState
        elif event.key == pygame.K_q:
            self.game.quit()

    def draw(self, screen: pygame.Surface) -> None:
        # We do NOT clear the screen, so the frozen PlayingState stays
        # visible underneath (see Game.run: it draws the whole stack).
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # semi-transparent black
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("arial", 48, bold=True)
        title = font.render("PAUSED", True, WHITE)
        title_rect = title.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 20)
        )
        screen.blit(title, title_rect)
        small = pygame.font.SysFont("arial", 20)
        hint = small.render("P / ESC resume    Q quit", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


class GameOverState(State):
    """Death / game-over screen."""

    def __init__(self, game: "Game", score: int) -> None:
        super().__init__(game)
        self.score = score

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_r, pygame.K_SPACE
        ):
            self.game.replace(PlayingState(self.game))

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK)
        font = pygame.font.SysFont("arial", 48, bold=True)
        title = font.render("GAME OVER", True, WHITE)
        title_rect = title.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 40)
        )
        screen.blit(title, title_rect)
        small = pygame.font.SysFont("arial", 24)
        score = small.render(f"Score: {self.score}", True, WHITE)
        score_rect = score.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 10)
        )
        screen.blit(score, score_rect)
        hint = small.render("R / SPACE restart", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))


class Game:
    """Owns the window, the clock, and the state stack."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game States Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        self.stack: list[State] = [MenuState(self)]

    @property
    def current(self) -> State:
        return self.stack[-1]

    def push(self, state: State) -> None:
        self.stack.append(state)

    def pop(self) -> None:
        self.stack.pop()

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
                else:
                    self.current.handle_event(event)  # only the top state
            self.current.update(dt)                    # only the top state
            # Draw the whole stack so an overlay (pause) sits on top of
            # the frozen state beneath it.
            for state in self.stack:
                state.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
