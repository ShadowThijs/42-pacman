"""State manager.

Manages the state of pygame.
"""

from typing import Any

import pygame as pg

from src.game import Game


class State:
    """State."""

    def __init__(self, name: str, game: Game) -> None:
        """Init."""
        self.name: str = name
        self.game: Game = game
        print("Init state")

    def handle_event(self, event: Any) -> None:
        """Handle event."""
        print(f"Handling event for: {self.name}")

    def update(self, dt: float) -> None:
        """Update state."""
        print(f"Handling update for: {self.name}")

    def draw(self, screen: pg.Surface) -> None:
        """Draw current state."""
        print(f"Drawing {self.name} now")


class StartMenu(State):
    """Start menu class."""

    def handle_event(self, event: Any) -> None:
        """Handle event."""

    def update(self, dt: float) -> None:
        """Update."""

    def draw(self, screen: pg.Surface) -> None:
        """Draw."""


class PauseMenu(State):
    """Pause menu class."""

    def handle_event(self, event: Any) -> None:
        """Handle event."""

    def update(self, dt: float) -> None:
        """Update."""

    def draw(self, screen: pg.Surface) -> None:
        """Draw."""


class GameState(State):
    """Game state class."""

    def handle_event(self, event: Any) -> None:
        """Handle event."""

    def update(self, dt: float) -> None:
        """Update."""

    def draw(self, screen: pg.Surface) -> None:
        """Draw."""


class StateManager:
    """State manager class."""

    def __init__(self) -> None:
        """Init."""
        self.stack: list[State] = []
        print("Init statemanager")

    def push(self, state: State) -> None:
        """Push state."""
        print(f"Pushing state: {state.name}")
        self.stack.append(state)

    def pop(self) -> None:
        """Pop state."""
        print(f"Popping state: {self.stack[len(self.stack) - 1].name}")
        self.stack.pop()

    def replace(self, state: State) -> None:
        """Replace top state."""
        self.pop()
        self.push(state)

    def current(self) -> State:
        """Current state."""
        length: int = len(self.stack) - 1
        return self.stack[length]

    def handle_event(self, event: Any) -> None:
        """Forward event to current event."""
        current: State = self.current()
        current.handle_event(event)

    def update(self, dt: float) -> None:
        """Update current state."""
        current: State = self.current()
        current.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw current state."""
        current: State = self.current()
        current.draw(screen)


# class State:
#     """State class handler."""
#
#     def __init__(self, game: Game) -> None:
#         """Init state."""
#         self.game: Game = game
#
#     def handle_event(self, event: pg.event.Event) -> None:
#         """Handle events."""
#
#     def update(self) -> None:
#         """Update State."""
#
#     def draw(self, screen: pg.Surface) -> None:
#         """Draw to screen in state."""
#
#
# class StartMenu(State):
#     """Start menu class."""
#
#     def handle_event(self, event: pg.event.Event) -> None:
#         """Handle key events."""
#         if event.type == pg.KEYDOWN:
#             if event.key == pg.K_SPACE:
#                 print("Starting game")
#             if event.key == pg.K_l:
#                 print("Going to leaderboard")
#
#
# class PauseMenu(State):
#     """Pause menu class."""
#
#     def handle_event(self, event: pg.event.Event) -> None:
#         """Handle Pause menu key events."""
#         if event.type != pg.KEYDOWN:
#             return
#         if event.key == pg.K_p:
#             return
#
#
# class GameState(State):
#     """Playing game state class."""
#
#     def __init__(self, game: Game) -> None:
#         """Init Game state."""
#         super().__init__(game)
#         self.x: int = game.config.width // 2
#         self.y: int = game.config.height // 2
#         self.score: int = 0
#
#     def handle_event(self, event: pg.event.Event) -> None:
#         """Handle input during Game state."""
#         if event.type != pg.KEYDOWN:
#             return
#         key: Any = event.key
#         if key == pg.K_q:
#             self.game.running = False
#         if key == pg.K_r:
#             self.game.new_level(self.game.config)
#         if key == pg.K_p:
#             self.game.push(PauseMenu(self.game))
#         if key == pg.K_UP:
#             self.game.pac.queue(Direction.North)
#         if key == pg.K_RIGHT:
#             self.game.pac.queue(Direction.East)
#         if key == pg.K_DOWN:
#             self.game.pac.queue(Direction.South)
#         if key == pg.K_LEFT:
#             self.game.pac.queue(Direction.West)
#
#     def draw(self, screen: pg.Surface) -> None:
#         """Drawing this state."""
#         dt: float = min(self.game.clock.tick(60) / 1000, 0.05)
#         self.game.screen.fill(Colors.black)
#         self.game.render_level(self.game.current_maze)
#         eaten: int = self.game.pac.update(
#             dt, self.game.current_maze.maze, self.game.pacgums
#         )
#         self.game.score += eaten * self.game.config.pp_pacgum
#         if not self.game.pacgums:
#             self.game.new_level(self.game.config)
#         self.game.pac.draw(self.game.screen, self.game.sprites)
#         pg.display.flip()


if __name__ == "__main__":
    # Run the excluded state tests here
    print("running states.py")
    game: Game = Game()
    first: State = State("first", game)
    second: State = State("second", game)

    def _test() -> None:
        print("test")

    manager: StateManager = StateManager()
    manager.push(first)
    manager.replace(second)
    print(f"current: {manager.current().name}")
    manager.push(first)
    manager.handle_event(_test)
    manager.update(1.0)
