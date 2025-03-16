import pygame
import sys
from enum import Enum, auto
from config import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BACKGROUND  # Import window dimensions from config
from title_screen import TitleScreen
from level_select import LevelSelectScreen
from gameplay import GameplayManager, GameState
from game_over_screen import GameOverScreen

class AppState(Enum):
    TITLE_SCREEN = auto()
    LEVEL_SELECT = auto()
    GAMEPLAY = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    QUIT = auto()

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Use constants from config
    pygame.display.set_caption("Mars Tower Defense")
    clock = pygame.time.Clock()
    
    # Initialize screens
    title_screen = TitleScreen()
    level_select_screen = LevelSelectScreen()
    gameplay = None
    game_over_screen = None
    
    current_state = AppState.TITLE_SCREEN
    prev_state = None  # Track previous state for transitions
    transition_timer = 0  # Add transition timer
    
    # Game loop
    while current_state != AppState.QUIT:
        dt = clock.tick(60) / 1000.0
        
        # Clear screen at start of frame to prevent smearing
        screen.fill(COLOR_BACKGROUND)
        
        # Handle state transitions
        if current_state != prev_state:
            prev_state = current_state
            transition_timer = 0.1  # Set 100ms transition guard
            if current_state == AppState.GAMEPLAY:
                # Clear all event handlers when transitioning to gameplay
                pygame.event.clear()
        
        # Update transition timer
        if transition_timer > 0:
            transition_timer = max(0, transition_timer - dt)
            
        # Process events only if not in transition
        if transition_timer <= 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    current_state = AppState.QUIT
                
                # Handle state-specific input
                if current_state == AppState.TITLE_SCREEN:
                    result = title_screen.handle_input(event)
                    if result == 'play':
                        current_state = AppState.LEVEL_SELECT
                    elif result == 'quit':
                        current_state = AppState.QUIT
                
                elif current_state == AppState.LEVEL_SELECT:
                    result = level_select_screen.handle_input(event)
                    if result:
                        if result['action'] == 'title_screen':
                            current_state = AppState.TITLE_SCREEN
                        elif result['action'] == 'start_level':
                            # Create gameplay manager with selected biome and level
                            gameplay = GameplayManager(result['biome'], result['level'])
                            current_state = AppState.GAMEPLAY
                            # Clear any remaining events
                            pygame.event.clear()
                
                elif current_state == AppState.GAMEPLAY:
                    result = gameplay.handle_input(event)
                    if result == 'menu':
                        current_state = AppState.TITLE_SCREEN
                    elif result == 'restart':
                        # Restart the current level
                        biome = gameplay.biome
                        level = gameplay.level
                        gameplay = GameplayManager(biome, level)
                
                elif current_state == AppState.GAME_OVER or current_state == AppState.VICTORY:
                    result = game_over_screen.handle_input(event)
                    if result == 'restart':
                        # Restart the current level
                        biome = gameplay.biome
                        level = gameplay.level
                        gameplay = GameplayManager(biome, level)
                        current_state = AppState.GAMEPLAY
                    elif result == 'menu':
                        current_state = AppState.LEVEL_SELECT
                    elif result == 'next_level' and current_state == AppState.VICTORY:
                        # Try to advance to next level
                        biome = gameplay.biome
                        level = gameplay.level + 1
                        # If we've reached the end of levels, go back to level select
                        if level > 15:
                            current_state = AppState.LEVEL_SELECT
                        else:
                            gameplay = GameplayManager(biome, level)
                            current_state = AppState.GAMEPLAY
        
        # Update based on current state
        if current_state == AppState.TITLE_SCREEN:
            title_screen.update(dt)
            
        elif current_state == AppState.LEVEL_SELECT:
            level_select_screen.update(dt)
            
        elif current_state == AppState.GAMEPLAY:
            game_state = gameplay.update(dt)
            
            if game_state == GameState.GAME_OVER:
                # Create game over screen with player statistics
                statistics = {
                    'Waves Survived': gameplay.wave_manager.current_wave,
                    'Towers Built': len(gameplay.towers),
                    # Add more statistics as needed
                }
                game_over_screen = GameOverScreen(False, statistics)  # False = defeat
                current_state = AppState.GAME_OVER
            
            elif game_state == GameState.VICTORY:
                # Mark the level as completed and save progress
                level_select_screen.mark_level_completed(gameplay.biome, gameplay.level)
                
                # Create victory screen with player statistics
                statistics = {
                    'Waves Completed': gameplay.wave_manager.current_wave,
                    'Towers Remaining': len(gameplay.towers),
                    # Add more statistics as needed
                }
                game_over_screen = GameOverScreen(True, statistics)  # True = victory
                current_state = AppState.VICTORY
        
        elif current_state == AppState.GAME_OVER or current_state == AppState.VICTORY:
            game_over_screen.update(dt)
        
        # Render based on current state - only draw the active screen
        if current_state == AppState.TITLE_SCREEN:
            title_screen.draw(screen)
        
        elif current_state == AppState.LEVEL_SELECT:
            level_select_screen.draw(screen)
        
        elif current_state == AppState.GAMEPLAY:
            gameplay.draw(screen)
        
        elif current_state == AppState.GAME_OVER or current_state == AppState.VICTORY:
            game_over_screen.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()