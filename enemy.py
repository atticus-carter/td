import pygame
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
        self.speed = enemy_def['speed']
        self.damage = enemy_def['damage']
        self.color = ENEMY_COLORS[enemy_type]
        
        # Size based on enemy type
        if enemy_type == 'ScoutDrone':
            self.width = 24
            self.height = 24
        elif enemy_type == 'ExosuitDiver':
            self.width = 32
            self.height = 32
        elif enemy_type == 'DrillingMech':
            self.width = 40
            self.height = 40
        elif enemy_type == 'CorporateSubmarine':
            self.width = 60
            self.height = 60
        
        # Special property for boss
        self.is_boss = (enemy_type == 'CorporateSubmarine')
        
        # Animation timing
        self.damage_flash = 0
        self.attack_cooldown = 0
        
    def update(self, dt, towers):
        self.x -= self.speed * dt
        
        # Decrease damage flash timer if active
        if self.damage_flash > 0:
            self.damage_flash -= dt
            
        # Decrease attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Check for collisions with towers
        for tower in towers:
            # Calculate tower's grid position in pixels
            tower_x = tower.x * CELL_WIDTH + SIDEBAR_WIDTH
            tower_y = tower.y * CELL_HEIGHT
            
            # Simple collision check
            if (self.x - self.width/2 < tower_x + CELL_WIDTH and 
                self.x + self.width/2 > tower_x and
                self.y - self.height/2 < tower_y + CELL_HEIGHT and
                self.y + self.height/2 > tower_y):
                
                # Attack tower if attack is available
                if self.attack_cooldown <= 0:
                    tower.take_damage(self.damage)
                    self.attack_cooldown = 1.0  # 1 second between attacks
                    
                    # Stop moving during attack
                    return
        
    def draw(self, surface):
        # Draw enemy with appropriate size and color
        color = self.color
        
        # Flash white when taking damage
        if self.damage_flash > 0:
            color = (255, 255, 255)
            
        pygame.draw.rect(surface, color,
                        (self.x - self.width/2, 
                         self.y - self.height/2, 
                         self.width, self.height))
                         
        # Draw health bar using shared HealthBar component
        HealthBar.draw(surface, self.x - self.width/2, self.y - self.height/2 - 8, self.width, self.health, self.max_health)
        
    def is_dead(self):
        return self.health <= 0
        
    def take_damage(self, amount):
        self.health -= amount
        self.damage_flash = 0.1  # Flash for 0.1 seconds when hit
        return self.is_dead()
        
    def get_reward(self):
        """Return resource reward for killing this enemy"""
        if self.enemy_type == 'ScoutDrone':
            return 10
        elif self.enemy_type == 'ExosuitDiver':
            return 20
        elif self.enemy_type == 'DrillingMech':
            return 40
        elif self.enemy_type == 'CorporateSubmarine':
            return 100
        return 0
