import pygame
import sys
from core import GameManager

if __name__ == "__main__":
    pygame.init()
    game = GameManager()
    game.run()
    pygame.quit()
    sys.exit()