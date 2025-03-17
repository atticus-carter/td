import pygame
import numpy as np
import noise
import math
import random
import colorsys
from config import *
from enum import Enum, auto

class SedimentType(Enum):
    VOLCANIC_SAND = auto()    # Black smoker deposits, rich in sulfides
    METHANE_MUD = auto()      # Cold seep sediments with carbonate concretions
    HALITE = auto()           # Brine pool precipitates and salt crystals
    ORGANIC_OOZE = auto()     # Whale fall decomposition products
    
class ForamType(Enum):
    GLOBIGERINA = auto()      # Planktonic species
    RADIOLARIA = auto()       # Silicon-based plankton
    PLANKTIC = auto()         # Surface-dwelling species
    BENTHIC = auto()          # Bottom-dwelling species

class SedimentGenerator:
    def __init__(self, biome, level):
        # Foram patterns for different species (4x4 pixel patterns)
        self.foram_patterns = {
            ForamType.GLOBIGERINA: [
                [0,1,1,0],
                [1,1,1,1],
                [1,1,1,1],
                [0,1,1,0]
            ],
            ForamType.RADIOLARIA: [
                [0,1,1,0],
                [1,0,0,1],
                [1,0,0,1],
                [0,1,1,0]
            ],
            ForamType.PLANKTIC: [
                [0,1,1,0],
                [1,1,1,1],
                [1,0,0,1],
                [0,1,1,0]
            ],
            ForamType.BENTHIC: [
                [1,1,0,1],
                [1,0,0,1],
                [1,0,0,1],
                [1,1,1,1]
            ]
        }
        
        self.biome = biome
        self.level = level
        self.width = WINDOW_WIDTH - SIDEBAR_WIDTH
        self.height = WINDOW_HEIGHT
        
        # Grid settings
        self.grid_cols = GRID_COLS
        self.grid_rows = GRID_ROWS
        self.cell_width = CELL_WIDTH
        self.cell_height = CELL_HEIGHT
        
        # Chunky pixel settings
        self.chunk_size = 8
        self.grid_width = self.width // self.chunk_size
        self.grid_height = self.height // self.chunk_size
        
        # Enhanced 3D effect settings
        self.perspective_strength = 0.4  # Increased for more pronounced effect
        self.view_angle = 35  # Slightly increased angle for better depth
        self.parallax_layers = 3
        self.sway_time = 0
        
        # Path and visual settings
        self.path_alpha = 40
        self.glow_radius = 25
        self.glow_intensity = 50
        self.shadow_strength = 60
        
        # Biome-specific colors and effects
        self.path_colors = {
            Biome.HYDROTHERMAL: {
                'path': (140, 50, 30),
                'glow': (255, 100, 50, 30),
                'highlight': (200, 80, 40)
            },
            Biome.COLDSEEP: {
                'path': (50, 70, 90),
                'glow': (100, 150, 200, 30),
                'highlight': (80, 100, 120)
            },
            Biome.BRINE_POOL: {
                'path': (70, 110, 110),
                'glow': (150, 200, 200, 30),
                'highlight': (100, 140, 140)
            },
            Biome.WHALEFALL: {
                'path': (70, 60, 80),
                'glow': (130, 110, 150, 30),
                'highlight': (100, 90, 110)
            }
        }
        
        # Base sediment palettes
        self.palettes = {
            Biome.HYDROTHERMAL: [
                (80, 30, 20),    # Iron-rich deposits (near)
                (60, 25, 15),    # Iron-rich deposits (mid)
                (40, 20, 10),    # Iron-rich deposits (far)
                (30, 15, 8),     # Iron-rich deposits (very far)
            ],
            Biome.COLDSEEP: [
                (70, 80, 90),    # Methane-derived carbonates (near)
                (60, 70, 80),    # Methane-derived carbonates (mid)
                (50, 60, 70),    # Methane-derived carbonates (far)
                (40, 50, 60),    # Methane-derived carbonates (very far)
            ],
            Biome.BRINE_POOL: [
                (180, 200, 200), # Halite crystals (near)
                (160, 180, 180), # Halite crystals (mid)
                (140, 160, 160), # Halite crystals (far)
                (120, 140, 140), # Halite crystals (very far)
            ],
            Biome.WHALEFALL: [
                (70, 60, 80),    # Organic matter (near)
                (60, 50, 70),    # Organic matter (mid)
                (50, 40, 60),    # Organic matter (far)
                (40, 30, 50),    # Organic matter (very far)
            ]
        }
        
        # Noise layer properties
        self.layer_scales = [4.0, 8.0, 16.0]
        self.layer_weights = [0.5, 0.3, 0.2]
        
        # Initialize surfaces for parallax layers
        self.parallax_surfaces = self.generate_parallax_layers()
        
    def generate_parallax_layers(self):
        """Generate multiple sediment layers for parallax effect"""
        layers = []
        for i in range(self.parallax_layers):
            layer = self.generate_sediment_layer(depth_offset=i/self.parallax_layers)
            layers.append(layer)
        return layers
        
    def generate_sediment_layer(self, depth_offset=0):
        """Generate a single sediment layer with perspective"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        noise_map = self.generate_base_sediment()
        
        for grid_y in range(self.grid_height):
            depth = (grid_y / self.grid_height + depth_offset) % 1.0
            
            for grid_x in range(self.grid_width):
                noise_val = noise_map[grid_y][grid_x]
                color_idx = min(len(self.palettes[self.biome])-1,
                              int((noise_val + depth) / 2 * len(self.palettes[self.biome])))
                color = self.palettes[self.biome][color_idx]
                
                # Add variation
                variation = random.randint(-10, 10)
                color = tuple(max(0, min(255, c + variation)) for c in color)
                
                # Apply depth-based alpha
                alpha = int(255 * (1 - depth_offset * 0.5))
                color = (*color, alpha)
                
                chunk_rect = pygame.Rect(
                    grid_x * self.chunk_size,
                    grid_y * self.chunk_size,
                    self.chunk_size,
                    self.chunk_size
                )
                pygame.draw.rect(surface, color, chunk_rect)
        
        return surface

    def generate_lane_markings(self, surface):
        """Generate subtle lane markings for enemy paths"""
        path_color = self.path_colors[self.biome]['path']
        glow_color = self.path_colors[self.biome]['glow']
        highlight_color = self.path_colors[self.biome]['highlight']
        
        # Create surface for lane markings
        lane_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw multiple lanes with perspective
        for row in range(self.grid_rows):
            y = row * self.cell_height
            depth = row / self.grid_rows
            
            # Calculate perspective offset
            offset_x = depth * math.sin(math.radians(self.view_angle)) * 100
            
            # Draw lane markers with perspective
            start_x = offset_x
            end_x = self.width
            
            # Create gradient for lane marker
            for x in range(int(start_x), int(end_x), 4):
                # Calculate alpha based on position
                alpha = int(self.path_alpha * (1 - (x - start_x)/(end_x - start_x)))
                current_color = (*path_color, alpha)
                
                # Draw lane marker with varying thickness
                thickness = max(1, int(3 * (1 - depth)))
                pygame.draw.line(lane_surface,
                               current_color,
                               (x, y + self.cell_height/2),
                               (x + 4, y + self.cell_height/2),
                               thickness)
                
            # Add highlight effect
            highlight_pos = (start_x + 20, y + self.cell_height/2)
            highlight_radius = int(self.glow_radius * (1 - depth))
            pygame.draw.circle(lane_surface, 
                             (*highlight_color, self.path_alpha//2),
                             highlight_pos, 
                             highlight_radius)
        
        return lane_surface

    def generate_layer(self, scale, octaves):
        """Generate a single noise layer with perspective distortion"""
        noise_map = np.zeros((self.grid_height, self.grid_width))
        
        for y in range(self.grid_height):
            # Calculate depth factor (0 near, 1 far)
            depth = y / self.grid_height
            
            # Apply perspective distortion
            perspective_y = y + (depth * self.perspective_strength * self.grid_height)
            
            for x in range(self.grid_width):
                # Adjust x based on perspective
                perspective_x = x + (depth * math.sin(math.radians(self.view_angle)) * self.grid_width * 0.2)
                
                noise_map[y][x] = noise.pnoise3(
                    perspective_x/scale, 
                    perspective_y/scale,
                    self.level/10.0,
                    octaves=octaves,
                    persistence=0.5,
                    lacunarity=2.0,
                    base=self.level + int(scale)
                )
        return noise_map
        
    def generate_base_sediment(self):
        """Generate multi-layered chunky sediment"""
        combined_map = np.zeros((self.grid_height, self.grid_width))
        
        octaves = 4  # Controls the level of detail
        persistence = 0.5  # Controls how much each octave contributes
        lacunarity = 2.0  # Controls how frequency increases each octave
        
        for i in range(octaves):
            frequency = lacunarity ** i
            amplitude = persistence ** i
            
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    # Generate coherent noise
                    value = noise.pnoise3(
                        x * frequency / self.grid_width,
                        y * frequency / self.grid_height,
                        self.level / 10.0,  # Use level as z-coordinate for variation
                        octaves=1,
                        persistence=0.5,
                        lacunarity=2.0,
                        base=self.level + i  # Different base for each octave
                    )
                    combined_map[y][x] += value * amplitude
                    
        # Normalize to 0-1 range
        combined_map = (combined_map - combined_map.min()) / (combined_map.max() - combined_map.min())
        return combined_map
        
    def generate_sediment_surface(self):
        """Generate complete sediment surface with chunky pixels and depth effect"""
        base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        noise_map = self.generate_base_sediment()
        
        # Get color palette for current biome
        palette = self.palettes[self.biome]
        
        # Create chunky pixel array
        for grid_y in range(self.grid_height):
            # Calculate depth factor for shading (0 = near, 1 = far)
            depth = grid_y / self.grid_height
            
            for grid_x in range(self.grid_width):
                noise_val = noise_map[grid_y][grid_x]
                
                # Add biome-specific patterns
                if self.biome == Biome.HYDROTHERMAL:
                    if noise_val > 0.8:
                        noise_val = 0.95
                elif self.biome == Biome.COLDSEEP:
                    if noise_val > 0.7 and random.random() < 0.1:
                        noise_val = 0.9
                elif self.biome == Biome.BRINE_POOL:
                    if noise_val > 0.6:
                        noise_val = min(1.0, noise_val * 1.3)
                elif self.biome == Biome.WHALEFALL:
                    if noise_val < 0.3:
                        noise_val *= 0.7
                
                # Apply depth-based color selection
                color_idx = min(len(palette)-1, int((noise_val + depth) / 2 * len(palette)))
                color = palette[color_idx]
                
                # Add slight random variation to chunk
                variation = random.randint(-10, 10)
                color = tuple(max(0, min(255, c + variation)) for c in color)
                
                # Draw chunky pixel
                chunk_rect = pygame.Rect(
                    grid_x * self.chunk_size,
                    grid_y * self.chunk_size,
                    self.chunk_size,
                    self.chunk_size
                )
                pygame.draw.rect(base_surface, color, chunk_rect)
                
                # Add simple shading for 3D effect
                if noise_val > 0.5:
                    highlight = pygame.Surface((self.chunk_size, self.chunk_size), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 30))  # Subtle white highlight
                    base_surface.blit(highlight, chunk_rect)
                elif noise_val < 0.3:
                    shadow = pygame.Surface((self.chunk_size, self.chunk_size), pygame.SRCALPHA)
                    shadow.fill((0, 0, 0, 30))  # Subtle shadow
                    base_surface.blit(shadow, chunk_rect)
        
        # Add foraminifera at a larger scale
        self.add_foraminifera(base_surface)
        
        return base_surface
        
    def add_foraminifera(self, surface):
        """Add biome-appropriate foraminifera with depth scaling"""
        biome_forams = {
            Biome.HYDROTHERMAL: [ForamType.BENTHIC],  # Heat-tolerant species
            Biome.COLDSEEP: [ForamType.BENTHIC, ForamType.PLANKTIC],  # Methane-tolerant species
            Biome.BRINE_POOL: [ForamType.BENTHIC],  # Halophilic species
            Biome.WHALEFALL: [ForamType.BENTHIC, ForamType.GLOBIGERINA]  # Organic matter processors
        }
        
        foram_count = random.randint(20, 30)  # Reduced count for chunky style
        available_types = biome_forams.get(self.biome, list(ForamType))
        
        for _ in range(foram_count):
            x = random.randint(0, self.width - 16)  # Larger spacing
            y = random.randint(0, self.height - 16)
            foram_type = random.choice(available_types)
            pattern = self.foram_patterns[foram_type]
            
            # Scale foram size based on depth
            depth = y / self.height
            scale = 2 - depth  # Larger at bottom, smaller at top
            
            color = self.get_foram_color(foram_type, depth)
            
            # Draw scaled foram
            for py, row in enumerate(pattern):
                for px, pixel in enumerate(row):
                    if pixel:
                        pos_x = int(x + px * scale)
                        pos_y = int(y + py * scale)
                        if 0 <= pos_x < self.width and 0 <= pos_y < self.height:
                            rect = pygame.Rect(pos_x, pos_y, max(1, int(scale)), max(1, int(scale)))
                            pygame.draw.rect(surface, color, rect)
                            
    def get_foram_color(self, foram_type, depth=0):
        """Get scientifically accurate foram coloring with depth adjustment"""
        base_colors = {
            ForamType.GLOBIGERINA: (220, 220, 200),  # Calcite shells
            ForamType.RADIOLARIA: (240, 240, 230),   # Silica shells
            ForamType.PLANKTIC: (230, 225, 215),     # Mixed composition
            ForamType.BENTHIC: (200, 195, 185)       # Sediment-dwelling species
        }
        base = base_colors[foram_type]
        
        # Darken color based on depth
        darkness = 1.0 - (depth * 0.4)  # Less dark for better visibility
        color = tuple(int(c * darkness) for c in base)
        
        variance = 15
        return tuple(max(0, min(255, c + random.randint(-variance, variance))) for c in color)
        
    def update(self, dt):
        """Update animated elements"""
        self.sway_time += dt * 0.5

    def draw(self, surface):
        """Draw all background elements with parallax effect"""
        # Draw parallax layers
        for i, layer in enumerate(self.parallax_surfaces):
            # Calculate parallax offset based on layer depth
            depth = i / len(self.parallax_surfaces)
            offset_x = math.sin(self.sway_time) * (20 * (1 - depth))
            
            # Draw layer with offset
            surface.blit(layer, (int(offset_x), 0))
        
        # Draw lane markings over the base layers
        lane_surface = self.generate_lane_markings(surface)
        surface.blit(lane_surface, (0, 0))

    def get_background(self):
        """Generate and return the complete background surface"""
        # Create the base background surface
        background = pygame.Surface((self.width, self.height))
        
        # Draw parallax layers onto background
        for i, layer in enumerate(self.parallax_surfaces):
            # Calculate initial parallax offset based on layer depth
            depth = i / len(self.parallax_surfaces)
            offset_x = 0  # Start with no offset for initial background
            
            # Draw layer with offset
            background.blit(layer, (int(offset_x), 0))
        
        # Draw lane markings
        lane_surface = self.generate_lane_markings(background)
        background.blit(lane_surface, (0, 0))
        
        return background