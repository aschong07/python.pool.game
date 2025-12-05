#imports
import pygame
import math
import random

#pygame is intiated
pygame.init()
pygame.mixer.init()

#Visuals:

#basic settings
WIDTH, HEIGHT = 900, 500 # window size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Pool Game_ECE160") #title of game
clock = pygame.time.Clock() #creates a clocked controled by FPS
FPS = 60

#colors
table_boarder = (50, 50, 50) #sets the boarder
#color of the balls
table_color = (0, 100, 200) # Blue table
green = (0, 128, 0)
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
purple = (128, 0, 128)
orange = (255, 165, 0)
maroon = (128, 0, 0)
gray = (128, 128, 128)
light_blue = (173, 216, 230)  # for prediction lines

#constants
ball_radius = 20 #balls radius
friction = 0.99 #slows down the ball
cue_power_multiplier = 0.12 #controls the strength of the shots
min_speed = 0.01 #stops the ball completely

#table boundaries
left_bound = 70
right_bound = WIDTH - 70 
top_bound = 50 
BOTTOM_BOUND = HEIGHT - 50

#pockets 
pocket_radius = 60
POCKETS = [
    #3 pockets on top
    (left_bound, top_bound),
    ((left_bound + right_bound) // 2, top_bound),
    (right_bound, top_bound),
    #3 pockets on bottom
    (left_bound, BOTTOM_BOUND),
    ((left_bound + right_bound) // 2, BOTTOM_BOUND),
    (right_bound, BOTTOM_BOUND)
]

#confetti class for winner
class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        #random horizontal speed
        self.vx = random.uniform(-2, 2)
        #randome falling speed
        self.vy = random.uniform(1, 4)
        #random colors
        self.color = random.choice([
            (255, 0, 0),    # Red
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 255, 255),  # Cyan
            (255, 0, 255),  # Magenta
            (255, 165, 0),  # Orange
            (128, 0, 128)   # Purple
        ])
        #random sizeing
        self.size = random.randint(3, 8)
        #random rotation
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        
    def update(self):
        #upate the velocity of the cofetti when falling down
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        #gravity
        self.vy += 0.1
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
    def is_offscreen(self):
        if self.y > HEIGHT + 20:
            return True
        return False

#th balls

#the ball itself 
class Ball: 
    def __init__(self, x, y, color, is_cue=False, is_striped=False):
        self.x = x         #Balls X Position
        self.y = y         #Balls Y Position
        self.vx = 0        #Velocity in X direction
        self.vy = 0        #Velocity in Y direction
        self.color = color  #Color of ball
        self.is_cue = is_cue #cue ball
        self.is_striped = is_striped #striped ball
        self.alive = True #still in game

#draws the balls
    def draw(self, screen):
        if self.is_striped:
            # Create a surface for the ball content (White ball + Colored Stripe)
            surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
            
            # 1. Draw white base circle
            pygame.draw.circle(surf, (255, 255, 255), (ball_radius, ball_radius), ball_radius)
            
            # 2. Draw colored stripe (rect)
            rect_height = ball_radius * 1.2
            rect = pygame.Rect(0, ball_radius - rect_height // 2, ball_radius * 2, rect_height)
            pygame.draw.rect(surf, self.color, rect)
            
            # 3. Create a mask surface to clip the corners of the rect
            mask = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255), (ball_radius, ball_radius), ball_radius)
            
            # 4. Apply mask using BLEND_RGBA_MULT
            # This keeps pixels where mask is white, and removes where mask is transparent
            surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            screen.blit(surf, (int(self.x) - ball_radius, int(self.y) - ball_radius))
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), ball_radius)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        
        # Wall collisions
        # Check left and right boundaries
        if self.x - ball_radius < left_bound:
            self.x = left_bound + ball_radius
            self.vx *= -1
        elif self.x + ball_radius > right_bound:
            self.x = right_bound - ball_radius
            self.vx *= -1
            
        # Check top and bottom boundaries
        if self.y - ball_radius < top_bound:
            self.y = top_bound + ball_radius
            self.vy *= -1
        elif self.y + ball_radius > BOTTOM_BOUND:
            self.y = BOTTOM_BOUND - ball_radius
            self.vy *= -1

        self.vx *= friction
        self.vy *= friction
        if abs(self.vx) < min_speed:
            self.vx = 0
        if abs(self.vy) < min_speed:
            self.vy = 0

#Cue
class Cue:
    def __init__(self, ball):
        self.ball = ball
        self.angle = 0
        self.power = 0
        # Animation state
        self.is_striking = False
        self.strike_progress = 0
        self.max_pullback = 200

    def update(self, mouse_pos):
        if not self.is_striking:
            dx = self.ball.x - mouse_pos[0]
            dy = self.ball.y - mouse_pos[1]
            self.angle = math.atan2(dy, dx)
            distance = math.hypot(dx, dy)
            self.power = min(distance, self.max_pullback) / self.max_pullback * 100
    
    def start_strike(self):
        if self.power > 5:
            self.is_striking = True
            self.strike_progress = 0
    
    def update_strike_animation(self):
        if self.is_striking:
            self.strike_progress += 0.15
            if self.strike_progress >= 1.0:
                self.is_striking = False
                self.strike_progress = 0
                return True
        return False
    
    def calculate_velocity(self):
        force = (self.power / 100) * 15
        vx = math.cos(self.angle) * force
        vy = math.sin(self.angle) * force
        return vx, vy

    def draw(self, screen):
        cue_angle = self.angle + math.pi
        
        if self.is_striking:
            max_offset = 25 + self.power
            min_offset = 10
            offset = max_offset - (max_offset - min_offset) * self.strike_progress
        else:
            offset = 25 + self.power
        
        length = 250
        start_x = self.ball.x + math.cos(cue_angle) * offset
        start_y = self.ball.y + math.sin(cue_angle) * offset
        end_x = start_x + math.cos(cue_angle) * length
        end_y = start_y + math.sin(cue_angle) * length
        
        pygame.draw.line(screen, (100, 50, 0), (start_x, start_y), (end_x, end_y), 8)
        pygame.draw.line(screen, (160, 82, 45), (start_x, start_y), (end_x, end_y), 4)
        
        tip_x = self.ball.x + math.cos(cue_angle) * (offset - 5)
        tip_y = self.ball.y + math.sin(cue_angle) * (offset - 5)
        pygame.draw.circle(screen, (255, 255, 255), (int(tip_x), int(tip_y)), 4)
        
        if not self.is_striking:
            aim_len = 100 + self.power * 3
            aim_end_x = self.ball.x + math.cos(self.angle) * aim_len
            aim_end_y = self.ball.y + math.sin(self.angle) * aim_len
            pygame.draw.line(screen, (255, 255, 255), (self.ball.x, self.ball.y), (aim_end_x, aim_end_y), 2)
            
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"Power: {int(self.power)}%", True, (255, 255, 255))
            screen.blit(text, (self.ball.x + 20, self.ball.y + 20))

    def draw_prediction(self, screen, balls):
        # simulate the actual shot using the game's physics and draw:
        # - a line from the real cue ball to the collision point (or stop point)
        # - a line from the struck object ball from collision to where it rolls to
        cue_ball = self.ball
        if not cue_ball.alive:
            return

        # ---Clone balls so we don't touch the real game sate ---
        sim_balls = []
        for b in balls:
            nb = Ball(b.x, b.y, b.color, b.is_cue, b.is_striped)
            nb.vx = b.vx
            nb.vy = b.vy
            nb.alive = b.alive
            sim_balls.append(nb)

        sim_cue = sim_balls[0]

        # same shot force as in the real game (human shot)
        force = (self.power / 100) * 15
        sim_cue.vx = math.cos(self.angle) * force
        sim_cue.vy = math.sin(self.angle) * force

        # real starting point (where to start the line from)
        real_start_x = cue_ball.x
        real_start_y = cue_ball.y

        collision_point = None
        obj_start_pos = None
        obj_final_pos = None
        hit_index = None

        max_steps = 250  # number of "frames" to simulate

        for _ in range(max_steps):
            # collision check (same as game, but on the sim copy)
            sim_collision_info = {
                "first_hit": None,
                "hit_pos": None,
                "hit_ball_index": None
            }
            check_collisions(sim_balls, cue_ball_in_hand=False, collision_info=sim_collision_info)

            # if we haven't recorded a collision yet, see if this frame has one
            if collision_point is None and sim_collision_info["hit_pos"] is not None:
                collision_point = sim_collision_info["hit_pos"]
                hit_index = sim_collision_info["hit_ball_index"]
                if hit_index is not None:
                    # object ball position at the moment of first contact
                    obj_start_pos = (sim_balls[hit_index].x, sim_balls[hit_index].y)

            # move all simulated balls (same physics as game)
            for sb in sim_balls:
                if sb.alive:
                    sb.move()

            # if we already know which object ball was hit, track its motion
            if hit_index is not None:
                obj_ball = sim_balls[hit_index]
                obj_final_pos = (obj_ball.x, obj_ball.y)

                # stop tracking when that ball basically stops or is pocketed
                if (abs(obj_ball.vx) < min_speed and abs(obj_ball.vy) < min_speed) or (not obj_ball.alive):
                    break
            else:
                # no collision yet: stop if cue ball basically stops
                if abs(sim_cue.vx) < min_speed and abs(sim_cue.vy) < min_speed:
                    break

        # --------- draw lines ---------

        # 1) cue ball path: from real cue ball to collision or stop point
        if collision_point is not None:
            cue_end_x, cue_end_y = collision_point
        else:
            cue_end_x, cue_end_y = sim_cue.x, sim_cue.y

        pygame.draw.line(
            screen,
            light_blue,
            (real_start_x, real_start_y),
            (cue_end_x, cue_end_y),
            2
        )

        # 2) object ball path (second segment)
        if obj_start_pos is not None and obj_final_pos is not None:
            pygame.draw.line(
                screen,
                light_blue,
                obj_start_pos,
                obj_final_pos,
                2
            )
def check_collisions(balls, cue_ball_in_hand=False, collision_info=None):
    for i in range(len(balls)):
        # If cue ball is in hand, skip checking it against other balls
        if cue_ball_in_hand and i == 0:
            continue
            
        for j in range(i + 1, len(balls)):
            b1 = balls[i]
            b2 = balls[j]
            
            if not b1.alive or not b2.alive:
                continue

            dx = b2.x - b1.x
            dy = b2.y - b1.y
            distance = math.hypot(dx, dy)

            if distance < ball_radius * 2:
                # Collision detected
                
                # track first ball hit by cue ball this turn
                if collision_info is not None and collision_info.get("first_hit") is None:
                    cue_ball = None
                    other = None
                    hit_index = None

                    if b1.is_cue and not cue_ball_in_hand:
                        cue_ball = b1
                        other = b2
                        hit_index = j
                    elif b2.is_cue and not cue_ball_in_hand:
                        cue_ball = b2
                        other = b1
                        hit_index = i

                    if cue_ball is not None and other is not None and other.alive:
                        # what type of ball was hit first?
                        if other.color == black:
                            collision_info["first_hit"] = "8ball"
                        elif other.is_striped:
                            collision_info["first_hit"] = "stripes"
                        else:
                            collision_info["first_hit"] = "solids"

                        # extra info for prediction line
                        collision_info["hit_pos"] = (cue_ball.x, cue_ball.y)
                        collision_info["hit_ball_index"] = hit_index
                
                # Resolve overlap
                overlap = ball_radius * 2 - distance
                angle = math.atan2(dy, dx)
                
                # Move balls apart
                b1.x -= math.cos(angle) * overlap / 2
                b1.y -= math.sin(angle) * overlap / 2
                b2.x += math.cos(angle) * overlap / 2
                b2.y += math.sin(angle) * overlap / 2
                
                # Resolve velocity (Elastic collision)
                # Normal vector
                nx = math.cos(angle)
                ny = math.sin(angle)
                
                # Tangent vector
                tx = -ny
                ty = nx
                
                # Dot product tangent
                dpTan1 = b1.vx * tx + b1.vy * ty
                dpTan2 = b2.vx * tx + b2.vy * ty
                
                # Dot product normal
                dpNorm1 = b1.vx * nx + b1.vy * ny
                dpNorm2 = b2.vx * nx + b2.vy * ny
                
                # Conservation of momentum in 1D
                m1 = (dpNorm1 * (1 - 1) + 2 * 1 * dpNorm2) / (1 + 1) # Mass is 1
                m2 = (dpNorm2 * (1 - 1) + 2 * 1 * dpNorm1) / (1 + 1)
                
                # Update velocities
                b1.vx = tx * dpTan1 + nx * m1
                b1.vy = ty * dpTan1 + ny * m1
                b2.vx = tx * dpTan2 + nx * m2
                b2.vy = ty * dpTan2 + ny * m2

def check_pockets(balls):
    potted_info = []
    for ball in balls:
        if not ball.alive:
            continue
            
        for pocket in POCKETS:
            px, py = pocket
            dist = math.hypot(ball.x - px, ball.y - py)
            
            if dist < pocket_radius:
                # Ball in pocket
                if ball.is_cue:
                    # Move cue ball off screen instead of resetting
                    ball.x = -1000
                    ball.y = -1000
                    ball.vx = 0
                    ball.vy = 0
                    potted_info.append("cue")
                else:
                    ball.alive = False
                    if ball.color == black:
                        potted_info.append("8ball")
                    elif ball.is_striped:
                        potted_info.append("stripe")
                    else:
                        potted_info.append("solid")
    return potted_info

def create_balls():
    balls = []
    # Cue ball
    balls.append(Ball(WIDTH//4, HEIGHT//2, white, is_cue=True))
    
    # 15 balls in triangle
    start_x = 3 * WIDTH // 4
    start_y = HEIGHT // 2
    rows = 5
    
    # Define the 14 object balls (excluding 8-ball)
    # 7 Solids and 7 Stripes
    # Colors: Yellow, Blue, Red, Purple, Orange, Green, Maroon
    colors = [yellow, blue, red, purple, orange, green, maroon]
    object_balls = []
    
    # Add solids
    for c in colors:
        object_balls.append({'color': c, 'striped': False})
    # Add stripes
    for c in colors:
        object_balls.append({'color': c, 'striped': True})
        
    # Simple shuffle by alternating or just using the list as is (it's mixed enough for now)
    # Or we can just pop from it.
    # Let's interleave them to mix solids and stripes
    mixed_balls = []
    for i in range(7):
        mixed_balls.append(object_balls[i]) # Solid
        mixed_balls.append(object_balls[i+7]) # Stripe
    
    # We need to assign them to positions.
    # Position (2, 1) is the 8-ball (Black, Solid).
    
    ball_idx = 0
    for col in range(rows):
        for row in range(col + 1):
            x = start_x + col * (ball_radius * 2 + 1)
            y = start_y - (col * ball_radius) + (row * (ball_radius * 2 + 1))
            
            if col == 2 and row == 1:
                # 8-Ball
                balls.append(Ball(x, y, black, is_striped=False))
            else:
                # Other balls
                props = mixed_balls[ball_idx]
                balls.append(Ball(x, y, props['color'], is_striped=props['striped']))
                ball_idx += 1
            
    return balls

# Menu and AI Helpers

class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_text(screen, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

def get_text_input(screen, prompt, font):
    input_text = ""
    active = True
    while active:
        screen.fill((30, 30, 30))
        draw_text(screen, prompt, font, (255, 255, 255), WIDTH//2, HEIGHT//2 - 50, center=True)
        
        # Draw input box
        input_box = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 40)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        
        text_surf = font.render(input_text, True, (255, 255, 255))
        screen.blit(text_surf, (input_box.x + 5, input_box.y + 5))
        
        draw_text(screen, "Press ENTER to confirm", font, (150, 150, 150), WIDTH//2, HEIGHT//2 + 60, center=True)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 15: # Limit length
                        input_text += event.unicode
    return input_text

def menu():
    font = pygame.font.SysFont(None, 40)
    title_font = pygame.font.SysFont(None, 60)
    
    # Buttons
    btn_ai = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "Play vs AI")
    btn_pvp = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Freeplay (PvP)")
    
    btn_easy = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "Easy")
    btn_hard = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Hard")
    
    state = "MAIN"
    
    while True:
        screen.fill((30, 30, 30))
        
        if state == "MAIN":
            draw_text(screen, "Pool Game", title_font, (255, 255, 255), WIDTH//2, 100, center=True)
            btn_ai.draw(screen, font)
            btn_pvp.draw(screen, font)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if btn_ai.is_clicked(event):
                    state = "AI_DIFF"
                if btn_pvp.is_clicked(event):
                    p1 = get_text_input(screen, "Enter Player 1 Name:", font)
                    if p1 is None: return None
                    p2 = get_text_input(screen, "Enter Player 2 Name:", font)
                    if p2 is None: return None
                    return {"mode": "pvp", "p1": p1 or "Player 1", "p2": p2 or "Player 2"}
                    
        elif state == "AI_DIFF":
            draw_text(screen, "Select Difficulty", title_font, (255, 255, 255), WIDTH//2, 100, center=True)
            btn_easy.draw(screen, font)
            btn_hard.draw(screen, font)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if btn_easy.is_clicked(event):
                    return {"mode": "ai", "difficulty": "easy", "p1": "You", "p2": "Easy AI"}
                if btn_hard.is_clicked(event):
                    return {"mode": "ai", "difficulty": "hard", "p1": "You", "p2": "Hard AI"}
        
        pygame.display.flip()

def get_ai_shot(balls, difficulty, my_group):
    cue_ball = balls[0]
    
    # Filter targets based on group
    valid_targets = []
    for b in balls[1:]:
        if not b.alive: continue
        
        is_8ball = (b.color == black)
        if is_8ball:
            # Only target 8-ball if group is cleared (or if open table and no other choice? No, 8-ball is last)
            # For simplicity, AI only targets 8-ball if it's the only thing left for them
            # But we need to know if group is cleared.
            # Let's count remaining balls for my_group
            pass
        else:
            is_stripe = b.is_striped
            if my_group == "solids" and not is_stripe:
                valid_targets.append(b)
            elif my_group == "stripes" and is_stripe:
                valid_targets.append(b)
            elif my_group is None: # Open table
                valid_targets.append(b)
    
    # If no valid targets found (group cleared), target 8-ball
    if not valid_targets:
        for b in balls[1:]:
            if b.alive and b.color == black:
                valid_targets.append(b)
                break
    
    if not valid_targets:
        return 0, 0

    target = random.choice(valid_targets)
    dx = target.x - cue_ball.x
    dy = target.y - cue_ball.y
    angle = math.atan2(dy, dx)
    
    if difficulty == 'easy':
        angle += random.uniform(-0.3, 0.3) # Significant error
        power = random.uniform(30, 70)
    else: # Hard
        # Try to find a pocket for this target
        best_pocket = None
        min_dist = float('inf')
        for pocket in POCKETS:
            d = math.hypot(target.x - pocket[0], target.y - pocket[1])
            if d < min_dist:
                min_dist = d
                best_pocket = pocket
        
        if best_pocket:
            # Calculate ghost ball position
            px, py = best_pocket
            dx_tp = px - target.x
            dy_tp = py - target.y
            angle_tp = math.atan2(dy_tp, dx_tp)
            
            aim_x = target.x - math.cos(angle_tp) * (ball_radius * 2)
            aim_y = target.y - math.sin(angle_tp) * (ball_radius * 2)
            
            dx_ca = aim_x - cue_ball.x
            dy_ca = aim_y - cue_ball.y
            angle = math.atan2(dy_ca, dx_ca)
            power = random.uniform(70, 100)
        else:
            power = random.uniform(50, 90)

    return angle, power

def ai_place_ball(balls):
    while True:
        x = random.randint(left_bound + ball_radius, right_bound - ball_radius)
        y = random.randint(top_bound + ball_radius, BOTTOM_BOUND - ball_radius)
        valid = True
        for ball in balls[1:]:
            if ball.alive:
                dist = math.hypot(x - ball.x, y - ball.y)
                if dist < ball_radius * 2:
                    valid = False
                    break
        if valid:
            balls[0].x = x
            balls[0].y = y
            balls[0].vx = 0
            balls[0].vy = 0
            return

def check_win_condition(balls, player_group):
    
    if player_group is None:
        return False  # Can't win without an assigned group
    
    # Check if 8-ball (last ball in list) is pocketed
    eight_ball = balls[-1]  # 8-ball is the last ball created
    if eight_ball.alive:
        return False  # 8-ball must be pocketed to win
    
    # Check if all player's balls are pocketed
    for i, ball in enumerate(balls):
        if i == 0:  # Skip cue ball
            continue
        if i == len(balls) - 1:  # Skip 8-ball (already checked)
            continue
            
        # Check if this is one of the player's balls
        if player_group == "solids" and not ball.is_striped:
            if ball.alive:
                return False  # Player still has solid balls on table
        elif player_group == "stripes" and ball.is_striped:
            if ball.alive:
                return False  # Player still has striped balls on table
    
    return True  # All conditions met!

def show_lose_screen(screen, loser_name):
    # display lose screen for the player who lost
    
    clock = pygame.time.Clock()
    
    # lose screen loop
    showing_lose_screen = True
    
    while showing_lose_screen:
        clock.tick(FPS)
        
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return "MENU"  # return to menu on esc or enter
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "MENU"  # click to return to menu
        
        # draw background (semi-transparent overlay)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # draw "you lose!" message
        lose_font = pygame.font.SysFont(None, 120)
        lose_text = lose_font.render("YOU LOSE!", True, (220, 20, 60))  # crimson color
        lose_rect = lose_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        
        # draw shadow for text
        shadow_text = lose_font.render("YOU LOSE!", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 3 + 5))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(lose_text, lose_rect)
        
        # draw loser name
        name_font = pygame.font.SysFont(None, 60)
        name_text = name_font.render(f"{loser_name} lost!", True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(name_text, name_rect)
        
        # draw instruction text
        instruction_font = pygame.font.SysFont(None, 36)
        instruction_text = instruction_font.render("Click or press ENTER to return to menu", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.update()
    
    return "MENU"

def show_win_screen(screen, winner_name, confetti_particles):
    # Display the win screen with confetti animation
    
    clock = pygame.time.Clock()
    
    # Try to load/play victory sound (optional)
    try:
        # Uncomment if you have a victory sound file
        # victory_sound = pygame.mixer.Sound("victory.wav")
        # victory_sound.play()
        pass
    except:
        pass  # No sound file, continue without audio
    
    # Create initial burst of confetti
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(-100, 0)  # Start above screen
        confetti_particles.append(Confetti(x, y))
    
    # Win screen loop
    showing_win_screen = True
    win_timer = 0
    
    while showing_win_screen:
        clock.tick(FPS)
        win_timer += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return "MENU"  # Return to menu on ESC or Enter
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "MENU"  # Click to return to menu
        
        # Draw background (semi-transparent overlay)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Update and draw confetti
        for confetti in confetti_particles[:]:
            confetti.update()
            confetti.draw(screen)
            if confetti.is_offscreen():
                confetti_particles.remove(confetti)
        
        # Add new confetti periodically
        if win_timer % 10 == 0 and len(confetti_particles) < 150:
            x = random.randint(0, WIDTH)
            confetti_particles.append(Confetti(x, -10))
        
        # Draw "YOU WIN!" message
        win_font = pygame.font.SysFont(None, 120)
        win_text = win_font.render("YOU WIN!", True, (255, 215, 0))  # Gold color
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        
        # Draw shadow for text
        shadow_text = win_font.render("YOU WIN!", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 3 + 5))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(win_text, win_rect)
        
        # Draw winner name
        name_font = pygame.font.SysFont(None, 60)
        name_text = name_font.render(f"{winner_name} win!", True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(name_text, name_rect)
        
        # Draw instruction text
        instruction_font = pygame.font.SysFont(None, 36)
        instruction_text = instruction_font.render("Click or press ENTER to return to menu", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.update()
    
    return "MENU"

# Main Game Loop
def run_game(config):
    balls = create_balls()
    cue = Cue(balls[0]) # Attach cue to the cue ball (first in list)
    
    # Game State
    player_turn = 1 # 1 or 2
    shot_in_progress = False
    cue_ball_in_hand = False
    
    # Group Assignments
    p1_group = None # "solids" or "stripes"
    
    # Score tracking
    p1_score = 0
    p2_score = 0
    
    # Power bar
    power_bar_rect = pygame.Rect(20, HEIGHT - 40, 200, 20)
    dragging_power = False
    
    # Win screen state
    confetti_particles = []  # List to hold confetti objects
    
    # Font for text
    font = pygame.font.SysFont(None, 36)
    
    # Buttons
    btn_menu = Button(10, 5, 100, 40, "Menu")
    btn_quit = Button(120, 5, 100, 40, "Quit")
    
    # AI Timer
    ai_timer = 0
    
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(table_boarder) # Background
        
        # Draw table (blue rect)
        pygame.draw.rect(screen, table_color, (left_bound, top_bound, right_bound - left_bound, BOTTOM_BOUND - top_bound))
        
        # Draw pockets
        for pocket in POCKETS:
            pygame.draw.circle(screen, black, pocket, pocket_radius)
            
        # Determine current player name
        current_player_name = config["p1"] if player_turn == 1 else config["p2"]
        is_ai_turn = (config["mode"] == "ai" and player_turn == 2)
        
        # Determine Group Text
        group_text = ""
        if p1_group:
            if player_turn == 1:
                group_text = f" ({p1_group.capitalize()})"
            else:
                p2_group = "stripes" if p1_group == "solids" else "solids"
                group_text = f" ({p2_group.capitalize()})"
        
        # Draw Player Turn
        if current_player_name == "You":
            turn_text = f"Your Turn{group_text}"
        else:
            turn_text = f"{current_player_name}'s Turn{group_text}"

        if cue_ball_in_hand:
            turn_text += " (Place Cue Ball)"
        text = font.render(turn_text, True, white)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

        # Show Groups if assigned
        if p1_group:
            p2_group = "stripes" if p1_group == "solids" else "solids"
            group_msg = f"{config['p1']}: {p1_group.capitalize()}  |  {config['p2']}: {p2_group.capitalize()}"
            group_surf = pygame.font.SysFont(None, 24).render(group_msg, True, (200, 200, 200))
            screen.blit(group_surf, (WIDTH // 2 - group_surf.get_width() // 2, 40))
        
        # Scoreboard
        score_text = f"{config['p1']}: {p1_score}  |  {config['p2']}: {p2_score}"
        score_img = font.render(score_text, True, white)
        screen.blit(score_img, (WIDTH // 2 - score_img.get_width() // 2, 45))

        # Draw Buttons
        btn_menu.draw(screen, font)
        btn_quit.draw(screen, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if btn_menu.is_clicked(event):
                return "MENU"
            if btn_quit.is_clicked(event):
                return "QUIT"
            
            if not is_ai_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Prevent shooting if clicking buttons
                    if btn_menu.rect.collidepoint(event.pos) or btn_quit.rect.collidepoint(event.pos):
                        continue
                    
                    # Power bar dragging
                    if event.button == 1:
                        if power_bar_rect.collidepoint(event.pos):
                            dragging_power = True
                            mouse_x = event.pos[0]
                            cue.power = max(10, min(100, (mouse_x - 20) / 2))

                    if cue_ball_in_hand:
                        # Try to place ball
                        # Check if valid placement (not colliding with others)
                        can_place = True
                        # Check collision with other balls
                        for ball in balls[1:]: # Skip cue ball
                            if ball.alive:
                                dist = math.hypot(balls[0].x - ball.x, balls[0].y - ball.y)
                                if dist < ball_radius * 2:
                                    can_place = False
                                    break
                        if can_place:
                            cue_ball_in_hand = False
                            balls[0].vx = 0
                            balls[0].vy = 0
                    elif balls[0].vx == 0 and balls[0].vy == 0 and not shot_in_progress:
                        # Start strike animation
                        cue.start_strike()
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging_power = False
                
                if event.type == pygame.MOUSEMOTION:
                    if dragging_power:
                        mouse_x = event.pos[0]
                        cue.power = max(10, min(100, (mouse_x - 20) / 2))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # AI Logic
        if is_ai_turn and not shot_in_progress:
            # Check if balls are stopped
            all_stopped = True
            for ball in balls:
                if ball.alive and (abs(ball.vx) > 0 or abs(ball.vy) > 0):
                    all_stopped = False
                    break
            
            if all_stopped:
                if cue_ball_in_hand:
                    ai_place_ball(balls)
                    cue_ball_in_hand = False
                else:
                    ai_timer += 1
                    if ai_timer > 60: # Wait 1 second
                        # Determine AI Group
                        ai_group = None
                        if p1_group:
                            ai_group = "stripes" if p1_group == "solids" else "solids"
                            
                        angle, power = get_ai_shot(balls, config["difficulty"], ai_group)
                        balls[0].vx = math.cos(angle) * (power * cue_power_multiplier)
                        balls[0].vy = math.sin(angle) * (power * cue_power_multiplier)
                        shot_in_progress = True
                        potted_this_turn = []
                        ai_timer = 0
        
        if cue_ball_in_hand and not is_ai_turn:
            # Move cue ball with mouse
            balls[0].x = max(left_bound + ball_radius, min(mouse_pos[0], right_bound - ball_radius))
            balls[0].y = max(top_bound + ball_radius, min(mouse_pos[1], BOTTOM_BOUND - ball_radius))
            balls[0].vx = 0
            balls[0].vy = 0
        
        # Physics Updates
        check_collisions(balls, cue_ball_in_hand)
        
        if not cue_ball_in_hand:
            potted = check_pockets(balls)
            if shot_in_progress:
                potted_this_turn.extend(potted)
        
        # Check if all balls stopped
        all_stopped = True
        for ball in balls:
            if ball.alive and (abs(ball.vx) > 0 or abs(ball.vy) > 0):
                all_stopped = False
                break
        
        if shot_in_progress and all_stopped:
            shot_in_progress = False
            # Turn Logic
            
            # Analyze potted balls
            potted_cue = "cue" in potted_this_turn
            potted_8ball = "8ball" in potted_this_turn
            potted_stripes = [x for x in potted_this_turn if x == "stripe"]
            potted_solids = [x for x in potted_this_turn if x == "solid"]
            
            # Assign Groups if Open Table
            if p1_group is None and not potted_cue and not potted_8ball:
                if potted_solids and not potted_stripes:
                    p1_group = "solids" if player_turn == 1 else "stripes"
                elif potted_stripes and not potted_solids:
                    p1_group = "stripes" if player_turn == 1 else "solids"
            
            # Scoring conditions
            for p in potted_this_turn:
                if p == "solid":
                    if player_turn == 1:
                        p1_score += 1
                    else:
                        p2_score += 1
                
                if p == "stripe":
                    if player_turn == 1:
                        p1_score += 1
                    else:
                        p2_score += 1
            
            # Determine if turn should switch
            switch_turn = True
            
            if potted_cue:
                switch_turn = True
                cue_ball_in_hand = True
                balls[0].alive = True
            elif potted_8ball:
                # check if cue ball and 8-ball were potted together - automatic loss
                if potted_cue:
                    loser_name = config["p1"] if player_turn == 1 else config["p2"]
                    winner = 3 - player_turn
                    winner_name = config["p1"] if winner == 1 else config["p2"]
                    
                    # Show brief game over message
                    screen.fill(table_boarder)
                    draw_text(screen, f"{loser_name} potted the cue ball with the 8-ball!", font, red, WIDTH // 2, HEIGHT // 2 - 20, center=True)
                    draw_text(screen, f"{winner_name} wins!", font, yellow, WIDTH // 2, HEIGHT // 2 + 20, center=True)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    
                    result = show_lose_screen(screen, loser_name)
                    return result
                
                # Check if this is a legitimate win (all player's balls cleared)
                current_player_group = None
                if p1_group:
                    if player_turn == 1:
                        current_player_group = p1_group
                    else:
                        current_player_group = "stripes" if p1_group == "solids" else "solids"
                
                # check win condition
                if current_player_group and check_win_condition(balls, current_player_group):
                    # player wins!
                    winner_name = config["p1"] if player_turn == 1 else config["p2"]
                    
                    # show win screen for winner
                    result = show_win_screen(screen, winner_name, confetti_particles)
                    return result
                else:
                    # potted 8-ball too early - current player loses
                    loser_name = config["p1"] if player_turn == 1 else config["p2"]
                    winner = 3 - player_turn
                    winner_name = config["p1"] if winner == 1 else config["p2"]
                    
                    # Show brief game over message
                    screen.fill(table_boarder)
                    draw_text(screen, f"{loser_name} potted the 8-ball too early!", font, red, WIDTH // 2, HEIGHT // 2 - 20, center=True)
                    draw_text(screen, f"{winner_name} wins!", font, yellow, WIDTH // 2, HEIGHT // 2 + 20, center=True)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    
                    # show lose screen for the player who made the mistake
                    result = show_lose_screen(screen, loser_name)
                    return result
            else:
                # Check if current player potted their own ball
                my_group = None
                if p1_group:
                    if player_turn == 1: my_group = p1_group
                    else: my_group = "stripes" if p1_group == "solids" else "solids"
                
                if my_group == "solids":
                    if potted_solids: switch_turn = False
                elif my_group == "stripes":
                    if potted_stripes: switch_turn = False
                else: # Open Table
                    if potted_solids or potted_stripes: switch_turn = False
            
            if switch_turn:
                player_turn = 3 - player_turn
            
        # Update and Draw Balls
        for ball in balls:
            if ball.alive:
                ball.move()
                ball.draw(screen)
            
        # Update and Draw Cue if cue ball is stopped
        if balls[0].vx == 0 and balls[0].vy == 0 and balls[0].alive and not cue_ball_in_hand and not is_ai_turn and not shot_in_progress:
            cue.update(mouse_pos)
            cue.draw(screen)
        
        # Update strike animation
        if cue.is_striking:
            strike_complete = cue.update_strike_animation()
            cue.draw(screen)
            if strike_complete:
                vx, vy = cue.calculate_velocity()
                balls[0].vx = vx
                balls[0].vy = vy
                shot_in_progress = True
                potted_this_turn = []
        
        # Power bar
        pygame.draw.rect(screen, (200, 200, 200), power_bar_rect, 2)
        fill_width = int(2 * cue.power)
        pygame.draw.rect(screen, (255, 0, 0), (20, HEIGHT - 40, fill_width, 20))
        
        pygame.display.update()
    
    return "MENU"

def main():
    while True:
        config = menu()
        if config is None:
            break
        
        result = run_game(config)
        if result == "QUIT":
            break
            
    pygame.quit()

if __name__ == "__main__":
    main()
