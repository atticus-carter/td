import pygame
from config import *
from enum import Enum
from typing import Dict, Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tower import Tower

class EnergySystem:
    """Energy management system for tower powers"""
    
    def __init__(self, tower: 'Tower', base_gen_rate: float = 10.0):
        self.tower = tower
        self.current_energy = 0.0
        self.max_energy = 100.0
        self.energy_cost = 100.0  # Default energy cost
        
        # Base generation rate per second
        self.base_generation_rate = base_gen_rate
        
        # Apply tower star level to generation rate
        self.generation_rate = base_gen_rate * (1.3 ** (tower.stars - 1))
        
        # Visual properties for the energy bar
        self.bar_width = 40
        self.bar_height = 4
        self.bar_color = (64, 192, 255)  # Blue energy color
        self.bar_bg_color = (32, 32, 32, 128)  # Semi-transparent dark background
        
        # Apply biome and star multipliers
        self.apply_multipliers()
        
    def apply_multipliers(self):
        """Apply generation rate multipliers based on tower stars and biome"""
        # Star multiplier: each star adds 20% to base generation rate
        star_multiplier = 1.0 + (self.tower.stars - 1) * 0.2
        
        # Biome multiplier: certain tower types get bonuses in their native biomes
        biome_multiplier = 1.0
        if self.tower.biome:
            # Resource towers in native biome
            if hasattr(self.tower, 'resource_type') and self.tower.biome.name.lower() in self.tower.resource_type.lower():
                biome_multiplier = 1.5
            
            # Projectile towers in Hydrothermal
            elif self.tower.__class__.__name__ == 'ProjectileTower' and self.tower.biome == Biome.HYDROTHERMAL:
                biome_multiplier = 1.3
                
            # Tank towers in Brine Pool
            elif self.tower.__class__.__name__ == 'TankTower' and self.tower.biome == Biome.BRINE_POOL:
                biome_multiplier = 1.3
                
            # Effect towers in Cold Seep
            elif self.tower.__class__.__name__ == 'EffectTower' and self.tower.biome == Biome.COLDSEEP:
                biome_multiplier = 1.3
                
        # Apply the combined multipliers
        self.generation_rate = self.base_generation_rate * star_multiplier * biome_multiplier
    
    def update(self, dt: float) -> bool:
        """Update energy generation and return True if enough energy for power use"""
        if not self.tower.stunned:  # Don't generate energy when tower is stunned
            self.current_energy += self.generation_rate * dt
            self.current_energy = min(self.current_energy, self.max_energy)
            
        return self.current_energy >= self.energy_cost
    
    def use_energy(self) -> bool:
        """Try to use energy for a power. Returns True if successful"""
        if self.current_energy >= self.energy_cost:
            self.current_energy -= self.energy_cost
            return True
        return False
    
    def draw(self, surface, x: int, y: int) -> None:
        """Draw the energy bar above the tower"""
        # Create a small transparent surface for the energy bar background
        bar_y = y - 12  # Position above health bar
        bg_rect = pygame.Rect(x + 5, bar_y, self.bar_width, self.bar_height)
        
        # Draw background with alpha
        s = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
        pygame.draw.rect(s, self.bar_bg_color, (0, 0, self.bar_width, self.bar_height))
        surface.blit(s, bg_rect)
        
        # Draw energy level
        energy_width = int((self.current_energy / self.max_energy) * self.bar_width)
        energy_rect = pygame.Rect(x + 5, bar_y, energy_width, self.bar_height)
        pygame.draw.rect(surface, self.bar_color, energy_rect)

# Dictionary to store energy costs for different tower types
ENERGY_COSTS = {
    # Resource Tower Powers
    'HydroPressure': 100,
    'MethaneEruption': 80,
    'BrineSpray': 70,
    'LipidSiphon': 60,
    
    # Projectile Tower Powers
    'VenomShot': 40,
    'SonicPulse': 90,
    'ElectricShock': 60,
    'InkCloud': 100,
    
    # Tank Tower Powers
    'Regeneration': 50,
    'SpikePlating': 50,
    'BerserkMode': 80,
    'FrenzyBite': 100,
    
    # Effect Tower Powers
    'ChainReaction': 70,
    'FilterFeeding': 60,
    'MusclePulse': 90,
    
    # Rare Tower Powers
    'TentacleSweep': 120,
    'DeepseaKing': 150,
    'OxygenBurst': 120,
    'ResourceNexus': 140
}

# Dictionary for base energy generation rates by tower type
ENERGY_GEN_RATES = {
    'ResourceTower': 10,
    'ProjectileTower': 12,
    'TankTower': 8,
    'EffectTower': 15,
    'Beggiatoa': 15  # Now just a regular effect tower
}

# Dictionary for biome modifiers to specific powers
BIOME_POWER_MODIFIERS = {
    'HYDROTHERMAL': {
        'HydroPressure': 1.5,
        'MethaneEruption': 0.8,
        'BrineSpray': 0.8,
        'TentacleSweep': 1.2,
        'SonicPulse': 1.2,
    },
    'COLDSEEP': {
        'MethaneEruption': 1.5,
        'HydroPressure': 0.8, 
        'ElectricShock': 1.2,
        'BerserkMode': 1.2,
    },
    'BRINE_POOL': {
        'BrineSpray': 1.5,
        'LipidSiphon': 0.8,
        'MusclePulse': 1.2,
        'InkCloud': 1.2,
    },
    'WHALEFALL': {
        'LipidSiphon': 1.5,
        'BrineSpray': 0.8,
        'FilterFeeding': 1.2,
        'Regeneration': 1.2,
    }
}