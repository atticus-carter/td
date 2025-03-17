from enum import Enum, auto
from typing import Dict, Any, Optional
from dataclasses import dataclass
from config import Biome, TOWER_DEFINITIONS, RARE_TOWERS

class TowerType(Enum):
    RESOURCE = "resource"
    PROJECTILE = "projectile"
    TANK = "tank"
    EFFECT = "effect"
    RARE = "rare"

@dataclass
class TowerStats:
    name: str
    tower_type: TowerType
    base_health: int = 100
    damage: float = 0
    range: float = 0
    cooldown: float = 0
    resource_type: Optional[str] = None
    gen_amount: float = 0
    radius: float = 0
    melee_damage: float = 0

class TowerFactory:
    @staticmethod
    def get_tower_stats(tower_name: str, biome: Optional[Biome] = None) -> TowerStats:
        # First check rare towers
        if tower_name in RARE_TOWERS:
            specs = RARE_TOWERS[tower_name]
            if 'resource' in specs:
                return TowerStats(
                    name=tower_name,
                    tower_type=TowerType.RESOURCE,
                    resource_type=specs['resource'],
                    gen_amount=specs['gen_amount']
                )
            elif 'health' in specs:
                return TowerStats(
                    name=tower_name,
                    tower_type=TowerType.TANK,
                    base_health=specs['health'],
                    melee_damage=specs['melee_damage'],
                    cooldown=specs.get('cooldown', 1.0)
                )
            elif 'radius' in specs:
                return TowerStats(
                    name=tower_name,
                    tower_type=TowerType.EFFECT,
                    damage=specs['damage'],
                    radius=specs['radius']
                )
            else:
                return TowerStats(
                    name=tower_name,
                    tower_type=TowerType.PROJECTILE,
                    damage=specs['damage'],
                    range=specs['range'],
                    cooldown=specs['cooldown']
                )

        # Check biome-specific towers
        if biome and biome in TOWER_DEFINITIONS:
            for tower_type, specs in TOWER_DEFINITIONS[biome].items():
                if specs['name'] == tower_name:
                    if tower_type == TowerType.RESOURCE:
                        return TowerStats(
                            name=tower_name,
                            tower_type=TowerType.RESOURCE,
                            resource_type=specs['resource'],
                            gen_amount=specs['gen_amount']
                        )
                    elif tower_type == TowerType.PROJECTILE:
                        return TowerStats(
                            name=tower_name,
                            tower_type=TowerType.PROJECTILE,
                            damage=specs['damage'],
                            range=specs['range'],
                            cooldown=specs['cooldown']
                        )
                    elif tower_type == TowerType.TANK:
                        return TowerStats(
                            name=tower_name,
                            tower_type=TowerType.TANK,
                            base_health=specs['health'],
                            melee_damage=specs['melee_damage']
                        )
                    elif tower_type == TowerType.EFFECT:
                        return TowerStats(
                            name=tower_name,
                            tower_type=TowerType.EFFECT,
                            damage=specs['damage'],
                            radius=specs['radius']
                        )

        # Default stats if tower not found
        return TowerStats(name=tower_name, tower_type=TowerType.PROJECTILE)

    @staticmethod
    def get_biome_towers(biome: Biome) -> Dict[TowerType, str]:
        """Get all available towers for a specific biome"""
        if biome in TOWER_DEFINITIONS:
            return {tower_type: specs['name'] 
                   for tower_type, specs in TOWER_DEFINITIONS[biome].items()}
        return {}