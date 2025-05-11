import pygame
import sys
from classes.game import Game

def main():
    pygame.init()

    BOARD_SIZE = 800
    MENU_WIDTH = 200
    WIDTH, HEIGHT = BOARD_SIZE + MENU_WIDTH, BOARD_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Enhanced Chess Game for Beginners")
    clock = pygame.time.Clock()

    game = Game(screen, BOARD_SIZE, BOARD_SIZE, MENU_WIDTH)
    game.start_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.process_input(event)

        game.update_game()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
