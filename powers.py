import random
import math
import pygame
from config import *
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from config import GameState
from base_types import BaseTower

# Only import types for type checking to avoid circular imports
if TYPE_CHECKING:
    from tower import ResourceTower, Tower

class Power:
    def __init__(self, tower: BaseTower):
        self.tower = tower
        self.active = True
        
    def update(self, dt, game_state):
        pass
        
    def on_damage_dealt(self, enemy, damage):
        pass
        
    def on_damaged(self, attacker, damage):
        pass

class TowerPower:
    def __init__(self, tower: BaseTower):
        self.tower = tower
        self.cooldown = 0
        self.active = False
        self.active_duration = 0
        
    def update(self, dt, game_state):
        if self.cooldown > 0:
            self.cooldown -= dt
            
        if self.active and self.active_duration > 0:
            self.active_duration -= dt
            if self.active_duration <= 0:
                self.deactivate()
                
    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False

# Resource Tower Powers
class HydroPressure(TowerPower):
    """BlackSmoker: Creates pressure waves that boost nearby resource generation"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.base_cooldown = 15.0
        self.cooldown = self.base_cooldown
        self.radius = 2 * CELL_WIDTH
        self.boost_amount = 0.5 * tower.stars  # 50/100/150% boost
        self.active_duration = 5.0
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            self.activate()
            self.cooldown = self.base_cooldown
            
        if self.active:
            for other_tower in game_state.towers:
                if other_tower != self.tower and isinstance(other_tower, ResourceTower):
                    dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                    dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                    if (dx*dx + dy*dy) <= self.radius*self.radius:
                        for resource in other_tower.resource_amounts:
                            other_tower.resource_amounts[resource] *= (1 + self.boost_amount)

class MethaneEruption(TowerPower):
    """BubblePlume: Periodically releases methane explosions"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.base_cooldown = 12.0
        self.cooldown = self.base_cooldown
        self.damage = 20 * tower.stars
        self.radius = 1.5 * CELL_WIDTH
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            # Create explosion effect
            for enemy in game_state.enemies:
                dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                if (dx*dx + dy*dy) <= self.radius*self.radius:
                    enemy.take_damage(self.damage)
            self.cooldown = self.base_cooldown

class BrineSpray(TowerPower):
    """BrinePool: Sprays corrosive brine that slows enemies"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.base_cooldown = 8.0
        self.cooldown = self.base_cooldown
        self.slow_factor = 0.3 * tower.stars  # 30/60/90% slow
        self.duration = 3.0
        self.radius = 2 * CELL_WIDTH
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            for enemy in game_state.enemies:
                dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                if (dx*dx + dy*dy) <= self.radius*self.radius:
                    enemy.speed_multiplier = max(0.1, 1 - self.slow_factor)
            self.cooldown = self.base_cooldown

class LipidSiphon(TowerPower):
    """OsedaxWorm: Drains resources from enemies to boost production"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.base_cooldown = 1.0
        self.cooldown = self.base_cooldown
        self.drain_amount = 2 * tower.stars
        self.radius = 1.5 * CELL_WIDTH
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            for enemy in game_state.enemies:
                dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                if (dx*dx + dy*dy) <= self.radius*self.radius:
                    enemy.take_damage(self.drain_amount)
                    for resource in self.tower.resource_amounts:
                        self.tower.resource_amounts[resource] += 1
            self.cooldown = self.base_cooldown

# Projectile Tower Powers
class VenomShot(TowerPower):
    """RiftiaTubeWorm: Applies poison damage over time"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.poison_damage = 5 * tower.stars
        self.poison_duration = 3.0
        self.poison_chance = 0.3 * tower.stars  # 30/60/90% chance
        
    def on_hit(self, target):
        if random.random() < self.poison_chance:
            target.poisoned = True
            target.poison_damage = self.poison_damage
            target.poison_duration = self.poison_duration

class SonicPulse(TowerPower):
    """Rockfish: Releases sonic waves that stun enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.base_cooldown = 10.0
        self.cooldown = self.base_cooldown
        self.stun_duration = 1.0 * tower.stars
        self.radius = 2 * CELL_WIDTH
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            for enemy in game_state.enemies:
                dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                if (dx*dx + dy*dy) <= self.radius*self.radius:
                    enemy.is_stunned = True
                    enemy.stun_timer = self.stun_duration
            self.cooldown = self.base_cooldown

class ElectricShock(TowerPower):
    """Hagfish: Chain lightning between enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.chain_count = tower.stars + 1  # 2/3/4 targets
        self.chain_damage = 15 * tower.stars
        self.chain_range = 150
        
    def on_hit(self, target):
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
        self.base_cooldown = 15.0
        self.cooldown = self.base_cooldown
        self.cloud_duration = 4.0 * tower.stars
        self.cloud_radius = 2 * CELL_WIDTH
        self.damage = 10 * tower.stars
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            # Create ink cloud effect
            for enemy in game_state.enemies:
                dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                if (dx*dx + dy*dy) <= self.cloud_radius*self.cloud_radius:
                    enemy.speed_multiplier *= 0.5
                    enemy.take_damage(self.damage)
            self.cooldown = self.base_cooldown

# Tank Tower Powers
class Regeneration(TowerPower):
    """SquatLobster: Regenerates health over time"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.heal_rate = 5 * tower.stars  # Health per second
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.tower.health < self.tower.max_health:
            self.tower.health = min(self.tower.max_health,
                                  self.tower.health + self.heal_rate * dt)

class SpikePlating(TowerPower):
    """SpiderCrab: Reflects damage back to attackers"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.reflect_percent = 0.2 * tower.stars  # 20/40/60% reflection
        
    def on_damaged(self, attacker, damage):
        reflected = damage * self.reflect_percent
        if attacker:
            attacker.take_damage(reflected)

class BerserkMode(TowerPower):
    """Chimaera: Gains attack speed when damaged"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.speed_boost = 0.2 * tower.stars  # 20/40/60% boost
        
    def on_damaged(self, attacker, damage):
        if self.tower.health < self.tower.max_health * 0.5:
            self.tower.attack_cooldown *= (1 - self.speed_boost)

class FrenzyBite(TowerPower):
    """SleeperShark: Multiple rapid attacks"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.base_cooldown = 20.0
        self.cooldown = self.base_cooldown
        self.frenzy_duration = 3.0
        self.attack_multiplier = tower.stars  # 1/2/3x attack speed
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            self.active = True
            self.active_duration = self.frenzy_duration
            self.tower.attack_cooldown /= (1 + self.attack_multiplier)
            self.cooldown = self.base_cooldown
        
        if self.active and self.active_duration <= 0:
            self.tower.attack_cooldown *= (1 + self.attack_multiplier)

# Effect Tower Powers
class ChainReaction(TowerPower):
    """BlueCilliates: Damage spreads between enemies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.spread_range = CELL_WIDTH
        self.spread_damage = tower.effect_damage * 0.3 * tower.stars
        
    def on_damage_dealt(self, target, damage):
        hit_enemies = [target]
        for enemy in self.tower.game_state.enemies:
            if enemy not in hit_enemies:
                dx = enemy.x - target.x
                dy = enemy.y - target.y
                if (dx*dx + dy*dy) <= self.spread_range*self.spread_range:
                    enemy.take_damage(self.spread_damage)
                    hit_enemies.append(enemy)

class FilterFeeding(TowerPower):
    """VesicomyidaeClams: Converts damage dealt to resources"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.conversion_rate = 0.1 * tower.stars  # 10/20/30% conversion
        
    def on_damage_dealt(self, target, damage):
        resource_gain = int(damage * self.conversion_rate)
        if self.tower.biome:
            if self.tower.biome == Biome.HYDROTHERMAL:
                resource = 'sulfides'
            elif self.tower.biome == Biome.COLDSEEP:
                resource = 'methane'
            elif self.tower.biome == Biome.BRINE_POOL:
                resource = 'salt'
            elif self.tower.biome == Biome.WHALEFALL:
                resource = 'lipids'
            
            if resource in self.tower.game_state.resources:
                self.tower.game_state.resources[resource] += resource_gain

class MusclePulse(TowerPower):
    """MuscleBed: Pulses that push enemies back"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.base_cooldown = 8.0
        self.cooldown = self.base_cooldown
        self.push_force = 50 * tower.stars
        self.radius = 2 * CELL_WIDTH
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            for enemy in game_state.enemies:
                dx = (enemy.x - (self.tower.x * CELL_WIDTH + SIDEBAR_WIDTH))
                dy = (enemy.y - (self.tower.y * CELL_HEIGHT))
                dist = (dx*dx + dy*dy) ** 0.5
                if dist <= self.radius:
                    # Push enemy away
                    if dist > 0:
                        enemy.x += (dx/dist) * self.push_force * dt
                        enemy.y += (dy/dist) * self.push_force * dt
            self.cooldown = self.base_cooldown

class BacterialBloom(TowerPower):
    """Beggiatoa: Creates damaging bacterial colonies"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.colony_damage = tower.effect_damage * 0.5 * tower.stars
        self.colony_duration = 3.0
        self.colonies = []  # List of active colony positions
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        # Update existing colonies
        self.colonies = [(x, y, t-dt) for x, y, t in self.colonies if t > 0]
        
        # Add new colonies where enemies die
        for enemy in game_state.enemies:
            if enemy.health <= 0:
                self.colonies.append((enemy.x, enemy.y, self.colony_duration))
        
        # Deal damage to enemies in colonies
        for enemy in game_state.enemies:
            for col_x, col_y, _ in self.colonies:
                dx = enemy.x - col_x
                dy = enemy.y - col_y
                if (dx*dx + dy*dy) <= (CELL_WIDTH * 0.5)**2:
                    enemy.take_damage(self.colony_damage * dt)

# Rare Tower Powers
class TentacleSweep(TowerPower):
    """GiantSquid: Sweeping tentacle attack"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.base_cooldown = 15.0
        self.cooldown = self.base_cooldown
        self.sweep_damage = 50 * tower.stars
        self.sweep_angle = 120  # Degrees
        self.range = 3 * CELL_WIDTH
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
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
            
            self.cooldown = self.base_cooldown

class DeepseaKing(TowerPower):
    """ColossalSquid: Dominates nearby towers"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.buff_radius = 2 * CELL_WIDTH
        self.damage_boost = 0.2 * tower.stars  # 20/40/60% damage boost
        self.speed_boost = 0.2 * tower.stars  # 20/40/60% attack speed boost
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
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

class OxygenBurst(TowerPower):
    """DumboOctopus: Creates oxygen-rich zones that enhance towers"""
    def __init__(self, tower: 'Tower'):
        super().__init__(tower)
        self.base_cooldown = 12.0
        self.cooldown = self.base_cooldown
        self.buff_duration = 5.0
        self.buff_radius = 2 * CELL_WIDTH
        self.heal_amount = 20 * tower.stars
        self.resource_bonus = 2 * tower.stars
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        if self.cooldown <= 0:
            for other_tower in game_state.towers:
                dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                if (dx*dx + dy*dy) <= self.buff_radius*self.buff_radius:
                    other_tower.health = min(other_tower.max_health,
                                          other_tower.health + self.heal_amount)
                    if isinstance(other_tower, ResourceTower):
                        for resource in other_tower.resource_amounts:
                            other_tower.resource_amounts[resource] += self.resource_bonus
            self.cooldown = self.base_cooldown

class ResourceNexus(TowerPower):
    """Nautilus: Creates resource link network"""
    def __init__(self, tower: "ResourceTower"):
        super().__init__(tower)
        self.link_radius = 3 * CELL_WIDTH
        self.resource_share = 0.2 * tower.stars  # 20/40/60% resource sharing
        
    def update(self, dt, game_state):
        super().update(dt, game_state)
        linked_towers = []
        
        # Find all resource towers in range
        for other_tower in game_state.towers:
            if isinstance(other_tower, ResourceTower) and other_tower != self.tower:
                dx = (other_tower.x - self.tower.x) * CELL_WIDTH
                dy = (other_tower.y - self.tower.y) * CELL_HEIGHT
                if (dx*dx + dy*dy) <= self.link_radius*self.link_radius:
                    linked_towers.append(other_tower)
        
        # Share resources between linked towers
        if linked_towers:
            for resource in self.tower.resource_amounts:
                total = sum(t.resource_amounts[resource] for t in linked_towers)
                share = total * self.resource_share / len(linked_towers)
                for tower in linked_towers:
                    tower.resource_amounts[resource] += share