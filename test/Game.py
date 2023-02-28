import pygame
import sys

from overworld import Overworld
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class Game:
    def __init__(self):
        self.max_level = 5
        self.overworld = Overworld(0, self.max_level, screen, 0)

    def run(self):
        self.overworld.run()


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('grey')
    game.run()

    pygame.display.update()
    clock.tick(60)
