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
        print(self.current_maze.maze)
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

    def render_level(
        self,
        maze: MazeGenerator
    ) -> None:
        """Render the maze."""
        for r, row in enumerate(maze.maze):
            for c, col in enumerate(row):
                if col & NORTH:
                    pygame.draw.rect(
                        self.screen,
                        Colors.white,
                        (
                            c * 20 + 50,
                            r * 20 + 50 - 10,
                            10,
                            10
                        )
                    )
                if col & EAST:
                    pygame.draw.rect(
                        self.screen,
                        Colors.white,
                        (
                            c * 20 + 50 + 10,
                            r * 20 + 50,
                            10,
                            10
                        )
                    )
                if col & SOUTH:
                    pygame.draw.rect(
                        self.screen,
                        Colors.white,
                        (
                            c * 20 + 50,
                            r * 20 + 50 + 10,
                            10,
                            10
                        )
                    )
                if col & WEST:
                    pygame.draw.rect(
                        self.screen,
                        Colors.white,
                        (
                            c * 20 + 50 - 10,
                            r * 20 + 50,
                            10,
                            10
                        )
                    )
                pygame.draw.rect(
                    self.screen,
                    Colors.red,
                    (
                        c * 20 + 50,
                        r * 20 + 50,
                        10,
                        10
                    )
                )
