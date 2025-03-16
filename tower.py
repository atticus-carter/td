import pygame
from config import *
from ui import HealthBar, StarDisplay

class Tower:
    def __init__(self, x, y, tower_type, biome=None):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.biome = biome
        self.stars = 1  # New: Star rating for tower
        
        # Get tower specs from definitions
        if tower_type in TOWER_COLORS:
            self.name = tower_type
            self.color = TOWER_COLORS[tower_type]
        else:
            self.name = "Unknown"
            self.color = (100, 100, 100)
        
        # Set tower properties
        self.health = 100
        self.max_health = 100
        self.attack_timer = 0
        self.level = 1
        
        # For projectile towers
        self.projectiles = []
        self.target_range = 400  # Default range
        
        # Specific tower setup based on name
        self._setup_tower_properties()
        
    def _setup_tower_properties(self):
        """Set up tower-specific properties based on tower name and apply star rating multipliers"""
        # Tank towers have higher health
        if self.name in ['SquatLobster', 'SpiderCrab', 'Chimaera', 'SleeperShark', 'ColossalSquid']:
            base_health = 300
            self.health = base_health * (1.5 ** (self.stars - 1))
            self.max_health = self.health
            
        # Set projectile properties for shooter towers
        if self.name in ['RiftiaTubeWorm', 'Rockfish', 'Hagfish', 'Muusoctopus', 'GiantSquid']:
            self.target_range = 400 * (1.2 ** (self.stars - 1))
            self.projectile_damage = 20 * (1.5 ** (self.stars - 1))
            self.cooldown = 0.5 * (0.8 ** (self.stars - 1))
            
        # Adjust rare tower stats
        if self.name == 'GiantSquid':
            self.projectile_damage = 30 * (1.5 ** (self.stars - 1))
            self.cooldown = 0.3 * (0.8 ** (self.stars - 1))
            self.target_range = 500 * (1.2 ** (self.stars - 1))

    def upgrade_star(self):
        """Upgrade tower to next star level"""
        if self.stars < 3:
            self.stars += 1
            self._setup_tower_properties()
            return True
        return False

    def update(self, dt, game_state):
        """Base update method, override in subclasses"""
        self.attack_timer += dt
        return False
        
    def draw(self, surface):
        """Draw the tower on the grid with star indicators"""
        pygame.draw.rect(surface, self.color, 
                        (self.x * CELL_WIDTH + SIDEBAR_WIDTH + 5,
                         self.y * CELL_HEIGHT + 5,
                         CELL_WIDTH - 10, CELL_HEIGHT - 10))
        
        # Draw stars using shared StarDisplay component
        StarDisplay.draw(surface, self.x * CELL_WIDTH + SIDEBAR_WIDTH + 5, self.y * CELL_HEIGHT + 5, self.stars)
        
        # Draw health bar if tower has been damaged using shared HealthBar component
        if self.health < self.max_health:
            HealthBar.draw(surface, self.x * CELL_WIDTH + SIDEBAR_WIDTH + 5, self.y * CELL_HEIGHT + 5 - 8, CELL_WIDTH - 10, self.health, self.max_health)
        
    def take_damage(self, amount):
        """Take damage from enemies"""
        self.health -= amount
        return self.health <= 0
        
    def can_upgrade(self, resources):
        """Check if tower can be upgraded with available resources"""
        upgrade_cost = TOWER_COSTS[self.name].copy()
        for resource, cost in upgrade_cost.items():
            upgrade_cost[resource] = int(cost * 0.75)  # 75% of original cost
        
        # Check if resources are sufficient
        for resource, cost in upgrade_cost.items():
            if resources.get(resource, 0) < cost:
                return False
        return True
        
    def upgrade(self):
        """Upgrade tower stats"""
        self.level += 1
        self.health = int(self.health * 1.25)
        self.max_health = int(self.max_health * 1.25)
        
        # Enhance tower-specific properties
        if hasattr(self, 'projectile_damage'):
            self.projectile_damage = int(self.projectile_damage * 1.25)
        if hasattr(self, 'cooldown'):
            self.cooldown = max(0.1, self.cooldown * 0.75)  # 25% faster, minimum 0.1s
        if hasattr(self, 'resource_amount'):
            self.resource_amount = int(self.resource_amount * 1.25)

class ResourceTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        super().__init__(x, y, tower_type, biome)
        self.resource_amounts = {
            'sulfides': 2,
            'methane': 2,
            'salt': 2,
            'lipids': 2
        }
        
        # Set primary resource based on biome
        if biome == Biome.HYDROTHERMAL:
            self.resource_amounts['sulfides'] = 10
        elif biome == Biome.COLDSEEP:
            self.resource_amounts['methane'] = 10
        elif biome == Biome.BRINE_POOL:
            self.resource_amounts['salt'] = 10
        elif biome == Biome.WHALEFALL:
            self.resource_amounts['lipids'] = 10
            
        # Special case for Nautilus rare tower
        if tower_type == 'Nautilus':
            for resource in self.resource_amounts:
                self.resource_amounts[resource] = 5
                
        # Apply star rating multiplier
        for resource in self.resource_amounts:
            self.resource_amounts[resource] *= (1.5 ** (self.stars - 1))
    
    def update(self, dt, game_state):
        self.attack_timer += dt
        if self.attack_timer >= 1.0:  # Generate resources every second
            self.attack_timer = 0
            generated_resources = []
            for resource, amount in self.resource_amounts.items():
                if amount > 0:
                    generated_resources.append((resource, amount))
            return generated_resources
        return None

class ProjectileTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        super().__init__(x, y, tower_type, biome)
        
    def update(self, dt, game_state):
        """Update projectile tower and check for enemy targets"""
        self.attack_timer += dt
        
        # Check if we can fire
        if self.attack_timer >= self.cooldown:
            # Find target enemy
            target = self._find_target(game_state.enemies)
            if target:
                self.attack_timer = 0
                return {
                    'x': self.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2,
                    'y': self.y * CELL_HEIGHT + CELL_HEIGHT/2,
                    'damage': self.projectile_damage,
                    'color': self.color,
                    'target': target
                }
        return None
    
    def _find_target(self, enemies):
        """Find nearest enemy in range to target"""
        center_x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
        center_y = self.y * CELL_HEIGHT + CELL_HEIGHT/2
        
        nearest_enemy = None
        nearest_dist = float('inf')
        
        for enemy in enemies:
            dx = enemy.x - center_x
            dy = enemy.y - center_y
            dist = (dx**2 + dy**2) ** 0.5
            
            # Only consider enemies in range and to the right of the tower
            if dist <= self.target_range and dx > 0:
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_enemy = enemy
                    
        return nearest_enemy

class TankTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        super().__init__(x, y, tower_type, biome)
        
    def update(self, dt, game_state):
        """Tank towers just block the path, no special update needed"""
        return False

class EffectTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        super().__init__(x, y, tower_type, biome)
        self.effect_radius = 1  # In grid cells
        self.effect_damage = 5  # Default damage per second
        
        # Special case for DumboOctopus
        if tower_type == 'DumboOctopus':
            self.effect_radius = 2
            self.effect_damage = 15
            
    def update(self, dt, game_state):
        """Apply damage to enemies within effect radius"""
        center_x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
        center_y = self.y * CELL_HEIGHT + CELL_HEIGHT/2
        radius_px = self.effect_radius * CELL_WIDTH
        
        affected_enemies = []
        
        for enemy in game_state.enemies:
            dx = enemy.x - center_x
            dy = enemy.y - center_y
            dist = (dx**2 + dy**2) ** 0.5
            
            if dist <= radius_px:
                # Apply damage based on time
                enemy.take_damage(self.effect_damage * dt)
                affected_enemies.append(enemy)
                
        return affected_enemies
    
    def draw(self, surface):
        """Draw the tower and effect radius"""
        # Draw base tower
        super().draw(surface)
        
        # Draw transparent effect radius
        center_x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
        center_y = self.y * CELL_HEIGHT + CELL_HEIGHT/2
        radius_px = self.effect_radius * CELL_WIDTH
        
        # Create a transparent surface for the effect area
        s = pygame.Surface((radius_px*2, radius_px*2), pygame.SRCALPHA)
        # Draw a transparent circle
        effect_color = (*self.color, 50)  # Add alpha channel (50 = semi-transparent)
        pygame.draw.circle(s, effect_color, (radius_px, radius_px), radius_px)
        
        # Blit the transparent surface onto the main surface
        surface.blit(s, (center_x - radius_px, center_y - radius_px))

class Projectile:
    def __init__(self, x, y, damage, color, target=None):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.speed = 400  # pixels per second
        self.target = target
        self.width = 10
        self.height = 10
        self.active = True
    
    def update(self, dt):
        """Move projectile toward target"""
        if not self.target or not self.active:
            return False
        
        if self.target.is_dead():
            self.active = False
            return False
            
        # Calculate direction vector to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = (dx**2 + dy**2) ** 0.5
        
        # Normalize direction vector
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Move projectile
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        
        # Check collision with target
        if (abs(self.x - self.target.x) < (self.width + self.target.width)/2 and 
            abs(self.y - self.target.y) < (self.height + self.target.height)/2):
            # Hit target
            self.target.take_damage(self.damage)
            self.active = False
            return True
            
        return False
    
    def draw(self, surface):
        """Draw projectile"""
        if self.active:
            pygame.draw.rect(surface, self.color, 
                          (self.x - self.width/2, self.y - self.height/2, 
                           self.width, self.height))
