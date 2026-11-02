"""State management for screens and the main game loop.

The game is a stack of :class:`State` objects.  The state on top of the
stack is the only one that receives events and updates, while every state
in the stack is drawn from bottom to top.  That makes overlays such as the
pause menu trivial: the frozen gameplay screen stays visible underneath.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from src.game import Game


class State:
    """Base class for a single screen or overlay."""

    name: str = "state"
    fills_background: bool = True

    def __init__(self, game: Game) -> None:
        """Store the game the state belongs to."""
        self.game: Game = game

    def on_enter(self) -> None:
        """Called every time the state becomes part of the stack."""

    def on_exit(self) -> None:
        """Called every time the state is removed from the stack."""

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle one input event while this state is on top."""

    def update(self, dt: float) -> None:
        """Advance the state by ``dt`` seconds while it is on top."""

    def draw(self, screen: pg.Surface) -> None:
        """Draw the state.  Must not mutate gameplay state."""

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"{type(self).__name__}()"


class StateManager:
    """Own and drive a stack of :class:`State` objects."""

    def __init__(self, game: Game) -> None:
        """Create an empty state stack for ``game``."""
        self.game: Game = game
        self._stack: list[State] = []

    def __len__(self) -> int:
        """Return the number of states in the stack."""
        return len(self._stack)

    def __bool__(self) -> bool:
        """Return whether the stack contains at least one state."""
        return bool(self._stack)

    @property
    def stack(self) -> tuple[State, ...]:
        """Return an immutable snapshot of the stack."""
        return tuple(self._stack)

    @property
    def current(self) -> State | None:
        """Return the top state, or ``None`` for an empty stack."""
        if not self._stack:
            return None
        return self._stack[-1]

    def push(self, state: State) -> None:
        """Push ``state`` on top of the stack and enter it."""
        self._stack.append(state)
        state.on_enter()

    def pop(self) -> State | None:
        """Remove and return the top state.

        Popping the last state leaves an empty stack.  The main loop treats
        that as a request to stop, so callers cannot accidentally keep a
        half-dead application alive.
        """
        if not self._stack:
            return None
        state: State = self._stack.pop()
        state.on_exit()
        return state

    def replace(self, state: State) -> None:
        """Replace the top state with ``state``."""
        if self._stack:
            old: State = self._stack.pop()
            old.on_exit()
        self.push(state)

    def reset(self, state: State) -> None:
        """Remove every state and start again with ``state``."""
        while self._stack:
            old: State = self._stack.pop()
            old.on_exit()
        self.push(state)

    def clear(self) -> None:
        """Remove every state from the stack."""
        while self._stack:
            old: State = self._stack.pop()
            old.on_exit()

    def handle_event(self, event: pg.event.Event) -> None:
        """Forward ``event`` to the top state only."""
        state: State | None = self.current
        if state is not None:
            state.handle_event(event)

    def update(self, dt: float) -> None:
        """Update the top state only."""
        state: State | None = self.current
        if state is not None:
            state.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw the whole stack from bottom to top."""
        for state in tuple(self._stack):
            state.draw(screen)
