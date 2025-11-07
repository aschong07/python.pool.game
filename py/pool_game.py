import pygame
import math
import random

# --- Constants ---
WIDTH, HEIGHT = 900, 500
TABLE_MARGIN = 20 # Space between the edge and where balls can go
PLAYABLE_WIDTH = WIDTH - 2 * TABLE_MARGIN
PLAYABLE_HEIGHT = HEIGHT - 2 * TABLE_MARGIN
BALL_RADIUS = 10
FPS = 60
FRICTION_FACTOR = 0.99
CUE_POWER_SCALE = 0.5 # Scales mouse distance to ball velocity

# --- Colors ---
TABLE_COLOR = (0, 100, 0)
WALL_COLOR = (150, 75, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Pool Game")
clock = pygame.time.Clock()

# --- Ball Class ---
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.radius = BALL_RADIUS
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0 # Standard mass for collision calculations
        self.moving = False # State flag

        # Pygame visual setup
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        # 1. Apply Movement
        self.x += self.vx
        self.y += self.vy
        
        # 2. Apply Friction (Deceleration)
        speed = math.hypot(self.vx, self.vy)
        if speed > 0:
            self.vx *= FRICTION_FACTOR
            self.vy *= FRICTION_FACTOR

            # Stop the ball if its speed is too low
            if speed < 0.1:
                self.vx = 0.0
                self.vy = 0.0
                self.moving = False
            else:
                self.moving = True
        
        # Update the sprite's position
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


# --- Physics Functions ---

def check_wall_collision(ball):
    """Checks and resolves collision with table boundaries."""
    # Left/Right walls
    if ball.x - ball.radius < TABLE_MARGIN:
        ball.vx *= -1
        ball.x = TABLE_MARGIN + ball.radius
    elif ball.x + ball.radius > WIDTH - TABLE_MARGIN:
        ball.vx *= -1
        ball.x = WIDTH - TABLE_MARGIN - ball.radius

    # Top/Bottom walls
    if ball.y - ball.radius < TABLE_MARGIN:
        ball.vy *= -1
        ball.y = TABLE_MARGIN + ball.radius
    elif ball.y + ball.radius > HEIGHT - TABLE_MARGIN:
        ball.vy *= -1
        ball.y = HEIGHT - TABLE_MARGIN - ball.radius

def resolve_ball_collision(ball1, ball2):
    """
    Handles perfectly elastic collision between two balls 
    using 2D vector math (conservation of momentum).
    """
    # Vector connecting the centers (normal vector)
    nx = ball2.x - ball1.x
    ny = ball2.y - ball1.y
    
    # Distance between centers (squared)
    distance_sq = nx**2 + ny**2
    min_dist = ball1.radius + ball2.radius
    
    if distance_sq < min_dist**2 and distance_sq > 0:
        # Collision detected
        distance = math.sqrt(distance_sq)
        
        # Normalize the vector
        unx = nx / distance
        uny = ny / distance
        
        # Separation to prevent sticking (pushing balls apart)
        overlap = min_dist - distance
        ball1.x -= unx * overlap / 2
        ball1.y -= uny * overlap / 2
        ball2.x += unx * overlap / 2
        ball2.y += uny * overlap / 2
        
        # Tangent vector (perpendicular to normal)
        utx = -uny
        uty = unx
        
        # Project velocities onto the normal and tangent axes
        v1n = ball1.vx * unx + ball1.vy * uny
        v1t = ball1.vx * utx + ball1.vy * uty
        v2n = ball2.vx * unx + ball2.vy * uny
        v2t = ball2.vx * utx + ball2.vy * uty
        
        # Calculate new normal velocities (standard 1D elastic collision)
        # Since masses are equal, they just swap normal velocities
        v1n_prime = v2n
        v2n_prime = v1n
        
        # Convert scalar normal/tangent velocities back to 2D velocity vectors
        ball1.vx = v1n_prime * unx + v1t * utx
        ball1.vy = v1n_prime * uny + v1t * uty
        ball2.vx = v2n_prime * unx + v2t * utx
        ball2.vy = v2n_prime * uny + v2t * uty

# --- Setup ---
def setup_balls():
    """Places balls in their initial positions (rack)."""
    cue_ball = Ball(100, HEIGHT // 2, WHITE)
    
    # Setup the rack (a simple triangle of 5 balls)
    balls = [cue_ball]
    
    # Starting position of the apex ball
    base_x = WIDTH - 200
    base_y = HEIGHT // 2
    
    # Create the rack of colored balls
    color_options = [(255, 0, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]
    
    for row in range(4):
        y_start = base_y - row * (BALL_RADIUS + 1)
        for col in range(row + 1):
            x = base_x + row * (BALL_RADIUS * 2 + 2)
            y = y_start + col * (BALL_RADIUS * 2 + 2)
            
            # Use random colors for variety
            color = random.choice(color_options) 
            balls.append(Ball(x, y, color))
    
    return pygame.sprite.Group(balls), cue_ball

all_balls, cue_ball = setup_balls()
game_state = {'shooting': False, 'mouse_pos': (0, 0)}

# --- Drawing Functions ---

def draw_table():
    """Draws the green felt and the wooden border."""
    screen.fill(WALL_COLOR)
    pygame.draw.rect(screen, TABLE_COLOR, 
                     (TABLE_MARGIN, TABLE_MARGIN, PLAYABLE_WIDTH, PLAYABLE_HEIGHT))
    
def draw_cue_aim():
    """Draws the aiming line and power indicator when shooting."""
    if game_state['shooting']:
        mx, my = game_state['mouse_pos']
        cbx, cby = cue_ball.x, cue_ball.y
        
        # Draw the line from the cue ball to the mouse position
        pygame.draw.line(screen, WHITE, (cbx, cby), (mx, my), 3)
        
        # Calculate shot distance (power)
        distance = math.hypot(mx - cbx, my - cby)
        power = min(distance * CUE_POWER_SCALE, 30) # Max power 30
        
        # Draw a power indicator behind the ball
        angle = math.atan2(my - cby, mx - cbx)
        
        # Line pointing away from the mouse
        end_x = cbx - math.cos(angle) * power * 3
        end_y = cby - math.sin(angle) * power * 3
        
        pygame.draw.line(screen, RED, (cbx, cby), (end_x, end_y), 5)


# --- Main Game Loop ---
running = True
while running:
    # --- 1. Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle Mouse Input
        if cue_ball.vx == 0 and cue_ball.vy == 0: # Only allow shot if cue ball is stopped
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click to start aiming
                    game_state['shooting'] = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and game_state['shooting']: # Left click release to shoot
                    game_state['shooting'] = False
                    
                    mx, my = pygame.mouse.get_pos()
                    
                    # Calculate velocity based on mouse distance from cue ball
                    dx = cue_ball.x - mx
                    dy = cue_ball.y - my
                    
                    # Scale velocity by the constant power scale (max speed 30)
                    speed = min(math.hypot(dx, dy) * CUE_POWER_SCALE, 30)
                    
                    # Apply velocity
                    cue_ball.vx = speed * (dx / math.hypot(dx, dy))
                    cue_ball.vy = speed * (dy / math.hypot(dx, dy))

    # Update mouse position for aiming
    game_state['mouse_pos'] = pygame.mouse.get_pos()


    # --- 2. Update Physics ---
    all_balls.update()  # Runs movement and friction

    # Collision checks
    for i, ball1 in enumerate(all_balls):
        check_wall_collision(ball1) # Check table boundaries
        
        # Check against all other balls (only checking pairs once)
        for j, ball2 in enumerate(all_balls):
            if i < j: # Ensures we check each pair once (i.e., (1, 2) but not (2, 1) or (1, 1))
                resolve_ball_collision(ball1, ball2)


    # --- 3. Drawing ---
    draw_table()
    draw_cue_aim()

    for ball in all_balls:
        ball.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()