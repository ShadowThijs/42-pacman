"""Pygame setup and the state-driven main loop."""

import math
import random

import pygame
from mazegenerator import MazeGenerator

from .cheats import Cheats
from .db import Database
from .ghost import Ghost, GhostState, spawn_ghosts
from .models import (
    CELL_SIZE,
    OFFSET,
    WALL_THICKNESS,
    Colors,
    Config,
    Direction,
)
from .player import PacMan
from .sprites import Sprites
from .state import StateManager


class Game:
    """Game class.

    Holds pygame functions, the play session and the state stack.
    """

    def __init__(self) -> None:
        """Init Game class."""
        self.running: bool = True
        self.width: int
        self.height: int
        self.screen: pygame.Surface
        self.clock: pygame.time.Clock
        self.start_level: bool
        self.base_seed: int
        self.current_maze: MazeGenerator
        self.config: Config
        self.pacgums: set[tuple[int, int]]
        self.supergums: list[tuple[int, int]]
        self.pac: PacMan
        self.sprites: Sprites
        self.score: int = 0
        self.level: int = 1
        self.game_over: bool = False
        self.db: Database | None = None
        self.states: StateManager = StateManager(self)
        self.ghosts: list[Ghost] = []
        self.to_spawn: list[Ghost] = []
        self.spawn_timer: float = 0.0
        self.first_input: bool = False
        self._maze_layer: pygame.Surface | None = None
        self.cheats: Cheats = Cheats()

    def init_game(
        self,
        width: int,
        height: int,
        cfg: Config,
        db: Database | None = None,
    ) -> None:
        """Initialize pygame and the game session without starting the loop."""
        self.config = cfg
        self.base_seed = cfg.seed
        self.db = db
        self.running = True
        self.start_level = False
        self.game_over = False
        self.score = 0
        self.level = 1
        self.width = width
        self.height = height

        pygame.init()
        flags: int = pygame.SCALED | pygame.RESIZABLE
        try:
            self.screen = pygame.display.set_mode(
                (width, height), flags
            )
        except pygame.error:
            self.screen = pygame.display.set_mode(
                (width, height), pygame.RESIZABLE
            )
        pygame.display.set_caption("42 PACMAN")
        self.clock = pygame.time.Clock()
        self.sprites = Sprites()
        self.states = StateManager(self)

    def start_new_game(self) -> None:
        """Reset score, level and lives, then build a fresh maze."""
        self.score = 0
        self.level = 1
        self.game_over = False
        self.start_level = False
        self.new_level(self.config)
        self.start_level = True

    def reset_death(self) -> None:
        """Respawn Pac-Man and reset the ghosts after a death."""
        x, y = self._player_spawn()
        self.pac.respawn(x, y)
        self._reset_ghosts()

    def _player_spawn(self) -> tuple[float, float]:
        """Return the pixel position where Pac-Man starts a level."""
        ox, oy = OFFSET
        sr, sc = next(
            (r, c)
            for r, row in enumerate(self.current_maze.maze)
            for c, v in enumerate(row)
            if v != Direction.All
            and r > self.config.height / 2 + 1
            and c > self.config.width / 2 - 2
        )
        return (
            ox + sc * CELL_SIZE + CELL_SIZE / 2,
            oy + sr * CELL_SIZE + CELL_SIZE / 2,
        )

    def _reset_ghosts(self) -> None:
        """Queue a fresh set of ghosts, released after the next input."""
        self.ghosts = []
        self.to_spawn = spawn_ghosts(self.current_maze, self.config)
        self.spawn_timer = 0.0
        self.first_input = False

    def new_level(
        self,
        cfg: Config,
        lives: int | None = None,
    ) -> None:
        """Create a new level; pass ``lives`` to carry them over."""
        seed: int = (
            random.randint(0, 2_147_483_648)
            if self.start_level
            else self.base_seed
        )
        self.current_maze = MazeGenerator(
            (cfg.width, cfg.height), False, seed=seed
        )
        x, y = self._player_spawn()
        self.pac = PacMan(
            x,
            y,
            lives=cfg.lives if lives is None else lives,
        )
        self.pacgums = self.pacgum_locations(self.current_maze)
        self.supergums = self.supergums_location(self.current_maze)
        self._maze_layer = self._build_maze_layer()
        self._reset_ghosts()

    def _build_maze_layer(self) -> pygame.Surface:
        """Pre-render the walls once per level instead of every frame."""
        layer: pygame.Surface = pygame.Surface(
            self.screen.get_size(), pygame.SRCALPHA
        )
        ox, oy = OFFSET
        for r, row in enumerate(self.current_maze.maze):
            for c, col in enumerate(row):
                x = ox + c * CELL_SIZE
                y = oy + r * CELL_SIZE

                if col & Direction.North:
                    pygame.draw.line(
                        layer,
                        Colors.blue,
                        (x, y),
                        (x + CELL_SIZE, y),
                        WALL_THICKNESS,
                    )
                if col & Direction.West:
                    pygame.draw.line(
                        layer,
                        Colors.blue,
                        (x, y),
                        (x, y + CELL_SIZE),
                        WALL_THICKNESS,
                    )
                if col & Direction.South:
                    pygame.draw.line(
                        layer,
                        Colors.blue,
                        (x, y + CELL_SIZE),
                        (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS,
                    )
                if col & Direction.East:
                    pygame.draw.line(
                        layer,
                        Colors.blue,
                        (x + CELL_SIZE, y),
                        (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS,
                    )
        return layer

    def _draw_supergums(self) -> None:
        """Draw the pulsing power pellets."""
        ox, oy = OFFSET
        for r, c in self.supergums:
            cx: int = ox + c * CELL_SIZE + CELL_SIZE // 2
            cy: int = oy + r * CELL_SIZE + CELL_SIZE // 2
            pulse: float = (math.sin(pygame.time.get_ticks() / 150) + 1) / 2
            pygame.draw.circle(
                self.screen, Colors.purple, (cx, cy), round(8 + pulse)
            )

    def _draw_pacgums(self) -> None:
        """Draw the small pellets."""
        ox, oy = OFFSET
        for r, c in self.pacgums:
            cx: int = ox + c * CELL_SIZE + CELL_SIZE // 2
            cy: int = oy + r * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, Colors.orange, (cx, cy), 4)

    def render_level(self) -> None:
        """Draw the maze walls and pellets."""
        if (
            self._maze_layer is None
            or self._maze_layer.get_size() != self.screen.get_size()
        ):
            self._maze_layer = self._build_maze_layer()
        self.screen.blit(self._maze_layer, (0, 0))
        self._draw_supergums()
        self._draw_pacgums()

    @staticmethod
    def _walkable_tiles(
        maze: MazeGenerator,
    ) -> list[tuple[int, int]]:
        """Return every tile Pac-Man and the ghosts may enter."""
        return [
            (r, c)
            for r, row in enumerate(maze.maze)
            for c, col in enumerate(row)
            if col != Direction.All
        ]

    def pacgum_locations(
        self,
        maze: MazeGenerator,
    ) -> set[tuple[int, int]]:
        """Return the configured number of pacgum locations."""
        eligible: list[tuple[int, int]] = self._walkable_tiles(maze)
        count: int = max(0, min(self.config.pacgum, len(eligible)))
        return set(random.sample(eligible, count))

    def supergums_location(self, maze: MazeGenerator) -> list[tuple[int, int]]:
        """Return up to four super gum tiles, clear of gums and Pac-Man."""
        pac_tile: tuple[int, int] = (self.pac.row, self.pac.col)
        eligible: list[tuple[int, int]] = [
            tile
            for tile in self._walkable_tiles(maze)
            if tile not in self.pacgums and tile != pac_tile
        ]
        return random.sample(eligible, min(4, len(eligible)))

    def quit(self) -> None:
        """Quit application."""
        self.running = False

    def die(self) -> None:
        """Pac-Man was caught by a ghost."""
        self.pac.lives -= 1
        if self.pac.lives <= 0:
            self.game_over = True
            return
        self.reset_death()

    def queue_direction(self, direction: int) -> None:
        """Queue a direction and arm the ghost release schedule."""
        self.first_input = True
        self.pac.queue(direction)

    def release_ghosts(self, dt: float) -> None:
        """Release queued ghosts once their delay after input has passed."""
        if not self.first_input:
            return
        self.spawn_timer += dt
        while (
            self.to_spawn
            and self.spawn_timer >= self.to_spawn[0].release_delay
        ):
            self.ghosts.append(self.to_spawn.pop(0))

    def update(self, dt: float) -> None:
        """Advance one gameplay frame."""
        if self.game_over:
            return

        eaten: int = self.pac.update(
            dt, self.current_maze.maze, self.pacgums
        )
        self.score += eaten * self.config.pp_pacgum

        pac_tile: tuple[int, int] = (self.pac.row, self.pac.col)
        if pac_tile in self.supergums:
            self.supergums.remove(pac_tile)
            self.score += self.config.pp_super_pacgum
            for ghost in self.ghosts:
                ghost.frighten()

        self.release_ghosts(dt)

        blinky: Ghost | None = self.ghosts[0] if self.ghosts else None
        for ghost in self.ghosts:
            ghost.update(dt, self.pac, blinky)
            if self._touches_pac(ghost):
                if ghost.state == GhostState.FRIGHTENED:
                    ghost.die()
                    self.score += self.config.pp_ghost
                elif ghost.state not in (
                    GhostState.DEAD_PATHING,
                    GhostState.DEAD_WAITING,
                ):
                    self.die()
                    break

        if not self.game_over and not self.pacgums:
            self.level += 1
            self.new_level(self.config, lives=self.pac.lives)

    def _touches_pac(self, ghost: Ghost) -> bool:
        """Return whether the ghost's sprite overlaps Pac-Man's."""
        half: float = CELL_SIZE / 2
        return (
            abs(ghost.x - self.pac.x) <= half
            and abs(ghost.y - self.pac.y) <= half
        )

    def draw_actors(
        self,
        screen: pygame.Surface,
        include_pacman: bool = True,
    ) -> None:
        """Draw ghosts, and optionally Pac-Man, on top of the maze."""
        for ghost in self.ghosts:
            ghost.draw(screen, self.sprites)
        if include_pacman:
            self.pac.draw(screen, self.sprites)

    def leaderboard(self, limit: int = 10) -> list[tuple[str, int]]:
        """Return the best scores from the database."""
        if self.db is None:
            return []
        return self.db.get_leaderboard(limit)

    def best_score(self) -> int:
        """Return the best recorded score, or zero without a database."""
        entries: list[tuple[str, int]] = self.leaderboard(1)
        if not entries:
            return 0
        return entries[0][1]

    def record_score(self, name: str, score: int | None = None) -> None:
        """Store the current score in the database, if one is attached."""
        if self.db is not None:
            self.db.add_leaderboard_entry(
                name, self.score if score is None else score
            )

    def run(self) -> None:
        """Run the state-driven main loop."""
        try:
            while self.running:
                dt: float = min(self.clock.tick(60) / 1000.0, 0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                        break
                    self.states.handle_event(event)
                if not self.running:
                    break
                if not self.states:
                    self.running = False
                    break
                self.states.update(dt)
                if not self.running:
                    break
                self.states.draw(self.screen)
                pygame.display.flip()
        finally:
            pygame.quit()
