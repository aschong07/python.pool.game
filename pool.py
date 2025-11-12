import pygame
import math

pygame.init()

# Game window dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Pool Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Ball class
class Ball:
    def __init__(self, x, y, radius, color, mass=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = 0
        self.vy = 0
        self.mass = mass

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self, dt):
        # Apply friction
        friction_factor = 0.98
        self.vx *= friction_factor
        self.vy *= friction_factor

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Basic wall collision (example)
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx *= -1
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy *= -1

# Game loop
running = True
clock = pygame.time.Clock()
cue_ball = Ball(200, 300, 15, WHITE)

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                mouse_x, mouse_y = event.pos
                dx = cue_ball.x - mouse_x
                dy = cue_ball.y - mouse_y
                angle = math.atan2(dy, dx)
                force = 200 # Example force
                cue_ball.vx = force * math.cos(angle)
                cue_ball.vy = force * math.sin(angle)

    # Update game elements
    cue_ball.update(dt)

    # Drawing
    screen.fill(BLACK) # Pool table background
    cue_ball.draw(screen)

    pygame.display.update()

pygame.quit()
