import pygame
import random
import os
from config import *
from ui import HealthBar, StarDisplay
from resource_orb import ResourceOrb
from base_types import BaseTower
from powers import *

# Global dictionary to store tower images
TOWER_IMAGES = {}

def initialize_tower_images():
    """Initialize tower images after pygame.display is initialized"""
    try:
        riftia_path = os.path.join(os.path.dirname(__file__), "assets", "riftia.png")
        if os.path.exists(riftia_path):
            # Load and scale the image to fit the cell size (minus padding)
            original = pygame.image.load(riftia_path).convert_alpha()
            scaled_size = (CELL_WIDTH - 10, CELL_HEIGHT - 10)  # -10 for padding
            TOWER_IMAGES['RiftiaTubeWorm'] = pygame.transform.scale(original, scaled_size)
    except Exception as e:
        print(f"Error loading tower images: {e}")

class Tower(BaseTower):
    # Add class-level constants needed for auto-collection
    CELL_WIDTH = CELL_WIDTH
    CELL_HEIGHT = CELL_HEIGHT
    SIDEBAR_WIDTH = SIDEBAR_WIDTH

    def __init__(self, x, y, tower_type, biome=None):
        super().__init__()
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.biome = biome
        self.stars = 1  # New: Star rating for tower
        self.power = None  # Will be set in _setup_tower_properties
        self.game_state = None  # Store reference to game state
        
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
        
        # Add collision properties
        self.has_collision = True  # Default to solid
        if tower_type in ['BlueCilliates', 'VesicomyidaeClams', 'MuscleBed', 'Beggiatoa', 'DumboOctopus']:
            self.has_collision = False  # Area effect towers can be walked through
        
        # Collision box (used for precise collision detection)
        self.collision_rect = pygame.Rect(
            x * CELL_WIDTH + SIDEBAR_WIDTH + 10,  # Add padding for visual alignment
            y * CELL_HEIGHT + 10,
            CELL_WIDTH - 20,  # Slightly smaller than cell for visual clarity
            CELL_HEIGHT - 20
        )
        
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

        # Set up star power based on tower type
        if self.name == 'BlackSmoker':
            self.power = HydroPressure(self)
        elif self.name == 'BubblePlume':
            self.power = MethaneEruption(self)
        elif self.name == 'BrinePool':
            self.power = BrineSpray(self)
        elif self.name == 'OsedaxWorm':
            self.power = LipidSiphon(self)
        elif self.name == 'RiftiaTubeWorm':
            self.power = VenomShot(self)
        elif self.name == 'Rockfish':
            self.power = SonicPulse(self)
        elif self.name == 'Hagfish':
            self.power = ElectricShock(self)
        elif self.name == 'Muusoctopus':
            self.power = InkCloud(self)
        elif self.name == 'SquatLobster':
            self.power = Regeneration(self)
        elif self.name == 'SpiderCrab':
            self.power = SpikePlating(self)
        elif self.name == 'Chimaera':
            self.power = BerserkMode(self)
        elif self.name == 'SleeperShark':
            self.power = FrenzyBite(self)
        elif self.name == 'BlueCilliates':
            self.power = ChainReaction(self)
        elif self.name == 'VesicomyidaeClams':
            self.power = FilterFeeding(self)
        elif self.name == 'MuscleBed':
            self.power = MusclePulse(self)
        elif self.name == 'Beggiatoa':
            self.power = BacterialBloom(self)
        elif self.name == 'GiantSquid':
            self.power = TentacleSweep(self)
        elif self.name == 'ColossalSquid':
            self.power = DeepseaKing(self)
        elif self.name == 'DumboOctopus':
            self.power = OxygenBurst(self)
        elif self.name == 'Nautilus':
            self.power = ResourceNexus(self)

    def upgrade_star(self):
        """Upgrade tower to next star level"""
        if self.stars < 3:
            self.stars += 1
            self._setup_tower_properties()
            return True
        return False

    def update(self, dt, game_state):
        """Base update method, override in subclasses"""
        self.game_state = game_state  # Store reference to current game state
        self.attack_timer += dt
        if self.power:
            self.power.update(dt, game_state)
        return False
        
    def draw(self, surface):
        """Draw the tower on the grid with star indicators"""
        # Calculate the position for drawing
        x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + 5
        y = self.y * CELL_HEIGHT + 5
        
        # If we have an image for this tower, use it
        if (self.name in TOWER_IMAGES):
            surface.blit(TOWER_IMAGES[self.name], (x, y))
        else:
            # Fallback to colored rectangle
            pygame.draw.rect(surface, self.color, 
                           (x, y, CELL_WIDTH - 10, CELL_HEIGHT - 10))
        
        # Draw stars using shared StarDisplay component
        StarDisplay.draw(surface, x, y, self.stars)
        
        # Draw health bar if tower has been damaged using shared HealthBar component
        if self.health < self.max_health:
            HealthBar.draw(surface, x, y - 8, CELL_WIDTH - 10, self.health, self.max_health)
        
    def take_damage(self, amount, attacker=None):
        """Take damage from enemies"""
        self.health -= amount
        if self.power and hasattr(self.power, 'on_damaged'):
            self.power.on_damaged(attacker, amount)
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
            
    def update_collision_rect(self):
        """Update collision rectangle position when tower moves"""
        self.collision_rect.x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + 10
        self.collision_rect.y = self.y * CELL_HEIGHT + 10
    
    def check_collision(self, enemy_rect):
        """Check if this tower collides with an enemy"""
        if not self.has_collision:
            return False
        return self.collision_rect.colliderect(enemy_rect)

class ResourceTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        super().__init__(x, y, tower_type, biome)
        self.resource_amounts = {
            'sulfides': 2,
            'methane': 2,
            'salt': 2,
            'lipids': 2
        }
        
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # Spawn resource every 2 seconds
        
        # Set primary resource based on biome
        if biome == Biome.HYDROTHERMAL:
            self.resource_amounts['sulfides'] = 10
            self.primary_resource = 'sulfides'
        elif biome == Biome.COLDSEEP:
            self.resource_amounts['methane'] = 10
            self.primary_resource = 'methane'
        elif biome == Biome.BRINE_POOL:
            self.resource_amounts['salt'] = 10
            self.primary_resource = 'salt'
        elif biome == Biome.WHALEFALL:
            self.resource_amounts['lipids'] = 10
            self.primary_resource = 'lipids'
            
        # Special case for Nautilus rare tower
        if tower_type == 'Nautilus':
            for resource in self.resource_amounts:
                self.resource_amounts[resource] = 5
            self.primary_resource = 'all'
                
        # Apply star rating multiplier
        for resource in self.resource_amounts:
            self.resource_amounts[resource] *= (1.5 ** (self.stars - 1))
    
    def update(self, dt, game_state):
        self.spawn_timer += dt
        spawned_orbs = []
        
        # Check if it's time to spawn resources
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            
            # Calculate spawn position above the tower
            tower_center_x = (self.x * CELL_WIDTH + CELL_WIDTH/2) + SIDEBAR_WIDTH
            tower_center_y = self.y * CELL_HEIGHT
            
            # Add small random horizontal offset but spawn above tower
            spawn_x = tower_center_x + random.randint(-10, 10)
            spawn_y = tower_center_y
            
            if self.primary_resource == 'all':
                # Nautilus spawns all resource types
                for resource, amount in self.resource_amounts.items():
                    if amount > 0:
                        spawned_orbs.append(ResourceOrb(spawn_x, spawn_y, resource, amount))
            else:
                # Other towers spawn their primary resource
                spawned_orbs.append(ResourceOrb(
                    spawn_x, spawn_y,
                    self.primary_resource,
                    self.resource_amounts[self.primary_resource]
                ))
                
        return spawned_orbs
        
    def draw(self, surface):
        # Draw base tower
        x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + 5
        y = self.y * CELL_HEIGHT + 5
        
        # If we have an image for this tower, use it
        if self.name in TOWER_IMAGES:
            surface.blit(TOWER_IMAGES[self.name], (x, y))
        else:
            # Fallback to colored rectangle
            pygame.draw.rect(surface, self.color, 
                           (x, y, CELL_WIDTH - 10, CELL_HEIGHT - 10))
        
        # Draw stars and health bar
        StarDisplay.draw(surface, x, y, self.stars)
        if self.health < self.max_health:
            HealthBar.draw(surface, x, y - 8, CELL_WIDTH - 10, self.health, self.max_health)

class ProjectileTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        super().__init__(x, y, tower_type, biome)
        
    def update(self, dt, game_state):
        """Update projectile tower and check for enemy targets"""
        super().update(dt, game_state)
        
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
                    'target': target,
                    'tower': self  # Pass tower reference for power effects
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
        self.attack_cooldown = 1.0  # Attack once per second
        self.attack_timer = 0
        self.melee_damage = 15  # Base melee damage
        
        # Special stats for Colossal Squid
        if tower_type == 'ColossalSquid':
            self.melee_damage = 25
            self.attack_cooldown = 0.8
            
        # Apply star rating multipliers
        self.melee_damage *= (1.5 ** (self.stars - 1))
        self.attack_cooldown *= (0.8 ** (self.stars - 1))
        
    def update(self, dt, game_state):
        """Tank towers deal damage to enemies that collide with them"""
        super().update(dt, game_state)
        
        # Check for colliding enemies when attack is ready
        if self.attack_timer >= self.attack_cooldown:
            for enemy in game_state.enemies:
                if self.check_collision(enemy.collision_rect):
                    enemy.take_damage(self.melee_damage)
                    if self.power and hasattr(self.power, 'on_damage_dealt'):
                        self.power.on_damage_dealt(enemy, self.melee_damage)
                    self.attack_timer = 0  # Reset attack timer
                    break  # Only damage one enemy per attack
        
        return False

class EffectTower(Tower):
    def __init__(self, x, y, tower_type, biome):
        # Set effect properties first
        self.effect_radius = 1  # In grid cells
        self.effect_damage = 5  # Default damage per second
        
        # Special case for DumboOctopus
        if tower_type == 'DumboOctopus':
            self.effect_radius = 2
            self.effect_damage = 15
            
        # Now call parent init which will set up powers
        super().__init__(x, y, tower_type, biome)
        
        # Apply star rating multiplier to effect damage
        self.effect_damage *= (1.5 ** (self.stars - 1))

    def update(self, dt, game_state):
        """Apply damage to enemies within effect radius"""
        super().update(dt, game_state)  # Call parent update to store game_state
        
        center_x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
        center_y = self.y * CELL_HEIGHT + CELL_HEIGHT/2
        radius_px = self.effect_radius * CELL_WIDTH
        
        affected_enemies = []
        
        for enemy in game_state.enemies:
            dx = enemy.x - center_x
            dy = enemy.y - center_y
            dist = (dx**2 + dy**2) ** 0.5
            
            if dist <= radius_px:
                damage = self.effect_damage * dt
                enemy.take_damage(damage)
                if self.power and hasattr(self.power, 'on_damage_dealt'):
                    self.power.on_damage_dealt(enemy, damage)
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
