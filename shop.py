import pygame
import random
from config import *
from ui import Button, Tooltip
from tooltip import get_tower_tooltip_text

class Shop:
    def __init__(self, biome):
        self.biome = biome
        self.slots = []
        self.selected_tower = None
        self.refresh_cost = SHOP_REFRESH_COST
        self.native_resource = self._get_native_resource()
        self.setup_shop()
        self.refresh_shop()
        
        # New: Track enemy kills and free refresh thresholds
        self.enemy_kills = 0
        self.free_refresh_index = 0  # Index into FREE_REFRESH_THRESHOLDS
        
        # Create refresh button using Button component
        self.refresh_button = Button(
            pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, WINDOW_HEIGHT - 60, 180, 40),
            "Refresh"
        )
        
        # Tooltip for shop items
        self.tooltip = Tooltip()
        
    def _get_native_resource(self):
        """Determine native resource based on biome"""
        if self.biome == Biome.HYDROTHERMAL:
            return 'sulfides'
        elif self.biome == Biome.COLDSEEP:
            return 'methane'
        elif self.biome == Biome.BRINE_POOL:
            return 'salt'
        elif self.biome == Biome.WHALEFALL:
            return 'lipids'
        return None
        
    def setup_shop(self):
        """Set up shop layout and buttons"""
        button_height = 80
        spacing = 10
        start_y = 100
        for i in range(SHOP_SLOTS):
            self.slots.append({
                'rect': pygame.Rect(
                    WINDOW_WIDTH - SIDEBAR_WIDTH + 10,
                    start_y + i * (button_height + spacing),
                    SIDEBAR_WIDTH - 20,
                    button_height
                ),
                'tower': None
            })

    def refresh_shop(self):
        """Refresh available towers in shop with improved odds"""
        available_towers = []
        
        # Add towers from current biome
        if self.biome:
            for tower_type in TOWER_DEFINITIONS[self.biome].values():
                available_towers.append(tower_type['name'])
        
        # Add rare towers
        rare_towers = list(RARE_TOWERS.keys())
        
        # Clear current slots
        for slot in self.slots:
            slot['tower'] = None
            
        # Fill slots with new towers
        for slot in self.slots:
            if not available_towers and not rare_towers:
                break
                
            # Determine if this slot will be a rare tower (15% chance)
            if rare_towers and random.random() < 0.15:
                tower_name = random.choice(rare_towers)
                rare_towers.remove(tower_name)
            elif available_towers:
                tower_name = random.choice(available_towers)
                available_towers.remove(tower_name)
            else:
                continue
            
            # Determine star level based on improved probabilities
            rand = random.random()
            if rand > 0.98:  # 2% chance for 3-star
                star_level = 3
            elif rand > 0.85:  # 13% chance for 2-star
                star_level = 2
            else:  # 85% chance for 1-star
                star_level = 1
            
            slot['tower'] = (tower_name, star_level)

    def try_refresh_shop(self, resources):
        """Try to refresh shop with resources"""
        # Check if we've reached a free refresh threshold
        if self.free_refresh_index < len(FREE_REFRESH_THRESHOLDS) and self.enemy_kills >= FREE_REFRESH_THRESHOLDS[self.free_refresh_index]:
            self.free_refresh_index += 1
            self.refresh_shop()
            return True
            
        if self.native_resource and resources[self.native_resource] >= self.refresh_cost:
            resources[self.native_resource] -= self.refresh_cost
            self.refresh_cost = min(self.refresh_cost + 3, 25)  # Smaller increase, lower max
            self.refresh_shop()
            return True
        return False
        
    def add_enemy_kill(self):
        """Track enemy kills for free refreshes"""
        self.enemy_kills += 1

    def get_tower_cost(self, tower_name, star_level):
        """Calculate the cost of a tower with star level"""
        if tower_name not in TOWER_COSTS:
            return None
            
        base_costs = TOWER_COSTS[tower_name].copy()
        multiplier = STAR_COST_MULTIPLIERS[star_level]
        
        return {resource: int(cost * multiplier) for resource, cost in base_costs.items()}

    def can_afford_tower(self, tower_info, resources):
        """Check if player can afford the tower"""
        if not tower_info:
            return False
            
        tower_name, star_level = tower_info
        costs = self.get_tower_cost(tower_name, star_level)
        
        if not costs:
            return False
            
        return all(resources.get(resource, 0) >= cost for resource, cost in costs.items())

    def handle_click(self, pos, resources):
        """Handle mouse click in shop area"""
        for i, slot in enumerate(self.slots):
            if slot['rect'].collidepoint(pos):
                if slot['tower'] and self.can_afford_tower(slot['tower'], resources):
                    self.selected_tower = slot['tower']
                    return True
        return False

    def purchase_tower(self, slot_index, resources):
        """Complete tower purchase"""
        if slot_index >= len(self.slots) or not self.slots[slot_index]['tower']:
            return False
            
        tower_info = self.slots[slot_index]['tower']
        if not self.can_afford_tower(tower_info, resources):
            return False
            
        tower_name, star_level = tower_info
        costs = self.get_tower_cost(tower_name, star_level)
        
        # Deduct resources
        for resource, cost in costs.items():
            resources[resource] -= cost
            
        # Clear the slot
        self.slots[slot_index]['tower'] = None
        return True

    def draw(self, surface, resources):
        """Draw the shop interface"""
        # Draw shop background
        shop_bg = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surface, COLOR_UI_BG, shop_bg)
        
        # Draw slots
        font = get_font(FONT_SIZE_SMALL)
        for i, slot in enumerate(self.slots):
            if slot['tower']:
                tower_name, star_level = slot['tower']
                color = TOWER_COLORS.get(tower_name, (100, 100, 100))
                
                # Draw slot background
                can_afford = self.can_afford_tower(slot['tower'], resources)
                bg_color = color if can_afford else (50, 50, 50)
                pygame.draw.rect(surface, bg_color, slot['rect'])
                
                # Draw tower name
                name_text = font.render(tower_name, True, COLOR_TEXT)
                name_rect = name_text.get_rect(center=(slot['rect'].centerx, slot['rect'].top + 20))
                surface.blit(name_text, name_rect)
                
                # Draw stars
                star_color = (255, 215, 0)  # Gold
                for s in range(star_level):
                    pygame.draw.polygon(surface, star_color, [
                        (slot['rect'].left + 10 + s*15, slot['rect'].top + 35),
                        (slot['rect'].left + 20 + s*15, slot['rect'].top + 35),
                        (slot['rect'].left + 15 + s*15, slot['rect'].top + 45)
                    ])
                
                # Draw costs
                costs = self.get_tower_cost(tower_name, star_level)
                if costs:
                    cost_text = []
                    for resource, amount in costs.items():
                        sufficient = resources.get(resource, 0) >= amount
                        color = (0, 255, 0) if sufficient else (255, 0, 0)
                        cost_text.append(font.render(f"{resource}: {amount}", True, color))
                    
                    y_offset = slot['rect'].bottom - 40
                    for text in cost_text:
                        text_rect = text.get_rect(centerx=slot['rect'].centerx, y=y_offset)
                        surface.blit(text, text_rect)
                        y_offset += 15
            else:
                # Draw empty slot
                pygame.draw.rect(surface, (50, 50, 50), slot['rect'])
                text = font.render("SOLD", True, COLOR_TEXT)
                text_rect = text.get_rect(center=slot['rect'].center)
                surface.blit(text, text_rect)
        
        # Draw refresh button
        self.refresh_button.draw(surface)
        
        # Show progress to next free refresh if available
        if self.free_refresh_index < len(FREE_REFRESH_THRESHOLDS):
            next_threshold = FREE_REFRESH_THRESHOLDS[self.free_refresh_index]
            kills_needed = next_threshold - self.enemy_kills
            if kills_needed <= 5:  # Show countdown when close
                refresh_text = f"Free in {kills_needed}"
            else:
                refresh_text = f"Refresh ({self.refresh_cost})"
        else:
            refresh_text = f"Refresh ({self.refresh_cost})"
            
        refresh_text = font.render(refresh_text, True, COLOR_TEXT)
        refresh_rect = refresh_text.get_rect(center=self.refresh_button.rect.center)
        surface.blit(refresh_text, refresh_rect)
        
        # Draw tooltip if hovering over a slot
        mouse_pos = pygame.mouse.get_pos()
        for slot in self.slots:
            if slot['rect'].collidepoint(mouse_pos) and slot['tower']:
                tower_name, star_level = slot['tower']
                tooltip_text = get_tower_tooltip_text(tower_name)
                self.tooltip.set_content(tooltip_text)
                self.tooltip.show(mouse_pos[0] + 15, mouse_pos[1] + 15)
                self.tooltip.draw(surface)
                break
        else:
            self.tooltip.hide()