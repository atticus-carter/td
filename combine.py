from config import *
from ui import StarDisplay

class CombineManager:
    def __init__(self):
        self.combining_towers = []  # List of towers selected for combining
        self.is_combining = False   # Whether we're in combining mode
        self.combine_preview = None # Preview position for combined tower
        self.towers = []            # Reference to the tower list

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
        if len(self.combining_towers) == 3 and grid_pos:
            grid_x, grid_y = grid_pos
            if self.is_valid_placement(grid_x, grid_y):
                # Create new upgraded tower
                first_tower = self.combining_towers[0]
                new_tower = create_tower_func(first_tower.name, grid_x, grid_y, first_tower.stars + 1)
                if new_tower:
                    # Remove old towers
                    for old_tower in self.combining_towers:
                        if old_tower in self.towers:
                            self.towers.remove(old_tower)
                    # Add new tower (must be done by the caller since we return the new tower)
                    self.towers.append(new_tower)
                    
                    # Reset combining state
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
            
        # Check if cell is empty
        for tower in self.towers:
            if tower.x == grid_x and tower.y == grid_y:
                return False
        return True

    def draw_combine_preview(self, surface):
        """Draw preview and selection highlights for combining"""
        # Draw selection highlights for selected towers
        for tower in self.combining_towers:
            rect = pygame.Rect(
                tower.x * CELL_WIDTH + SIDEBAR_WIDTH,
                tower.y * CELL_HEIGHT,
                CELL_WIDTH,
                CELL_HEIGHT
            )
            pygame.draw.rect(surface, (255, 215, 0), rect, 3)  # Gold outline

        # Draw combine preview if we have 3 towers selected
        if self.is_combining and len(self.combining_towers) == 3 and self.combine_preview:
            grid_x, grid_y = self.combine_preview
            if self.is_valid_placement(grid_x, grid_y):
                preview_color = (255, 215, 0, 128)  # Semi-transparent gold
            else:
                preview_color = (255, 0, 0, 128)  # Semi-transparent red
                
            preview_surf = pygame.Surface((CELL_WIDTH, CELL_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(preview_surf, preview_color, 
                           (0, 0, CELL_WIDTH, CELL_HEIGHT))
            surface.blit(preview_surf, 
                        (grid_x * CELL_WIDTH + SIDEBAR_WIDTH, 
                         grid_y * CELL_HEIGHT))
            
            # Draw star level indicator using shared StarDisplay component
            next_star_level = self.combining_towers[0].stars + 1
            StarDisplay.draw(surface, grid_x * CELL_WIDTH + SIDEBAR_WIDTH + 5, grid_y * CELL_HEIGHT + 5, next_star_level)
        
    def draw_combine_instructions(self, surface, font):
        """Draw instructions for combining"""
        if self.is_combining:
            instruction_text = ""
            if len(self.combining_towers) < 3:
                instruction_text = f"Select {3 - len(self.combining_towers)} more towers to combine (ESC to cancel)"
            else:
                instruction_text = "Click to place combined tower (ESC to cancel)"
            
            text_surface = font.render(instruction_text, True, (255, 215, 0))
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
            surface.blit(text_surface, text_rect)