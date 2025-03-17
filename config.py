import pygame
from enum import Enum, auto
import os

# Font setup
def get_font(size):
    """Get the C&C Red Alert font in specified size"""
    try:
        font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "C&C Red Alert [INET].ttf")
        return pygame.font.Font(font_path, size)
    except:
        print("Warning: Could not load C&C Red Alert font, falling back to system font")
        return pygame.font.SysFont('Arial', size)

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
SIDEBAR_WIDTH = 200
GRID_COLS = 9
GRID_ROWS = 5
CELL_WIDTH = (WINDOW_WIDTH - SIDEBAR_WIDTH) // GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT // GRID_ROWS

# Resource colors - add consistent color scheme
RESOURCE_COLORS = {
    'sulfides': (255, 200, 0),  # Golden yellow
    'methane': (0, 200, 255),   # Bright blue
    'salt': (255, 255, 255),    # White
    'lipids': (255, 100, 200)   # Pink
}

# Colors
COLOR_BG = (10, 20, 40)
COLOR_BACKGROUND = (10, 20, 40)  # Added this line to fix the reference in level_select.py
COLOR_UI_BG = (20, 30, 50)
COLOR_TEXT = (200, 200, 200)
COLOR_BUTTON = (40, 60, 100)
COLOR_BUTTON_HOVER = (60, 80, 120)

# Biome specific background colors
BIOME_COLORS = {
    'HYDROTHERMAL': (40, 10, 10),
    'COLDSEEP': (10, 10, 40),
    'BRINE_POOL': (10, 30, 30),
    'WHALEFALL': (30, 20, 40)
}

# Tower colors - update resource generator colors to match resources
TOWER_COLORS = {
    # Hydrothermal
    'BlackSmoker': RESOURCE_COLORS['sulfides'],
    'RiftiaTubeWorm': (255, 80, 80),
    'SquatLobster': (180, 80, 30),
    'BlueCilliates': (80, 80, 255),
    
    # Coldseep
    'BubblePlume': RESOURCE_COLORS['methane'],
    'Rockfish': (120, 120, 180),
    'SpiderCrab': (180, 150, 100),
    'VesicomyidaeClams': (220, 220, 180),
    
    # Brine Pool
    'BrinePool': RESOURCE_COLORS['salt'],
    'Hagfish': (180, 180, 180),
    'Chimaera': (220, 180, 100),
    'MuscleBed': (180, 100, 100),
    
    # Whalefall
    'OsedaxWorm': RESOURCE_COLORS['lipids'],
    'Muusoctopus': (150, 50, 150),
    'SleeperShark': (50, 50, 100),
    'Beggiatoa': (255, 255, 200),
    
    # Rare towers
    'GiantSquid': (100, 0, 100),
    'ColossalSquid': (150, 0, 150),
    'DumboOctopus': (200, 100, 200),
    'Nautilus': (255, 200, 100)
}

# Enemy colors - updated for new enemy types
ENEMY_COLORS = {
    'ScoutDrone': (100, 180, 255),      # Light blue for recon units
    'ExosuitDiver': (255, 140, 0),      # Orange for human units
    'DrillingMech': (180, 180, 180),    # Gray for mechanical units
    'CorporateSubmarine': (255, 0, 100), # Pink for boss units
    'ROV': (0, 255, 255),               # Cyan for ROVs
    'HarvesterDrone': (255, 200, 0),    # Gold for resource collectors
    'MiningLaser': (255, 50, 50),       # Red for laser units
    'SonicDisruptor': (180, 0, 255),    # Purple for sonic units
    'CollectorCrab': (255, 160, 0),     # Orange-gold for collector units
    'SeabedCrawler': (120, 120, 120),   # Dark gray for heavy units
    'PressureCrusher': (200, 0, 0),     # Dark red for crusher units
    'VortexGenerator': (0, 200, 200),   # Teal for vortex units
    'BionicSquid': (255, 0, 255),       # Magenta for enhanced units
    'NaniteSwarm': (0, 255, 150)        # Bright green for swarm units
}

# Game settings
BUILDUP_TIME = 10
WAVE_TIME = 30
INITIAL_RESOURCES = 150

class GameState(Enum):
    TITLE = auto()
    SETTINGS = auto()
    LEVEL_SELECT = auto()
    GAMEPLAY = auto()
    GAME_OVER = auto()
    VICTORY = auto()

class Biome(Enum):
    HYDROTHERMAL = auto()
    COLDSEEP = auto()
    BRINE_POOL = auto()
    WHALEFALL = auto()

class TowerType(Enum):
    RESOURCE = auto()
    PROJECTILE = auto()
    TANK = auto()
    EFFECT = auto()
    RARE = auto()

# Tower definitions per biome
TOWER_DEFINITIONS = {
    # Hydrothermal biome
    Biome.HYDROTHERMAL: {
        TowerType.RESOURCE: {'name': 'BlackSmoker', 'resource': 'sulfides', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'RiftiaTubeWorm', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'SquatLobster', 'health': 350, 'melee_damage': 15},
        TowerType.EFFECT: {'name': 'BlueCilliates', 'damage': 5, 'radius': 1}
    },
    # Coldseep biome
    Biome.COLDSEEP: {
        TowerType.RESOURCE: {'name': 'BubblePlume', 'resource': 'methane', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'Rockfish', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'SpiderCrab', 'health': 400, 'melee_damage': 20},
        TowerType.EFFECT: {'name': 'VesicomyidaeClams', 'damage': 5, 'radius': 1}
    },
    # Brine Pool biome
    Biome.BRINE_POOL: {
        TowerType.RESOURCE: {'name': 'BrinePool', 'resource': 'salt', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'Hagfish', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'Chimaera', 'health': 300, 'melee_damage': 25},
        TowerType.EFFECT: {'name': 'MuscleBed', 'damage': 5, 'radius': 1}
    },
    # Whalefall biome
    Biome.WHALEFALL: {
        TowerType.RESOURCE: {'name': 'OsedaxWorm', 'resource': 'lipids', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'Muusoctopus', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'SleeperShark', 'health': 375, 'melee_damage': 18},
        TowerType.EFFECT: {'name': 'Beggiatoa', 'damage': 5, 'radius': 1}
    }
}

# Rare towers available in all biomes
RARE_TOWERS = {
    'GiantSquid': {'damage': 30, 'range': 500, 'cooldown': 0.3},
    'ColossalSquid': {'health': 600, 'melee_damage': 25, 'cooldown': 0.8},
    'DumboOctopus': {'damage': 15, 'radius': 2},
    'Nautilus': {'resource': 'all', 'gen_amount': 5}
}

# Shop settings
SHOP_HEIGHT = 120  # Height of shop area at bottom of screen
SHOP_REFRESH_COST = 10  # Base cost to refresh shop
SHOP_SLOTS = 5  # Number of tower slots in shop
COMBINE_RANGE = 100  # Pixel range for combining towers
FREE_REFRESH_THRESHOLDS = [5,7,8,9,10,15,20,22,25,35,50]  # Enemy kills needed for free refreshes

# Base tower costs for 1-star towers
TOWER_COSTS = {
    # Hydrothermal towers - cost sulfides
    'BlackSmoker': {'sulfides': 30},
    'RiftiaTubeWorm': {'sulfides': 60},
    'SquatLobster': {'sulfides': 75},  # Reduced cost due to slower damage output
    'BlueCilliates': {'sulfides': 45},
    
    # Coldseep towers - cost methane
    'BubblePlume': {'methane': 30},
    'Rockfish': {'methane': 60},
    'SpiderCrab': {'methane': 85},  # Higher cost for better stats
    'VesicomyidaeClams': {'methane': 45},
    
    # Brine Pool towers - cost salt
    'BrinePool': {'salt': 30},
    'Hagfish': {'salt': 60},
    'Chimaera': {'salt': 80},  # High damage but less health
    'MuscleBed': {'salt': 45},
    
    # Whalefall towers - cost lipids
    'OsedaxWorm': {'lipids': 30},
    'Muusoctopus': {'lipids': 60},
    'SleeperShark': {'lipids': 80},
    'Beggiatoa': {'lipids': 45},
    
    # Rare towers (cost all resources)
    'GiantSquid': {'sulfides': 25, 'methane': 25, 'salt': 25, 'lipids': 25},
    'ColossalSquid': {'sulfides': 30, 'methane': 30, 'salt': 30, 'lipids': 30},
    'DumboOctopus': {'sulfides': 20, 'methane': 20, 'salt': 20, 'lipids': 20},
    'Nautilus': {'sulfides': 35, 'methane': 35, 'salt': 35, 'lipids': 35}
}

# Star level multipliers for tower costs
STAR_COST_MULTIPLIERS = {
    1: 1.0,    # Base cost
    2: 3.0,    # 3x cost for 2-star towers
    3: 9.0     # 9x cost for 3-star towers
}

# Star appearance rates in shop
STAR_RATES = {
    1: 0.70,   # 70% chance for 1-star
    2: 0.25,   # 25% chance for 2-star
    3: 0.05    # 5% chance for 3-star
}

# Resource generation rates (per second)
BASE_RESOURCE_GEN = {
    'primary': 10,    # Rate for biome's primary resource
    'secondary': 2    # Rate for other resources
}

# Enemy definitions with expanded mechanics
ENEMY_DEFINITIONS = {
    # Basic Units
    'ScoutDrone': {
        'health': 60, 
        'speed': 120, 
        'damage': 10,
        'abilities': ['detect_towers', 'fast_movement']
    },
    'ExosuitDiver': {
        'health': 180, 
        'speed': 70, 
        'damage': 25,
        'abilities': ['shield_generator', 'repair_nearby']
    },
    'DrillingMech': {
        'health': 400, 
        'speed': 45, 
        'damage': 50,
        'abilities': ['break_terrain', 'armor_plating']
    },
    
    # Advanced Units
    'ROV': {
        'health': 120,
        'speed': 90,
        'damage': 20,
        'abilities': ['emp_pulse', 'resource_steal']
    },
    'HarvesterDrone': {
        'health': 150,
        'speed': 80,
        'damage': 15,
        'abilities': ['collect_resources', 'energy_shield']
    },
    'MiningLaser': {
        'health': 200,
        'speed': 60,
        'damage': 40,
        'abilities': ['beam_attack', 'heat_resistance']
    },
    'SonicDisruptor': {
        'health': 160,
        'speed': 75,
        'damage': 30,
        'abilities': ['stun_towers', 'echo_location']
    },
    
    # Special Units
    'CollectorCrab': {
        'health': 250,
        'speed': 50,
        'damage': 35,
        'abilities': ['resource_drain', 'armored_shell']
    },
    'SeabedCrawler': {
        'health': 500,
        'speed': 35,
        'damage': 60,
        'abilities': ['crush_defenses', 'heavy_plating']
    },
    'PressureCrusher': {
        'health': 300,
        'speed': 55,
        'damage': 45,
        'abilities': ['pressure_wave', 'depth_adapted']
    },
    'VortexGenerator': {
        'health': 220,
        'speed': 65,
        'damage': 25,
        'abilities': ['create_currents', 'water_shield']
    },
    
    # Elite Units
    'BionicSquid': {
        'health': 450,
        'speed': 85,
        'damage': 55,
        'abilities': ['ink_cloud', 'tentacle_grab']
    },
    'NaniteSwarm': {
        'health': 280,
        'speed': 95,
        'damage': 35,
        'abilities': ['self_repair', 'divide']
    },
    
    # Boss Units
    'CorporateSubmarine': {
        'health': 1200,
        'speed': 30,
        'damage': 100,
        'abilities': ['deploy_drones', 'energy_barrier', 'missile_barrage']
    }
}

# Enemy ability effects
ENEMY_ABILITIES = {
    'detect_towers': {'range': 300, 'reveal_duration': 5.0},
    'fast_movement': {'speed_boost': 1.5, 'duration': 3.0},
    'shield_generator': {'shield_amount': 50, 'radius': 100},
    'repair_nearby': {'heal_amount': 10, 'radius': 150, 'interval': 2.0},
    'break_terrain': {'damage_multiplier': 2.0, 'cooldown': 5.0},
    'armor_plating': {'damage_reduction': 0.3},
    'emp_pulse': {'stun_duration': 2.0, 'radius': 120, 'cooldown': 8.0},
    'resource_steal': {'amount': 15, 'radius': 100},
    'collect_resources': {'rate': 5, 'radius': 80},
    'energy_shield': {'absorb_damage': 40, 'recharge_time': 6.0},
    'beam_attack': {'dps': 20, 'range': 200},
    'heat_resistance': {'fire_damage_reduction': 0.5},
    'stun_towers': {'duration': 1.5, 'radius': 150, 'cooldown': 10.0},
    'echo_location': {'reveal_radius': 250, 'duration': 4.0},
    'resource_drain': {'drain_rate': 8, 'radius': 120},
    'armored_shell': {'damage_reduction': 0.4},
    'crush_defenses': {'bonus_damage': 100, 'cooldown': 12.0},
    'heavy_plating': {'damage_reduction': 0.5},
    'pressure_wave': {'damage': 60, 'radius': 180, 'cooldown': 8.0},
    'depth_adapted': {'speed_in_effects': 1.2},
    'create_currents': {'push_force': 150, 'radius': 200, 'duration': 3.0},
    'water_shield': {'damage_reduction': 0.35, 'duration': 4.0},
    'ink_cloud': {'radius': 160, 'duration': 4.0, 'damage': 15},
    'tentacle_grab': {'range': 140, 'hold_duration': 2.0, 'damage': 30},
    'self_repair': {'heal_rate': 10, 'interval': 1.0},
    'divide': {'clone_health_percent': 0.3, 'max_clones': 2, 'cooldown': 15.0},
    'deploy_drones': {'drone_count': 3, 'drone_health': 80, 'cooldown': 20.0},
    'energy_barrier': {'absorb_amount': 200, 'duration': 5.0},
    'missile_barrage': {'missile_count': 5, 'damage_per_missile': 40, 'cooldown': 15.0}
}

# Wave patterns for different difficulty levels
WAVE_PATTERNS = {
    'early_game': {
        'basic_rush': ['ScoutDrone', 'ScoutDrone', 'ExosuitDiver'],
        'resource_raid': ['HarvesterDrone', 'ROV', 'HarvesterDrone'],
        'drilling_team': ['ExosuitDiver', 'DrillingMech', 'ExosuitDiver']
    },
    'mid_game': {
        'tech_squad': ['ROV', 'MiningLaser', 'SonicDisruptor'],
        'heavy_assault': ['SeabedCrawler', 'PressureCrusher', 'DrillingMech'],
        'collection_team': ['CollectorCrab', 'HarvesterDrone', 'VortexGenerator']
    },
    'late_game': {
        'elite_force': ['BionicSquid', 'NaniteSwarm', 'PressureCrusher'],
        'swarm_attack': ['NaniteSwarm', 'NaniteSwarm', 'SonicDisruptor'],
        'boss_raid': ['CorporateSubmarine', 'BionicSquid', 'MiningLaser']
    }
}

# UI settings
TOWER_CARD_SIZE = 80
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 18
FONT_SIZE_LARGE = 24
