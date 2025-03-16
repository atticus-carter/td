import pygame
from config import *
from ui import Button
import random
import os

# Initialize mixer for sound effects - wrapping in try/except to handle potential initialization issues
try:
    pygame.mixer.init()
    # Load eerie background sound - only if file exists
    eerie_sound_path = os.path.join(os.path.dirname(__file__), "eerie_sound.wav")
    if os.path.exists(eerie_sound_path):
        try:
            pygame.mixer.music.load(eerie_sound_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)  # Loop infinitely
        except Exception as e:
            print(f"Could not play background music: {e}")
except Exception as e:
    print(f"Could not initialize audio mixer: {e}")

class TitleScreen:
    def __init__(self):
        self.font_large = get_font(FONT_SIZE_LARGE)
        self.font_medium = get_font(FONT_SIZE_MEDIUM)
        
        # Create buttons
        button_width = 200
        button_height = 60
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        
        self.play_button = Button(
            pygame.Rect(button_x, 300, button_width, button_height),
            "Play"
        )
        
        self.quit_button = Button(
            pygame.Rect(button_x, 380, button_width, button_height),
            "Quit"
        )
        
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
        # First, update the hover state of the buttons for better visual feedback
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.play_button.hover = self.play_button.rect.collidepoint(mouse_pos)
            self.quit_button.hover = self.quit_button.rect.collidepoint(mouse_pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.handle_event(event):
                return 'play'
            if self.quit_button.handle_event(event):
                return 'quit'
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
        try:
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
        except Exception as e:
            print(f"Error in drawing frosted effect: {e}")
            # Fallback to a simple dark overlay
            dark_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            dark_overlay.fill((20, 20, 30))
            dark_overlay.set_alpha(180)
            surface.blit(dark_overlay, (0, 0))
        
    def draw(self, surface):
        try:
            # Draw the deep gradient and moving blurred shapes background
            self.draw_gradient_background(surface)
            for shape in self.shapes:
                self.draw_blurred_shape(surface, shape)
            
            # Draw frosted effect overlay with moving, pixelated circles
            self.draw_frosted_effect(surface)
            
            title_text = "Deep Sea TD"
            title_surface = self.font_large.render(title_text, True, COLOR_TEXT)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 150))
            surface.blit(title_surface, title_rect)
            
            # Draw subtitle
            subtitle_text = "v.0.0.01A (Anton Only Alpha)"
            subtitle_surface = self.font_medium.render(subtitle_text, True, COLOR_TEXT)
            subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, 200))
            surface.blit(subtitle_surface, subtitle_rect)
            
            # Draw buttons
            self.play_button.draw(surface)
            self.quit_button.draw(surface)
        except Exception as e:
            # Fallback rendering in case of any drawing errors
            print(f"Error in title screen drawing: {e}")
            surface.fill((0, 0, 20))  # Simple dark background
            
            # Simple text rendering
            try:
                title_text = self.font_large.render("Mars Tower Defense", True, (255, 255, 255))
                surface.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 150))
                
                subtitle_text = self.font_medium.render("Deep Sea Adventures", True, (200, 200, 200))
                surface.blit(subtitle_text, (WINDOW_WIDTH//2 - subtitle_text.get_width()//2, 200))
                
                # Simple buttons
                pygame.draw.rect(surface, (40, 60, 100), self.play_button.rect)
                pygame.draw.rect(surface, (40, 60, 100), self.quit_button.rect)
                
                play_text = self.font_medium.render("Play", True, (255, 255, 255))
                surface.blit(play_text, (self.play_button.rect.centerx - play_text.get_width()//2, 
                                        self.play_button.rect.centery - play_text.get_height()//2))
                
                quit_text = self.font_medium.render("Quit", True, (255, 255, 255))
                surface.blit(quit_text, (self.quit_button.rect.centerx - quit_text.get_width()//2, 
                                        self.quit_button.rect.centery - quit_text.get_height()//2))
            except:
                # Absolute fallback if even simple rendering fails
                pass

def run_title_screen(screen):
    """
    Run the title screen and return the selected option.
    Returns:
        'play' - Play
        'quit' - Quit
    """
    try:
        title_screen = TitleScreen()
        clock = pygame.time.Clock()
        
        while True:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                    
                result = title_screen.handle_input(event)
                if result is not None:
                    return result
                    
            title_screen.update(dt)
            title_screen.draw(screen)
            pygame.display.flip()
    except Exception as e:
        print(f"Error in title screen: {e}")
        return 'play'  # Default to Play if an error occurs
    
    return 'play'  # Default to Play if loop exits unexpectedly