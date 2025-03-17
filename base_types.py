from enum import Enum, auto
import pygame
from config import *

class TowerType(Enum):
    RESOURCE = auto()
    PROJECTILE = auto()
    TANK = auto()
    EFFECT = auto()

# Base class that will be used by both tower.py and powers.py
class BaseTower:
    """Base class for tower functionality needed by powers"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.name = ""
        self.stars = 1
        self.health = 100
        self.max_health = 100
        self.power = None
        self.color = (100, 100, 100)
        self.game_state = None
        self.biome = None
        self.attack_timer = 0
        self.level = 1
        self.projectile_damage = 0
        self.melee_damage = 0
        self.effect_damage = 0
        self.cooldown = 1.0
        self.attack_cooldown = 1.0
        self.resource_amounts = {}
        
    def take_damage(self, amount, attacker=None):
        """Base damage handling that powers need to access"""
        self.health -= amount
        if self.power and hasattr(self.power, 'on_damaged'):
            self.power.on_damaged(attacker, amount)
        return self.health <= 0