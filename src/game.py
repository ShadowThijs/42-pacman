"""Pygame setup."""

import random
import sys

import pygame
from mazegenerator import MazeGenerator

from .models import (
    CELL_SIZE, OFFSET, WALL_THICKNESS,
    Colors, Config, Direction
)
from .player import PacMan
from .sprites import Sprites


class Game:
    """Game class.

    Holds pygame functions and setup
    """

    def __init__(self) -> None:
        """Init Game class."""
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

    def init_game(
        self,
        width: int,
        height: int,
        cfg: Config
    ) -> None:
        """Initialize game."""
        self.start_level = False
        self.new_level(cfg)
        self.start_level = True
        self.sprites = Sprites()
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("42PacMan")

        self.clock = pygame.time.Clock()

        while True:
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
                        self.new_level(cfg)
                    if event.key == pygame.K_UP:
                        self.pac.queue(Direction.North)
                    if event.key == pygame.K_DOWN:
                        self.pac.queue(Direction.South)
                    if event.key == pygame.K_LEFT:
                        self.pac.queue(Direction.West)
                    if event.key == pygame.K_RIGHT:
                        self.pac.queue(Direction.East)
            self.screen.fill(Colors.black)
            self.render_level(self.current_maze)
            self.pac.update(dt, self.current_maze.maze)
            self.pac.draw(self.screen, self.sprites)
            pygame.display.flip()

    def new_level(
        self,
        cfg: Config
    ) -> None:
        """Create new level."""
        if self.start_level:
            cfg.seed = random.randint(0, 2_147_483_648)
        self.current_maze = MazeGenerator(
            (cfg.width, cfg.height),
            False,
            seed=cfg.seed
        )
        self.config = cfg
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
        self.pacgums = self.pacgum_locations(self.current_maze)

    def render_level(
        self,
        maze: MazeGenerator
    ) -> None:
        """Render the maze."""
        ox, oy = OFFSET
        radius: int = 4
        for r, row in enumerate(maze.maze):
            for c, col in enumerate(row):
                x = ox + c * CELL_SIZE
                y = oy + r * CELL_SIZE

                if col & Direction.North:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x, y), (x + CELL_SIZE, y),
                        WALL_THICKNESS
                    )
                if col & Direction.West:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x, y), (x, y + CELL_SIZE),
                        WALL_THICKNESS
                    )
                if col & Direction.South:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS
                    )
                if col & Direction.East:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS
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
