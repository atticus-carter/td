import pygame
import math
import random
import time
from config import RESOURCE_COLORS

class ResourceOrb:
    def __init__(self, x, y, resource_type, amount, manual_bonus=1.5):
        self.x = x
        self.y = y
        self.resource_type = resource_type
        self.base_amount = amount
        self.manual_bonus = manual_bonus
        self.radius = 8
        self.collected = False
        
        # Enhanced physics for better floating behavior
        self.velocity_x = random.uniform(-25, 25)  # Wider initial spread
        self.velocity_y = random.uniform(-200, -160)  # Stronger upward burst
        self.gravity = 200  # Stronger gravity
        self.buoyancy = 180  # Stronger upward force
        self.air_resistance = 0.97  # Slightly less resistance for smoother motion
        self.lifetime = 15.0  # Longer lifetime
        self.alpha = 255
        self.active = True
        self.time_offset = random.random() * math.pi * 2
        self.color = RESOURCE_COLORS.get(resource_type, (255, 255, 255))
        
        # Additional visual properties
        self.glow_intensity = random.uniform(0.8, 1.2)
        self.pulse_speed = random.uniform(3.5, 4.5)
        self.float_amplitude = random.uniform(0.7, 0.9)
        self.float_speed = random.uniform(2.3, 2.7)

    def update(self, dt):
        if not self.active or self.collected:
            return True

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return True

        # Enhanced physics simulation
        # Apply buoyancy against gravity
        net_force = self.gravity - self.buoyancy
        self.velocity_y += net_force * dt
        
        # Apply air resistance
        self.velocity_x *= self.air_resistance
        self.velocity_y *= self.air_resistance
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Add smooth floating motion
        float_offset = math.sin(time.time() * self.float_speed + self.time_offset) * self.float_amplitude
        self.y += float_offset

        # Gradual fade out near end of lifetime
        if self.lifetime < 2.0:
            self.alpha = int(255 * (self.lifetime / 2.0))

        return False

    def draw(self, surface):
        if not self.active:
            return

        # Calculate base alpha with pulsing effect
        base_alpha = int(self.alpha * (0.8 + 0.2 * math.sin(time.time() * self.pulse_speed + self.time_offset)))
        
        # Create surface for the orb with extra space for glow
        orb_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        center = (self.radius * 1.5, self.radius * 1.5)
        
        # Draw outer glow
        for r in range(6, 0, -1):
            glow_alpha = int((base_alpha // (r + 2)) * self.glow_intensity)
            glow_color = (*self.color, glow_alpha)
            pygame.draw.circle(orb_surface, glow_color, center, self.radius + r)
        
        # Draw main orb body
        main_color = (*self.color, base_alpha)
        pygame.draw.circle(orb_surface, main_color, center, self.radius)
        
        # Add highlight for shininess
        highlight_pos = (center[0] - 2, center[1] - 2)
        highlight_alpha = int(base_alpha * 0.7)
        highlight_color = (255, 255, 255, highlight_alpha)
        pygame.draw.circle(orb_surface, highlight_color, highlight_pos, self.radius // 2)
        
        # Draw small sparkles
        sparkle_time = time.time() * 3 + self.time_offset
        for i in range(3):
            angle = sparkle_time + (i * math.pi * 2 / 3)
            sparkle_x = center[0] + math.cos(angle) * (self.radius - 2)
            sparkle_y = center[1] + math.sin(angle) * (self.radius - 2)
            sparkle_alpha = int(base_alpha * 0.5 * (0.7 + 0.3 * math.sin(sparkle_time + i)))
            sparkle_color = (255, 255, 255, sparkle_alpha)
            pygame.draw.circle(orb_surface, sparkle_color, (sparkle_x, sparkle_y), 1)

        # Draw the orb surface
        draw_x = int(self.x - self.radius * 1.5)
        draw_y = int(self.y - self.radius * 1.5)
        surface.blit(orb_surface, (draw_x, draw_y))

    def collect(self, auto_collected=False):
        """Collect the resource orb and return the amount gained"""
        if not self.collected and self.active:
            self.collected = True
            self.active = False
            return self.base_amount * (1.0 if auto_collected else self.manual_bonus)
        return 0

    def contains_point(self, x, y):
        """Check if a point is within the orb's clickable area"""
        if not self.active:
            return False
        dx = x - self.x
        dy = y - self.y
        # Slightly larger collision radius for easier clicking
        click_radius = self.radius * 1.2
        return (dx * dx + dy * dy) <= (click_radius * click_radius)