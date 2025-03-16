import pygame
from config import *
from ui import Button
import random
import os

# Initialize mixer for sound effects
pygame.mixer.init()
# Load eerie background sound - ensure the file path is correct
eerie_sound_path = os.path.join(os.path.dirname(__file__), "eerie_sound.wav")
if os.path.exists(eerie_sound_path):
    pygame.mixer.music.load(eerie_sound_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)  # Loop infinitely

class TitleScreen:
    def __init__(self):
        center_x = WINDOW_WIDTH // 2
        self.title_font = get_font(FONT_SIZE_LARGE)
        
        # Create buttons using shared Button component
        self.buttons = [
            Button((center_x - 100, 300, 200, 50), "Play"),
            Button((center_x - 100, 370, 200, 50), "Settings"),
            Button((center_x - 100, 440, 200, 50), "Quit")
        ]
        
        # Create dark moving shapes for a deep, blurred atmosphere
        self.shapes = []
        for _ in range(10):
            self.shapes.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.randint(50, 150),
                'dx': random.uniform(-20, 20),
                'dy': random.uniform(-20, 20)
            })
        
        # Create frosted circles for the overlay effect
        self.frosted_circles = []
        for _ in range(50):
            self.frosted_circles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'radius': random.randint(10, 40),
                'dx': random.uniform(-10, 10),
                'dy': random.uniform(-10, 10),
                'alpha': random.randint(50, 150)
            })
        
    def update(self, dt):
        # Update moving dark blurred shapes
        for shape in self.shapes:
            shape['x'] += shape['dx'] * dt
            shape['y'] += shape['dy'] * dt

            # Wrap shapes around the screen
            if shape['x'] < -shape['size']:
                shape['x'] = WINDOW_WIDTH + shape['size']
            elif shape['x'] > WINDOW_WIDTH + shape['size']:
                shape['x'] = -shape['size']
            if shape['y'] < -shape['size']:
                shape['y'] = WINDOW_HEIGHT + shape['size']
            elif shape['y'] > WINDOW_HEIGHT + shape['size']:
                shape['y'] = -shape['size']
        
        # Update frosted circles positions (floating effect)
        for circle in self.frosted_circles:
            circle['x'] += circle['dx'] * dt
            circle['y'] += circle['dy'] * dt
            # Wrap around the screen for circles
            if circle['x'] < -circle['radius']:
                circle['x'] = WINDOW_WIDTH + circle['radius']
            elif circle['x'] > WINDOW_WIDTH + circle['radius']:
                circle['x'] = -circle['radius']
            if circle['y'] < -circle['radius']:
                circle['y'] = WINDOW_HEIGHT + circle['radius']
            elif circle['y'] > WINDOW_HEIGHT + circle['radius']:
                circle['y'] = -circle['radius']
        
    def handle_input(self, event):
        for i, button in enumerate(self.buttons):
            if button.handle_event(event):
                return i  # Return button index
        return None

    def draw_gradient_background(self, surface):
        # Create a deep, dark gradient for the background
        top_color = (10, 10, 30)
        bottom_color = (0, 0, 0)
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
    def draw_blurred_shape(self, surface, shape):
        # Simulate a blurred shape by drawing multiple semi-transparent circles
        base_color = (0, 0, 0)
        layers = 5
        for i in range(layers, 0, -1):
            layer_surface = pygame.Surface((shape['size']*2, shape['size']*2), pygame.SRCALPHA)
            alpha = int(30 * i)
            color = (base_color[0], base_color[1], base_color[2], alpha)
            radius = int(shape['size'] * (i / layers))
            pygame.draw.circle(layer_surface, color, (shape['size'], shape['size']), radius)
            pos = (int(shape['x'] - shape['size']), int(shape['y'] - shape['size']))
            surface.blit(layer_surface, pos)
    
    def draw_frosted_effect(self, surface):
        # Create an overlay covering the entire screen with a dark base
        frosted_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        frosted_surface.fill((20, 20, 20, 180))  # Dark rectangle with transparency
        
        # Draw moving circles on the frosted surface
        for circle in self.frosted_circles:
            circle_color = (30, 30, 30, circle['alpha'])
            pygame.draw.circle(frosted_surface, circle_color, (int(circle['x']), int(circle['y'])), circle['radius'])
        
        # Apply pixelation (dithering) effect: scale down then up
        scale_factor = 10
        small = pygame.transform.scale(frosted_surface, (WINDOW_WIDTH // scale_factor, WINDOW_HEIGHT // scale_factor))
        pixelated = pygame.transform.scale(small, (WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.blit(pixelated, (0, 0))
        
    def draw(self, surface):
        # Draw the deep gradient and moving blurred shapes background
        self.draw_gradient_background(surface)
        for shape in self.shapes:
            self.draw_blurred_shape(surface, shape)
        
        # Draw frosted effect overlay with moving, pixelated circles
        self.draw_frosted_effect(surface)
        
        # Render new title "Deep Sea TD" with a shadow
        title_text = "Deep Sea TD"
        title_surface = self.title_font.render(title_text, True, (0, 80, 200))
        title_shadow = self.title_font.render(title_text, True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 200))
        surface.blit(title_surface, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
        

def run_title_screen(screen):
    """
    Run the title screen and return the selected option.
    Returns:
        0 - Play
        1 - Settings
        2 - Quit
    """
    title_screen = TitleScreen()
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 2  # Quit
                
            result = title_screen.handle_input(event)
            if result is not None:
                return result
                
        title_screen.update(dt)
        title_screen.draw(screen)
        pygame.display.flip()
    
    return 0  # Default to Play if loop exits unexpectedly