"""State manager.

Manages the state of pygame.
"""

import pygame as pg

from src.game import Game


class State:
    """State."""

    def __init__(self, name: str, game: Game) -> None:
        """Init."""
        self.name: str = name
        self.game: Game = game
        print("Init state")

    def handle_event(self, e) -> None:
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

    def handle_event(self, e) -> None:
        """Handle event."""

    def update(self, dt: float) -> None:
        """Update."""

    def draw(self, screen: pg.Surface) -> None:
        """Draw."""


class PauseMenu(State):
    """Pause menu class."""

    def handle_event(self, e) -> None:
        """Handle event."""

    def update(self, dt: float) -> None:
        """Update."""

    def draw(self, screen: pg.Surface) -> None:
        """Draw."""


class GameState(State):
    """Game state class."""

    def handle_event(self, e) -> None:
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

    def handle_event(self, e) -> None:
        """Forward event to current event."""
        current: State = self.current()
        current.handle_event(e)

    def update(self, dt: float) -> None:
        """Update current state."""
        current: State = self.current()
        current.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw current state."""
        current: State = self.current()
        current.draw(screen)


if __name__ == "__main__":
    # Run the excluded state tests here
    print("running states.py")
    game: Game = Game()
    first: State = State("first", game)
    second: State = State("second", game)

    manager: StateManager = StateManager()
    manager.push(first)
    manager.replace(second)
    print(f"current: {manager.current().name}")
    manager.push(first)
    manager.handle_event("test")
    manager.update(1.0)
