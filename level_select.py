import pygame
import json
import os
from config import *
from ui import Button

class LevelSelectScreen:
    def __init__(self):
        self.current_biome = Biome.HYDROTHERMAL
        self.font_large = get_font(FONT_SIZE_LARGE)
        self.font_medium = get_font(FONT_SIZE_MEDIUM)
        self.font_small = get_font(FONT_SIZE_SMALL)
        
        # Create biome tab buttons with better spacing and width
        self.biome_tabs = []
        biome_list = list(Biome)
        tab_width = 200
        spacing = 20
        start_x = (WINDOW_WIDTH - (len(biome_list) * (tab_width + spacing) - spacing)) // 2
        
        for i, biome in enumerate(biome_list):
            x = start_x + i * (tab_width + spacing)
            self.biome_tabs.append({
                'button': Button(
                    pygame.Rect(x, 50, tab_width, 40),
                    biome.name.capitalize(),
                    color=(60, 80, 120),
                    hover_color=(80, 100, 140)
                ),
                'biome': biome
            })
        
        # Load saved progress or initialize with defaults
        self.progress = self.load_progress()
        
        # Back button to return to title screen
        self.back_button = Button(
            pygame.Rect(50, WINDOW_HEIGHT - 70, 120, 50), 
            "Back"
        )
        
        # Level buttons for each biome (5x3 grid)
        self.level_buttons = {}
        self.initialize_level_buttons()
        
        # Add a tracker for button hover states
        self.hover_button = None
        
        # Debug flag to track clicks
        self.debug_last_click = None
    
    def initialize_level_buttons(self):
        """Initialize level button grid for each biome"""
        for biome in Biome:
            # Create a 5x3 grid of level buttons for each biome
            buttons = []
            for row in range(3):
                for col in range(5):
                    level_num = row * 5 + col + 1
                    
                    # Position the buttons in a grid
                    button_rect = pygame.Rect(
                        100 + col * 180,
                        150 + row * 120,
                        100,
                        100
                    )
                    
                    # Check if level is unlocked
                    unlocked = self.is_level_unlocked(biome, level_num)
                    
                    buttons.append({
                        'rect': button_rect,
                        'level': level_num,
                        'unlocked': unlocked,
                        'completed': self.is_level_completed(biome, level_num),
                        'hover': False
                    })
            
            self.level_buttons[biome] = buttons
    
    def is_level_unlocked(self, biome, level_num):
        """Check if a level is unlocked based on progress"""
        # First 5 levels are always unlocked
        if level_num <= 5:
            return True
        
        # For later levels, require completion of prior levels
        biome_name = biome.name
        if biome_name in self.progress:
            # For each level after 5, need to complete the previous level
            required_level = level_num - 1
            if required_level in self.progress[biome_name].get('completed', []):
                return True
        
        return False
    
    def is_level_completed(self, biome, level_num):
        """Check if a level has been completed"""
        biome_name = biome.name
        if biome_name in self.progress:
            return level_num in self.progress[biome_name].get('completed', [])
        return False
    
    def load_progress(self):
        """Load saved game progress from file"""
        try:
            if os.path.exists('save_data.json'):
                with open('save_data.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading progress: {e}")
        
        # Default progress (all biomes with first 5 levels unlocked)
        return {biome.name: {'completed': [], 'unlocked': list(range(1, 6))} for biome in Biome}
    
    def save_progress(self):
        """Save game progress to file"""
        try:
            with open('save_data.json', 'w') as f:
                json.dump(self.progress, f)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def mark_level_completed(self, biome, level_num):
        """Mark a level as completed and unlock the next level"""
        biome_name = biome.name
        
        # Initialize biome data if it doesn't exist
        if biome_name not in self.progress:
            self.progress[biome_name] = {'completed': [], 'unlocked': list(range(1, 6))}
        
        # Add to completed levels if not already there
        if level_num not in self.progress[biome_name]['completed']:
            self.progress[biome_name]['completed'].append(level_num)
        
        # Unlock next level if not the last one (level 15)
        if level_num < 15:
            next_level = level_num + 1
            if next_level not in self.progress[biome_name].get('unlocked', []):
                if 'unlocked' not in self.progress[biome_name]:
                    self.progress[biome_name]['unlocked'] = []
                self.progress[biome_name]['unlocked'].append(next_level)
        
        # Save progress
        self.save_progress()
        
        # Reinitialize level buttons to reflect new state
        self.initialize_level_buttons()
    
    def update(self, dt):
        """Update any animations or effects"""
        # This could be used for animations in the future
        pass
    
    def handle_input(self, event):
        """Handle user input for level select screen"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Update back button hover state
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
            
            # Update biome tab hover states
            for tab in self.biome_tabs:
                tab['button'].hover = tab['button'].rect.collidepoint(mouse_pos)
            
            # Update level button hover states
            for button_data in self.level_buttons[self.current_biome]:
                button_data['hover'] = button_data['rect'].collidepoint(mouse_pos) and button_data['unlocked']
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check if back button clicked
            if self.back_button.handle_event(event):
                return {'action': 'title_screen'}
            
            # Check if biome tab clicked - improved click detection
            for tab in self.biome_tabs:
                if tab['button'].rect.collidepoint(mouse_pos):
                    old_biome = self.current_biome
                    self.current_biome = tab['biome']
                    # Only return action if biome actually changed
                    if old_biome != self.current_biome:
                        return {'action': 'change_biome'}
            
            # Check if level button clicked
            for button_data in self.level_buttons[self.current_biome]:
                if button_data['unlocked'] and button_data['rect'].collidepoint(mouse_pos):
                    return {
                        'action': 'start_level',
                        'biome': self.current_biome,
                        'level': button_data['level']
                    }
        
        return None
    
    def draw(self, surface):
        """Draw level select screen"""
        # Draw background
        surface.fill(COLOR_BACKGROUND)
        
        # Draw title
        biome_name = self.current_biome.name.capitalize()
        title_text = f"{biome_name} Levels"
        title_surface = self.font_large.render(title_text, True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 20))
        surface.blit(title_surface, title_rect)
        
        # Draw biome tabs with improved visual feedback
        for tab in self.biome_tabs:
            button = tab['button']
            is_current = self.current_biome == tab['biome']
            
            # Override button colors for current tab
            if is_current:
                original_color = button.color
                original_hover_color = button.hover_color
                button.color = (80, 100, 140)
                button.hover_color = (100, 120, 160)
                button.draw(surface)
                button.color = original_color
                button.hover_color = original_hover_color
            else:
                button.draw(surface)
        
        # Draw level buttons
        for button_data in self.level_buttons[self.current_biome]:
            button_rect = button_data['rect']
            level_num = button_data['level']
            unlocked = button_data['unlocked']
            completed = button_data['completed']
            hovering = button_data['hover']
            
            # Draw button background with appropriate color
            if not unlocked:
                color = (100, 100, 100)  # Locked level
                text_color = (150, 150, 150)
            elif completed:
                color = (0, 150, 0)  # Completed level
                if hovering:
                    color = (0, 180, 0)  # Lighter green when hovering
                text_color = COLOR_TEXT
            else:
                color = (50, 100, 150)  # Unlocked but not completed
                if hovering:
                    color = (70, 120, 170)  # Lighter blue when hovering
                text_color = COLOR_TEXT
                
            pygame.draw.rect(surface, color, button_rect, border_radius=5)
            pygame.draw.rect(surface, (255, 255, 255), button_rect, width=2, border_radius=5)
            
            # Draw level number
            level_text = self.font_medium.render(str(level_num), True, text_color)
            level_rect = level_text.get_rect(center=button_rect.center)
            surface.blit(level_text, level_rect)
            
            # Draw lock icon for locked levels
            if not unlocked:
                lock_rect = pygame.Rect(button_rect.centerx - 15, button_rect.centery - 15, 30, 30)
                pygame.draw.rect(surface, (50, 50, 50), lock_rect)
                pygame.draw.rect(surface, (200, 200, 200), lock_rect, width=2)
                
                # Draw keyhole
                pygame.draw.circle(surface, (200, 200, 200), (button_rect.centerx, button_rect.centery - 5), 5)
                pygame.draw.rect(surface, (200, 200, 200), (button_rect.centerx - 2, button_rect.centery, 4, 10))
                
            # Draw checkmark for completed levels
            elif completed:
                # Draw checkmark
                points = [
                    (button_rect.right - 25, button_rect.bottom - 25),
                    (button_rect.right - 20, button_rect.bottom - 15),
                    (button_rect.right - 10, button_rect.bottom - 35)
                ]
                pygame.draw.lines(surface, (255, 255, 0), False, points, 3)
            
            # Draw extra visual cue for clickable levels
            if unlocked and hovering:
                # Draw a pulsing border to indicate clickable
                pygame.draw.rect(surface, (200, 200, 255), button_rect, width=3, border_radius=5)
        
        # Draw back button
        self.back_button.draw(surface)
        
        # Draw debug info if a click was recorded but did not trigger a level
        if self.debug_last_click:
            debug_text = f"Last click: {self.debug_last_click}"
            debug_surface = self.font_small.render(debug_text, True, (255, 255, 255))
            surface.blit(debug_surface, (10, WINDOW_HEIGHT - 20))