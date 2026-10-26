"""Pygame setup."""

import random
import sys

import pygame
from mazegenerator import MazeGenerator

from .ghost import Ghost, spawn_ghosts
from .models import (
    CELL_SIZE,
    OFFSET,
    WALL_THICKNESS,
    Colors,
    Config,
    Direction,
    # State,
)
from .player import PacMan
from .sprites import Sprites


class Game:
    """Game class.

    Holds pygame functions and setup
    """

    def __init__(self) -> None:
        """Init Game class."""
        self.running = True
        self.width: int
        self.height: int
        self.screen: pygame.Surface
        self.clock: pygame.time.Clock
        self.start_level: bool
        self.current_maze: MazeGenerator
        self.config: Config
        self.pacgums: list[tuple[int, int]]
        self.pac: PacMan
        self.sprites: Sprites
        self.score: int = 0
        # self.stack: list[State]
        self.ghosts: list[Ghost] = []
        self.to_spawn: list[Ghost] = []
        self.spawn_timer: float = 0.0

    def init_game(self, width: int, height: int, cfg: Config) -> None:
        """Initialize game."""
        self.config = cfg
        self.start_level = False
        self.new_level(cfg)
        self.start_level = True
        self.sprites = Sprites()
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("42PacMan")

        self.clock = pygame.time.Clock()

        self.run()

    def new_level(self, cfg: Config) -> None:
        """Create new level."""
        if self.start_level:
            cfg.seed = random.randint(0, 2_147_483_648)
        self.current_maze = MazeGenerator(
            (cfg.width, cfg.height), False, seed=cfg.seed
        )
        ox, oy = OFFSET
        sr, sc = next(
            (r, c)
            for r, row in enumerate(self.current_maze.maze)
            for c, v in enumerate(row)
            if v != Direction.All
            and r > cfg.height / 2 + 1
            and c > cfg.width / 2 - 2
        )
        self.pac = PacMan(
            ox + sc * CELL_SIZE + CELL_SIZE / 2,
            oy + sr * CELL_SIZE + CELL_SIZE / 2,
        )
        self.ghosts = []
        self.to_spawn = spawn_ghosts(self.current_maze, self.config)
        self.spawn_timer = 0.0
        self.pacgums = self.pacgum_locations(self.current_maze)

    def render_level(self, maze: MazeGenerator) -> None:
        """Render the maze."""
        ox, oy = OFFSET
        radius: int = 4
        for r, row in enumerate(maze.maze):
            for c, col in enumerate(row):
                x = ox + c * CELL_SIZE
                y = oy + r * CELL_SIZE

                if col & Direction.North:
                    pygame.draw.line(
                        self.screen,
                        Colors.blue,
                        (x, y),
                        (x + CELL_SIZE, y),
                        WALL_THICKNESS,
                    )
                if col & Direction.West:
                    pygame.draw.line(
                        self.screen,
                        Colors.blue,
                        (x, y),
                        (x, y + CELL_SIZE),
                        WALL_THICKNESS,
                    )
                if col & Direction.South:
                    pygame.draw.line(
                        self.screen,
                        Colors.blue,
                        (x, y + CELL_SIZE),
                        (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS,
                    )
                if col & Direction.East:
                    pygame.draw.line(
                        self.screen,
                        Colors.blue,
                        (x + CELL_SIZE, y),
                        (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS,
                    )

        for r, c in self.pacgums:
            cx: int = ox + c * CELL_SIZE + CELL_SIZE // 2
            cy: int = oy + r * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, Colors.orange, (cx, cy), radius)

    def pacgum_locations(self, maze: MazeGenerator) -> list[tuple[int, int]]:
        """Return all pacgum locations."""
        eligible: list[tuple[int, int]] = [
            (r, c)
            for r, row in enumerate(maze.maze)
            for c, col in enumerate(row)
            if col != Direction.All
        ]
        return random.sample(eligible, min(self.config.pacgum, len(eligible)))

    def quit(self) -> None:
        """Quit application."""
        self.running = False

    def die(self) -> None:
        """pac-man was caught by ghost"""
        self.running = False

    def run(self) -> None:
        """Run the game."""
        while self.running:
            dt: float = min(self.clock.tick(60) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self.new_level(self.config)
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.pac.queue(Direction.North)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.pac.queue(Direction.South)
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.pac.queue(Direction.West)
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.pac.queue(Direction.East)
            self.screen.fill(Colors.black)
            self.render_level(self.current_maze)
            eaten: int = self.pac.update(
                dt, self.current_maze.maze, self.pacgums
            )
            self.spawn_timer += dt
            if self.to_spawn and self.spawn_timer >= 2.0:
                self.ghosts.append(self.to_spawn.pop(0))
                self.spawn_timer = 0.0

            blinky = self.ghosts[0] if self.ghosts else None
            for ghost in self.ghosts:
                ghost.target = ghost.chase_target(self.pac, blinky)
                ghost.update(dt)
                if ghost.row == self.pac.row and ghost.col == self.pac.col:
                    self.die()
                    break
                ghost.draw(self.screen, self.sprites)
            self.score += eaten * self.config.pp_pacgum
            if not self.pacgums:
                self.new_level(self.config)
            self.pac.draw(self.screen, self.sprites)
            pygame.display.flip()
        pygame.quit()
        sys.exit()
