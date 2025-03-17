import pygame
import random
from config import *
from ui import HealthBar

class Enemy:
    def __init__(self, y, enemy_type):
        # Position starts at right edge of grid
        self.x = WINDOW_WIDTH - SIDEBAR_WIDTH
        self.y = y * CELL_HEIGHT + CELL_HEIGHT // 2
        self.enemy_type = enemy_type
        
        # Get enemy properties from definitions
        enemy_def = ENEMY_DEFINITIONS[enemy_type]
        self.health = enemy_def['health']
        self.max_health = enemy_def['health']
        self.base_speed = enemy_def['speed']
        self.speed = self.base_speed
        self.damage = enemy_def['damage']
        self.color = ENEMY_COLORS[enemy_type]
        self.abilities = enemy_def['abilities']
        
        # Size based on enemy type (updated for new types)
        if enemy_type in ['ScoutDrone', 'ROV', 'HarvesterDrone']:
            self.width = 24
            self.height = 24
        elif enemy_type in ['ExosuitDiver', 'MiningLaser', 'SonicDisruptor']:
            self.width = 32
            self.height = 32
        elif enemy_type in ['DrillingMech', 'SeabedCrawler', 'PressureCrusher']:
            self.width = 40
            self.height = 40
        elif enemy_type == 'CorporateSubmarine':
            self.width = 60
            self.height = 60
        else:
            self.width = 36
            self.height = 36
        
        # Special property for boss
        self.is_boss = (enemy_type == 'CorporateSubmarine')
        
        # Animation and ability timing
        self.damage_flash = 0
        self.attack_cooldown = 0
        self.ability_cooldowns = {ability: 0 for ability in self.abilities}
        
        # Status effects
        self.shield_amount = 0
        self.speed_multiplier = 1.0
        self.damage_reduction = 0
        self.is_stunned = False
        self.stun_timer = 0
        
        # Ability-specific properties
        self.clones = []
        self.deployed_drones = []
        self.energy_barrier_active = False
        self.energy_barrier_health = 0
        
        # Movement properties
        self.velocity_x = -self.speed
        self.velocity_y = 0
        
        # Create collision rect
        self.collision_rect = pygame.Rect(
            self.x - self.width/2,
            self.y - self.height/2,
            self.width,
            self.height
        )
        
    def update(self, dt, towers, gameplay_manager=None):
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
            return
            
        # Store old position for collision resolution
        old_x = self.x
        old_y = self.y
        
        # Update actual speed based on multipliers
        self.speed = self.base_speed * self.speed_multiplier
        
        # Apply movement if not stunned
        if not self.is_stunned:
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
        
        # Update collision rect
        self.collision_rect.x = self.x - self.width/2
        self.collision_rect.y = self.y - self.height/2
        
        # Update ability cooldowns
        for ability in self.ability_cooldowns:
            if self.ability_cooldowns[ability] > 0:
                self.ability_cooldowns[ability] -= dt
                
        # Check collisions with towers
        collided = False
        for tower in towers:
            if tower.check_collision(self.collision_rect):
                if tower.has_collision:
                    # Revert to old position if tower has collision
                    self.x = old_x
                    self.y = old_y
                    self.collision_rect.x = self.x - self.width/2
                    self.collision_rect.y = self.y - self.height/2
                    collided = True
                    
                    # Attack tower if attack is available
                    if self.attack_cooldown <= 0:
                        damage = self.damage
                        if 'break_terrain' in self.abilities:
                            ability_data = ENEMY_ABILITIES['break_terrain']
                            if self.ability_cooldowns['break_terrain'] <= 0:
                                damage *= ability_data['damage_multiplier']
                                self.ability_cooldowns['break_terrain'] = ability_data['cooldown']
                        
                        tower.take_damage(damage)
                        self.attack_cooldown = 1.0
                        
                        # Apply special effects on hit
                        if 'emp_pulse' in self.abilities and self.ability_cooldowns['emp_pulse'] <= 0:
                            self.use_emp_pulse(towers)
                        if 'pressure_wave' in self.abilities and self.ability_cooldowns['pressure_wave'] <= 0:
                            self.use_pressure_wave(towers)
                    
        # Handle pathing and movement
        if collided:
            # Try to find an open path
            can_move_up = True
            can_move_down = True
            
            test_distance = 50
            
            # Test upward movement
            self.collision_rect.y -= test_distance
            for tower in towers:
                if tower.has_collision and tower.check_collision(self.collision_rect):
                    can_move_up = False
                    break
            self.collision_rect.y += test_distance
            
            # Test downward movement
            self.collision_rect.y += test_distance
            for tower in towers:
                if tower.has_collision and tower.check_collision(self.collision_rect):
                    can_move_down = False
                    break
            self.collision_rect.y -= test_distance
            
            # Choose direction based on available paths
            if can_move_up and not can_move_down:
                self.velocity_y = -self.speed
            elif can_move_down and not can_move_up:
                self.velocity_y = self.speed
            elif can_move_up and can_move_down:
                if self.velocity_y == 0:
                    self.velocity_y = self.speed if random.random() > 0.5 else -self.speed
            else:
                self.velocity_y = 0
        else:
            # Gradually return to horizontal movement
            self.velocity_y *= 0.9
            if abs(self.velocity_y) < 1:
                self.velocity_y = 0
        
        # Use abilities
        self.update_abilities(dt, towers, gameplay_manager)
        
        # Update status effect timers
        if self.damage_flash > 0:
            self.damage_flash -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
    def update_abilities(self, dt, towers, gameplay_manager):
        if not gameplay_manager:
            return
            
        for ability in self.abilities:
            if self.ability_cooldowns[ability] <= 0:
                if ability == 'fast_movement':
                    self.use_fast_movement()
                elif ability == 'shield_generator':
                    self.use_shield_generator()
                elif ability == 'repair_nearby':
                    self.use_repair_nearby()
                elif ability == 'resource_steal':
                    self.use_resource_steal(gameplay_manager)
                elif ability == 'divide':
                    self.use_divide(gameplay_manager)
                elif ability == 'deploy_drones':
                    self.use_deploy_drones(gameplay_manager)
                    
        # Update active effects
        if 'self_repair' in self.abilities:
            self.use_self_repair(dt)
            
    def use_fast_movement(self):
        ability_data = ENEMY_ABILITIES['fast_movement']
        self.speed_multiplier = ability_data['speed_boost']
        self.ability_cooldowns['fast_movement'] = ability_data['duration']
        
    def use_shield_generator(self):
        ability_data = ENEMY_ABILITIES['shield_generator']
        self.shield_amount = ability_data['shield_amount']
        self.ability_cooldowns['shield_generator'] = ability_data['duration']
        
    def use_repair_nearby(self):
        ability_data = ENEMY_ABILITIES['repair_nearby']
        for enemy in self.nearby_enemies:
            if enemy != self and enemy.health < enemy.max_health:
                enemy.health = min(enemy.max_health, enemy.health + ability_data['heal_amount'])
        self.ability_cooldowns['repair_nearby'] = ability_data['interval']
        
    def use_resource_steal(self, gameplay_manager):
        ability_data = ENEMY_ABILITIES['resource_steal']
        # Steal from random resource type
        resources = list(gameplay_manager.resources.keys())
        if resources:
            resource = random.choice(resources)
            amount = min(ability_data['amount'], gameplay_manager.resources[resource])
            gameplay_manager.resources[resource] -= amount
        self.ability_cooldowns['resource_steal'] = 5.0
        
    def use_emp_pulse(self, towers):
        ability_data = ENEMY_ABILITIES['emp_pulse']
        for tower in towers:
            dx = tower.x * CELL_WIDTH + CELL_WIDTH/2 - self.x
            dy = tower.y * CELL_HEIGHT + CELL_HEIGHT/2 - self.y
            if (dx*dx + dy*dy) <= ability_data['radius']**2:
                tower.stun(ability_data['stun_duration'])
        self.ability_cooldowns['emp_pulse'] = ability_data['cooldown']
        
    def use_pressure_wave(self, towers):
        ability_data = ENEMY_ABILITIES['pressure_wave']
        for tower in towers:
            dx = tower.x * CELL_WIDTH + CELL_WIDTH/2 - self.x
            dy = tower.y * CELL_HEIGHT + CELL_HEIGHT/2 - self.y
            if (dx*dx + dy*dy) <= ability_data['radius']**2:
                tower.take_damage(ability_data['damage'])
        self.ability_cooldowns['pressure_wave'] = ability_data['cooldown']
        
    def use_self_repair(self, dt):
        if self.health < self.max_health:
            ability_data = ENEMY_ABILITIES['self_repair']
            self.health = min(self.max_health, 
                            self.health + ability_data['heal_rate'] * dt)
            
    def use_divide(self, gameplay_manager):
        ability_data = ENEMY_ABILITIES['divide']
        if len(self.clones) < ability_data['max_clones']:
            clone = Enemy(int(self.y / CELL_HEIGHT), self.enemy_type)
            clone.health = self.max_health * ability_data['clone_health_percent']
            clone.max_health = clone.health
            gameplay_manager.enemies.append(clone)
            self.clones.append(clone)
        self.ability_cooldowns['divide'] = ability_data['cooldown']
        
    def use_deploy_drones(self, gameplay_manager):
        ability_data = ENEMY_ABILITIES['deploy_drones']
        for _ in range(ability_data['drone_count']):
            drone = Enemy(int(self.y / CELL_HEIGHT), 'ScoutDrone')
            drone.health = ability_data['drone_health']
            drone.max_health = drone.health
            gameplay_manager.enemies.append(drone)
            self.deployed_drones.append(drone)
        self.ability_cooldowns['deploy_drones'] = ability_data['cooldown']
        
    def take_damage(self, amount):
        # Apply damage reduction from abilities
        for ability in self.abilities:
            if ability in ['armor_plating', 'heavy_plating', 'armored_shell', 'water_shield']:
                ability_data = ENEMY_ABILITIES[ability]
                amount *= (1 - ability_data.get('damage_reduction', 0))
                
        # Check energy shield
        if 'energy_shield' in self.abilities and self.shield_amount > 0:
            absorbed = min(self.shield_amount, amount)
            self.shield_amount -= absorbed
            amount -= absorbed
            
        if amount > 0:
            self.health -= amount
            self.damage_flash = 0.1
            
        return self.is_dead()
        
    def draw(self, surface):
        # Draw enemy with appropriate size and color
        color = self.color
        
        # Flash white when taking damage
        if self.damage_flash > 0:
            color = (255, 255, 255)
            
        # Draw base shape
        pygame.draw.rect(surface, color,
                        (self.x - self.width/2, 
                         self.y - self.height/2, 
                         self.width, self.height))
                         
        # Draw shield if active
        if self.shield_amount > 0:
            shield_surface = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(shield_surface, (100, 200, 255, 128),
                           (0, 0, self.width + 8, self.height + 8))
            surface.blit(shield_surface, 
                        (self.x - (self.width + 8)/2, 
                         self.y - (self.height + 8)/2))
                         
        # Draw health bar using shared HealthBar component
        HealthBar.draw(surface, 
                      self.x - self.width/2, 
                      self.y - self.height/2 - 8,
                      self.width, self.health, self.max_health)
        
        # Draw ability indicators
        self.draw_ability_indicators(surface)
        
    def draw_ability_indicators(self, surface):
        # Draw small indicators for active abilities
        indicator_size = 4
        spacing = 6
        x_start = self.x - (len(self.abilities) * spacing) / 2
        
        for i, ability in enumerate(self.abilities):
            if self.ability_cooldowns[ability] <= 0:
                color = (0, 255, 0)  # Ready
            else:
                color = (255, 0, 0)  # On cooldown
                
            pygame.draw.circle(surface, color,
                             (int(x_start + i * spacing),
                              int(self.y + self.height/2 + 8)),
                             indicator_size)
    
    def is_dead(self):
        return self.health <= 0
        
    def get_reward(self):
        """Return resource reward for killing this enemy"""
        base_rewards = {
            'ScoutDrone': 10,
            'ExosuitDiver': 20,
            'DrillingMech': 40,
            'ROV': 15,
            'HarvesterDrone': 25,
            'MiningLaser': 30,
            'SonicDisruptor': 35,
            'CollectorCrab': 45,
            'SeabedCrawler': 60,
            'PressureCrusher': 50,
            'VortexGenerator': 40,
            'BionicSquid': 70,
            'NaniteSwarm': 55,
            'CorporateSubmarine': 150
        }
        return base_rewards.get(self.enemy_type, 20)
