"""Pygame setup."""

import sys

import pygame

from .models import Config


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

    def init_game(self, width: int, height: int):
        """Initialize game."""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("42PacMan")

        self.clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0,0,0))

            pygame.display.flip()

            self.clock.tick(60)

    # def new_level(self, cfg: Config)
