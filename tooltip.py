import pygame
from config import *
from ui import HealthBar

class Tooltip:
    """
    A class for displaying hoverable tooltips in the game.
    Tooltips can display information about towers, resources, or any other game element.
    """
    def __init__(self):
        self.font = get_font(FONT_SIZE_SMALL)
        self.visible = False
        self.content = []
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.background_color = (40, 40, 50, 230)  # Dark blue with alpha
        self.text_color = COLOR_TEXT
        self.padding = 10
        self.max_width = 250
        self.line_height = FONT_SIZE_SMALL + 4
        
    def set_content(self, content):
        """
        Set the tooltip content.
        Content can be a single string or a list of strings for multiple lines.
        """
        if isinstance(content, str):
            self.content = [content]
        else:
            self.content = content
        
        # Calculate tooltip size based on content
        width = 0
        for line in self.content:
            text_surface = self.font.render(line, True, self.text_color)
            width = max(width, text_surface.get_width())
        
        # Cap width and calculate height
        width = min(width, self.max_width) + self.padding * 2
        height = len(self.content) * self.line_height + self.padding * 2
        
        self.rect.width = width
        self.rect.height = height
        
    def show(self, x, y):
        """Show the tooltip at the specified position"""
        self.visible = True
        
        # Position tooltip - ensure it stays within screen bounds
        self.rect.x = min(x, WINDOW_WIDTH - self.rect.width)
        self.rect.y = min(y, WINDOW_HEIGHT - self.rect.height)
        
    def hide(self):
        """Hide the tooltip"""
        self.visible = False
        
    def draw(self, surface):
        """Draw the tooltip if visible"""
        if not self.visible or not self.content:
            return
            
        # Create a transparent surface for the background
        tooltip_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        tooltip_surface.fill(self.background_color)
        
        # Draw each line of text
        for i, line in enumerate(self.content):
            text_surface = self.font.render(line, True, self.text_color)
            tooltip_surface.blit(text_surface, (self.padding, self.padding + i * self.line_height))
        
        # Draw the tooltip surface on the main surface
        surface.blit(tooltip_surface, (self.rect.x, self.rect.y))

    def draw_health_bar(self, surface, x, y, width, current_health, max_health):
        """Draw a health bar using the shared HealthBar component"""
        HealthBar.draw(surface, x, y, width, current_health, max_health)

def get_tower_tooltip_text(tower_name):
    """
    Return tooltip text for a specific tower.
    Returns a list of strings, each string representing a line in the tooltip.
    """
    # Base tooltips for each tower type
    tooltips = {
        # Hydrothermal towers
        'BlackSmoker': [
            "Black Smoker",
            "Type: Resource Generator",
            "Generates sulfides over time",
            "Cost: 50 sulfides"
        ],
        'RiftiaTubeWorm': [
            "Riftia Tube Worm",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 sulfides"
        ],
        'SquatLobster': [
            "Squat Lobster",
            "Type: Tank",
            "Blocks enemy path with high health",
            "Health: 300",
            "Cost: 150 sulfides"
        ],
        'BlueCilliates': [
            "Blue Cilliates",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 sulfides"
        ],
        
        # Coldseep towers
        'BubblePlume': [
            "Bubble Plume",
            "Type: Resource Generator",
            "Generates methane over time",
            "Cost: 50 methane"
        ],
        'Rockfish': [
            "Rockfish",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 methane"
        ],
        'SpiderCrab': [
            "Spider Crab",
            "Type: Tank",
            "Blocks enemy path with high health",
            "Health: 300",
            "Cost: 150 methane"
        ],
        'VesicomyidaeClams': [
            "Vesicomyidae Clams",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 methane"
        ],
        
        # Brine Pool towers
        'BrinePool': [
            "Brine Pool",
            "Type: Resource Generator",
            "Generates salt over time",
            "Cost: 50 salt"
        ],
        'Hagfish': [
            "Hagfish",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 salt"
        ],
        'Chimaera': [
            "Chimaera",
            "Type: Tank",
            "Blocks enemy path with high health",
            "Health: 300",
            "Cost: 150 salt"
        ],
        'MuscleBed': [
            "Muscle Bed",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 salt"
        ],
        
        # Whalefall towers
        'OsedaxWorm': [
            "Osedax Worm",
            "Type: Resource Generator",
            "Generates lipids over time",
            "Cost: 50 lipids"
        ],
        'Muusoctopus': [
            "Muusoctopus",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 lipids"
        ],
        'SleeperShark': [
            "Sleeper Shark",
            "Type: Tank",
            "Blocks enemy path with high health",
            "Health: 300",
            "Cost: 150 lipids"
        ],
        'Beggiatoa': [
            "Beggiatoa",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 lipids"
        ],
        
        # Rare towers
        'GiantSquid': [
            "Giant Squid",
            "Type: Rare Projectile",
            "Powerful shooter with extended range",
            "Damage: 30, Range: 500px",
            "Cost: 40 of each resource"
        ],
        'ColossalSquid': [
            "Colossal Squid",
            "Type: Rare Tank",
            "Extremely durable blocking tower",
            "Health: 500",
            "Cost: 50 of each resource"
        ],
        'DumboOctopus': [
            "Dumbo Octopus",
            "Type: Rare Area Effect",
            "Enhanced area damage tower",
            "Damage: 15 per second, Radius: 2 cells",
            "Cost: 35 of each resource"
        ],
        'Nautilus': [
            "Nautilus",
            "Type: Rare Resource Generator",
            "Generates all resource types",
            "Output: 5 of each resource per second",
            "Cost: 60 of each resource"
        ]
    }
    
    # Return the tooltip for the specified tower, or a generic message if not found
    return tooltips.get(tower_name, [f"Unknown Tower: {tower_name}"])


def get_enemy_tooltip_text(enemy_type):
    """
    Return tooltip text for a specific enemy type.
    """
    tooltips = {
        'ScoutDrone': [
            "Scout Drone",
            "Fast but fragile reconnaissance unit",
            "Health: 50, Speed: Fast",
            "Damage: 10"
        ],
        'ExosuitDiver': [
            "Exosuit Diver",
            "Medium armored human diver",
            "Health: 150, Speed: Medium",
            "Damage: 20"
        ],
        'DrillingMech': [
            "Drilling Mech",
            "Heavy mining machine",
            "Health: 300, Speed: Slow",
            "Damage: 40"
        ],
        'CorporateSubmarine': [
            "Corporate Submarine",
            "Boss unit - heavily armored sub",
            "Health: 1000, Speed: Very Slow",
            "Damage: 100"
        ]
    }
    
    return tooltips.get(enemy_type, [f"Unknown Enemy: {enemy_type}"])