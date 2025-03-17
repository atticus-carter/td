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
            "Cost: 50 sulfides",
            "",
            "Power: Hydro Pressure",
            "Creates pressure waves that boost nearby",
            "resource generation by 50/100/150%",
            "",
            "⭐ Star Upgrades:",
            "+50% resource generation per star",
            "+50% pressure wave boost per star"
        ],
        'RiftiaTubeWorm': [
            "Riftia Tube Worm",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 sulfides",
            "",
            "Power: Venom Shot",
            "Applies poison damage over time",
            "30/60/90% chance, 5/10/15 damage per tick",
            "",
            "⭐ Star Upgrades:",
            "+50% damage per star",
            "+30% poison chance per star"
        ],
        'SquatLobster': [
            "Squat Lobster",
            "Type: Tank",
            "Blocks enemy path and deals melee damage",
            "Health: 350, Melee Damage: 15",
            "Attack Speed: 1.0s",
            "Cost: 75 sulfides",
            "",
            "Power: Regeneration",
            "Regenerates 5/10/15 health per second",
            "",
            "⭐ Star Upgrades:",
            "+50% health per star",
            "+50% melee damage per star"
        ],
        'BlueCilliates': [
            "Blue Cilliates",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 sulfides",
            "",
            "Power: Chain Reaction",
            "Damage spreads to nearby enemies",
            "30/60/90% spread damage",
            "",
            "⭐ Star Upgrades:",
            "+50% area damage per star",
            "+30% spread damage per star"
        ],
        
        # Coldseep towers
        'BubblePlume': [
            "Bubble Plume",
            "Type: Resource Generator",
            "Generates methane over time",
            "Cost: 50 methane",
            "",
            "Power: Methane Eruption",
            "Releases explosive methane bursts",
            "20/40/60 explosion damage",
            "",
            "⭐ Star Upgrades:",
            "+50% resource generation per star",
            "+50% explosion damage per star"
        ],
        'Rockfish': [
            "Rockfish",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 methane",
            "",
            "Power: Sonic Pulse",
            "Releases stunning sonic waves",
            "1/2/3s stun duration",
            "",
            "⭐ Star Upgrades:",
            "+50% damage per star",
            "+50% stun duration per star"
        ],
        'SpiderCrab': [
            "Spider Crab",
            "Type: Tank",
            "Blocks enemy path and deals melee damage",
            "Health: 400, Melee Damage: 20",
            "Attack Speed: 1.0s",
            "Cost: 85 methane",
            "",
            "Power: Spike Plating",
            "Reflects 20/40/60% damage back",
            "",
            "⭐ Star Upgrades:",
            "+50% health per star",
            "+50% melee damage per star"
        ],
        'VesicomyidaeClams': [
            "Vesicomyidae Clams",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 methane",
            "",
            "Power: Filter Feeding",
            "Converts 10/20/30% of damage to resources",
            "",
            "⭐ Star Upgrades:",
            "+50% area damage per star",
            "+10% resource conversion per star"
        ],
        
        # Brine Pool towers
        'BrinePool': [
            "Brine Pool",
            "Type: Resource Generator",
            "Generates salt over time",
            "Cost: 50 salt",
            "",
            "Power: Brine Spray",
            "Sprays corrosive brine that slows",
            "30/60/90% slow effect",
            "",
            "⭐ Star Upgrades:",
            "+50% resource generation per star",
            "+30% slow effect per star"
        ],
        'Hagfish': [
            "Hagfish",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 salt",
            "",
            "Power: Electric Shock",
            "Chain lightning between 2/3/4 enemies",
            "15/30/45 chain damage",
            "",
            "⭐ Star Upgrades:",
            "+50% damage per star",
            "+1 chain target per star"
        ],
        'Chimaera': [
            "Chimaera",
            "Type: Tank",
            "Blocks enemy path and deals melee damage",
            "Health: 300, Melee Damage: 25",
            "Attack Speed: 1.0s",
            "Cost: 80 salt",
            "",
            "Power: Berserk Mode",
            "20/40/60% attack speed when damaged",
            "",
            "⭐ Star Upgrades:",
            "+50% health per star",
            "+50% melee damage per star"
        ],
        'MuscleBed': [
            "Muscle Bed",
            "Type: Area Effect",
            "Damages enemies that pass nearby",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 salt",
            "",
            "Power: Muscle Pulse",
            "Pushes enemies back with 50/100/150 force",
            "",
            "⭐ Star Upgrades:",
            "+50% area damage per star",
            "+50% push force per star"
        ],
        
        # Whalefall towers
        'OsedaxWorm': [
            "Osedax Worm",
            "Type: Resource Generator",
            "Generates lipids over time",
            "Cost: 50 lipids",
            "",
            "Power: Lipid Siphon",
            "Drains resources from enemies",
            "2/4/6 drain amount",
            "",
            "⭐ Star Upgrades:",
            "+50% resource generation per star",
            "+2 resource drain per star"
        ],
        'Muusoctopus': [
            "Muusoctopus",
            "Type: Projectile Shooter",
            "Fires projectiles at enemies",
            "Damage: 20, Range: 400px",
            "Cost: 100 lipids",
            "",
            "Power: Ink Cloud",
            "Creates blinding ink clouds",
            "4/8/12s duration, slows enemies",
            "",
            "⭐ Star Upgrades:",
            "+50% damage per star",
            "+4s ink cloud duration per star"
        ],
        'SleeperShark': [
            "Sleeper Shark",
            "Type: Tank",
            "Blocks enemy path and deals melee damage",
            "Health: 375, Melee Damage: 18",
            "Attack Speed: 1.0s",
            "Cost: 80 lipids",
            "",
            "Power: Frenzy Bite",
            "1/2/3x attack speed burst",
            "",
            "⭐ Star Upgrades:",
            "+50% health per star",
            "+50% melee damage per star"
        ],
        'Beggiatoa': [
            "Beggiatoa",
            "Type: Area Effect",
            "Creates evolving bacterial colonies",
            "Damage: 5 per second, Radius: 1 cell",
            "Cost: 75 lipids",
            "",
            "Power: Bacterial Bloom",
            "Colonies spread and adapt over time",
            "- Forms colonies from defeated enemies",
            "- Colonies can develop adaptations:",
            "  • Acidic: +50% damage",
            "  • Sticky: 30% slow effect",
            "  • Parasitic: Drains resources",
            "  • Sulfuric: Reduces armor",
            "",
            "⭐ Star Upgrades:",
            "+50% colony damage per star",
            "+2 max colonies per star",
            "+15% mutation chance per star"
        ],
        
        # Rare towers
        'GiantSquid': [
            "Giant Squid",
            "Type: Rare Projectile",
            "Powerful shooter with extended range",
            "Damage: 30, Range: 500px",
            "Cost: 40 of each resource",
            "",
            "Power: Tentacle Sweep",
            "Sweeping tentacle attack",
            "50/100/150 sweep damage",
            "",
            "⭐ Star Upgrades:",
            "+50% damage per star",
            "+50% sweep damage per star"
        ],
        'ColossalSquid': [
            "Colossal Squid",
            "Type: Rare Tank",
            "Extremely durable with high melee damage",
            "Health: 600, Melee Damage: 25",
            "Attack Speed: 0.8s",
            "Cost: 30 of each resource",
            "",
            "Power: Deepsea King",
            "Buffs nearby towers by 20/40/60%",
            "",
            "⭐ Star Upgrades:",
            "+50% health per star",
            "+50% buff effect per star"
        ],
        'DumboOctopus': [
            "Dumbo Octopus",
            "Type: Rare Area Effect",
            "Enhanced area damage tower",
            "Damage: 15 per second, Radius: 2 cells",
            "Cost: 35 of each resource",
            "",
            "Power: Oxygen Burst",
            "Heals and boosts nearby towers",
            "20/40/60 heal, 2/4/6 resource bonus",
            "",
            "⭐ Star Upgrades:",
            "+50% area damage per star",
            "+20 healing per star"
        ],
        'Nautilus': [
            "Nautilus",
            "Type: Rare Resource Generator",
            "Generates all resource types",
            "Output: 5 of each resource per second",
            "Cost: 60 of each resource",
            "",
            "Power: Resource Nexus",
            "Links resource towers, shares 20/40/60%",
            "",
            "⭐ Star Upgrades:",
            "+50% resource generation per star",
            "+20% resource sharing per star"
        ]
    }
    
    # Return the tooltip for the specified tower, or a generic message if not found
    return tooltips.get(tower_name, [f"Unknown Tower: {tower_name}"])

def get_colony_tooltip_text(colony):
    """Return tooltip text for a bacterial colony"""
    lines = [
        f"Bacterial Colony - Generation {colony.generation}",
        f"Health: {int(colony.health)}%",
        f"Maturity: {int(colony.maturity * 100)}%",
        "",
        "Adaptations:"
    ]
    
    if colony.strain_type == "acidic":
        lines.extend([
            "• Acidic Strain",
            "  Increased damage output",
            f"  +50% damage"
        ])
    elif colony.strain_type == "sticky":
        lines.extend([
            "• Sticky Strain",
            "  Slows nearby enemies",
            f"  30% movement reduction"
        ])
    elif colony.strain_type == "parasitic":
        lines.extend([
            "• Parasitic Strain",
            "  Drains resources from enemies",
            f"  {int(colony.resource_consumption)} resource drain"
        ])
    elif colony.strain_type == "sulfuric":
        lines.extend([
            "• Sulfuric Strain",
            "  Reduces enemy armor",
            "  20% armor reduction"
        ])
    
    return lines

def get_enemy_tooltip_text(enemy_type):
    """
    Return tooltip text for a specific enemy type.
    """
    tooltips = {
        # Basic Units
        'ScoutDrone': [
            "Scout Drone",
            "Fast recon unit that reveals tower positions",
            "Can temporarily boost its speed",
            "Low health but quick and agile"
        ],
        'ExosuitDiver': [
            "Exosuit Diver",
            "Armored deep-sea mining personnel",
            "Generates protective shields",
            "Can repair nearby units"
        ],
        'DrillingMech': [
            "Drilling Mech",
            "Heavy mining mech with reinforced plating",
            "Deals extra damage to structures",
            "High health and armor"
        ],
        
        # Advanced Units
        'ROV': [
            "ROV",
            "Remote Operated Vehicle",
            "Can emit EMP pulses to stun towers",
            "Steals resources from your stockpile"
        ],
        'HarvesterDrone': [
            "Harvester Drone",
            "Automated resource collection unit",
            "Protected by energy shields",
            "Drains resources from the area"
        ],
        'MiningLaser': [
            "Mining Laser",
            "High-powered cutting equipment",
            "Continuous beam attack",
            "Resistant to heat damage"
        ],
        'SonicDisruptor': [
            "Sonic Disruptor",
            "Uses sonic waves to disorient defenses",
            "Can stun multiple towers",
            "Uses echolocation to reveal hidden units"
        ],
        
        # Special Units
        'CollectorCrab': [
            "Collector Crab",
            "Biomechanically enhanced crustacean",
            "Heavily armored shell",
            "Drains resources over time"
        ],
        'SeabedCrawler': [
            "Seabed Crawler",
            "Heavy tracked mining vehicle",
            "Extremely durable armor",
            "Crushes through defenses"
        ],
        'PressureCrusher': [
            "Pressure Crusher",
            "Weaponized pressure manipulation",
            "Creates damaging pressure waves",
            "Adapted to extreme depths"
        ],
        'VortexGenerator': [
            "Vortex Generator",
            "Creates powerful water currents",
            "Pushes back defensive units",
            "Protected by water shield"
        ],
        
        # Elite Units
        'BionicSquid': [
            "Bionic Squid",
            "Enhanced deep sea predator",
            "Releases ink clouds for cover",
            "Can grab and hold towers"
        ],
        'NaniteSwarm': [
            "Nanite Swarm",
            "Self-replicating micro-machines",
            "Continuously repairs itself",
            "Can split into multiple units"
        ],
        
        # Boss Unit
        'CorporateSubmarine': [
            "Corporate Submarine",
            "Massive command vessel",
            "Deploys support drones",
            "Protected by energy barrier",
            "Launches missile barrages"
        ]
    }
    
    return tooltips.get(enemy_type, ["Unknown Enemy Type"])