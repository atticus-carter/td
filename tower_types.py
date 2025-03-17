from enum import Enum

class TowerType(Enum):
    RESOURCE = "resource"
    PROJECTILE = "projectile" 
    TANK = "tank"
    EFFECT = "effect"

# Base Tower class definition that other tower types inherit from
class BaseTower:
    """Base class for all tower types with common functionality"""
    def __init__(self, x, y, tower_type, biome=None):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.biome = biome
        self.stars = 1
        self.power = None
        self.health = 100
        self.max_health = 100
        self.level = 1

class ResourceTowerType(BaseTower):
    """Resource generator tower type"""
    pass

class ProjectileTowerType(BaseTower):
    """Projectile shooting tower type"""
    pass

class TankTowerType(BaseTower):
    """Tank/defensive tower type"""
    pass

class EffectTowerType(BaseTower):
    """Area effect tower type"""
    pass