import pygame
import sys
from config import *
from title_screen import run_title_screen
from level_select import run_level_select
from gameplay import GameplayManager
from game_over_screen import run_game_over_screen

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Deep Sea TD")
    clock = pygame.time.Clock()
    
    # Game state
    current_state = GameState.TITLE
    selected_biome = None
    current_level = None
    gameplay = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if gameplay and current_state == GameState.GAMEPLAY:
                gameplay.handle_input(event)
                
        if current_state == GameState.TITLE:
            result = run_title_screen(screen)
            if result == 0:  # Play selected
                selected_biome = Biome.HYDROTHERMAL  # For now, start with Hydrothermal
                current_state = GameState.LEVEL_SELECT
            elif result == 1:  # Settings
                pass  # TODO: Implement settings
            elif result == 2:  # Quit
                break
                
        elif current_state == GameState.LEVEL_SELECT:
            selected_level = run_level_select(screen)
            if selected_level is None:
                current_state = GameState.TITLE
            else:
                current_level = selected_level
                gameplay = GameplayManager(selected_biome, current_level)
                current_state = GameState.GAMEPLAY
                
        elif current_state == GameState.GAMEPLAY:
            dt = clock.tick(60) / 1000.0
            result = gameplay.update(dt)
            
            if result == GameState.VICTORY:
                current_state = GameState.VICTORY
            elif result == GameState.GAME_OVER:
                current_state = GameState.GAME_OVER
            else:
                screen.fill(COLOR_BG)
                gameplay.draw(screen)
                pygame.display.flip()
                
        elif current_state in [GameState.VICTORY, GameState.GAME_OVER]:
            is_victory = (current_state == GameState.VICTORY)
            result = run_game_over_screen(screen, is_victory)
            
            if result == 'restart':
                gameplay = GameplayManager(selected_biome, current_level)
                current_state = GameState.GAMEPLAY
            else:  # Back to menu
                current_state = GameState.TITLE
                
        # Ensure display is updated
        if current_state != GameState.GAMEPLAY:  # Gameplay handles its own display updates
            pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()