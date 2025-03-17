import pygame
from config import *

class CombineManager:
    def __init__(self):
        self.combining_towers = []  # List of towers selected for combining
        self.is_combining = False   # Whether we're in combining mode
        self.combine_preview = None # Preview position for combined tower
        self.towers = []           # Reference to the tower list
        
    def find_combinable_towers(self, selected_tower):
        """Find towers that can be combined with the selected tower"""
        same_towers = []
        for tower in self.towers:
            if (tower != selected_tower and 
                tower.name == selected_tower.name and 
                tower.stars == selected_tower.stars and
                tower.stars < 3):  # Prevent combining 3-star towers
                same_towers.append(tower)
        return same_towers
        
    def start_combining(self, tower, towers):
        """Start the combining process with the selected tower"""
        self.towers = towers  # Store reference to tower list
        if tower.stars >= 3:
            return False
        combinable = self.find_combinable_towers(tower)
        if len(combinable) >= 2:
            self.is_combining = True
            self.combining_towers = [tower]
            return True
        return False
        
    def try_select_for_combine(self, tower):
        """Try to select a tower for combining"""
        if not self.is_combining:
            return False
            
        if len(self.combining_towers) < 3:
            first_tower = self.combining_towers[0]
            if (tower not in self.combining_towers and 
                tower.name == first_tower.name and 
                tower.stars == first_tower.stars):
                self.combining_towers.append(tower)
                if len(self.combining_towers) == 3:
                    self.combine_preview = None
                return True
        return False
        
    def complete_combine(self, grid_pos, create_tower_func):
        """Complete the combining process at the specified grid position"""
        if len(self.combining_towers) != 3:
            return False
            
        grid_x, grid_y = grid_pos
        if not self.is_valid_placement(grid_x, grid_y):
            return False
            
        # Get properties from first tower
        base_tower = self.combining_towers[0]
        tower_name = base_tower.name
        current_stars = base_tower.stars
        biome = base_tower.biome
        
        # Create new tower with increased star level
        new_tower = create_tower_func(tower_name, grid_x, grid_y, current_stars + 1)
        if new_tower:
            # Remove the old towers
            for tower in self.combining_towers:
                if tower in self.towers:
                    self.towers.remove(tower)
            
            # Add the new tower
            self.towers.append(new_tower)
            self.reset()
            return True
            
        return False
        
    def cancel_combine(self):
        """Cancel the current combining operation"""
        self.reset()
        
    def reset(self):
        """Reset the combine manager state"""
        self.combining_towers = []
        self.is_combining = False
        self.combine_preview = None
        
    def is_valid_placement(self, grid_x, grid_y):
        """Check if tower placement is valid"""
        if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
            return False
            
        # Check if cell is empty (except for towers being combined)
        for tower in self.towers:
            if tower not in self.combining_towers:
                if tower.x == grid_x and tower.y == grid_y:
                    return False
        return True
        
    def draw_combine_preview(self, surface):
        """Draw preview and selection highlights for combining"""
        if not self.is_combining:
            return
            
        # Highlight selected towers
        for tower in self.combining_towers:
            x = tower.x * CELL_WIDTH + SIDEBAR_WIDTH
            y = tower.y * CELL_HEIGHT
            pygame.draw.rect(surface, (255, 255, 0), 
                           (x, y, CELL_WIDTH, CELL_HEIGHT), 2)
        
        # Draw preview at mouse position if we have all towers selected
        if len(self.combining_towers) == 3 and self.combine_preview:
            grid_x, grid_y = self.combine_preview
            if self.is_valid_placement(grid_x, grid_y):
                preview_color = (0, 255, 0, 100)  # Green with transparency
            else:
                preview_color = (255, 0, 0, 100)  # Red with transparency
                
            s = pygame.Surface((CELL_WIDTH, CELL_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(s, preview_color, 
                           (0, 0, CELL_WIDTH, CELL_HEIGHT))
            surface.blit(s, (grid_x * CELL_WIDTH + SIDEBAR_WIDTH,
                           grid_y * CELL_HEIGHT))
        
    def draw_combine_instructions(self, surface, font):
        """Draw instructions for combining"""
        if self.is_combining:
            text = font.render(f"Select {3 - len(self.combining_towers)} more identical towers", 
                             True, COLOR_TEXT)
            surface.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 10))
            
            if len(self.combining_towers) == 3:
                text = font.render("Click empty cell to place combined tower", 
                                 True, COLOR_TEXT)
                surface.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 40))