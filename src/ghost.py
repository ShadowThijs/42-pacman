"""Ghost class."""

from __future__ import annotations

import random
from collections import deque
from enum import Enum, auto

import pygame
from mazegenerator import MazeGenerator

from src.player import PacMan

from .models import CELL_SIZE, OFFSET, Config, Direction, Position
from .sprites import Sprites

VECTORS: dict[int, tuple[int, int]] = {
    Direction.North: (0, -1),
    Direction.South: (0, 1),
    Direction.East: (1, 0),
    Direction.West: (-1, 0),
}

REVERSE: dict[int, int] = {
    Direction.North: Direction.South,
    Direction.South: Direction.North,
    Direction.East: Direction.West,
    Direction.West: Direction.East,
}

SWITCH_DT: float = 0.2
# Seconds between each ghost's release after Pac-Man's first input.
GHOST_RELEASE_INTERVAL: float = 2.0


class GhostState(Enum):
    """Ghost states."""
    CHASE = auto()  # normal behaviour, hunting pac-man
    SCATTER = auto()  # normal behaviour, going to their corner
    FRIGHTENED = auto()  # blue and edible (super gum)
    DEAD_PATHING = auto()  # floating eyes returning to spawn
    DEAD_WAITING = auto()  # reached corner, waiting for 5 sec to respawn


class Ghost:
    """Base ghost: shared movement, pathfinding and drawing.

    Subclasses only need to set COLOR and override ``_spawn_tile()``
    to choose their start position. The tile they hunt is set per
    frame through the ``target`` attribute.
    """

    COLOR: str = "red"
    RESPAWN_DELAY: float = 5.0  # for 5-10s before respawining
    FRIGHTENED_DURATION: float = 7.0  # how long the ghosts stay blue

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
        # seconds after Pac-Man's first input before this ghost appears
        self.release_delay: float = 0.0

        # start by going to corners
        self.state: GhostState = GhostState.SCATTER
        self.timer: float = 0.0

        # save the spawn position so we can return when we're dead
        self.spawn_pos: Position = (
            spawn if spawn is not None else self._spawn_tile()
        )
        self.row: int = self.spawn_pos.row
        self.col: int = self.spawn_pos.col

        self.progress: float = 0.0
        self.direction: int | None = None
        self.facing: int = Direction.East
        self.frame: int = 1
        self.anim_t: float = 0.0
        self.anim_frame: int = 0

        # target start as the spawn position
        self.target: Position = self.spawn_pos

    def reset_to_spawn(self) -> None:
        """Resets ghosts to spawn after pacman dies."""
        self.state = GhostState.SCATTER
        self.timer = 0.0

        self.row = self.spawn_pos.row
        self.col = self.spawn_pos.col
        self.target = self.spawn_pos

        self.progress = 0.0
        self.direction = None
        self.facing = Direction.East

    def _spawn_tile(self) -> Position:
        """Start tile of this ghost type; default is the top-left corner."""
        return self._corner(top=True, left=True)

    def _corner(self, top: bool, left: bool) -> Position:
        """Corner tile of the maze grid: (top|bottom, left|right)."""
        height: int = len(self.maze.maze)
        width: int = len(self.maze.maze[0])
        row: int = 0 if top else height - 1
        col: int = 0 if left else width - 1
        return Position(row, col)

    def update(self, dt: float) -> None:
        """Advance the ghost one frame toward its target."""
        # deacrease timer if active, and revert state when time is up
        if self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0.0
                if (
                    self.state in (
                        GhostState.FRIGHTENED,
                        GhostState.DEAD_WAITING
                    )
                ):
                    self.state = GhostState.CHASE

        if self.state == GhostState.DEAD_WAITING:
            return

        if self.progress == 0.0:
            self._decide()

        if self.direction is None:
            return

        # use current_speed instead of based on state (slower for frightened)
        current_speed: float = float(self.base_speed)
        if self.state == GhostState.FRIGHTENED:
            current_speed *= 0.6  # 40% slower when edible
        elif self.state == GhostState.DEAD_PATHING:
            current_speed *= 2.0

        step: float = current_speed * dt / CELL_SIZE
        self.progress += step
        while self.progress >= 1.0:
            self.progress -= 1.0
            dx, dy = VECTORS[self.direction]
            self.col += dx
            self.row += dy

            if (
                (self.state == GhostState.DEAD_PATHING)
                and (self.row == self.spawn_pos.row)
                and (self.col == self.spawn_pos.col)
            ):
                self.state = GhostState.DEAD_WAITING
                # wait 5 seconds before reviving
                self.timer = self.RESPAWN_DELAY
                self.progress = 0.0
                return

            self._decide()
            if self.direction is None:
                self.progress = 0.0
                return

        self.anim_t += dt
        if self.anim_t >= SWITCH_DT:
            self.anim_t = 0.0
            self.anim_frame = 1 - self.anim_frame
        self.frame = self.anim_frame + 1

    def _decide(self) -> None:
        """Pick the direction on the shortest path to the target."""
        nxt: int | None = None

        if self.state == GhostState.FRIGHTENED:
            nxt = self._random_direction()
        else:
            nxt = self._shortest_direction(
                self.maze.maze, Position(self.row, self.col), self.target
            )

            if nxt is None:
                nxt = self._nearest_direction()
        if nxt is not None:
            self.direction = nxt
            self.facing = nxt
        if self.direction is not None and not self._open(
            self.maze.maze, self.row, self.col, self.direction
        ):
            self.direction = None

    def _nearest_direction(self) -> int | None:
        """Fallback when the target is unreachable: head toward it.

        No U-turns at intersections, but they are allowed in dead ends.
        """
        forbidden: int | None = (
            REVERSE[self.direction] if self.direction is not None else None
        )
        best: int | None = None
        best_dist: float = float("inf")
        for direction, (dx, dy) in VECTORS.items():
            if direction == forbidden:
                continue
            if not self._open(self.maze.maze, self.row, self.col, direction):
                continue
            nr, nc = self.row + dy, self.col + dx
            dist: float = (nr - self.target.row) ** 2 + (
                nc - self.target.col
            ) ** 2
            if dist < best_dist:
                best_dist = dist
                best = direction
        if (
            best is None
            and forbidden is not None
            and self._open(self.maze.maze, self.row, self.col, forbidden)
        ):
            return forbidden
        return best

    def _random_direction(self) -> int | None:
        """Used in frightened state to wander randomly at intersections."""
        forbidden: int | None = (
            REVERSE[self.direction] if self.direction is not None else None
        )
        possible_moves: list[int] = []

        for direction in VECTORS:
            if direction == forbidden:
                continue
            if self._open(self.maze.maze, self.row, self.col, direction):
                possible_moves.append(direction)

        if (
            not possible_moves
            and forbidden is not None
            and self._open(self.maze.maze, self.row, self.col, forbidden)
        ):
            return forbidden
        elif possible_moves:
            return random.choice(possible_moves)
        return None

    def draw(self, screen: pygame.Surface, sp: Sprites) -> None:
        """Draw the ghost."""
        if self.state == GhostState.DEAD_WAITING:
            return

        spr: pygame.Surface

        timer: float = 2.0
        if self.state == GhostState.FRIGHTENED:
            is_flashing: bool = (
                self.timer < timer and int(self.timer * 4) % 2 == 0
            )
            spr = sp.vulnerable(white=is_flashing, frame=self.frame)

        elif self.state == GhostState.DEAD_PATHING:
            spr = sp.eyes(self.facing)

        else:
            spr = sp.ghost(self.COLOR, self.facing, self.frame)
        screen.blit(spr, (self.x - 16, self.y - 16))

    @property
    def x(self) -> float:
        """Pixel x, interpolated between current tile and the next."""
        ox, _ = OFFSET
        base: float = ox + self.col * CELL_SIZE + CELL_SIZE / 2
        if self.direction is None:
            return base
        return base + VECTORS[self.direction][0] * CELL_SIZE * self.progress

    @property
    def y(self) -> float:
        """Pixel y, interpolated between current tile and the next."""
        _, oy = OFFSET
        base: float = oy + self.row * CELL_SIZE + CELL_SIZE / 2
        if self.direction is None:
            return base
        return base + VECTORS[self.direction][1] * CELL_SIZE * self.progress

    @staticmethod
    def _open(
        maze: list[list[int]], row: int, col: int, direction: int
    ) -> bool:
        """No wall on `direction`'s side of cell (row, col)."""
        return maze[row][col] & direction == 0

    @staticmethod
    def _shortest_direction(
        maze: list[list[int]],
        start: Position,
        target: Position,
    ) -> int | None:
        """BFS from `start` to `target`; return the first step direction."""
        if start == target:
            return None
        visited: dict[Position, tuple[Position, int]] = {start: (start, 0)}
        queue: deque[Position] = deque([start])
        while queue:
            pos = queue.popleft()
            for direction, (dx, dy) in VECTORS.items():
                if maze[pos.row][pos.col] & direction:
                    continue
                nxt = Position(pos.row + dy, pos.col + dx)
                if not (
                    0 <= nxt.row < len(maze) and 0 <= nxt.col < len(maze[0])
                ):
                    continue
                if nxt in visited:
                    continue
                visited[nxt] = (pos, direction)
                if nxt == target:
                    cur = nxt
                    while visited[cur][0] != start:
                        cur = visited[cur][0]
                    return visited[cur][1]
                queue.append(nxt)
        return None

    def chase_target(
        self,
        pac: PacMan,
        blinky: Ghost | None
    ) -> Position:
        """Target Pacman."""
        return Position(pac.row, pac.col)

    def die(self) -> None:
        """Trigegered when pac-man eats this ghost."""
        self.state = GhostState.DEAD_PATHING
        self.target = self.spawn_pos  # set target back to their home corner


class Blinky(Ghost):
    """Blinky (red) ghost.

    Follows Pac-Man directly (shortest path)
    Goes to the upper-right corner in Scatter mode
    """

    COLOR: str = "red"

    def _spawn_tile(self) -> Position:
        return self._corner(top=True, left=False)

    def chase_target(
        self,
        pac: PacMan,
        blinky: Ghost | None = None
    ) -> Position:
        """Target Pacman directly."""
        return Position(pac.row, pac.col)


class Pinky(Ghost):
    """Pinky (pink) ghost.

    Target spot 2 cells in front of Pac-Man
        * Will target 2 to the left when Pac-Man faces up
    Goes to upper-left corner in Scatter mode
    """

    COLOR: str = "pink"

    def _spawn_tile(self) -> Position:
        return self._corner(top=True, left=True)

    def chase_target(
        self, pac: PacMan, blinky: Ghost | None = None
    ) -> Position:
        """Chase target: 2 tiles ahead of the pac-man."""
        dx, dy = VECTORS[pac.facing]
        if pac.facing == Direction.North:
            dx -= 1
        row = pac.row + 2 * dy
        col = pac.col + 2 * dx

        row = max(0, min(row, len(self.maze.maze) - 1))
        col = max(0, min(col, len(self.maze.maze[0]) - 1))

        return Position(row, col)


class Inky(Ghost):
    """Inky (cyan) ghost.

    Target is relative to both Blinky and Pac-Man,
        where the distance Blinky is from Pinky's target
        is doubled to get Inky's target
    Goes to the lower-right corner in Scatter mode
    """

    COLOR: str = "cyan"

    def _spawn_tile(self) -> Position:
        return self._corner(top=False, left=False)

    def chase_target(self, pac: PacMan, blinky: Ghost | None) -> Position:
        """Chase pacman based on Blink & Inky."""
        if blinky is None:
            return Position(0, 0)
        dx, dy = VECTORS[pac.facing]
        if pac.facing == Direction.North:
            dx = -1

        pivot_row = pac.row + 2 * dy
        pivot_col = pac.col + 2 * dx

        row = 2 * pivot_row - blinky.row
        col = 2 * pivot_col - blinky.col

        row = max(0, min(row, len(self.maze.maze) - 1))
        col = max(0, min(col, len(self.maze.maze[0]) - 1))

        return Position(row, col)


class Clyde(Ghost):
    """Clyde (orange) ghost.

    Target is Pac-Man directly, but tries to target,
        Scatter corner when within 8 cell radius of Pac-Man
    Goes to lower-left in Scatter mode
    """

    COLOR: str = "orange"

    def _spawn_tile(self) -> Position:
        return self._corner(top=False, left=True)

    def chase_target(
        self, pac: PacMan, blinky: Ghost | None = None
    ) -> Position:
        """Chase pacman but shy."""
        dist_sq = (self.row - pac.row) ** 2 + (self.col - pac.col) ** 2

        if dist_sq < 3**2:
            return self._spawn_tile()
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
