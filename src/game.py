"""Pygame setup."""

import random
import sys

import pygame
from mazegenerator import MazeGenerator

from .models import Colors, Config

NORTH: int = 0x1
EAST: int = 0x2
SOUTH: int = 0x4
WEST: int = 0x8
ENCLOSED: int = NORTH | EAST | SOUTH | WEST

CELL_SIZE: int = 30
WALL_THICKNESS: int = 3


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
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("42PacMan")

        self.clock = pygame.time.Clock()

        while True:
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
                        print(cfg.seed)
                    if event.key == pygame.K_UP:
                        # Move up
                        print("Move up")
                    if event.key == pygame.K_DOWN:
                        # Move down
                        print("Move down")
                    if event.key == pygame.K_LEFT:
                        # Move left
                        print("Move left")
                    if event.key == pygame.K_RIGHT:
                        # Move right
                        print("Move right")
            self.screen.fill(Colors.black)
            self.render_level(self.current_maze)
            pygame.display.flip()

            self.clock.tick(60)

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
        self.pacgums = self.pacgum_locations(self.current_maze)

    def render_level(
        self,
        maze: MazeGenerator
    ) -> None:
        """Render the maze."""
        ox: int = 50
        oy: int = 50
        radius: int = 4
        for r, row in enumerate(maze.maze):
            for c, col in enumerate(row):
                x = ox + c * CELL_SIZE
                y = oy + r * CELL_SIZE

                if col & NORTH:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x, y), (x + CELL_SIZE, y),
                        WALL_THICKNESS
                    )
                if col & WEST:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x, y), (x, y + CELL_SIZE),
                        WALL_THICKNESS
                    )
                if col & SOUTH:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS
                    )
                if col & EAST:
                    pygame.draw.line(
                        self.screen, Colors.blue,
                        (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE),
                        WALL_THICKNESS
                    )

        for r, c in self.pacgums:
            cx = ox + c * CELL_SIZE + CELL_SIZE // 2
            cy = oy + r * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, Colors.orange, (cx, cy), radius)

    def pacgum_locations(self, maze: MazeGenerator) -> list[tuple[int, int]]:
        """Return all pacgum locations."""
        eligible: list[tuple[int, int]] = [
            (r, c)
            for r, row in enumerate(maze.maze)
            for c, col in enumerate(row)
            if col != ENCLOSED
        ]
        return random.sample(eligible, min(self.config.pacgum, len(eligible)))
