"""Ghost class."""

from __future__ import annotations

from collections import deque
from enum import Enum, auto
from typing import ClassVar

import pygame
from mazegenerator import MazeGenerator

from src.player import PacMan

from .models import (
    ANIMATION_FRAME_TIME,
    CELL_SIZE,
    DIRECTION_ORDER,
    OFFSET,
    REVERSE,
    VECTORS,
    Config,
    Direction,
    Position,
    can_move,
)
from .sprites import Sprites

GHOST_RELEASE_INTERVAL: float = 2.0


class GhostState(Enum):
    """Ghost states."""

    FROZEN = auto()
    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()
    DEAD_PATHING = auto()
    DEAD_WAITING = auto()


class Ghost:
    """Base ghost: shared movement, pathfinding and drawing.

    Subclasses set ``COLOR``, their ``CORNER`` and ``chase_target``.
    Ghosts never reverse direction at a junction unless the maze leaves
    them no other choice, which keeps their movement smooth.
    """

    COLOR: str = "red"
    CORNER: ClassVar[tuple[bool, bool]] = (True, True)
    RESPAWN_DELAY: float = 5.0
    FRIGHTENED_DURATION: float = 7.0
    FLASH_TIME: float = 2.0

    def __init__(
        self,
        maze: MazeGenerator,
        cfg: Config,
        speed: int = 80,
        spawn: Position | None = None,
    ) -> None:
        """Initialize the ghost at its spawn tile (or `spawn` if given)."""
        self.maze: MazeGenerator = maze
        self.config: Config = cfg
        self.base_speed: int = speed
        self.release_delay: float = 0.0

        self.scatter_corner: Position = self._corner(*self.CORNER)
        self.spawn_pos: Position = (
            self.scatter_corner if spawn is None else spawn
        )

        self.state: GhostState = GhostState.CHASE
        self.resume_state: GhostState = GhostState.CHASE
        self.timer: float = 0.0

        self.row: int = self.spawn_pos.row
        self.col: int = self.spawn_pos.col

        self.progress: float = 0.0
        self.direction: int | None = None
        self.reverse_allowed: bool = False
        self.facing: int = Direction.East
        self.frame: int = 1
        self.anim_t: float = 0.0
        self.anim_frame: int = 0

        self.target: Position = self.spawn_pos
        self._base_px: float = 0.0
        self._base_py: float = 0.0
        self._face_dx: float = 0.0
        self._face_dy: float = 0.0
        self._sync_geometry()

    def reset_to_spawn(self) -> None:
        """Resets ghosts to spawn after pacman dies."""
        self.state = GhostState.CHASE
        self.resume_state = GhostState.CHASE
        self.timer = 0.0

        self.row = self.spawn_pos.row
        self.col = self.spawn_pos.col
        self.target = self.spawn_pos

        self.progress = 0.0
        self.direction = None
        self.reverse_allowed = False
        self.facing = Direction.East
        self.anim_t = 0.0
        self.anim_frame = 0
        self.frame = 1
        self._sync_geometry()

    def _sync_geometry(self) -> None:
        """Cache the tile centre and facing offset used by x/y and draw."""
        ox, oy = OFFSET
        self._base_px = ox + self.col * CELL_SIZE + CELL_SIZE / 2
        self._base_py = oy + self.row * CELL_SIZE + CELL_SIZE / 2
        dx, dy = VECTORS[self.facing]
        self._face_dx = dx
        self._face_dy = dy

    def _corner(self, top: bool, left: bool) -> Position:
        """Corner tile of the maze grid: (top|bottom, left|right)."""
        height: int = len(self.maze.maze)
        width: int = len(self.maze.maze[0])
        row: int = 0 if top else height - 1
        col: int = 0 if left else width - 1
        return Position(row, col)

    def update(
        self,
        dt: float,
        pac: PacMan,
        blinky: Ghost | None,
    ) -> None:
        """Advance the ghost one frame toward its current target."""
        if self.state == GhostState.FROZEN:
            return

        self._tick_timer(dt)

        if self.state == GhostState.DEAD_WAITING:
            return

        if self.progress == 0.0:
            if self._reached_spawn():
                return
            self._decide(pac, blinky)

        if self.direction is None:
            return

        current_speed: float = float(self.base_speed)
        if self.state == GhostState.FRIGHTENED:
            current_speed *= 0.6
        elif self.state == GhostState.DEAD_PATHING:
            current_speed *= 2.0

        step: float = current_speed * dt / CELL_SIZE
        self.progress += step
        while self.progress >= 1.0:
            self.progress -= 1.0
            dx, dy = VECTORS[self.direction]
            self.col += dx
            self.row += dy
            self._sync_geometry()

            if self._reached_spawn():
                self.progress = 0.0
                return

            self._decide(pac, blinky)
            if self.direction is None:
                self.progress = 0.0
                return

        self._animate(dt)

    def _animate(self, dt: float) -> None:
        """Advance the two-frame walk cycle."""
        self.anim_t += dt
        if self.anim_t >= ANIMATION_FRAME_TIME:
            self.anim_t = 0.0
            self.anim_frame = 1 - self.anim_frame
            self.frame = self.anim_frame + 1

    def _tick_timer(self, dt: float) -> None:
        """Advance the state timer and resume normal behaviour when done."""
        if self.timer > 0.0:
            self.timer = max(0.0, self.timer - dt)
        elif self.state != GhostState.DEAD_WAITING:
            return
        if self.timer > 0.0:
            return
        if self.state in (
            GhostState.FRIGHTENED,
            GhostState.DEAD_WAITING,
        ):
            self.state = GhostState.CHASE
            self.resume_state = GhostState.CHASE
            self.reverse_allowed = False

    def _reached_spawn(self) -> bool:
        """Finish a dead ghost's trip once its eyes reach the spawn tile."""
        if self.state != GhostState.DEAD_PATHING:
            return False
        if (self.row, self.col) != (
            self.spawn_pos.row,
            self.spawn_pos.col,
        ):
            return False
        self.state = GhostState.DEAD_WAITING
        self.resume_state = GhostState.DEAD_WAITING
        self.timer = self.RESPAWN_DELAY
        return True

    def _decide(self, pac: PacMan, blinky: Ghost | None) -> None:
        """Pick the next direction, preferring the shortest forward route."""
        self.target = self.target_tile(pac, blinky)
        options: list[int] = self._open_directions()
        if not options:
            self.direction = None
            return

        back: int | None = (
            None if self.direction is None else REVERSE[self.direction]
        )
        at_target: bool = (self.row, self.col) == (
            self.target.row,
            self.target.col,
        )
        if at_target and self.state in (
            GhostState.FRIGHTENED,
            GhostState.SCATTER,
        ):
            # Once home, leave again instead of jittering in place.
            self.reverse_allowed = False

        # While chasing, avoid blind U-turns so the ghost keeps momentum.
        # A retreat target may be behind the ghost, so allow one U-turn
        # right after the target changes, then patrol smoothly.
        if self.reverse_allowed and not at_target:
            choices: list[int] = list(options)
        else:
            choices = [direction for direction in options if direction != back]
        if not choices:
            choices = options

        if len(choices) == 1:
            nxt: int | None = choices[0]
        else:
            nxt = self._shortest_direction(
                self.maze.maze,
                self.row,
                self.col,
                self.target,
                choices,
            )
            if nxt is None:
                nxt = self._nearest_direction(choices)

        if nxt is not None:
            if nxt == back:
                self.reverse_allowed = False
            self.direction = nxt
            self.facing = nxt
            self._face_dx, self._face_dy = VECTORS[nxt]

    def _open_directions(self) -> list[int]:
        """Return every direction this ghost may take from its tile."""
        return [
            direction
            for direction in DIRECTION_ORDER
            if can_move(self.maze.maze, self.row, self.col, direction)
        ]

    def _nearest_direction(self, choices: list[int]) -> int | None:
        """Fallback when the target is unreachable: head toward it.

        ``choices`` is already ordered by the classic tie-break, so the
        first direction wins whenever two options are equally close.
        """
        if not choices:
            return None
        best: int = choices[0]
        best_dist: float = float("inf")
        for direction in choices:
            dx, dy = VECTORS[direction]
            nr = self.row + dy
            nc = self.col + dx
            dist: float = (nr - self.target.row) ** 2 + (
                nc - self.target.col
            ) ** 2
            if dist < best_dist:
                best_dist = dist
                best = direction
        return best

    def target_tile(
        self,
        pac: PacMan,
        blinky: Ghost | None,
    ) -> Position:
        """Return the tile this ghost wants to reach right now.

        Frightened ghosts and returning eyes retreat to the ghost's own
        corner instead of chasing Pac-Man.
        """
        if self.state == GhostState.DEAD_PATHING:
            return self.spawn_pos
        if self.state in (GhostState.FRIGHTENED, GhostState.SCATTER):
            return self.scatter_corner
        return self.chase_target(pac, blinky)

    def _clamp(self, row: int, col: int) -> Position:
        """Clamp a target to a valid maze tile."""
        height: int = len(self.maze.maze)
        width: int = len(self.maze.maze[0])
        return Position(
            max(0, min(row, height - 1)),
            max(0, min(col, width - 1)),
        )

    def draw(self, screen: pygame.Surface, sp: Sprites) -> None:
        """Draw the ghost."""
        spr: pygame.Surface | None = self.sprite(sp)
        if spr is not None:
            screen.blit(
                spr, spr.get_rect(center=(round(self.x), round(self.y)))
            )

    def sprite(self, sp: Sprites) -> pygame.Surface | None:
        """Return the current sprite, or ``None`` if nothing is visible."""
        if self.state == GhostState.DEAD_WAITING:
            return None
        if self.is_frightened():
            is_flashing: bool = (
                self.timer < self.FLASH_TIME and int(self.timer * 4) % 2 == 0
            )
            return sp.vulnerable(white=is_flashing, frame=self.frame)
        if self.state == GhostState.DEAD_PATHING:
            return sp.eyes(self.facing)
        return sp.ghost(self.COLOR, self.facing, self.frame)

    def is_frightened(self) -> bool:
        """Return whether the ghost is edible or frozen while vulnerable."""
        return self.state == GhostState.FRIGHTENED or (
            self.state == GhostState.FROZEN
            and self.resume_state == GhostState.FRIGHTENED
        )

    @property
    def x(self) -> float:
        """Pixel x, interpolated between current tile and the next."""
        if self.direction is None:
            return self._base_px
        return self._base_px + self._face_dx * CELL_SIZE * self.progress

    @property
    def y(self) -> float:
        """Pixel y, interpolated between current tile and the next."""
        if self.direction is None:
            return self._base_py
        return self._base_py + self._face_dy * CELL_SIZE * self.progress

    @staticmethod
    def _shortest_direction(
        maze: list[list[int]],
        start_row: int,
        start_col: int,
        target: Position,
        choices: list[int],
    ) -> int | None:
        """BFS from (start_row, start_col) toward ``target``.

        Only ``choices`` may be used for the first step, which is how the
        ghost avoids blind U-turns while still taking the shortest route.
        Returns the first direction of that route, or ``None`` if no route
        exists.
        """
        if not choices or (start_row, start_col) == (
            target.row,
            target.col,
        ):
            return None

        height: int = len(maze)
        width: int = len(maze[0])
        seen: list[list[bool]] = [[False] * width for _ in range(height)]
        seen[start_row][start_col] = True

        queue: deque[tuple[int, int, int]] = deque()
        for direction in choices:
            dx, dy = VECTORS[direction]
            nr, nc = start_row + dy, start_col + dx
            if not (0 <= nr < height and 0 <= nc < width):
                continue
            if (nr, nc) == (target.row, target.col):
                return direction
            seen[nr][nc] = True
            queue.append((nr, nc, direction))

        while queue:
            row, col, first = queue.popleft()
            for direction in DIRECTION_ORDER:
                if not can_move(maze, row, col, direction):
                    continue
                dx, dy = VECTORS[direction]
                nr, nc = row + dy, col + dx
                if not (0 <= nr < height and 0 <= nc < width):
                    continue
                if seen[nr][nc]:
                    continue
                if (nr, nc) == (target.row, target.col):
                    return first
                seen[nr][nc] = True
                queue.append((nr, nc, first))
        return None

    def chase_target(
        self,
        pac: PacMan,
        blinky: Ghost | None,
    ) -> Position:
        """Target Pac-Man directly."""
        return Position(pac.row, pac.col)

    def die(self) -> None:
        """Triggered when pac-man eats this ghost."""
        self.resume_state = GhostState.DEAD_PATHING
        self.state = GhostState.DEAD_PATHING
        self.target = self.spawn_pos
        self.reverse_allowed = True

    def frighten(self) -> None:
        """Triggered when pac-man eats a super gum."""
        if self.state in (
            GhostState.DEAD_PATHING,
            GhostState.DEAD_WAITING,
        ):
            return
        if self.state == GhostState.FROZEN:
            self.resume_state = GhostState.FRIGHTENED
            return
        self.state = GhostState.FRIGHTENED
        self.resume_state = GhostState.FRIGHTENED
        self.timer = self.FRIGHTENED_DURATION
        self.reverse_allowed = True

    def freeze(self) -> None:
        """Hold the ghost in place until it is unfrozen."""
        if self.state == GhostState.FROZEN:
            return
        if self.state == GhostState.DEAD_WAITING:
            self.resume_state = GhostState.CHASE
        elif self.state == GhostState.DEAD_PATHING:
            self.resume_state = GhostState.DEAD_PATHING
        elif self.state == GhostState.FRIGHTENED:
            self.resume_state = GhostState.FRIGHTENED
        else:
            self.resume_state = self.state
        self.state = GhostState.FROZEN

    def unfreeze(self) -> None:
        """Resume the behaviour the ghost had when it was frozen."""
        if self.state != GhostState.FROZEN:
            return
        resumed: GhostState = self.resume_state
        if resumed in (GhostState.DEAD_PATHING, GhostState.DEAD_WAITING):
            self.direction = None
            self.progress = 0.0
            self.state = GhostState.DEAD_WAITING
            self.resume_state = GhostState.DEAD_WAITING
            self.timer = self.RESPAWN_DELAY
            return
        self.state = resumed
        if resumed == GhostState.FRIGHTENED:
            self.timer = self.FRIGHTENED_DURATION
            self.target = self.scatter_corner
        self.reverse_allowed = True


class Blinky(Ghost):
    """Blinky (red) ghost.

    Follows Pac-Man directly (shortest path).
    Goes to the upper-right corner in Scatter mode.
    """

    COLOR = "red"
    CORNER: ClassVar[tuple[bool, bool]] = (True, False)


class Pinky(Ghost):
    """Pinky (pink) ghost.

    Target spot 2 cells in front of Pac-Man.
        * Will target 2 up and 1 left when Pac-Man faces up.
    Goes to the upper-left corner in Scatter mode.
    """

    COLOR = "pink"
    CORNER: ClassVar[tuple[bool, bool]] = (True, True)

    def chase_target(
        self, pac: PacMan, blinky: Ghost | None = None
    ) -> Position:
        """Chase target: 2 tiles ahead of Pac-Man."""
        dx, dy = VECTORS[pac.facing]
        if pac.facing == Direction.North:
            dx -= 1
        return self._clamp(pac.row + 2 * dy, pac.col + 2 * dx)


class Inky(Ghost):
    """Inky (cyan) ghost.

    Target is relative to both Blinky and Pac-Man: the vector from
    Blinky to Pinky's target is doubled.
    Goes to the lower-right corner in Scatter mode.
    """

    COLOR = "cyan"
    CORNER: ClassVar[tuple[bool, bool]] = (False, False)

    def chase_target(self, pac: PacMan, blinky: Ghost | None) -> Position:
        """Chase Pac-Man based on Blinky and Inky."""
        if blinky is None:
            return Position(0, 0)
        dx, dy = VECTORS[pac.facing]
        if pac.facing == Direction.North:
            dx = -1

        pivot_row = pac.row + 2 * dy
        pivot_col = pac.col + 2 * dx
        return self._clamp(
            2 * pivot_row - blinky.row,
            2 * pivot_col - blinky.col,
        )


class Clyde(Ghost):
    """Clyde (orange) ghost.

    Targets Pac-Man directly, but retreats to his corner when he gets
    too close (within eight tiles), then comes back for another try.
    Goes to the lower-left corner in Scatter mode.
    """

    COLOR = "orange"
    CORNER: ClassVar[tuple[bool, bool]] = (False, True)
    SHY_RADIUS: ClassVar[int] = 8

    def chase_target(
        self, pac: PacMan, blinky: Ghost | None = None
    ) -> Position:
        """Chase Pac-Man but retreat when he is close."""
        dist_sq: int = (self.row - pac.row) ** 2 + (self.col - pac.col) ** 2
        if dist_sq < self.SHY_RADIUS**2:
            return self.scatter_corner
        return Position(pac.row, pac.col)


def spawn_ghosts(maze: MazeGenerator, cfg: Config) -> list[Ghost]:
    """Create the four ghosts, one in each maze corner."""
    ghosts: list[Ghost] = [
        Blinky(maze, cfg),
        Pinky(maze, cfg),
        Inky(maze, cfg),
        Clyde(maze, cfg),
    ]
    for index, ghost in enumerate(ghosts):
        ghost.release_delay = (index + 1) * GHOST_RELEASE_INTERVAL
    return ghosts
