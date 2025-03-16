import pygame
from config import *
from ui import Button, StarDisplay

class LevelButton(Button):
    def __init__(self, x, y, level_num, is_unlocked=True):
        super().__init__(
            pygame.Rect(x, y, 100, 100), 
            str(level_num),
            color=(40, 60, 100) if is_unlocked else (50, 50, 50)
        )
        self.level_num = level_num
        self.is_unlocked = is_unlocked
        self.border_radius = 10
        
    def draw(self, surface):
        super().draw(surface)
        
        if not self.is_unlocked:
            lock_text = self.font.render("🔒", True, COLOR_TEXT)
            lock_rect = lock_text.get_rect(center=(self.rect.centerx, self.rect.centery + 20))
            surface.blit(lock_text, lock_rect)

class LevelSelect:
    def __init__(self, max_level=20, unlocked_levels=5):
        self.max_level = max_level
        self.unlocked_levels = unlocked_levels
        self.buttons = []
        self.title_font = get_font(FONT_SIZE_LARGE)
        self.create_buttons()
        
        # Create back button using Button component
        self.back_button = Button(
            pygame.Rect(50, WINDOW_HEIGHT - 80, 120, 50),
            "Back"
        )
        
    def create_buttons(self):
        levels_per_row = 5
        button_size = 100
        spacing = 30
        start_x = (WINDOW_WIDTH - (levels_per_row * button_size + (levels_per_row-1) * spacing)) // 2
        start_y = 150
        
        for level in range(1, self.max_level + 1):
            row = (level - 1) // levels_per_row
            col = (level - 1) % levels_per_row
            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + spacing)
            is_unlocked = level <= self.unlocked_levels
            self.buttons.append(LevelButton(x, y, level, is_unlocked))
            
    def handle_input(self, event):
        if self.back_button.handle_event(event):
            return 'back'
                
        for button in self.buttons:
            if button.handle_event(event):
                if button.is_unlocked:
                    return button.level_num
        return None
        
    def draw(self, surface):
        # Draw background
        surface.fill(COLOR_BG)
        
        # Draw title
        title_text = "Select Level"
        title_surface = self.title_font.render(title_text, True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 80))
        surface.blit(title_surface, title_rect)
        
        # Draw level buttons
        for button in self.buttons:
            button.draw(surface)
            
        # Draw back button
        self.back_button.draw(surface)
        
def run_level_select(screen):
    """
    Run the level select screen.
    Returns:
        int: selected level number
        None: if back was pressed
    """
    level_select = LevelSelect()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
                
            result = level_select.handle_input(event)
            if result == 'back':
                return None
            elif result is not None:
                return result
                
        level_select.draw(screen)
        pygame.display.flip()
        clock.tick(60)