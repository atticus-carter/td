import pygame
from config import *
from ui import Button

class GameOverScreen:
    """Screen displayed when the game ends (either victory or defeat)"""
    def __init__(self, is_victory, statistics=None):
        self.is_victory = is_victory
        self.statistics = statistics or {}  # Statistics to display (kills, waves survived, etc.)
        
        # Setup fonts
        self.title_font = get_font(FONT_SIZE_LARGE)
        self.subtitle_font = get_font(FONT_SIZE_MEDIUM)
        self.text_font = get_font(FONT_SIZE_SMALL)
        
        # Create buttons using the Button component
        restart_color = (0, 150, 0) if self.is_victory else (150, 0, 0)
        self.restart_button = Button(
            pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 50, 200, 50),
            "Play Again",
            color=restart_color
        )
        self.menu_button = Button(
            pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 120, 200, 50),
            "Main Menu",
            color=(50, 50, 100)
        )
        
        # Additional visual elements
        self.flash_alpha = 255
        self.message_alpha = 0
        self.alpha_direction = -1
        
    def update(self, dt):
        """Update animations and effects"""
        # Update flashing effect
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 150 * dt)
            
        # Update pulsing message effect
        self.message_alpha += self.alpha_direction * 60 * dt
        if self.message_alpha > 240:
            self.message_alpha = 240
            self.alpha_direction = -1
        elif self.message_alpha < 130:
            self.message_alpha = 130
            self.alpha_direction = 1
    
    def handle_input(self, event):
        """Handle input events"""
        if self.restart_button.handle_event(event):
            return 'restart'
        elif self.menu_button.handle_event(event):
            return 'menu'
        return None
    
    def draw(self, surface):
        """Draw the game over screen"""
        # Draw background (darker for defeat, brighter for victory)
        if self.is_victory:
            # Gradient background for victory
            for y in range(0, WINDOW_HEIGHT, 2):
                color_value = max(10, min(40, 10 + int(y / WINDOW_HEIGHT * 50)))
                color = (0, color_value, color_value * 2)
                pygame.draw.line(surface, color, (0, y), (WINDOW_WIDTH, y))
        else:
            # Darker solid background for defeat
            surface.fill((20, 0, 0))
            
        # Draw main title
        if self.is_victory:
            title_text = "VICTORY!"
            title_color = (50, 255, 100)
            subtitle_text = "You successfully defended the deep sea ecosystem!"
        else:
            title_text = "GAME OVER"
            title_color = (255, 50, 50)
            subtitle_text = "The corporate invaders have reached the ecosystem core"
        
        # Draw title with glow effect
        title_shadow = self.title_font.render(title_text, True, (0, 0, 0))
        title = self.title_font.render(title_text, True, title_color)
        
        # Multiple shadows for pseudo-glow effect
        shadow_offsets = [(3, 3), (2, 2), (1, 1), (-1, -1), (-2, -2), (-3, -3)]
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        
        for offset_x, offset_y in shadow_offsets:
            shadow_rect = title_shadow.get_rect(
                center=(WINDOW_WIDTH//2 + offset_x, WINDOW_HEIGHT//3 + offset_y)
            )
            surface.blit(title_shadow, shadow_rect)
            
        # Draw main title
        surface.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.subtitle_font.render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 60))
        surface.blit(subtitle, subtitle_rect)
        
        # Draw statistics if provided
        y_offset = WINDOW_HEIGHT//3 + 120
        for stat, value in self.statistics.items():
            stat_text = f"{stat}: {value}"
            stat_surface = self.text_font.render(stat_text, True, (200, 200, 200))
            stat_rect = stat_surface.get_rect(center=(WINDOW_WIDTH//2, y_offset))
            surface.blit(stat_surface, stat_rect)
            y_offset += 30
            
        # Draw buttons
        self.restart_button.draw(surface)
        self.menu_button.draw(surface)
        
        # Draw flash effect when screen first appears
        if self.flash_alpha > 0:
            flash_color = (255, 255, 255) if self.is_victory else (255, 0, 0)
            flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((*flash_color, int(self.flash_alpha)))
            surface.blit(flash_surface, (0, 0))
            
        # Draw pulsing action message
        action_text = "Click a button to continue..."
        action_surface = self.text_font.render(action_text, True, (255, 255, 255))
        action_surface.set_alpha(int(self.message_alpha))
        action_rect = action_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
        surface.blit(action_surface, action_rect)
        

def run_game_over_screen(screen, is_victory=False, statistics=None):
    """
    Run the game over screen and return the selected option
    Returns:
        'restart' - Player wants to restart the level
        'menu' - Player wants to return to the main menu
    """
    game_over = GameOverScreen(is_victory, statistics)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'menu'  # Return to menu if window is closed
                
            result = game_over.handle_input(event)
            if result:
                return result
                
        game_over.update(dt)
        game_over.draw(screen)
        pygame.display.flip()
    
    return 'menu'  # Default to menu if loop exits unexpectedly

# Import here to avoid circular imports
import random