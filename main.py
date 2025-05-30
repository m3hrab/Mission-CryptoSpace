import pygame
import sys
from core import GameManager

def main():
    # Initialize Pygame and set up the game window
    pygame.init()
    pygame.display.set_caption("Mission CryptoSpace (Crypternity)")
    game = GameManager() 
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()