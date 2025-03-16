import pygame
import random
from config import *
from tower import *
from enemy import Enemy
from tooltip import Tooltip, get_tower_tooltip_text, get_enemy_tooltip_text
from shop import Shop
from wave_manager import WaveManager
from combine import CombineManager
from ui import Button, ResourceDisplay, WaveInfoDisplay, PauseOverlay, GridDisplay, TowerPreview, PauseScreen

class GameplayManager:
    def __init__(self, biome, level):
        self.biome = biome
        self.level = level
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
        if tower_name in ['BlackSmoker', 'BubblePlume', 'BrinePool', 'OsedaxWorm', 'Nautilus']:
            tower = ResourceTower(grid_x, grid_y, tower_name, self.biome)
        elif tower_name in ['RiftiaTubeWorm', 'Rockfish', 'Hagfish', 'Muusoctopus', 'GiantSquid']:
            tower = ProjectileTower(grid_x, grid_y, tower_name, self.biome)
        elif tower_name in ['SquatLobster', 'SpiderCrab', 'Chimaera', 'SleeperShark', 'ColossalSquid']:
            tower = TankTower(grid_x, grid_y, tower_name, self.biome)
        elif tower_name in ['BlueCilliates', 'VesicomyidaeClams', 'MuscleBed', 'Beggiatoa', 'DumboOctopus']:
            tower = EffectTower(grid_x, grid_y, tower_name, self.biome)
            
        if tower:
            tower.stars = star_level
            tower._setup_tower_properties()
        return tower

    def handle_input(self, event):
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
            
            # Handle pause button
            if self.pause_button.handle_event(event):
                self.paused = not self.paused
                return
                
            # Handle shop refresh button and interactions
            if mouse_y > WINDOW_HEIGHT - SHOP_HEIGHT:
                refresh_button = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - SHOP_HEIGHT + 10, 100, 40)
                if refresh_button.collidepoint(mouse_x, mouse_y):
                    self.shop.try_refresh_shop(self.resources)
                else:
                    self.shop.handle_click(event.pos, self.resources)
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
                grid_pos = self.get_grid_pos(event.pos)
                if grid_pos and self.is_valid_placement(*grid_pos):
                    self.dragging_tower.x, self.dragging_tower.y = grid_pos
                self.dragging_tower = None
                self.drag_start_pos = None
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.is_pause_hover = self.pause_button.rect.collidepoint(mouse_pos)
            
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
        if self.paused:
            # Only handle pause button when paused
            mouse_pos = pygame.mouse.get_pos()
            self.is_pause_hover = self.pause_button.collidepoint(mouse_pos)
            return GameState.GAMEPLAY
            
        # Update wave state and spawn enemies
        if not self.wave_manager.update(dt, self.enemies):
            # No more waves and all enemies defeated
            if len(self.enemies) == 0:
                return GameState.VICTORY
                
        # Update towers and handle resource generation
        for tower in self.towers[:]:
            result = tower.update(dt, self)
            
            if isinstance(tower, ResourceTower) and result:
                for resource_type, amount in result:
                    if resource_type == 'all':
                        for res in self.resources:
                            self.resources[res] += amount
                    else:
                        self.resources[resource_type] += amount
                    
            elif isinstance(tower, ProjectileTower) and result:
                self.projectiles.append(Projectile(
                    result['x'], result['y'],
                    result['damage'], result['color'],
                    result['target']))
                    
            # Remove destroyed towers
            if tower.health <= 0:
                self.towers.remove(tower)
                
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
                
        self.tooltip.hide()

    def draw(self, surface):
        # Draw background grid
        self.grid.draw(surface)

        # Draw towers
        for tower in self.towers:
            tower.draw(surface)

        # Draw combine manager elements
        self.combine_manager.draw_combine_preview(surface)
        self.combine_manager.draw_combine_instructions(surface, self.pause_font)

        # Draw enemies and projectiles
        for enemy in self.enemies:
            enemy.draw(surface)
        for projectile in self.projectiles:
            projectile.draw(surface)

        # Draw resources in sidebar
        self.resource_display.draw(surface, self.resources)

        # Draw wave info
        wave_status = self.wave_manager.get_wave_status()
        self.wave_info.draw(surface, wave_status)

        # Draw pause button
        self.pause_button.text = "Resume" if self.paused else "Pause"
        self.pause_button.draw(surface)

        # Draw pause overlay when paused
        if self.paused:
            self.pause_screen.draw(surface)

        # Draw tower placement preview
        if self.placement_preview and self.shop.selected_tower:
            TowerPreview.draw(surface, self.placement_preview, self.placement_valid)
        
        # Draw dragging tower
        if self.dragging_tower:
            mouse_pos = pygame.mouse.get_pos()
            color = TOWER_COLORS.get(self.dragging_tower.name, (100, 100, 100))
            TowerPreview.draw(surface, 
                            (int((mouse_pos[0] - SIDEBAR_WIDTH) / CELL_WIDTH),
                             int(mouse_pos[1] / CELL_HEIGHT)),
                            True, color)

        # Draw remaining UI elements
        self.tooltip.draw(surface)
        self.shop.draw(surface, self.resources)
