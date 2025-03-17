import pygame
from typing import Dict, List, Tuple
from config import TOWER_DEFINITIONS, Biome, RARE_TOWERS, TowerType

# Create a global instance of AutoCollector
_collector = None

def get_collector():
    """Get or create the global AutoCollector instance"""
    global _collector
    if (_collector is None):
        _collector = AutoCollector()
    return _collector

def check_auto_collect(orb, tower) -> bool:
    """Check if a tower can auto-collect a specific orb"""
    return get_collector().check_auto_collect(orb, tower)

class AutoCollector:
    def __init__(self):
        # Build the collection relationships from tower definitions
        self.collection_relationships = {}
        
        # Add biome-specific collectors
        for biome in Biome:
            if biome in TOWER_DEFINITIONS:
                resource_tower = TOWER_DEFINITIONS[biome][TowerType.RESOURCE]
                projectile_tower = TOWER_DEFINITIONS[biome][TowerType.PROJECTILE]
                self.collection_relationships[resource_tower['name']] = resource_tower['resource']
                self.collection_relationships[projectile_tower['name']] = resource_tower['resource']
        
        # Add rare tower collectors
        for name, specs in RARE_TOWERS.items():
            if 'resource' in specs:
                self.collection_relationships[name] = specs['resource']

    def check_auto_collect(self, orb, tower) -> bool:
        """Check if a tower can auto-collect a specific resource orb"""
        if not tower.name in self.collection_relationships:
            return False
            
        collect_type = self.collection_relationships[tower.name]
        if collect_type == 'all' or collect_type == orb.resource_type:
            # Calculate tower collection area (slightly larger than tower bounds)
            tower_rect = pygame.Rect(
                tower.x * tower.CELL_WIDTH + tower.SIDEBAR_WIDTH - 5,
                tower.y * tower.CELL_HEIGHT - 5,
                tower.CELL_WIDTH + 10,
                tower.CELL_HEIGHT + 10
            )
            
            # Check if orb is within collection area
            orb_pos = pygame.Vector2(orb.x, orb.y)
            return tower_rect.collidepoint(orb_pos)
        return False

    def process_orbs(self, orbs: List, towers: List) -> List[Tuple[str, float]]:
        """Process all orbs against all towers for collection
        Returns list of (resource_type, amount) tuples for collected resources"""
        collected_orbs = []
        
        # Process each orb
        for orb in orbs[:]:  # Use slice to allow modification during iteration
            if not orb.active:
                continue
                
            # Check each tower for collection
            for tower in towers:
                if self.check_auto_collect(orb, tower):
                    collected_amount = orb.collect(auto_collected=True)
                    if collected_amount > 0:
                        collected_orbs.append((orb.resource_type, collected_amount))
                        break  # Stop checking other towers once collected
                        
        return collected_orbs

    def get_collector_types(self) -> Dict[str, str]:
        """Get a dictionary of all tower types that can collect resources"""
        return self.collection_relationships.copy()