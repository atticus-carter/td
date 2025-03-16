import pygame
from config import *

class Button:
    def __init__(self, rect, text, font_size=FONT_SIZE_MEDIUM, color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER):
        self.rect = rect if isinstance(rect, pygame.Rect) else pygame.Rect(rect)
        self.text = text
        self.hover = False
        self.font = get_font(font_size)
        self.color = color
        self.hover_color = hover_color
        self.border_radius = 5
        
    def draw(self, surface):
        color = self.hover_color if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, width=2, border_radius=self.border_radius)
        text_surface = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover and event.button == 1:  # Left mouse button
                return True
        return False

class ResourceDisplay:
    def __init__(self, x, y, font_size=FONT_SIZE_SMALL):
        self.x = x
        self.y = y
        self.font = get_font(font_size)
        self.spacing = 30
        
    def draw(self, surface, resources):
        y_offset = self.y
        for resource, amount in resources.items():
            text = f"{resource}: {amount}"
            resource_text = self.font.render(text, True, COLOR_TEXT)
            surface.blit(resource_text, (self.x, y_offset))
            y_offset += self.spacing

class WaveInfoDisplay:
    def __init__(self, x, y, font_size=FONT_SIZE_MEDIUM):
        self.x = x
        self.y = y
        self.font = get_font(font_size)
        
    def draw(self, surface, wave_status):
        wave_info = self.font.render(wave_status, True, COLOR_TEXT)
        surface.blit(wave_info, (self.x, self.y))

class PauseOverlay:
    def __init__(self):
        self.font = get_font(FONT_SIZE_LARGE)
        
    def draw(self, surface):
        pause_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 128))
        surface.blit(pause_overlay, (0, 0))
        
        pause_title = self.font.render("PAUSED", True, COLOR_TEXT)
        pause_title_rect = pause_title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        surface.blit(pause_title, pause_title_rect)

class PauseScreen:
    def __init__(self):
        self.font = get_font(FONT_SIZE_LARGE)
        self.buttons = [
            Button(pygame.Rect(WINDOW_WIDTH // 2 - 100, 200, 200, 50), "Resume"),
            Button(pygame.Rect(WINDOW_WIDTH // 2 - 100, 270, 200, 50), "Restart"),
            Button(pygame.Rect(WINDOW_WIDTH // 2 - 100, 340, 200, 50), "Settings"),
            Button(pygame.Rect(WINDOW_WIDTH // 2 - 100, 410, 200, 50), "Main Menu")
        ]
        
    def handle_input(self, event):
        for i, button in enumerate(self.buttons):
            if button.handle_event(event):
                return i  # Return button index
        return None
        
    def draw(self, surface):
        # Draw pause overlay
        pause_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 128))
        surface.blit(pause_overlay, (0, 0))
        
        # Draw pause title
        pause_title = self.font.render("PAUSED", True, COLOR_TEXT)
        pause_title_rect = pause_title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        surface.blit(pause_title, pause_title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class GridDisplay:
    def __init__(self):
        self.cell_color = (40, 40, 40)
        
    def draw(self, surface):
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                rect = pygame.Rect(
                    SIDEBAR_WIDTH + x * CELL_WIDTH,
                    y * CELL_HEIGHT,
                    CELL_WIDTH,
                    CELL_HEIGHT
                )
                pygame.draw.rect(surface, self.cell_color, rect, 1)

class TowerPreview:
    @staticmethod
    def draw(surface, grid_pos, is_valid, tower_color=None):
        if not grid_pos:
            return
            
        grid_x, grid_y = grid_pos
        preview_color = (0, 255, 0, 128) if is_valid else (255, 0, 0, 128)
        preview_surf = pygame.Surface((CELL_WIDTH, CELL_HEIGHT), pygame.SRCALPHA)
        
        if tower_color:
            pygame.draw.rect(preview_surf, (*tower_color, 180), (0, 0, CELL_WIDTH, CELL_HEIGHT))
        else:
            pygame.draw.rect(preview_surf, preview_color, (0, 0, CELL_WIDTH, CELL_HEIGHT))
            
        surface.blit(preview_surf, 
                    (grid_x * CELL_WIDTH + SIDEBAR_WIDTH, 
                     grid_y * CELL_HEIGHT))

class StarDisplay:
    @staticmethod
    def draw(surface, x, y, star_level, size=8):
        star_color = (255, 215, 0)  # Gold
        for i in range(star_level):
            star_x = x + (i * (size + 2))
            star_y = y
            pygame.draw.polygon(surface, star_color, [
                (star_x + size/2, star_y),
                (star_x + size, star_y + size/2),
                (star_x + size*0.7, star_y + size*0.7),
                (star_x + size*0.3, star_y + size*0.7),
                (star_x, star_y + size/2)
            ])

class HealthBar:
    @staticmethod
    def draw(surface, x, y, width, current_health, max_health):
        if current_health < max_health:
            health_pct = current_health / max_health
            health_width = width * health_pct
            
            # Background of health bar
            pygame.draw.rect(surface, (80, 0, 0),
                           (x, y, width, 5))
                           
            # Filled portion of health bar
            pygame.draw.rect(surface, (0, 200, 0),
                           (x, y, health_width, 5))