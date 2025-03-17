import pygame
import math
from config import RESOURCE_COLORS

class ResourceOrb:
    def __init__(self, x, y, resource_type, amount, lifetime=5.0):
        self.x = x
        self.y = y
        self.resource_type = resource_type
        self.amount = amount
        self.radius = 12  # Increased radius for better visibility
        self.color = RESOURCE_COLORS.get(resource_type, (200, 200, 200))
        self.lifetime = lifetime
        self.time_left = lifetime
        self.active = True
        
        # Add upward movement
        self.float_speed = 50  # pixels per second upward
        self.horizontal_speed = 20  # pixels per second sideways
        
        # Add subtle floating motion
        self.base_x = x
        self.base_y = y
        self.float_offset = 0
        self.float_time = 0
        
    def update(self, dt):
        """Update the orb's state and return False if it should be removed"""
        if not self.active:
            return False
            
        self.time_left -= dt
        if self.time_left <= 0:
            return False
            
        # Move upward
        self.base_y -= self.float_speed * dt
        
        # Update floating motion
        self.float_time += dt * 2
        self.float_offset = math.sin(self.float_time) * 15  # Increased amplitude
        self.x = self.base_x + self.float_offset
        self.y = self.base_y
        
        return True
        
    def draw(self, surface):
        if not self.active:
            return
            
        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (self.time_left / self.lifetime))
        color_with_alpha = (*self.color, alpha)
        
        # Create a surface for the semi-transparent orb
        orb_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Draw main orb
        pygame.draw.circle(orb_surface, color_with_alpha, (self.radius, self.radius), self.radius)
        
        # Add inner glow
        inner_radius = self.radius - 4
        inner_color = (255, 255, 255, alpha)
        pygame.draw.circle(orb_surface, inner_color, (self.radius, self.radius), inner_radius)
        
        # Add outer glow
        glow_radius = self.radius + 4
        glow_color = (*self.color, alpha // 4)
        pygame.draw.circle(orb_surface, glow_color, (self.radius, self.radius), glow_radius)
        
        # Draw the orb surface
        surface.blit(orb_surface, (self.x - self.radius, self.y - self.radius))
        
    def contains_point(self, x, y):
        """Check if a point is within the orb's clickable area"""
        dx = x - self.x
        dy = y - self.y
        # Use slightly larger radius for easier clicking
        click_radius = self.radius + 4
        return (dx * dx + dy * dy) <= (click_radius * click_radius)