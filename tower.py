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
    tower_names = [
        'RiftiaTubeWorm', 'Rockfish', 'Hagfish', 'Muusoctopus', 'GiantSquid',
        'SquatLobster', 'SpiderCrab', 'Chimaera', 'SleeperShark', 'ColossalSquid',
        'BlackSmoker', 'BubblePlume', 'BrinePool', 'OsedaxWorm', 'Nautilus',
        'BlueCilliates', 'VesicomyidaeClams', 'MuscleBed', 'DumboOctopus', 'Beggiatoa'
    ]
    
    try:
        for tower_name in tower_names:
            image_path = os.path.join(os.path.dirname(__file__), "assets", f"{tower_name.lower()}.png")
            if os.path.exists(image_path):
                # Load and scale the image to fit the cell size (minus padding)
                original = pygame.image.load(image_path).convert_alpha()
                scaled_size = (CELL_WIDTH - 10, CELL_HEIGHT - 10)  # -10 for padding
                TOWER_IMAGES[tower_name] = pygame.transform.scale(original, scaled_size)
    except Exception as e:
        print(f"Error loading tower images: {e}")

class Tower(BaseTower):
    # Add class-level constants needed for auto-collection
    CELL_WIDTH = CELL_WIDTH
    CELL_HEIGHT = CELL_HEIGHT
    SIDEBAR_WIDTH = SIDEBAR_WIDTH

    def __init__(self, x, y, tower_type, gameplay_manager, biome=None):
        super().__init__()
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.biome = biome
        self.stars = 1  # New: Star rating for tower
        self.power = None  # Will be set in _setup_tower_properties
        self.game_state = None  # Store reference to game state
        self.stunned = False
        self.stun_timer = 0
        self.gameplay_manager = gameplay_manager
        
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

        # Set up star power based on tower type - Beggiatoa handled in its own class
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
        elif self.name == 'GiantSquid':
            self.power = TentacleSweep(self)
        elif self.name == 'ColossalSquid':
            self.power = DeepseaKing(self)
        elif self.name == 'DumboOctopus':
            self.power = OxygenBurst(self)
        elif self.name == 'Nautilus':
            self.power = ResourceNexus(self)
        elif self.name == 'Beggiatoa':
            self.power = BacterialBloom(self)

    def upgrade_star(self):
        """Upgrade tower to next star level"""
        if self.stars < 3:
            self.stars += 1
            self._setup_tower_properties()
            return True
        return False

    def stun(self, duration):
        """Stun the tower for the specified duration"""
        self.stunned = True
        self.stun_timer = duration

    def update(self, dt, game_state):
        """Base update method, override in subclasses"""
        self.game_state = game_state  # Store reference to current game state
        
        # Handle stun effect
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return False

        self.attack_timer += dt
        if self.power:
            self.power.update(dt, game_state)
        return False
        
    def draw(self, surface):
        # Draw tower base
        tower_x = self.x * CELL_WIDTH + SIDEBAR_WIDTH
        tower_y = self.y * CELL_HEIGHT
        
        if self.name in TOWER_IMAGES:
            surface.blit(TOWER_IMAGES[self.name], (tower_x, tower_y))
        else:
            pygame.draw.rect(surface, self.color,
                           (tower_x, tower_y, CELL_WIDTH, CELL_HEIGHT))
        
        # Draw health bar if tower has taken damage
        if self.health < self.max_health:
            HealthBar.draw(surface,
                          tower_x,
                          tower_y - 8,
                          CELL_WIDTH - 10,
                          self.health,
                          self.max_health)
        
        # Draw power effects and energy bar if tower has a power
        if self.power:
            self.power.draw(surface)
            self.power.draw_energy_bar(surface, tower_x, tower_y)

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
    def __init__(self, x, y, tower_type, gameplay_manager, biome):
        super().__init__(x, y, tower_type, gameplay_manager, biome)
        
        # Initialize resource generation properties
        self.resource_amounts = {
            'sulfides': 0,
            'methane': 0,
            'salt': 0,
            'lipids': 0
        }
        
        # Resource spawn timing and position variation
        self.spawn_timer = random.random() * 2.0  # Randomize initial timing
        self.spawn_interval = 2.0  # Base interval, modified by stars
        self.spawn_offset_x = random.randint(-15, 15)  # Fixed offset per tower
        self.manual_collect_bonus = 1.5  # Bonus for manual collection
        
        # Calculate base resource amount with star rating
        base_amount = 10 * (1.35 ** (self.stars - 1))
        
        # Determine resource type based on tower name
        if tower_type == 'Nautilus':
            self.primary_resource = 'all'
            for resource in self.resource_amounts:
                self.resource_amounts[resource] = base_amount * 0.4
            self.spawn_interval = 3.0
        elif tower_type == 'BlackSmoker':
            self.primary_resource = 'sulfides'
            self.resource_amounts[self.primary_resource] = base_amount
        elif tower_type == 'BubblePlume':
            self.primary_resource = 'methane'
            self.resource_amounts[self.primary_resource] = base_amount
        elif tower_type == 'BrinePool':
            self.primary_resource = 'salt'
            self.resource_amounts[self.primary_resource] = base_amount
        elif tower_type == 'OsedaxWorm':
            self.primary_resource = 'lipids'
            self.resource_amounts[self.primary_resource] = base_amount

    def update(self, dt, game_state):
        """Update resource generation and spawn resource orbs"""
        super().update(dt, game_state)
        
        # Don't spawn if stunned
        if self.stunned:
            return []
            
        self.spawn_timer += dt
        spawned_orbs = []
        
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            
            # Calculate spawn position with variation
            tower_center_x = (self.x * CELL_WIDTH + CELL_WIDTH/2) + SIDEBAR_WIDTH
            tower_center_y = self.y * CELL_HEIGHT + CELL_HEIGHT/2
            
            # Add fixed offset plus small random variation
            spawn_x = tower_center_x + self.spawn_offset_x + random.randint(-5, 5)
            spawn_y = tower_center_y - CELL_HEIGHT/4
            
            if self.primary_resource == 'all':
                # Spawn all resource types with slight position variation
                for resource, amount in self.resource_amounts.items():
                    if amount > 0:
                        resource_x = spawn_x + random.randint(-10, 10)
                        resource_y = spawn_y + random.randint(-5, 5)
                        
                        # Create orb with visual enhancements
                        orb = ResourceOrb(
                            resource_x, resource_y,
                            resource, amount,
                            manual_bonus=self.manual_collect_bonus
                        )
                        spawned_orbs.append(orb)
            else:
                # Spawn single resource type
                amount = self.resource_amounts[self.primary_resource]
                if amount > 0:
                    orb = ResourceOrb(
                        spawn_x, spawn_y,
                        self.primary_resource, amount,
                        manual_bonus=self.manual_collect_bonus
                    )
                    spawned_orbs.append(orb)
        
        return spawned_orbs

    def draw(self, surface):
        """Draw the resource tower with enhanced visuals"""
        super().draw(surface)
        
        # Draw resource type indicator
        x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + 5
        y = self.y * CELL_HEIGHT + 5
        
        # Draw tower image or color block
        if self.name in TOWER_IMAGES:
            surface.blit(TOWER_IMAGES[self.name], (x, y))
        else:
            pygame.draw.rect(surface, self.color, 
                           (x, y, CELL_WIDTH - 10, CELL_HEIGHT - 10))
        
        # Draw resource generation indicator
        if self.spawn_timer >= self.spawn_interval * 0.8:
            progress = (self.spawn_timer - self.spawn_interval * 0.8) / (self.spawn_interval * 0.2)
            indicator_alpha = int(255 * progress)
            
            # Create glowing effect for resource generation
            glow_surface = pygame.Surface((CELL_WIDTH, CELL_HEIGHT), pygame.SRCALPHA)
            center_x = CELL_WIDTH // 2
            center_y = CELL_HEIGHT // 2
            
            # Draw multiple circles with decreasing alpha for glow effect
            for r in range(4, 0, -1):
                glow_alpha = indicator_alpha // (r + 1)
                glow_color = (*self.color[:3], glow_alpha)
                radius = 3 + (4 - r) * 2 * progress
                pygame.draw.circle(glow_surface, glow_color,
                                 (center_x, center_y), radius)
            
            # Apply glow effect
            surface.blit(glow_surface, (x, y), special_flags=pygame.BLEND_ADD)
            
    def upgrade(self):
        """Upgrade the tower's resource generation"""
        if super().upgrade():
            # Increase resource generation
            for resource in self.resource_amounts:
                if self.resource_amounts[resource] > 0:
                    self.resource_amounts[resource] *= 1.5
            
            # Decrease spawn interval
            self.spawn_interval *= 0.8
            return True
        return False

class ProjectileTower(Tower):
    """A tower that fires projectiles at enemies"""
    def __init__(self, x, y, tower_type, gameplay_manager, biome):
        super().__init__(x, y, tower_type, gameplay_manager, biome)
        self.projectiles = []
        self.target_range = 400  # Default range, will be modified by _setup_tower_properties
        self.cooldown = 0.5  # Default cooldown between shots

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
    def __init__(self, x, y, tower_type, gameplay_manager, biome):
        super().__init__(x, y, tower_type, gameplay_manager, biome)
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
    def __init__(self, x, y, tower_type, gameplay_manager, biome):
        # Set effect properties first - increase base values
        self.effect_radius = 2.0  # Increased base radius in grid cells
        self.effect_damage = 15  # Increased base damage per second
        
        # Special case for DumboOctopus
        if tower_type == 'DumboOctopus':
            self.effect_radius = 2.5
            self.effect_damage = 20
            
        # Now call parent init which will set up powers
        super().__init__(x, y, tower_type, gameplay_manager, biome)
        
        # Apply star rating multiplier to effect damage
        self.effect_damage *= (1.5 ** (self.stars - 1))
        
        # Effect towers don't have collision to allow stacking
        self.has_collision = False
        
        # Track enemies in range for consistent damage application
        self.affected_enemies = set()
        self.damage_timer = 0
        self.damage_interval = 0.1  # Apply damage every 0.1 seconds for smoother application
        
    def update(self, dt, game_state):
        """Apply damage to enemies within effect radius"""
        super().update(dt, game_state)  # Call parent update to store game_state
        
        if not self.stunned:  # Only apply effects if not stunned
            self.damage_timer += dt
            
            if self.damage_timer >= self.damage_interval:
                center_x = self.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
                center_y = self.y * CELL_HEIGHT + CELL_HEIGHT/2
                radius_px = self.effect_radius * CELL_WIDTH
                
                # Clear old affected enemies set
                self.affected_enemies.clear()
                
                # Check which enemies are in range and apply damage
                for enemy in game_state.enemies:
                    dx = enemy.x - center_x
                    dy = enemy.y - center_y
                    dist = (dx**2 + dy**2) ** 0.5
                    
                    if dist <= radius_px:
                        # Calculate damage with distance falloff
                        falloff = 1.0 - (dist / radius_px)
                        # Calculate damage for this interval
                        interval_damage = self.effect_damage * falloff * self.damage_timer
                        
                        # Apply damage and notify power
                        enemy.take_damage(interval_damage)
                        if self.power and hasattr(self.power, 'on_damage_dealt'):
                            self.power.on_damage_dealt(enemy, interval_damage)
                        self.affected_enemies.add(enemy)
                
                # Reset damage timer
                self.damage_timer = 0
                
                # Update power and check if it wants to apply additional effects
                if self.power:
                    power_ready = self.power.update(dt, game_state)
                    if power_ready:
                        self.power.activate()
            
            return list(self.affected_enemies)
        return []
        
    def draw(self, surface):
        """Draw the tower"""
        # Draw base tower
        super().draw(surface)
        
        # Let the power handle drawing the effect area
        # The effect area is now handled by TowerPower.draw_area_effect()

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

class EffectProjectile:
    """Invisible projectile for handling area effect damage"""
    def __init__(self, x, y, damage, effect_radius, tower):
        self.x = x
        self.y = y
        self.damage = damage
        self.effect_radius = effect_radius
        self.tower = tower
        self.active = True
        self.lifetime = 0.1  # Short lifetime for quick damage application
        
    def update(self, dt, enemies):
        """Apply damage to enemies in range"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return False
            
        # Find all enemies in range and apply damage
        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            
            if dist <= self.effect_radius:
                # Calculate damage falloff
                falloff = 1.0 - (dist / self.effect_radius)
                actual_damage = self.damage * falloff * dt
                
                # Apply damage and notify power
                enemy.take_damage(actual_damage)
                if self.tower.power and hasattr(self.tower.power, 'on_damage_dealt'):
                    self.tower.power.on_damage_dealt(enemy, actual_damage)
                    
        return True

# Keep the create_tower function
def create_tower(tower_name, grid_x, grid_y, gameplay_manager, star_level=1):
    """Create a new tower of the appropriate type"""
    tower = None
    
    # Handle all tower types equally
    if tower_name in ['BlackSmoker', 'BubblePlume', 'BrinePool', 'OsedaxWorm', 'Nautilus']:
        tower = ResourceTower(grid_x, grid_y, tower_name, gameplay_manager, gameplay_manager.biome)
    elif tower_name in ['RiftiaTubeWorm', 'Rockfish', 'Hagfish', 'Muusoctopus', 'GiantSquid']:
        tower = ProjectileTower(grid_x, grid_y, tower_name, gameplay_manager, gameplay_manager.biome)
    elif tower_name in ['SquatLobster', 'SpiderCrab', 'Chimaera', 'SleeperShark', 'ColossalSquid']:
        tower = TankTower(grid_x, grid_y, tower_name, gameplay_manager, gameplay_manager.biome)
    elif tower_name in ['BlueCilliates', 'VesicomyidaeClams', 'MuscleBed', 'DumboOctopus', 'Beggiatoa']:
        tower = EffectTower(grid_x, grid_y, tower_name, gameplay_manager, gameplay_manager.biome)
            
    if tower:
        tower.stars = star_level
        tower._setup_tower_properties()
    return tower
