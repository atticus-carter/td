from typing import Dict, List, Optional
import pygame
from config import *
from base_types import TowerType, BaseTower
from tower import Tower, ResourceTower, ProjectileTower, TankTower, EffectTower, Projectile
from enemy import Enemy
from resource_orb import ResourceOrb
from shop import Shop
from ui import (ResourceDisplay, WaveInfoDisplay, Button, Tooltip, GridDisplay, 
               PauseOverlay, PauseScreen, TowerPreview)
from wave_manager import WaveManager
from combine import CombineManager
from tooltip import get_tower_tooltip_text, get_enemy_tooltip_text
from auto_collect import check_auto_collect
from sediment_generator import SedimentGenerator
import random

class GameplayManager:
    def __init__(self, biome, level):
        self.biome = biome
        self.level = level
        
        # Initialize sediment generator
        self.sediment_generator = SedimentGenerator(biome, level)
        self.background = self.sediment_generator.get_background()
        
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.tooltip = Tooltip()
        self.hovering_tower = None
        self.hovering_enemy = None
        self.wave_manager = WaveManager(level)
        self.paused = False
        
        # Tower placement preview
        self.placement_preview = None
        self.placement_valid = False
        
        # Tower dragging
        self.dragging_tower = None
        self.drag_start_pos = None
        self.drag_offset = (0, 0)
        
        # Initialize combine manager
        self.combine_manager = CombineManager()
        
        # Shop system
        self.shop = Shop(biome)
        
        # Initialize resources
        self.resources = {
            'sulfides': INITIAL_RESOURCES,
            'methane': INITIAL_RESOURCES,
            'salt': INITIAL_RESOURCES,
            'lipids': INITIAL_RESOURCES
        }
        
        # Set native resource based on biome
        if self.biome == Biome.HYDROTHERMAL:
            self.native_resource = 'sulfides'
        elif self.biome == Biome.COLDSEEP:
            self.native_resource = 'methane'
        elif self.biome == Biome.BRINE_POOL:
            self.native_resource = 'salt'
        elif self.biome == Biome.WHALEFALL:
            self.native_resource = 'lipids'
        
        # Initialize UI components
        self.grid = GridDisplay()
        self.resource_display = ResourceDisplay(10, 10)
        self.wave_info = WaveInfoDisplay(SIDEBAR_WIDTH + 10, 10)
        self.pause_button = Button(
            pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 40),
            "Pause",
            color=(50, 120, 190),
            hover_color=(70, 140, 210)
        )
        self.pause_overlay = PauseOverlay()
        self.pause_font = get_font(FONT_SIZE_MEDIUM)  # Added to provide a font for combine instructions

        # Initialize PauseScreen
        self.pause_screen = PauseScreen()

        # Initialize sell bin
        self.sell_bin_rect = pygame.Rect(10, WINDOW_HEIGHT - 90, 80, 80)
        self.hovering_sell_bin = False
        
        self.resource_orbs = []  # Add list to track active resource orbs
        
        # Load PNG images for towers with fallback for missing assets
        self.tower_images = {}
        tower_types = [
            'BlackSmoker', 'RiftiaTubeWorm', 'BlueCilliates', 'SquatLobster',
            'SpiderCrab', 'GiantSquid', 'ColossalSquid', 'DumboOctopus'
        ]
        
        # Create a default surface for missing assets
        default_surface = pygame.Surface((32, 32))  # Adjust size as needed
        default_surface.fill((100, 100, 100))  # Gray color
        pygame.draw.rect(default_surface, (150, 150, 150), (8, 8, 16, 16))  # Simple shape
        
        for tower_name in tower_types:
            try:
                img_path = f'assets/{tower_name}.png'
                self.tower_images[tower_name] = pygame.image.load(img_path).convert_alpha()
            except (FileNotFoundError, pygame.error):
                # Use default surface for missing assets
                self.tower_images[tower_name] = default_surface.copy()
        
    def get_tower_sell_value(self, tower):
        """Calculate refund value for selling a tower (50% of purchase cost)"""
        tower_costs = {}
        
        if tower.name in TOWER_COSTS:
            base_costs = TOWER_COSTS[tower.name].copy()
            multiplier = STAR_COST_MULTIPLIERS.get(tower.stars, 1.0)
            
            # Calculate 50% refund of the purchase cost
            for resource, cost in base_costs.items():
                tower_costs[resource] = int(cost * multiplier * 0.5)
                
        return tower_costs

    def get_grid_pos(self, mouse_pos):
        """Convert mouse position to grid position"""
        if mouse_pos[0] > SIDEBAR_WIDTH:
            grid_x = (mouse_pos[0] - SIDEBAR_WIDTH) // CELL_WIDTH
            grid_y = mouse_pos[1] // CELL_HEIGHT
            if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                return grid_x, grid_y
        return None

    def is_valid_placement(self, grid_x, grid_y):
        """Check if tower placement is valid"""
        if not (0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS):
            return False
            
        # Check if cell is empty
        for tower in self.towers:
            if tower.x == grid_x and tower.y == grid_y:
                return False
        return True

    def create_tower(self, tower_name, grid_x, grid_y, star_level=1):
        """Create a new tower of the appropriate type"""
        tower = None
        
        # Handle tower types
        if tower_name in ['BlackSmoker', 'BubblePlume', 'BrinePool', 'OsedaxWorm', 'Nautilus']:
            tower = ResourceTower(grid_x, grid_y, tower_name, self, self.biome)
        elif tower_name in ['RiftiaTubeWorm', 'Rockfish', 'Hagfish', 'Muusoctopus', 'GiantSquid']:
            tower = ProjectileTower(grid_x, grid_y, tower_name, self, self.biome)
        elif tower_name in ['SquatLobster', 'SpiderCrab', 'Chimaera', 'SleeperShark', 'ColossalSquid']:
            tower = TankTower(grid_x, grid_y, tower_name, self, self.biome)
        elif tower_name in ['BlueCilliates', 'VesicomyidaeClams', 'MuscleBed', 'DumboOctopus', 'Beggiatoa']:
            tower = EffectTower(grid_x, grid_y, tower_name, self, self.biome)
                
        if tower:
            tower.stars = star_level
            tower._setup_tower_properties()
        return tower

    def place_tower(self, tower_type, grid_x, grid_y):
        """Place a new tower on the grid"""
        if tower_type == "basic":
            tower_name = "RiftiaTubeWorm"  # Default basic tower
        elif tower_type == "frost":
            tower_name = "Rockfish"  # Default frost tower
        else:
            return
            
        tower = self.create_tower(tower_name, grid_x, grid_y)
        if tower:
            self.towers.append(tower)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.combine_manager.is_combining:
                    self.combine_manager.cancel_combine()
                else:
                    self.paused = not self.paused
                    return
        
        if self.paused:
            result = self.pause_screen.handle_input(event)
            if result == 0:  # Resume
                self.paused = False
            elif result == 1:  # Restart
                return 'restart'
            elif result == 2:  # Settings
                pass  # TODO: Implement settings
            elif result == 3:  # Main Menu
                return 'menu'
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # First check for resource orb clicks
            for orb in self.resource_orbs[:]:  # Use slice to avoid modification during iteration
                if orb.contains_point(mouse_x, mouse_y) and orb.active:
                    # Collect the resource
                    self.resources[orb.resource_type] += orb.amount
                    orb.active = False
                    self.resource_orbs.remove(orb)
                    return  # Don't process other clicks if we collected a resource
            
            # Handle pause button
            if self.pause_button.handle_event(event):
                self.paused = not self.paused
                return
                
            # Handle shop refresh button and interactions
            if self.shop.refresh_button.rect.collidepoint(mouse_x, mouse_y):
                self.shop.try_refresh_shop(self.resources)
                return
                
            # Handle shop interactions
            if self.shop.handle_click(event.pos, self.resources):
                return
                
            # Handle tower placement, combining, or dragging
            grid_pos = self.get_grid_pos(event.pos)
            if grid_pos:
                grid_x, grid_y = grid_pos
                
                # Check if clicking on existing tower
                clicked_tower = None
                for tower in self.towers:
                    if tower.x == grid_x and tower.y == grid_y:
                        clicked_tower = tower
                        break
                
                if clicked_tower:
                    if event.button == 1:  # Left click
                        if self.combine_manager.is_combining:
                            self.combine_manager.try_select_for_combine(clicked_tower)
                        else:
                            # Start dragging
                            self.dragging_tower = clicked_tower
                            self.drag_start_pos = event.pos
                            tower_center = (
                                clicked_tower.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2,
                                clicked_tower.y * CELL_HEIGHT + CELL_HEIGHT/2
                            )
                            self.drag_offset = (
                                tower_center[0] - event.pos[0],
                                tower_center[1] - event.pos[1]
                            )
                    elif event.button == 3:  # Right click
                        if not self.combine_manager.is_combining:
                            self.combine_manager.start_combining(clicked_tower, self.towers)
                elif self.combine_manager.is_combining and len(self.combine_manager.combining_towers) == 3:
                    # Try to place combined tower
                    self.combine_manager.complete_combine(grid_pos, self.create_tower)
                elif self.shop.selected_tower:
                    # Try to place new tower from shop
                    if self.is_valid_placement(grid_x, grid_y):
                        tower_name, star_level = self.shop.selected_tower
                        new_tower = self.create_tower(tower_name, grid_x, grid_y, star_level)
                        if new_tower:
                            for i, slot in enumerate(self.shop.slots):
                                if slot['tower'] == self.shop.selected_tower:
                                    if self.shop.purchase_tower(i, self.resources):
                                        self.towers.append(new_tower)
                                        self.shop.selected_tower = None
                                    break
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_tower:
                mouse_pos = event.pos
                
                # Check if tower was dropped on sell bin
                if self.sell_bin_rect.collidepoint(mouse_pos):
                    # Get sell value and add to resources
                    sell_value = self.get_tower_sell_value(self.dragging_tower)
                    for resource, amount in sell_value.items():
                        self.resources[resource] += amount
                    
                    # Remove the tower
                    self.towers.remove(self.dragging_tower)
                else:
                    # Normal tower placement
                    grid_pos = self.get_grid_pos(mouse_pos)
                    if grid_pos and self.is_valid_placement(*grid_pos):
                        self.dragging_tower.x, self.dragging_tower.y = grid_pos
                
                self.dragging_tower = None
                self.drag_start_pos = None
                self.hovering_sell_bin = False
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.is_pause_hover = self.pause_button.rect.collidepoint(mouse_pos)
            
            # Check if dragging over sell bin
            if self.dragging_tower:
                self.hovering_sell_bin = self.sell_bin_rect.collidepoint(mouse_pos)
            else:
                self.hovering_sell_bin = False
            
            # Update tower placement preview
            if self.shop.selected_tower and not self.dragging_tower:
                grid_pos = self.get_grid_pos(mouse_pos)
                if grid_pos:
                    self.placement_preview = grid_pos
                    self.placement_valid = self.is_valid_placement(*grid_pos)
                else:
                    self.placement_preview = None
            elif self.combine_manager.is_combining and len(self.combine_manager.combining_towers) == 3:
                grid_pos = self.get_grid_pos(mouse_pos)
                if grid_pos:
                    self.combine_manager.combine_preview = grid_pos
            
            # Update tooltip
            self.handle_hover(mouse_pos)
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.combine_manager.is_combining:
                    self.combine_manager.cancel_combine()

    def update(self, dt):
        """Update game state"""
        if self.paused:
            return None
            
        # Update towers and collect spawned orbs
        for tower in self.towers[:]:
            result = tower.update(dt, self)
            
            # Handle spawned resource orbs
            if isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'resource_type'):
                self.resource_orbs.extend(result)
            
            if tower.health <= 0:
                self.towers.remove(tower)
                
        # Update resource orbs and check for auto-collection
        for orb in self.resource_orbs[:]:
            if orb.update(dt):  # Returns True when orb should be removed
                if orb.active:  # If orb is still active, auto-collect it
                    self.resources[orb.resource_type] += orb.collect(auto_collected=True)
                self.resource_orbs.remove(orb)
                continue
                
            # Check for auto-collection by appropriate towers
            for tower in self.towers:
                if check_auto_collect(orb, tower):
                    self.resources[orb.resource_type] += orb.collect(auto_collected=True)
                    self.resource_orbs.remove(orb)
                    break

        # Update wave state and spawn enemies
        if not self.wave_manager.update(dt, self.enemies):
            # No more waves and all enemies defeated
            if len(self.enemies) == 0:
                return GameState.VICTORY
                
        # Update towers and handle resource generation
        for tower in self.towers[:]:
            result = tower.update(dt, self)
            
            if isinstance(tower, ResourceTower) and result:
                # Add any spawned resource orbs
                self.resource_orbs.extend(result)
            elif isinstance(tower, ProjectileTower) and result:
                self.projectiles.append(Projectile(
                    result['x'], result['y'],
                    result['damage'], result['color'],
                    result['target']))
                    
            # Remove destroyed towers
            if tower.health <= 0:
                self.towers.remove(tower)
                
        # Update resource orbs and check for auto-collection
        for orb in self.resource_orbs[:]:
            if not orb.update(dt):
                self.resource_orbs.remove(orb)
                continue
                
            # Check for auto-collection by appropriate towers
            for tower in self.towers:
                if check_auto_collect(orb, tower):
                    self.resources[orb.resource_type] += orb.amount
                    orb.active = False
                    self.resource_orbs.remove(orb)
                    break
                
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.towers)
            
            if enemy.x < SIDEBAR_WIDTH:  # Enemy reached base
                return GameState.GAME_OVER
            elif enemy.is_dead():
                reward = enemy.get_reward()
                self.resources[self.native_resource] += reward
                self.enemies.remove(enemy)
                # Track enemy kill for shop free refreshes
                self.shop.add_enemy_kill()
                
        # Update projectiles
        for projectile in self.projectiles[:]:
            if projectile.update(dt):
                self.projectiles.remove(projectile)
                
        # Update sediment generator for animated elements
        self.sediment_generator.update(dt)
                
        return GameState.GAMEPLAY

    def handle_hover(self, mouse_pos):
        """Handle mouse hover for tooltips"""
        mouse_x, mouse_y = mouse_pos
        self.hovering_tower = None
        self.hovering_enemy = None
        
        # Check for towers on grid hover
        if mouse_x > SIDEBAR_WIDTH:
            grid_x = (mouse_x - SIDEBAR_WIDTH) // CELL_WIDTH
            grid_y = mouse_y // CELL_HEIGHT
            
            # Then check towers
            for tower in self.towers:
                if tower.x == grid_x and tower.y == grid_y:
                    self.hovering_tower = tower.name
                    tooltip_text = get_tower_tooltip_text(tower.name).copy()
                    if tower.level > 1:
                        tooltip_text.append(f"Level: {tower.level}")
                    if hasattr(tower, 'projectile_damage'):
                        tooltip_text.append(f"Current Damage: {tower.projectile_damage}")
                    if hasattr(tower, 'health'):
                        tooltip_text.append(f"Current Health: {tower.health}/{tower.max_health}")
                    self.tooltip.set_content(tooltip_text)
                    self.tooltip.show(mouse_x + 15, mouse_y + 15)
                    return
                    
        # Check for enemy hover
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(
                enemy.x - enemy.width/2,
                enemy.y - enemy.height/2,
                enemy.width, enemy.height
            )
            if enemy_rect.collidepoint(mouse_x, mouse_y):
                self.hovering_enemy = enemy.enemy_type
                tooltip_text = get_enemy_tooltip_text(enemy.enemy_type).copy()
                tooltip_text.append(f"Current Health: {enemy.health}/{enemy.max_health}")
                self.tooltip.set_content(tooltip_text)
                self.tooltip.show(mouse_x + 15, mouse_y + 15)
                return
        
        # Show tooltip for sell bin when hovering
        if self.sell_bin_rect.collidepoint(mouse_x, mouse_y):
            self.tooltip.set_content(["Sell Tower", "Drag towers here to sell", "Refunds 50% of cost"])
            self.tooltip.show(mouse_x + 15, mouse_y + 15)
            self.hovering_sell_bin = True
            return
            
        self.hovering_sell_bin = False
        self.tooltip.hide()

    def draw_sell_bin(self, surface):
        """Draw the sell bin UI element"""
        # Draw sell bin with a trash icon
        bin_color = (200, 50, 50) if self.hovering_sell_bin else (150, 50, 50)
        
        # Draw bin base
        pygame.draw.rect(surface, bin_color, self.sell_bin_rect, border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), self.sell_bin_rect, width=2, border_radius=5)
        
        # Draw trash can icon
        icon_rect = pygame.Rect(
            self.sell_bin_rect.x + 20, 
            self.sell_bin_rect.y + 15,
            40, 50
        )
        pygame.draw.rect(surface, (80, 80, 80), icon_rect)
        
        # Draw trash can lid
        lid_rect = pygame.Rect(
            self.sell_bin_rect.x + 15,
            self.sell_bin_rect.y + 10,
            50, 10
        )
        pygame.draw.rect(surface, (80, 80, 80), lid_rect)
        
        # Draw "SELL" text
        sell_font = get_font(FONT_SIZE_SMALL)
        sell_text = sell_font.render("SELL", True, (255, 255, 255))
        text_rect = sell_text.get_rect(center=(self.sell_bin_rect.centerx, self.sell_bin_rect.bottom - 10))
        surface.blit(sell_text, text_rect)

    def draw_tower_effects(self, surface, tower):
        """Draw shadow and glow effects for a tower"""
        # Calculate tower center position
        tower_x = tower.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
        tower_y = tower.y * CELL_HEIGHT + CELL_HEIGHT/2

        glow_size = int(CELL_WIDTH * 1.3)  # Slightly larger than the tower
        
        # Create a small surface first for chunky pixelation
        small_size = 6  # Very small for even chunkier pixelation
        small_glow = pygame.Surface((small_size, small_size), pygame.SRCALPHA)
        
        # Very subtle glow colors - much more transparent now (alpha reduced to 12)
        if isinstance(tower, ResourceTower):
            glow_color = (255, 230, 180, 1)  # Very subtle golden glow
        elif isinstance(tower, ProjectileTower):
            glow_color = (180, 210, 255, 1)  # Very subtle blue glow
        elif isinstance(tower, TankTower):
            glow_color = (255, 190, 190, 1)  # Very subtle red glow
        elif isinstance(tower, EffectTower):
            glow_color = (190, 255, 190, 1)  # Very subtle green glow
        else:
            glow_color = (235, 235, 235, 1)  # Very subtle white glow
        
        # Use fixed noise pattern (based on tower position) to avoid wiggling
        # This makes the noise "attached" to the tower position instead of random each frame
        noise_seed = hash(f"{tower.x}{tower.y}") % 1000  # Deterministic seed based on tower position
        random.seed(noise_seed)
        noise_map = [[random.uniform(0.7, 1.0) for _ in range(small_size)] for _ in range(small_size)]
        random.seed()  # Reset the random seed
        
        # Draw a noisy, imperfect glow on the small surface
        for y in range(small_size):
            for x in range(small_size):
                # Calculate distance from center (normalized)
                center = small_size / 2
                dx = (x - center) / center
                dy = (y - center) / center
                distance = min(1.0, (dx*dx + dy*dy) ** 0.5)
                
                # Apply subtle irregularity based on fixed noise pattern
                if 0.7 < distance < 1.0:
                    # Use position-based noise instead of random per-frame
                    distance += (noise_map[y][x] - 0.85) * 0.2
                
                # Gradient alpha based on distance from center
                if distance < 1.0:
                    # Create a steeper falloff for more gradient
                    falloff = 1.0 - (distance ** 1.5)  # Steeper power curve
                    # Add noise to the alpha for uneven glow but much more subtle
                    alpha = int(glow_color[3] * falloff * noise_map[y][x])
                    if alpha > 0:
                        small_glow.set_at((x, y), (glow_color[0], glow_color[1], glow_color[2], alpha))
        
        # Scale up the small glow for chunky pixelated effect
        pixelated_glow = pygame.transform.scale(small_glow, (glow_size, glow_size))
        
        # Add a very minimal fixed offset based on tower position (no randomness for stability)
        # This gives each tower a slightly unique look but doesn't change frame to frame
        offset_x = ((tower.x * 3) % 3) - 1
        offset_y = ((tower.y * 3) % 3) - 1
        
        # Blit the pixelated glow
        surface.blit(pixelated_glow,
                   (int(tower_x - glow_size/2) + offset_x,
                    int(tower_y - glow_size/2) + offset_y),
                   special_flags=pygame.BLEND_ADD)

    def draw(self, surface):
        # Draw background with sediment first (sediment should be visible underneath everything)
        surface.blit(self.background, (SIDEBAR_WIDTH, 0))
        
        # Create a new surface for this frame
        frame_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw the sediment generator's animated elements
        self.sediment_generator.draw(frame_surface)
        
        # Draw background grid
        self.grid.draw(frame_surface)

        # Draw towers
        for tower in self.towers:
            self.draw_tower_effects(frame_surface, tower)
            tower.draw(frame_surface)

        # Draw combine manager elements
        self.combine_manager.draw_combine_preview(frame_surface)
        self.combine_manager.draw_combine_instructions(frame_surface, self.pause_font)
        
        # Draw resource orbs before enemies so they appear under them
        for orb in self.resource_orbs:
            orb.draw(frame_surface)

        # Draw enemies and projectiles
        for enemy in self.enemies:
            enemy.draw(frame_surface)
        for projectile in self.projectiles:
            projectile.draw(frame_surface)
        
        # Draw resource orbs on the topmost layer
        for orb in self.resource_orbs:
            orb.draw(frame_surface)
        
        # Draw resources in sidebar
        self.resource_display.draw(frame_surface, self.resources)

        # Draw wave info
        wave_status = self.wave_manager.get_wave_status()
        self.wave_info.draw(frame_surface, wave_status)

        # Draw sell bin
        self.draw_sell_bin(frame_surface)

        # Draw pause button
        self.pause_button.text = "Resume" if self.paused else "Pause"
        self.pause_button.draw(frame_surface)

        # Draw pause overlay when paused
        if self.paused:
            self.pause_screen.draw(frame_surface)

        # Draw tower placement preview
        if self.placement_preview and self.shop.selected_tower:
            TowerPreview.draw(frame_surface, self.placement_preview, self.placement_valid)
        
        # Draw dragging tower
        if self.dragging_tower:
            mouse_pos = pygame.mouse.get_pos()
            color = TOWER_COLORS.get(self.dragging_tower.name, (100, 100, 100))
            TowerPreview.draw(frame_surface, 
                            (int((mouse_pos[0] - SIDEBAR_WIDTH) / CELL_WIDTH),
                             int(mouse_pos[1] / CELL_HEIGHT)),
                            True, color)

        # Draw remaining UI elements
        self.tooltip.draw(frame_surface)
        self.shop.draw(frame_surface, self.resources)
        
        # Blit the frame surface onto the main surface
        surface.blit(frame_surface, (0, 0))
