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

# Tower colors
TOWER_COLORS = {
    # Hydrothermal
    'BlackSmoker': (50, 50, 50),
    'RiftiaTubeWorm': (255, 80, 80),
    'SquatLobster': (180, 80, 30),
    'BlueCilliates': (80, 80, 255),
    
    # Coldseep
    'BubblePlume': (200, 200, 255),
    'Rockfish': (120, 120, 180),
    'SpiderCrab': (180, 150, 100),
    'VesicomyidaeClams': (220, 220, 180),
    
    # Brine Pool
    'BrinePool': (0, 180, 180),
    'Hagfish': (180, 180, 180),
    'Chimaera': (220, 180, 100),
    'MuscleBed': (180, 100, 100),
    
    # Whalefall
    'OsedaxWorm': (255, 100, 100),
    'Muusoctopus': (150, 50, 150),
    'SleeperShark': (50, 50, 100),
    'Beggiatoa': (255, 255, 200),
    
    # Rare towers
    'GiantSquid': (100, 0, 100),
    'ColossalSquid': (150, 0, 150),
    'DumboOctopus': (200, 100, 200),
    'Nautilus': (255, 200, 100)
}

# Enemy colors
ENEMY_COLORS = {
    'ScoutDrone': (255, 0, 0),
    'ExosuitDiver': (255, 100, 0),
    'DrillingMech': (255, 200, 0),
    'CorporateSubmarine': (255, 0, 255)
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
        TowerType.TANK: {'name': 'SquatLobster', 'health': 300},
        TowerType.EFFECT: {'name': 'BlueCilliates', 'damage': 5, 'radius': 1}
    },
    # Coldseep biome
    Biome.COLDSEEP: {
        TowerType.RESOURCE: {'name': 'BubblePlume', 'resource': 'methane', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'Rockfish', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'SpiderCrab', 'health': 300},
        TowerType.EFFECT: {'name': 'VesicomyidaeClams', 'damage': 5, 'radius': 1}
    },
    # Brine Pool biome
    Biome.BRINE_POOL: {
        TowerType.RESOURCE: {'name': 'BrinePool', 'resource': 'salt', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'Hagfish', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'Chimaera', 'health': 300},
        TowerType.EFFECT: {'name': 'MuscleBed', 'damage': 5, 'radius': 1}
    },
    # Whalefall biome
    Biome.WHALEFALL: {
        TowerType.RESOURCE: {'name': 'OsedaxWorm', 'resource': 'lipids', 'gen_amount': 10},
        TowerType.PROJECTILE: {'name': 'Muusoctopus', 'damage': 20, 'range': 400, 'cooldown': 0.5},
        TowerType.TANK: {'name': 'SleeperShark', 'health': 300},
        TowerType.EFFECT: {'name': 'Beggiatoa', 'damage': 5, 'radius': 1}
    }
}

# Rare towers available in all biomes
RARE_TOWERS = {
    'GiantSquid': {'damage': 30, 'range': 500, 'cooldown': 0.3},
    'ColossalSquid': {'health': 500, 'damage': 10},
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
    'SquatLobster': {'sulfides': 90},
    'BlueCilliates': {'sulfides': 45},
    
    # Coldseep towers - cost methane
    'BubblePlume': {'methane': 30},
    'Rockfish': {'methane': 60},
    'SpiderCrab': {'methane': 90},
    'VesicomyidaeClams': {'methane': 45},
    
    # Brine Pool towers - cost salt
    'BrinePool': {'salt': 30},
    'Hagfish': {'salt': 60},
    'Chimaera': {'salt': 90},
    'MuscleBed': {'salt': 45},
    
    # Whalefall towers - cost lipids
    'OsedaxWorm': {'lipids': 30},
    'Muusoctopus': {'lipids': 60},
    'SleeperShark': {'lipids': 90},
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

# Enemy definitions
ENEMY_DEFINITIONS = {
    'ScoutDrone': {'health': 50, 'speed': 100, 'damage': 10},
    'ExosuitDiver': {'health': 150, 'speed': 60, 'damage': 20},
    'DrillingMech': {'health': 300, 'speed': 40, 'damage': 40},
    'CorporateSubmarine': {'health': 1000, 'speed': 20, 'damage': 100}
}

# UI settings
TOWER_CARD_SIZE = 80
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 18
FONT_SIZE_LARGE = 24
