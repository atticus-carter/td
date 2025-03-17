import random
import math
import pygame
from config import *
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from config import GameState
from base_types import BaseTower
from energy_system import EnergySystem, ENERGY_COSTS, ENERGY_GEN_RATES, BIOME_POWER_MODIFIERS

# Only import types for type checking to avoid circular imports
if TYPE_CHECKING:
    from tower import ResourceTower, Tower

class Power:
    def __init__(self, tower: 'BaseTower'):
        self.tower = tower
        self.active = True
        
    def update(self, dt, game_state):
        pass
        
    def on_damage_dealt(self, enemy, damage):
        pass
        
    def on_damaged(self, attacker, damage):
        pass

class PowerEffect:
    def __init__(self, x, y, color, duration=0.5, size=32, style='burst'):
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.size = size
        self.style = style  # 'burst', 'wave', 'spiral', 'rays'
        self.alpha = 255
        self.scale = 1.0
        self.angle = 0
        self.cell_size = 8  # Size of pixelation cells
        self.effect_alpha = 60  # Base effect opacity
        self.effect_pulse_speed = 30  # Speed of alpha pulsing
        self.alpha_direction = 1  # Direction of alpha pulsing

    def update(self, dt):
        self.duration -= dt
        progress = 1 - (self.duration / self.max_duration)
        self.alpha = int(255 * (1 - progress))
        self.scale = 1 + progress
        self.angle += dt * 180  # Rotate 180 degrees per second
        
        # Pulse the effect alpha
        self.effect_alpha += dt * self.effect_pulse_speed * self.alpha_direction
        if self.effect_alpha > 60:  # Max alpha
            self.alpha_direction = -1
        elif self.effect_alpha < 10:  # Min alpha
            self.alpha_direction = 1
            
    def draw(self, surface):
        if self.duration <= 0:
            return
            
        # Create pixelated effect surface
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        cells = self.size * 2 // self.cell_size
        
        for x in range(cells):
            for y in range(cells):
                # Calculate distance from center for circular effect
                cx = (x * self.cell_size + self.cell_size/2) - self.size
                cy = (y * self.cell_size + self.cell_size/2) - self.size
                dist = (cx*cx + cy*cy) ** 0.5
                
                if dist <= self.size:
                    # Calculate alpha based on distance and current effect alpha
                    alpha = int(max(0, self.effect_alpha * (1 - dist/self.size)))
                    
                    # Add some randomization for texture
                    if random.random() > 0.3:
                        color = (*self.color, alpha)
                        pygame.draw.rect(s, color,
                                      (x * self.cell_size, y * self.cell_size,
                                       self.cell_size, self.cell_size))
                       
        # Draw the effect with rotation and scaling
        rotated = pygame.transform.rotate(s, self.angle)
        scaled = pygame.transform.scale(rotated, 
                                     (int(rotated.get_width() * self.scale),
                                      int(rotated.get_height() * self.scale)))
        
        # Center the effect on its position
        pos = (self.x - scaled.get_width()//2,
               self.y - scaled.get_height()//2)
        surface.blit(scaled, pos)

class TowerPower(Power):
    def __init__(self, tower: 'BaseTower'):
        super().__init__(tower)
        power_class_name = self.__class__.__name__
        
        # Initialize energy system
        self.energy = EnergySystem(tower)
        
        # Visual effect properties
        self.active_duration = 0
        self.active = False
        self.effect_alpha = 0
        self.effect_pulse_speed = 40  # Slower pulse
        self.cell_size = 8  # Smaller cells for more detail
        self.effect_radius = CELL_WIDTH  # Default radius
        self.aura_alpha = 35  # Lower base alpha for less opacity
        self.alpha_direction = 1
        self.grid_seed = hash(f"{tower.x}{tower.y}")  # Fixed seed for this tower's pattern
        self.colony_noise = {}  # Store noise values for colony shape
        
        # Set power-specific effect colors
        if isinstance(self, (HydroPressure, OxygenBurst)):
            self.effect_color = (180, 220, 255)  # Blue for water/oxygen effects
        elif isinstance(self, (MethaneEruption, BacterialBloom)):
            self.effect_color = (200, 150, 255)  # Purple for gas/bacterial effects
        elif isinstance(self, (VenomShot, BrineSpray)):
            self.effect_color = (150, 255, 150)  # Green for poison/corrosive effects
        elif isinstance(self, ElectricShock):
            self.effect_color = (255, 255, 150)  # Yellow for electric effects
        elif isinstance(self, InkCloud):
            self.effect_color = (100, 100, 100)  # Dark gray for ink effects
        else:
            self.effect_color = (220, 220, 255)  # Default effect color
            
    def _get_colony_noise(self, x, y):
        """Get deterministic noise value for colony shape"""
        key = f"{x},{y}"
        if key not in self.colony_noise:
            random.seed(self.grid_seed + hash(key))
            # Create more organic shapes by using multiple noise frequencies
            base_noise = random.random()
            detail_noise = random.random() * 0.3
            self.colony_noise[key] = base_noise + detail_noise
            random.seed()  # Reset seed
        return self.colony_noise[key]
            
    def draw_area_effect(self, surface, persistent=False):
        """Draw a standardized area effect for powers"""
        if not (self.active or persistent):
            return
            
        # Calculate center position
        center_x = self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
        center_y = self.tower.y * CELL_HEIGHT + CELL_HEIGHT/2
        
        # Create effect surface with alpha
        s = pygame.Surface((int(self.effect_radius * 2.2), int(self.effect_radius * 2.2)), pygame.SRCALPHA)
        
        # Create organic colony pattern
        cells = int(self.effect_radius * 2.2 // self.cell_size)
        
        for x in range(cells):
            for y in range(cells):
                # Calculate base position relative to center
                cx = (x * self.cell_size + self.cell_size/2) - self.effect_radius
                cy = (y * self.cell_size + self.cell_size/2) - self.effect_radius
                base_dist = math.sqrt(cx*cx + cy*cy)
                
                # Get noise value for this cell
                noise = self._get_colony_noise(x, y)
                
                # Modify the distance check with noise to create irregular edges
                effective_radius = self.effect_radius * (0.8 + noise * 0.4)
                
                if base_dist <= effective_radius:
                    # Use either pulse effect or persistent aura with distance falloff
                    if persistent:
                        base_alpha = self.aura_alpha
                    else:
                        base_alpha = self.effect_alpha
                    
                    # Calculate alpha with distance falloff and noise
                    dist_factor = 1.0 - (base_dist / effective_radius)
                    noise_factor = 0.7 + (noise * 0.3)  # Noise affects transparency
                    alpha = int(max(0, base_alpha * dist_factor * noise_factor))
                    
                    if noise > 0.3:  # Only draw some cells for more organic look
                        # Draw cell with slight random offset
                        offset_x = int(noise * 2) - 1
                        offset_y = int((noise * 7919) % 2) - 1  # Use prime for different pattern
                        
                        pygame.draw.rect(s, (*self.effect_color, alpha),
                                       (x * self.cell_size + offset_x,
                                        y * self.cell_size + offset_y,
                                        self.cell_size - 1, self.cell_size - 1))
        
        # Draw the effect centered on the tower
        surface.blit(s, (center_x - self.effect_radius * 1.1, 
                        center_y - self.effect_radius * 1.1))

    def update(self, dt, game_state):
        # Update energy generation
        energy_ready = self.energy.update(dt)
            
        # Update visual effects with slower pulsing
        if self.effect_alpha > 0:
            self.effect_alpha = max(0, self.effect_alpha - dt * self.effect_pulse_speed)
            
        # Pulse the aura alpha very slowly
        self.aura_alpha += dt * 20 * self.alpha_direction  # Much slower pulse
        if self.aura_alpha > 50:
            self.alpha_direction = -1
        elif self.aura_alpha < 30:
            self.alpha_direction = 1
        
        # Check for active abilities
        if self.active and self.active_duration > 0:
            self.active_duration -= dt
            if self.active_duration <= 0:
                self.deactivate()
        
        return energy_ready
                
    def activate(self):
        """Activate the power if we have enough energy"""
        if self.energy.use_energy():
            self.active = True
            self.effect_alpha = 60  # Flash effect on activation
            return True
        return False
        
    def deactivate(self):
        self.active = False

    def draw(self, surface):
        """Draw power effect if active"""
        if self.effect_alpha > 0:
            # Create pixelated effect surface
            effect_size = int(CELL_WIDTH * 2)
            s = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)
            
            # Calculate center position
            center_x = self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
            center_y = self.tower.y * CELL_HEIGHT + CELL_HEIGHT/2
            
            cells_x = effect_size // self.cell_size
            cells_y = effect_size // self.cell_size
            
            for x in range(cells_x):
                for y in range(cells_y):
                    # Calculate distance from center for circular effect
                    cx = (x * self.cell_size + self.cell_size/2) - effect_size/2
                    cy = (y * self.cell_size + self.cell_size/2) - effect_size/2
                    dist = math.sqrt(cx*cx + cy*cy)
                    
                    if dist <= effect_size/2:
                        # Calculate alpha based on distance and current effect alpha
                        alpha = int(max(0, self.effect_alpha * (1 - dist/(effect_size/2))))
                        color = (*self.effect_color, alpha)
                        
                        # Add some randomization for pixelated effect
                        if random.random() > 0.3:
                            pygame.draw.rect(s, color,
                                          (x * self.cell_size, y * self.cell_size,
                                           self.cell_size, self.cell_size))
            
            # Draw the effect centered on the tower
            surface.blit(s, (center_x - effect_size/2, center_y - effect_size/2))
    
    def draw_energy_bar(self, surface, x, y):
        """Draw the energy bar for this tower power"""
        self.energy.draw(surface, x, y)

# Resource Tower Powers
class HydroPressure(TowerPower):
    """BlackSmoker: Creates pressure waves that boost nearby resource generation"""
    def __init__(self, tower: 'BaseTower'):
        super().__init__(tower)
        self.radius = 2 * CELL_WIDTH
        self.boost_amount = 0.3 * tower.stars  # Reduced to 30/60/90% boost
        self.active_duration = 4.0  # Shorter duration
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        # Use energy when available and not already active
        if energy_ready and not self.active:
            if self.activate():
                self.active_duration = 4.0
            
        if self.active:
            for other_tower in game_state.towers:
                if other_tower != self.tower and hasattr(other_tower, 'resource_amounts'):
                    dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                    dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                    if (dx*dx + dy*dy) <= self.radius*self.radius:
                        # Apply temporary boost that doesn't compound
                        for resource in other_tower.resource_amounts:
                            other_tower.resource_amounts[resource] *= (1 + self.boost_amount)

class MethaneEruption(TowerPower):
    """BubblePlume: Periodically releases methane explosions"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.damage = 20 * tower.stars
        self.radius = 1.5 * CELL_WIDTH
        self.effect_color = (200, 150, 255)  # Purple-tinted methane
        self.effect_pulse_speed = 240  # Faster pulse for explosion effect
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                # Create explosion effect
                self.effect_alpha = 60  # Bright flash
                for enemy in game_state.enemies:
                    dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                    dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                    if (dx*dx + dy*dy) <= self.radius*self.radius:
                        enemy.take_damage(self.damage)

class BrineSpray(TowerPower):
    """BrinePool: Sprays corrosive brine that slows enemies"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.slow_factor = 0.3 * tower.stars  # 30/60/90% slow
        self.slow_duration = 3.0
        self.radius = 2 * CELL_WIDTH
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                for enemy in game_state.enemies:
                    dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                    dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                    if (dx*dx + dy*dy) <= self.radius*self.radius:
                        enemy.speed_multiplier = max(0.1, 1 - self.slow_factor)
                        enemy.slow_duration = self.slow_duration

class LipidSiphon(TowerPower):
    """OsedaxWorm: Drains resources from enemies to boost production"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.drain_amount = 2 * tower.stars
        self.radius = 1.5 * CELL_WIDTH
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                for enemy in game_state.enemies:
                    dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                    dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                    if (dx*dx + dy*dy) <= self.radius*self.radius:
                        enemy.take_damage(self.drain_amount)
                        for resource in self.tower.resource_amounts:
                            self.tower.resource_amounts[resource] += 1

# Projectile Tower Powers
class VenomShot(TowerPower):
    """RiftiaTubeWorm: Applies poison damage over time"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.poison_damage = 5 * tower.stars
        self.poison_duration = 3.0
        self.poison_chance = 0.3 * tower.stars  # 30/60/90% chance
        
    def on_hit(self, target):
        # For passive powers that trigger on hit, try to use energy
        if self.energy.use_energy() and random.random() < self.poison_chance:
            target.poisoned = True
            target.poison_damage = self.poison_damage
            target.poison_duration = self.poison_duration

class SonicPulse(TowerPower):
    """Rockfish: Releases sonic waves that stun enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.stun_duration = 1.0 * tower.stars
        self.radius = 2 * CELL_WIDTH
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                for enemy in game_state.enemies:
                    dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                    dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                    if (dx*dx + dy*dy) <= self.radius*self.radius:
                        enemy.is_stunned = True
                        enemy.stun_timer = self.stun_duration

class ElectricShock(TowerPower):
    """Hagfish: Chain lightning between enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.chain_count = tower.stars + 1  # 2/3/4 targets
        self.chain_damage = 15 * tower.stars
        self.chain_range = 150
        
    def on_hit(self, target):
        # For powers that trigger on hit, try to use energy
        if self.energy.use_energy():
            hit_enemies = [target]
            current_target = target
            damage = self.chain_damage
            
            # Find additional chain targets
            for _ in range(self.chain_count - 1):
                next_target = None
                min_dist = self.chain_range
                
                for enemy in self.tower.game_state.enemies:
                    if enemy not in hit_enemies:
                        dx = enemy.x - current_target.x
                        dy = enemy.y - current_target.y
                        dist = (dx*dx + dy*dy) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            next_target = enemy
                
                if next_target:
                    damage *= 0.7  # Reduce damage by 30% per jump
                    next_target.take_damage(damage)
                    hit_enemies.append(next_target)
                    current_target = next_target
                else:
                    break

class InkCloud(TowerPower):
    """Muusoctopus: Creates ink clouds that blind enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.cloud_duration = 4.0 * tower.stars
        self.cloud_radius = 2 * CELL_WIDTH
        self.damage = 10 * tower.stars
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                # Create ink cloud effect
                for enemy in game_state.enemies:
                    dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                    dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                    if (dx*dx + dy*dy) <= self.cloud_radius*self.cloud_radius:
                        enemy.speed_multiplier *= 0.5
                        enemy.take_damage(self.damage)
                self.active_duration = self.cloud_duration

# Tank Tower Powers
class Regeneration(TowerPower):
    """SquatLobster: Regenerates health over time"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.heal_rate = 5 * tower.stars  # Health per second
        # Passive power with low energy cost
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        # If we have energy and the tower needs healing, use energy to heal
        if energy_ready and self.tower.health < self.tower.max_health:
            if self.activate():
                self.tower.health = min(self.tower.max_health,
                                      self.tower.health + self.heal_rate * 5)

class SpikePlating(TowerPower):
    """SpiderCrab: Reflects damage back to attackers"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.reflect_percent = 0.2 * tower.stars  # 20/40/60% reflection
        
    def on_damaged(self, attacker, damage):
        # For defensive powers that trigger on being attacked
        if self.energy.use_energy() and attacker:
            reflected = damage * self.reflect_percent
            attacker.take_damage(reflected)

class BerserkMode(TowerPower):
    """Chimaera: Gains attack speed when damaged"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.speed_boost = 0.2 * tower.stars  # 20/40/60% boost
        self.active_duration = 5.0
        
    def on_damaged(self, attacker, damage):
        if self.tower.health < self.tower.max_health * 0.5:
            if self.energy.use_energy():
                self.active = True
                self.active_duration = 5.0
                self.tower.attack_cooldown *= (1 - self.speed_boost)
                
    def deactivate(self):
        super().deactivate()
        # Restore original attack cooldown when effect ends
        if hasattr(self, 'speed_boost'):
            self.tower.attack_cooldown /= (1 - self.speed_boost)

class FrenzyBite(TowerPower):
    """SleeperShark: Multiple rapid attacks"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.frenzy_duration = 3.0
        self.attack_multiplier = tower.stars  # 1/2/3x attack speed
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready and not self.active:
            if self.activate():
                self.active = True
                self.active_duration = self.frenzy_duration
                self.tower.attack_cooldown /= (1 + self.attack_multiplier)
        
        if self.active and self.active_duration <= 0:
            self.tower.attack_cooldown *= (1 + self.attack_multiplier)
            self.active = False

# Effect Tower Powers
class ChainReaction(TowerPower):
    """BlueCilliates: Damage spreads between enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.effect_radius = CELL_WIDTH * 2.0  # Increased radius
        self.chain_cooldown = 0.2  # Faster chains
        self.chain_timer = 0
        self.chain_damage = tower.effect_damage * 0.4 * tower.stars
        self.active = True
        
    def on_damage_dealt(self, enemy, damage):
        """When base damage is dealt, try to chain to nearby enemies"""
        if self.energy.use_energy():
            # Find nearby enemies to chain to
            center_x = enemy.x
            center_y = enemy.y
            chained = [enemy]  # Track who we've already hit
            current_damage = self.chain_damage
            
            for potential in self.tower.game_state.enemies:
                if potential not in chained:
                    dx = potential.x - center_x
                    dy = potential.y - center_y
                    dist = (dx*dx + dy*dy) ** 0.5
                    
                    if dist <= self.effect_radius:
                        potential.take_damage(current_damage)
                        chained.append(potential)
                        current_damage *= 0.7  # Reduce chain damage
                        
            # Visual feedback
            self.effect_alpha = 40
    
    def draw(self, surface):
        self.draw_area_effect(surface, persistent=True)
        super().draw(surface)

class FilterFeeding(TowerPower):
    """VesicomyidaeClams: Converts damage dealt to resources"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.effect_radius = CELL_WIDTH * 1.8
        self.conversion_rate = 0.2 * tower.stars  # Increased conversion
        self.stored_damage = 0
        self.conversion_threshold = 5  # Lower threshold
        self.active = True
        
    def on_damage_dealt(self, enemy, damage):
        # Store damage for conversion
        self.stored_damage += damage * self.conversion_rate
        
        # Convert stored damage to resources when threshold is reached
        while self.stored_damage >= self.conversion_threshold:
            self.stored_damage -= self.conversion_threshold
            if hasattr(self.tower, 'resource_amounts'):
                for resource in self.tower.resource_amounts:
                    self.tower.resource_amounts[resource] += 1
                # Visual feedback
                self.effect_alpha = 40
    
    def draw(self, surface):
        self.draw_area_effect(surface, persistent=True)
        super().draw(surface)

class MusclePulse(TowerPower):
    """MuscleBed: Pulses that push enemies back"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.effect_radius = CELL_WIDTH * 2.2
        self.push_force = 100 * tower.stars  # Increased force
        self.pulse_interval = 0.5  # Faster pulses
        self.pulse_timer = 0
        self.active = True
        
    def on_damage_dealt(self, enemy, damage):
        """Apply push effect when damage is dealt"""
        if self.energy.use_energy():
            # Calculate push direction
            center_x = self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH + CELL_WIDTH/2
            center_y = self.tower.y * CELL_HEIGHT + CELL_HEIGHT/2
            dx = enemy.x - center_x
            dy = enemy.y - center_y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist > 0:
                dx /= dist
                dy /= dist
                
                # Calculate push force with falloff
                falloff = 1.0 - (dist / self.effect_radius)
                force = self.push_force * falloff
                
                # Apply push
                enemy.x += dx * force * 0.016  # Assuming 60fps for consistent push
                enemy.y += dy * force * 0.016
                
            # Visual feedback
            self.effect_alpha = 40
    
    def draw(self, surface):
        self.draw_area_effect(surface, persistent=True)
        super().draw(surface)

class BacterialBloom(TowerPower):
    """Power for Beggiatoa: Creates a toxic area that damages enemies over time"""
    def __init__(self, tower):
        super().__init__(tower)
        self.effect_radius = CELL_WIDTH * 2.0
        self.damage_multiplier = 0.3  # Additional damage on top of base
        self.slow_effect = 0.4 * tower.stars  # Increased slow
        self.active = True
        
    def on_damage_dealt(self, enemy, damage):
        """Apply additional effects when base damage is dealt"""
        if self.energy.use_energy():
            # Apply additional damage
            enemy.take_damage(damage * self.damage_multiplier)
            
            # Apply slow effect
            enemy.speed_multiplier = max(0.2, enemy.speed_multiplier * (1.0 - self.slow_effect))
            
            # Visual feedback
            self.effect_alpha = 40
    
    def draw(self, surface):
        self.draw_area_effect(surface, persistent=True)
        super().draw(surface)

# Rare Tower Powers
class TentacleSweep(TowerPower):
    """GiantSquid: Sweeping tentacle attack"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.sweep_damage = 50 * tower.stars
        self.sweep_angle = 120  # Degrees
        self.range = 3 * CELL_WIDTH
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                center_x = self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH
                center_y = self.tower.y * CELL_HEIGHT
                
                for enemy in game_state.enemies:
                    dx = enemy.x - center_x
                    dy = enemy.y - center_y
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist <= self.range:
                        angle = math.degrees(math.atan2(dy, dx))
                        if abs(angle) <= self.sweep_angle/2:
                            enemy.take_damage(self.sweep_damage)

class DeepseaKing(TowerPower):
    """ColossalSquid: Dominates nearby towers"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.buff_radius = 2 * CELL_WIDTH
        self.damage_boost = 0.2 * tower.stars  # 20/40/60% damage boost
        self.speed_boost = 0.2 * tower.stars  # 20/40/60% attack speed boost
        self.buff_duration = 5.0
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        # Only activate if not already active
        if energy_ready and not self.active:
            if self.activate():
                self.active = True
                self.active_duration = self.buff_duration
                
                # Apply buffs at activation time
                for other_tower in game_state.towers:
                    if other_tower != self.tower:
                        dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                        dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                        if (dx*dx + dy*dy) <= self.buff_radius*self.buff_radius:
                            if hasattr(other_tower, 'projectile_damage'):
                                other_tower.projectile_damage *= (1 + self.damage_boost)
                            if hasattr(other_tower, 'melee_damage'):
                                other_tower.melee_damage *= (1 + self.damage_boost)
                            if hasattr(other_tower, 'effect_damage'):
                                other_tower.effect_damage *= (1 + self.damage_boost)
                            if hasattr(other_tower, 'attack_cooldown'):
                                other_tower.attack_cooldown *= (1 - self.speed_boost)
        
        # When deactivating, remove buffs                
        if self.active and self.active_duration <= 0:
            for other_tower in game_state.towers:
                if other_tower != self.tower:
                    dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                    dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                    if (dx*dx + dy*dy) <= self.buff_radius*self.buff_radius:
                        if hasattr(other_tower, 'projectile_damage'):
                            other_tower.projectile_damage /= (1 + self.damage_boost)
                        if hasattr(other_tower, 'melee_damage'):
                            other_tower.melee_damage /= (1 + self.damage_boost)
                        if hasattr(other_tower, 'effect_damage'):
                            other_tower.effect_damage /= (1 + self.damage_boost)
                        if hasattr(other_tower, 'attack_cooldown'):
                            other_tower.attack_cooldown /= (1 - self.speed_boost)

class OxygenBurst(TowerPower):
    """DumboOctopus: Creates oxygen-rich zones that enhance towers"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.buff_duration = 5.0
        self.buff_radius = 2 * CELL_WIDTH
        self.heal_amount = 20 * tower.stars
        self.resource_bonus = 1 * tower.stars  # Reduced flat bonus amount
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready:
            if self.activate():
                for other_tower in game_state.towers:
                    dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                    dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                    if (dx*dx + dy*dy) <= self.buff_radius*self.buff_radius:
                        other_tower.health = min(other_tower.max_health,
                                              other_tower.health + self.heal_amount)
                        # Apply smaller flat bonus instead of percentage
                        if hasattr(other_tower, 'resource_amounts'):
                            for resource in other_tower.resource_amounts:
                                other_tower.resource_amounts[resource] += self.resource_bonus

class ResourceNexus(TowerPower):
    """Nautilus: Creates resource link network"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.link_radius = 3 * CELL_WIDTH
        self.resource_share = 0.15 * tower.stars  # Reduced to 15/30/45% sharing
        self.active_duration = 6.0  # Shorter duration
        self.resource_cap = 15  # Cap on shared resources per tower
        
    def update(self, dt, game_state):
        energy_ready = super().update(dt, game_state)
        
        if energy_ready and not self.active:
            if self.activate():
                self.active = True
                self.active_duration = self.active_duration
                
        if self.active:
            linked_towers = []
            
            # Find all resource towers in range
            for other_tower in game_state.towers:
                if hasattr(other_tower, 'resource_amounts') and other_tower != self.tower:
                    dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                    dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                    if (dx*dx + dy*dy) <= self.link_radius*self.link_radius:
                        linked_towers.append(other_tower)
            
            # Share resources between linked towers with cap
            if linked_towers and hasattr(self.tower, 'resource_amounts'):
                for resource in self.tower.resource_amounts:
                    if all(resource in t.resource_amounts for t in linked_towers):
                        total = sum(t.resource_amounts[resource] for t in linked_towers)
                        share = min(
                            self.resource_cap,
                            total * self.resource_share / len(linked_towers)
                        )
                        for tower in linked_towers:
                            tower.resource_amounts[resource] += share

class BacterialBloom(TowerPower):
    """Power for Beggiatoa: Creates a toxic area that damages enemies over time"""
    def __init__(self, tower):
        super().__init__(tower)
        self.effect_radius = CELL_WIDTH * 2.0
        self.damage_multiplier = 0.3  # Additional damage on top of base
        self.slow_effect = 0.4 * tower.stars  # Increased slow
        self.active = True
        
    def on_damage_dealt(self, enemy, damage):
        """Apply additional effects when base damage is dealt"""
        if self.energy.use_energy():
            # Apply additional damage
            enemy.take_damage(damage * self.damage_multiplier)
            
            # Apply slow effect
            enemy.speed_multiplier = max(0.2, enemy.speed_multiplier * (1.0 - self.slow_effect))
            
            # Visual feedback
            self.effect_alpha = 40
    
    def draw(self, surface):
        self.draw_area_effect(surface, persistent=True)
        super().draw(surface)
