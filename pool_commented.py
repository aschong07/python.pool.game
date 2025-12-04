# imports - bringing in necessary libraries
import pygame  # for game graphics and window management
import math  # for trigonometry calculations (angles, distances)
import random  # for randomizing ball placement and ai behavior

# pygame is initiated - start up pygame system
pygame.init()

# visuals:

# basic settings
WIDTH, HEIGHT = 900, 500  # window size in pixels (width x height)
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # create game window
pygame.display.set_caption("2D Pool Game_ECE160")  # title of game window
clock = pygame.time.Clock()  # creates a clock controlled by fps
FPS = 60  # frames per second - how fast game updates

# colors - rgb tuples for different colors
table_boarder = (50, 50, 50)  # sets the boarder color (dark gray)
# color of the balls
table_color = (0, 100, 200)  # blue table surface
green = (0, 128, 0)  # green color
white = (255, 255, 255)  # white color for cue ball
red = (255, 0, 0)  # red ball color
yellow = (255, 255, 0)  # yellow ball color
blue = (0, 0, 255)  # blue ball color
black = (0, 0, 0)  # black color for 8-ball
purple = (128, 0, 128)  # purple ball color
orange = (255, 165, 0)  # orange ball color
maroon = (128, 0, 0)  # maroon ball color
gray = (128, 128, 128)  # gray color

# constants - fixed values used throughout game
ball_radius = 20  # balls radius in pixels
friction = 0.99  # slows down the ball each frame (0.99 = 1% speed loss)
cue_power_multiplier = 0.12  # controls the strength of the shots
min_speed = 0.01  # stops the ball completely when below this speed

# table boundaries - where balls can and can't go
left_bound = 70  # left edge of playable area
right_bound = WIDTH - 70  # right edge of playable area
top_bound = 50  # top edge of playable area
BOTTOM_BOUND = HEIGHT - 50  # bottom edge of playable area

# pockets - locations where balls can be potted
pocket_radius = 30  # how big each pocket is
POCKETS = [  # list of all pocket positions (x, y)
    # 3 pockets on top row
    (left_bound, top_bound),  # top left corner
    ((left_bound + right_bound) // 2, top_bound),  # top middle
    (right_bound, top_bound),  # top right corner
    # 3 pockets on bottom row
    (left_bound, BOTTOM_BOUND),  # bottom left corner
    ((left_bound + right_bound) // 2, BOTTOM_BOUND),  # bottom middle
    (right_bound, BOTTOM_BOUND)  # bottom right corner
]

# confetti particle class for win screen celebration
class Confetti:
    def __init__(self, x, y):  # constructor - creates a new confetti piece
        self.x = x  # horizontal position on screen
        self.y = y  # vertical position on screen
        # random horizontal velocity - makes confetti drift left or right
        self.vx = random.uniform(-2, 2)  # random speed between -2 and 2
        # random falling speed - how fast it falls
        self.vy = random.uniform(1, 4)  # random speed between 1 and 4
        # random color for variety - picks one of these colors
        self.color = random.choice([
            (255, 0, 0),    # red
            (255, 255, 0),  # yellow
            (0, 255, 0),    # green
            (0, 255, 255),  # cyan
            (255, 0, 255),  # magenta
            (255, 165, 0),  # orange
            (128, 0, 128)   # purple
        ])
        # random size - makes confetti pieces different sizes
        self.size = random.randint(3, 8)  # between 3 and 8 pixels
        # random rotation for visual variety - starting angle
        self.rotation = random.uniform(0, 360)  # degrees
        self.rotation_speed = random.uniform(-5, 5)  # how fast it spins
        
    def update(self):  # update confetti position and rotation each frame
        """update confetti position and rotation"""
        self.x += self.vx  # move horizontally
        self.y += self.vy  # move vertically (fall down)
        self.rotation += self.rotation_speed  # spin the confetti
        # add slight gravity - makes confetti accelerate downward
        self.vy += 0.1  # increase falling speed each frame
        
    def draw(self, screen):  # draw the confetti piece on screen
        """draw the confetti piece"""
        # draw as a small circle for confetti effect
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
    def is_offscreen(self):  # check if confetti has fallen off screen
        """check if confetti has fallen off screen"""
        return self.y > HEIGHT + 20  # if below screen plus 20 pixel buffer

# the balls

# the ball itself - represents one pool ball
class Ball: 
    def __init__(self, x, y, color, is_cue=False, is_striped=False):  # creates a new ball
        self.x = x  # balls x position on table
        self.y = y  # balls y position on table
        self.vx = 0  # velocity in x direction (horizontal speed)
        self.vy = 0  # velocity in y direction (vertical speed)
        self.color = color  # color of ball (rgb tuple)
        self.is_cue = is_cue  # true if this is the cue ball (white)
        self.is_striped = is_striped  # true if this is a striped ball
        self.alive = True  # true if still in game (not potted)

    def draw(self, screen):  # draws the ball on the screen
        if self.is_striped:  # if this is a striped ball
            # create a surface for the ball content (white ball + colored stripe)
            surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)  # transparent surface
            
            # 1. draw white base circle - the background of striped ball
            pygame.draw.circle(surf, (255, 255, 255), (ball_radius, ball_radius), ball_radius)
            
            # 2. draw colored stripe (rect) - horizontal stripe across middle
            rect_height = ball_radius * 1.2  # stripe is slightly taller than radius
            rect = pygame.Rect(0, ball_radius - rect_height // 2, ball_radius * 2, rect_height)  # centered stripe
            pygame.draw.rect(surf, self.color, rect)  # draw the colored stripe
            
            # 3. create a mask surface to clip the corners of the rect
            mask = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)  # transparent mask
            pygame.draw.circle(mask, (255, 255, 255), (ball_radius, ball_radius), ball_radius)  # circular mask
            
            # 4. apply mask using blend_rgba_mult
            # this keeps pixels where mask is white, and removes where mask is transparent
            surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # blend mask with ball
            
            screen.blit(surf, (int(self.x) - ball_radius, int(self.y) - ball_radius))  # draw to screen
        else:  # solid colored ball
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), ball_radius)  # draw solid circle

    def move(self):  # updates ball position based on velocity
        self.x += self.vx  # move horizontally by velocity
        self.y += self.vy  # move vertically by velocity
        
        # wall collisions - bounce off edges of table
        # check left and right boundaries
        if self.x - ball_radius < left_bound:  # if ball hits left wall
            self.x = left_bound + ball_radius  # push ball back inside
            self.vx *= -1  # reverse horizontal velocity (bounce)
        elif self.x + ball_radius > right_bound:  # if ball hits right wall
            self.x = right_bound - ball_radius  # push ball back inside
            self.vx *= -1  # reverse horizontal velocity (bounce)
            
        # check top and bottom boundaries
        if self.y - ball_radius < top_bound:  # if ball hits top wall
            self.y = top_bound + ball_radius  # push ball back inside
            self.vy *= -1  # reverse vertical velocity (bounce)
        elif self.y + ball_radius > BOTTOM_BOUND:  # if ball hits bottom wall
            self.y = BOTTOM_BOUND - ball_radius  # push ball back inside
            self.vy *= -1  # reverse vertical velocity (bounce)

        self.vx *= friction  # apply friction to horizontal velocity (slow down)
        self.vy *= friction  # apply friction to vertical velocity (slow down)
        if abs(self.vx) < min_speed:  # if moving very slowly horizontally
            self.vx = 0  # stop completely
        if abs(self.vy) < min_speed:  # if moving very slowly vertically
            self.vy = 0  # stop completely

# cue - the pool stick for aiming and shooting
class Cue:
    def __init__(self, ball):  # creates cue stick attached to a ball
        self.ball = ball  # reference to the cue ball
        self.angle = 0  # direction cue is pointing (radians)
        self.power = 0  # how hard the shot will be (0-100)
        # animation state for strike animation
        self.is_striking = False  # true when animating forward strike
        self.strike_progress = 0  # 0 to 1, tracks animation progress
        self.max_pullback = 200  # maximum distance in pixels for pullback

    def update(self, mouse_pos):  # updates cue angle and power based on mouse
        if not self.is_striking:  # only update if not currently striking
            dx = self.ball.x - mouse_pos[0]  # horizontal distance from ball to mouse
            dy = self.ball.y - mouse_pos[1]  # vertical distance from ball to mouse
            self.angle = math.atan2(dy, dx)  # calculate angle from ball to mouse
            distance = math.hypot(dx, dy)  # calculate straight-line distance
            self.power = min(distance, self.max_pullback) / self.max_pullback * 100  # convert distance to power (0-100)
    
    def start_strike(self):  # initiates the forward strike animation
        if self.power > 5:  # only strike if power is above minimum
            self.is_striking = True  # start the strike animation
            self.strike_progress = 0  # reset animation progress
    
    def update_strike_animation(self):  # updates the strike animation each frame
        if self.is_striking:  # if currently animating a strike
            self.strike_progress += 0.15  # advance animation (0.15 per frame = ~7 frames total)
            if self.strike_progress >= 1.0:  # if animation complete
                self.is_striking = False  # stop animation
                self.strike_progress = 0  # reset progress
                return True  # signal that strike is complete
        return False  # animation not complete
    
    def calculate_velocity(self):  # calculates ball velocity based on current power
        force = (self.power / 100) * 15  # convert power percentage to force value
        vx = math.cos(self.angle) * force  # horizontal component of velociy
        vy = math.sin(self.angle) * force  # vertical component of velocity
        return vx, vy  # return both components

    def draw(self, screen):  # draws the cue stick on screen
        cue_angle = self.angle + math.pi  # reverse angle (cue goes opposite direction)
        
        if self.is_striking:  # if animating forward strike
            max_offset = 25 + self.power  # starting distance (pulled back)
            min_offset = 10  # ending distance (close to ball)
            offset = max_offset - (max_offset - min_offset) * self.strike_progress  # interpolate offset
        else:  # normal aiming mode
            offset = 25 + self.power  # distance from ball increases with power
        
        length = 250  # total length of cue stick in pixels
        start_x = self.ball.x + math.cos(cue_angle) * offset  # start of cue (near ball)
        start_y = self.ball.y + math.sin(cue_angle) * offset  # start y position
        end_x = start_x + math.cos(cue_angle) * length  # end of cue (far from ball)
        end_y = start_y + math.sin(cue_angle) * length  # end y position
        
        pygame.draw.line(screen, (100, 50, 0), (start_x, start_y), (end_x, end_y), 8)  # dark brown outline
        pygame.draw.line(screen, (160, 82, 45), (start_x, start_y), (end_x, end_y), 4)  # lighter brown inner
        
        tip_x = self.ball.x + math.cos(cue_angle) * (offset - 5)  # white tip position
        tip_y = self.ball.y + math.sin(cue_angle) * (offset - 5)  # white tip y
        pygame.draw.circle(screen, (255, 255, 255), (int(tip_x), int(tip_y)), 4)  # white cue tip
        
        if not self.is_striking:  # only show aiming aids when not striking
            aim_len = 100 + self.power * 3  # aiming line length increases with power
            aim_end_x = self.ball.x + math.cos(self.angle) * aim_len  # end of aim line x
            aim_end_y = self.ball.y + math.sin(self.angle) * aim_len  # end of aim line y
            pygame.draw.line(screen, (255, 255, 255), (self.ball.x, self.ball.y), (aim_end_x, aim_end_y), 2)  # white aim line
            
            font = pygame.font.SysFont(None, 24)  # create font for power text
            text = font.render(f"Power: {int(self.power)}%", True, (255, 255, 255))  # render power percentage
            screen.blit(text, (self.ball.x + 20, self.ball.y + 20))  # draw power text near ball

    def draw_prediction(self, screen, balls):  # placeholder for trajectory prediction
        pass 

def check_collisions(balls, cue_ball_in_hand=False):  # checks for collisions between all balls
    for i in range(len(balls)):  # loop through each ball
        # if cue ball is in hand, skip checking it against other balls
        if cue_ball_in_hand and i == 0:  # cue ball is first in list
            continue  # skip to next ball
            
        for j in range(i + 1, len(balls)):  # check against all other balls
            b1 = balls[i]  # first ball in collision pair
            b2 = balls[j]  # second ball in collision pair
            
            if not b1.alive or not b2.alive:  # if either ball is potted
                continue  # skip collision check

            dx = b2.x - b1.x  # horizontal distance between ball centers
            dy = b2.y - b1.y  # vertical distance between ball centers
            distance = math.hypot(dx, dy)  # straight-line distance between centers

            if distance < ball_radius * 2:  # if balls are touching or overlapping
                # collision detected
                
                # resolve overlap - push balls apart
                overlap = ball_radius * 2 - distance  # how much balls overlap
                angle = math.atan2(dy, dx)  # angle of collision
                
                # move balls apart along collision angle
                b1.x -= math.cos(angle) * overlap / 2  # push first ball back half the overlap
                b1.y -= math.sin(angle) * overlap / 2  # push first ball back half the overlap
                b2.x += math.cos(angle) * overlap / 2  # push second ball forward half the overlap
                b2.y += math.sin(angle) * overlap / 2  # push second ball forward half the overlap
                
                # resolve velocity (elastic collision) - calculate new velocities
                # normal vector - perpendicular to collision surface
                nx = math.cos(angle)  # normal x component
                ny = math.sin(angle)  # normal y component
                
                # tangent vector - parallel to collision surface
                tx = -ny  # tangent x component (perpendicular to normal)
                ty = nx  # tangent y component
                
                # dot product tangent - project velocities onto tangent
                dpTan1 = b1.vx * tx + b1.vy * ty  # ball 1 tangent velocity
                dpTan2 = b2.vx * tx + b2.vy * ty  # ball 2 tangent velocity
                
                # dot product normal - project velocities onto normal
                dpNorm1 = b1.vx * nx + b1.vy * ny  # ball 1 normal velocity
                dpNorm2 = b2.vx * nx + b2.vy * ny  # ball 2 normal velocity
                
                # conservation of momentum in 1d - calculate new normal velocities
                m1 = (dpNorm1 * (1 - 1) + 2 * 1 * dpNorm2) / (1 + 1)  # mass is 1 for both balls
                m2 = (dpNorm2 * (1 - 1) + 2 * 1 * dpNorm1) / (1 + 1)  # swap velocities
                
                # update velocities - combine tangent (unchanged) and normal (swapped) components
                b1.vx = tx * dpTan1 + nx * m1  # new ball 1 x velocity
                b1.vy = ty * dpTan1 + ny * m1  # new ball 1 y velocity
                b2.vx = tx * dpTan2 + nx * m2  # new ball 2 x velocity
                b2.vy = ty * dpTan2 + ny * m2  # new ball 2 y velocity

def check_pockets(balls):  # checks if any balls have fallen into pockets
    potted_info = []  # list to store info about potted balls
    for ball in balls:  # check each ball
        if not ball.alive:  # if ball already potted
            continue  # skip to next ball
            
        for pocket in POCKETS:  # check each pocket
            px, py = pocket  # pocket x and y coordinates
            dist = math.hypot(ball.x - px, ball.y - py)  # distance from ball to pocket center
            
            if dist < pocket_radius:  # if ball is inside pocket
                # ball in pocket
                if ball.is_cue:  # if this is the cue ball
                    # move cue ball off screen instead of resetting
                    ball.x = -1000  # move far left off screen
                    ball.y = -1000  # move far up off screen
                    ball.vx = 0  # stop horizontal motion
                    ball.vy = 0  # stop vertical motion
                    potted_info.append("cue")  # record cue ball potted
                else:  # regular ball
                    ball.alive = False  # mark ball as potted
                    if ball.color == black:  # if 8-ball
                        potted_info.append("8ball")  # record 8-ball potted
                    elif ball.is_striped:  # if striped ball
                        potted_info.append("stripe")  # record stripe potted
                    else:  # solid ball
                        potted_info.append("solid")  # record solid potted
    return potted_info  # return list of what was potted

def create_balls():  # creates all 16 balls in starting positions
    balls = []  # empty list to hold all balls
    # cue ball - white ball at left side
    balls.append(Ball(WIDTH//4, HEIGHT//2, white, is_cue=True))  # add cue ball to list
    
    # 15 balls in triangle formation
    start_x = 3 * WIDTH // 4  # starting x position (right side)
    start_y = HEIGHT // 2  # starting y position (center)
    rows = 5  # triangle has 5 rows
    
    # define the 14 object balls (excluding 8-ball)
    # 7 solids and 7 stripes
    # colors: yellow, blue, red, purple, orange, green, maroon
    colors = [yellow, blue, red, purple, orange, green, maroon]  # list of ball colors
    object_balls = []  # list to hold ball definitions
    
    # add solids - one of each color
    for c in colors:  # for each color
        object_balls.append({'color': c, 'striped': False})  # add solid ball
    # add stripes - one of each color
    for c in colors:  # for each color
        object_balls.append({'color': c, 'striped': True})  # add striped ball
        
    # simple shuffle by alternating or just using the list as is (it's mixed enough for now)
    # or we can just pop from it.
    # let's interleave them to mix solids and stripes
    mixed_balls = []  # list to hold mixed ball order
    for i in range(7):  # for each color
        mixed_balls.append(object_balls[i])  # add solid
        mixed_balls.append(object_balls[i+7])  # add stripe
    
    # we need to assign them to positions.
    # position (2, 1) is the 8-ball (black, solid).
    
    ball_idx = 0  # index for mixed_balls list
    for col in range(rows):  # for each column in triangle
        for row in range(col + 1):  # for each row in this column
            x = start_x + col * (ball_radius * 2 + 1)  # calculate x position
            y = start_y - (col * ball_radius) + (row * (ball_radius * 2 + 1))  # calculate y position
            
            if col == 2 and row == 1:  # middle position in triangle
                # 8-ball goes in center
                balls.append(Ball(x, y, black, is_striped=False))  # add 8-ball
            else:  # all other positions
                # other balls
                props = mixed_balls[ball_idx]  # get ball properties
                balls.append(Ball(x, y, props['color'], is_striped=props['striped']))  # add ball
                ball_idx += 1  # move to next ball in list
            
    return balls  # return list of all balls

# menu and ai helpers

class Button:  # clickable button for menu
    def __init__(self, x, y, w, h, text, action=None):  # creates a new button
        self.rect = pygame.Rect(x, y, w, h)  # button rectangle (position and size)
        self.text = text  # text to display on button
        self.action = action  # function to call when clicked (unused)
        self.color = (100, 100, 100)  # normal button color (gray)
        self.hover_color = (150, 150, 150)  # color when mouse hovers over (lighter gray)

    def draw(self, screen, font):  # draws button on screen
        mouse_pos = pygame.mouse.get_pos()  # get current mouse position
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color  # use hover color if mouse over button
        pygame.draw.rect(screen, color, self.rect)  # draw filled rectangle
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)  # draw white border
        
        text_surf = font.render(self.text, True, (255, 255, 255))  # render text in white
        text_rect = text_surf.get_rect(center=self.rect.center)  # center text in button
        screen.blit(text_surf, text_rect)  # draw text on button

    def is_clicked(self, event):  # checks if button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if left mouse button clicked
            if self.rect.collidepoint(event.pos):  # if click was on this button
                return True  # button was clicked
        return False  # button not clicked

def draw_text(screen, text, font, color, x, y, center=False):  # draws text on screen
    img = font.render(text, True, color)  # render text with given color
    if center:  # if centering text
        rect = img.get_rect(center=(x, y))  # get rectangle centered at x, y
        screen.blit(img, rect)  # draw centered text
    else:  # not centering
        screen.blit(img, (x, y))  # draw text at x, y

def get_text_input(screen, prompt, font):  # gets text input from player
    input_text = ""  # string to store typed text
    active = True  # whether input is still active
    while active:  # loop until done
        screen.fill((30, 30, 30))  # fill screen with dark gray
        draw_text(screen, prompt, font, (255, 255, 255), WIDTH//2, HEIGHT//2 - 50, center=True)  # show prompt
        
        # draw input box
        input_box = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 40)  # create rectangle for input box
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)  # draw white border
        
        text_surf = font.render(input_text, True, (255, 255, 255))  # render typed text
        screen.blit(text_surf, (input_box.x + 5, input_box.y + 5))  # draw text in box
        
        draw_text(screen, "Press ENTER to confirm", font, (150, 150, 150), WIDTH//2, HEIGHT//2 + 60, center=True)  # show instruction
        
        pygame.display.flip()  # update display
        
        for event in pygame.event.get():  # check for events
            if event.type == pygame.QUIT:  # if closing window
                pygame.quit()  # quit pygame
                return None  # return none
            if event.type == pygame.KEYDOWN:  # if key pressed
                if event.key == pygame.K_RETURN:  # if enter pressed
                    active = False  # stop input loop
                elif event.key == pygame.K_BACKSPACE:  # if backspace pressed
                    input_text = input_text[:-1]  # remove last character
                else:  # other key
                    if len(input_text) < 15:  # limit length to 15 characters
                        input_text += event.unicode  # add character to text
    return input_text  # return the typed text

def menu():  # displays main menu and gets player choices
    font = pygame.font.SysFont(None, 40)  # create font for buttons
    title_font = pygame.font.SysFont(None, 60)  # create larger font for title
    
    # buttons for menu options
    btn_ai = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "Play vs AI")  # vs ai button
    btn_pvp = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Freeplay (PvP)")  # pvp button
    
    btn_easy = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "Easy")  # easy difficulty button
    btn_hard = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Hard")  # hard difficulty button
    
    state = "MAIN"  # current menu state
    
    while True:  # menu loop
        screen.fill((30, 30, 30))  # fill screen with dark gray
        
        if state == "MAIN":  # main menu screen
            draw_text(screen, "Pool Game", title_font, (255, 255, 255), WIDTH//2, 100, center=True)  # draw title
            btn_ai.draw(screen, font)  # draw ai button
            btn_pvp.draw(screen, font)  # draw pvp button
            
            for event in pygame.event.get():  # check for events
                if event.type == pygame.QUIT:  # if closing window
                    pygame.quit()  # quit pygame
                    return None  # return none
                if btn_ai.is_clicked(event):  # if ai button clicked
                    state = "AI_DIFF"  # go to difficulty selection
                if btn_pvp.is_clicked(event):  # if pvp button clicked
                    p1 = get_text_input(screen, "Enter Player 1 Name:", font)  # get player 1 name
                    if p1 is None: return None  # if cancelled, exit
                    p2 = get_text_input(screen, "Enter Player 2 Name:", font)  # get player 2 name
                    if p2 is None: return None  # if cancelled, exit
                    return {"mode": "pvp", "p1": p1 or "Player 1", "p2": p2 or "Player 2"}  # return pvp config
                    
        elif state == "AI_DIFF":  # difficulty selection screen
            draw_text(screen, "Select Difficulty", title_font, (255, 255, 255), WIDTH//2, 100, center=True)  # draw title
            btn_easy.draw(screen, font)  # draw easy button
            btn_hard.draw(screen, font)  # draw hard button
            
            for event in pygame.event.get():  # check for events
                if event.type == pygame.QUIT:  # if closing window
                    pygame.quit()  # quit pygame
                    return None  # return none
                if btn_easy.is_clicked(event):  # if easy clicked
                    return {"mode": "ai", "difficulty": "easy", "p1": "You", "p2": "Easy AI"}  # return easy config
                if btn_hard.is_clicked(event):  # if hard clicked
                    return {"mode": "ai", "difficulty": "hard", "p1": "You", "p2": "Hard AI"}  # return hard config
        
        pygame.display.flip()  # update display


#ai's shots

def get_ai_shot(balls, difficulty, my_group):  # calculates ai shot angle and power
    cue_ball = balls[0]  # get reference to cue ball
    
    # filter targets based on group - ai only aims at its assigned balls
    valid_targets = []  # list to hold balls ai can shoot at
    for b in balls[1:]:  # check each ball (skip cue ball)
        if not b.alive: continue  # skip potted balls
        
        is_8ball = (b.color == black)  # check if this is 8-ball
        if is_8ball:  # if 8-ball
            # only target 8-ball if group is cleared (or if open table and no other choice? no, 8-ball is last)
            # for simplicity, ai only targets 8-ball if it's the only thing left for them
            # but we need to know if group is cleared.
            # let's count remaining balls for my_group
            pass  # handled below
        else:  # regular ball
            is_stripe = b.is_striped  # check if striped
            if my_group == "solids" and not is_stripe:  # if ai has solids and this is solid
                valid_targets.append(b)  # add to targets
            elif my_group == "stripes" and is_stripe:  # if ai has stripes and this is stripe
                valid_targets.append(b)  # add to targets
            elif my_group is None:  # open table - no groups assigned yet
                valid_targets.append(b)  # add to targets
    
    # if no valid targets found (group cleared), target 8-ball
    if not valid_targets:  # if no balls left in group
        for b in balls[1:]:  # check each ball
            if b.alive and b.color == black:  # if 8-ball is alive
                valid_targets.append(b)  # add 8-ball as target
                break  # only one 8-ball
    
    if not valid_targets:  # if still no targets (shouldn't happen)
        return 0, 0  # return no shot

    target = random.choice(valid_targets)  # randomly pick one of valid targets
    dx = target.x - cue_ball.x  # horizontal distance to target
    dy = target.y - cue_ball.y  # vertical distance to target
    angle = math.atan2(dy, dx)  # angle from cue ball to target
    
    if difficulty == 'easy':  # easy ai - less accurate
        angle += random.uniform(-0.3, 0.3)  # add significant angle error
        power = random.uniform(30, 70)  # random moderate power
    else:  # hard ai - more accurate
        # try to find a pocket for this target - aims for best pocket
        best_pocket = None  # variable to hold best pocket
        min_dist = float('inf')  # start with infinite distance
        for pocket in POCKETS:  # check each pocket
            d = math.hypot(target.x - pocket[0], target.y - pocket[1])  # distance from target to pocket
            if d < min_dist:  # if this pocket is closer
                min_dist = d  # update minimum distance
                best_pocket = pocket  # update best pocket
        
        if best_pocket:  # if found a good pocket
            # calculate ghost ball position - where cue ball needs to hit target
            px, py = best_pocket  # pocket coordinates
            dx_tp = px - target.x  # horizontal distance target to pocket
            dy_tp = py - target.y  # vertical distance target to pocket
            angle_tp = math.atan2(dy_tp, dx_tp)  # angle from target to pocket
            
            aim_x = target.x - math.cos(angle_tp) * (ball_radius * 2)  # ghost ball x position
            aim_y = target.y - math.sin(angle_tp) * (ball_radius * 2)  # ghost ball y position
            
            dx_ca = aim_x - cue_ball.x  # horizontal distance cue to ghost
            dy_ca = aim_y - cue_ball.y  # vertical distance cue to ghost
            angle = math.atan2(dy_ca, dx_ca)  # angle to shoot
            power = random.uniform(70, 100)  # high power
        else:  # no good pocket found
            power = random.uniform(50, 90)  # moderate power

    return angle, power  # return calculated angle and power

def ai_place_ball(balls):  # places cue ball after foul (ai logic)
    while True:  # keep trying until valid placement found
        x = random.randint(left_bound + ball_radius, right_bound - ball_radius)  # random x position
        y = random.randint(top_bound + ball_radius, BOTTOM_BOUND - ball_radius)  # random y position
        valid = True  # assume position is valid
        for ball in balls[1:]:  # check against all other balls
            if ball.alive:  # if ball is still on table
                dist = math.hypot(x - ball.x, y - ball.y)  # distance to this ball
                if dist < ball_radius * 2:  # if too close (would overlap)
                    valid = False  # position not valid
                    break  # stop checking
        if valid:  # if found valid position
            balls[0].x = x  # set cue ball x
            balls[0].y = y  # set cue ball y
            balls[0].vx = 0  # stop cue ball
            balls[0].vy = 0  # stop cue ball
            return  # done placing ball

def check_win_condition(balls, player_group):  # checks if player has won the game
    """
    check if the player has won the game
    win condition: all player's balls are pocketed and the 8-ball is pocketed
    
    args:
        balls: list of all balls in the game
        player_group: "solids" or "stripes" - the player's assigned group
    
    returns:
        true if player has won, false otherwise
    """
    if player_group is None:  # if no group assigned yet
        return False  # can't win without an assigned group
    
    # check if 8-ball (last ball in list) is pocketed
    eight_ball = balls[-1]  # 8-ball is the last ball created
    if eight_ball.alive:  # if 8-ball still on table
        return False  # 8-ball must be pocketed to win
    
    # check if all player's balls are pocketed
    for i, ball in enumerate(balls):  # check each ball
        if i == 0:  # if cue ball
            continue  # skip cue ball
        if i == len(balls) - 1:  # if 8-ball
            continue  # skip 8-ball (already checked)
            
        # check if this is one of the player's balls
        if player_group == "solids" and not ball.is_striped:  # if player has solids and this is solid
            if ball.alive:  # if ball still on table
                return False  # player still has solid balls on table
        elif player_group == "stripes" and ball.is_striped:  # if player has stripes and this is stripe
            if ball.alive:  # if ball still on table
                return False  # player still has striped balls on table
    
    return True  # all conditions met - player wins!

def show_win_screen(screen, winner_name, confetti_particles):  # displays win screen with celebration
    """
    display the win screen with confetti animation
    
    args:
        screen: pygame screen surface
        winner_name: name of the winning player
        confetti_particles: list of confetti objects to animate
    
    returns:
        string indicating next action ("menu" or "quit")
    """
    clock = pygame.time.Clock()  # create clock for win screen
    
    # try to load/play victory sound (optional)
    try:  # attempt to play sound
        # uncomment if you have a victory sound file
        # victory_sound = pygame.mixer.sound("victory.wav")
        # victory_sound.play()
        pass  # no sound implemented
    except:  # if sound fails
        pass  # no sound file, continue without audio
    
    # create initial burst of confetti
    for _ in range(100):  # create 100 confetti pieces
        x = random.randint(0, WIDTH)  # random x position across screen
        y = random.randint(-100, 0)  # start above screen
        confetti_particles.append(Confetti(x, y))  # add confetti to list
    
    # win screen loop
    showing_win_screen = True  # flag to keep showing screen
    win_timer = 0  # counter for animation timing
    
    while showing_win_screen:  # loop until player exits
        clock.tick(FPS)  # maintain 60 fps
        win_timer += 1  # increment timer
        
        # handle events
        for event in pygame.event.get():  # check for events
            if event.type == pygame.QUIT:  # if closing window
                return "QUIT"  # return quit command
            if event.type == pygame.KEYDOWN:  # if key pressed
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:  # if esc or enter
                    return "MENU"  # return to menu on esc or enter
            if event.type == pygame.MOUSEBUTTONDOWN:  # if mouse clicked
                return "MENU"  # click to return to menu
        
        # draw background (semi-transparent overlay)
        overlay = pygame.Surface((WIDTH, HEIGHT))  # create surface same size as screen
        overlay.set_alpha(200)  # make mostly opaque (200 out of 255)
        overlay.fill((0, 0, 0))  # fill with black
        screen.blit(overlay, (0, 0))  # draw overlay on screen
        
        # update and draw confetti
        for confetti in confetti_particles[:]:  # iterate over copy of list
            confetti.update()  # update confetti position
            confetti.draw(screen)  # draw confetti
            if confetti.is_offscreen():  # if confetti fell off screen
                confetti_particles.remove(confetti)  # remove from list
        
        # add new confetti periodically
        if win_timer % 10 == 0 and len(confetti_particles) < 150:  # every 10 frames, if not too many
            x = random.randint(0, WIDTH)  # random x position
            confetti_particles.append(Confetti(x, -10))  # add new confetti at top
        
        # draw "you win!" message
        win_font = pygame.font.SysFont(None, 120)  # large font for win text
        win_text = win_font.render("YOU WIN!", True, (255, 215, 0))  # render in gold color
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))  # center text
        
        # draw shadow for text
        shadow_text = win_font.render("YOU WIN!", True, (0, 0, 0))  # render in black
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 3 + 5))  # offset shadow
        screen.blit(shadow_text, shadow_rect)  # draw shadow first
        screen.blit(win_text, win_rect)  # draw main text on top
        
        # draw winner name
        name_font = pygame.font.SysFont(None, 60)  # medium font for name
        name_text = name_font.render(f"{winner_name} win!", True, (255, 255, 255))  # render name in white
        name_rect = name_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # center name
        screen.blit(name_text, name_rect)  # draw winner name
        
        # draw instruction text
        instruction_font = pygame.font.SysFont(None, 36)  # small font for instructions
        instruction_text = instruction_font.render("Click or press ENTER to return to menu", True, (200, 200, 200))  # render in light gray
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))  # center at bottom third
        screen.blit(instruction_text, instruction_rect)  # draw instructions
        
        pygame.display.update()  # update display
    
    return "MENU"  # return to menu

# main game loop - runs the actual pool game
def run_game(config):  # main game function
    balls = create_balls()  # create all 16 balls
    cue = Cue(balls[0])  # create cue stick attached to cue ball (first in list)
    
    # game state variables
    player_turn = 1  # current player (1 or 2)
    shot_in_progress = False  # true when balls are moving
    cue_ball_in_hand = False  # true when placing cue ball after foul
    
    # group assignments - which player has which type of balls
    p1_group = None  # player 1's group ("solids" or "stripes") - none until first ball potted
    
    # win screen state
    confetti_particles = []  # list to hold confetti objects for win screen
    
    # font for text
    font = pygame.font.SysFont(None, 36)  # create font for ui text
    
    # buttons for ui
    btn_menu = Button(10, 5, 100, 40, "Menu")  # menu button top left
    btn_quit = Button(120, 5, 100, 40, "Quit")  # quit button next to menu
    
    # ai timer - for delaying ai shots
    ai_timer = 0  # counter for ai shot delay
    
    running = True  # flag to keep game loop running
    while running:  # main game loop
        clock.tick(FPS)  # maintain 60 fps
        screen.fill(table_boarder)  # fill background with dark gray
        
        # draw table (blue rect) - playing surface
        pygame.draw.rect(screen, table_color, (left_bound, top_bound, right_bound - left_bound, BOTTOM_BOUND - top_bound))  # draw blue table
        
        # draw pockets - black circles at each pocket location
        for pocket in POCKETS:  # for each pocket position
            pygame.draw.circle(screen, black, pocket, pocket_radius)  # draw black circle
            
        # determine current player name
        current_player_name = config["p1"] if player_turn == 1 else config["p2"]  # get name based on turn
        is_ai_turn = (config["mode"] == "ai" and player_turn == 2)  # check if ai's turn
        
        # determine group text to show which balls player needs to pot
        group_text = ""  # empty string initially
        if p1_group:  # if groups have been assigned
            if player_turn == 1:  # if player 1's turn
                group_text = f" ({p1_group.capitalize()})"  # show player 1's group
            else:  # player 2's turn
                p2_group = "stripes" if p1_group == "solids" else "solids"  # player 2 has opposite group
                group_text = f" ({p2_group.capitalize()})"  # show player 2's group
        
        # draw player turn indicator at top of screen
        if current_player_name == "You":  # if human player
            turn_text = f"Your Turn{group_text}"  # personalized message
        else:  # ai or other player
            turn_text = f"{current_player_name}'s Turn{group_text}"  # show player name
        
        if cue_ball_in_hand:  # if placing cue ball
            turn_text += " (Place Cue Ball)"  # add instruction
        text = font.render(turn_text, True, white)  # render text in white
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))  # draw centered at top

        # show groups if assigned - permanent display of who has what
        if p1_group:  # if groups assigned
            p2_group = "stripes" if p1_group == "solids" else "solids"  # get player 2 group
            group_msg = f"{config['p1']}: {p1_group.capitalize()}  |  {config['p2']}: {p2_group.capitalize()}"  # format message
            group_surf = pygame.font.SysFont(None, 24).render(group_msg, True, (200, 200, 200))  # render in light gray
            screen.blit(group_surf, (WIDTH // 2 - group_surf.get_width() // 2, 40))  # draw below turn indicator

        # draw buttons
        btn_menu.draw(screen, font)  # draw menu buttn 
        btn_quit.draw(screen, font)  # draw quit button

        for event in pygame.event.get():  # check for evnets
            if event.type == pygame.QUIT:  # if closing windows
                return "QUIT"  # return quit command
            
            if btn_menu.is_clicked(event):  # if menu button clicked
                return "MENU"  # return to menu
            if btn_quit.is_clicked(event):  # if quit button clicked
                return "QUIT"  # quit game
            
            if not is_ai_turn:  # if human player's turn
                if event.type == pygame.MOUSEBUTTONDOWN:  # if mouse clicked
                    # prevent shooting if clicking buttons
                    if btn_menu.rect.collidepoint(event.pos) or btn_quit.rect.collidepoint(event.pos):  # if clicking button
                        continue  # ignore this click

                    if cue_ball_in_hand:  # if placing cue ball
                        # try to place ball at click location
                        # check if valid placement (not colliding with others)
                        can_place = True  # assume valid
                        # check collision with other balls
                        for ball in balls[1:]:  # check each ball except cue ball
                            if ball.alive:  # if ball on table
                                dist = math.hypot(balls[0].x - ball.x, balls[0].y - ball.y)  # distance to ball
                                if dist < ball_radius * 2:  # if too close
                                    can_place = False  # can't place here
                                    break  # stop checking
                        if can_place:  # if valid placement
                            cue_ball_in_hand = False  # done placing
                            balls[0].vx = 0  # make sure ball is stopped
                            balls[0].vy = 0  # make sure ball is stopped
                    elif balls[0].vx == 0 and balls[0].vy == 0 and not shot_in_progress:  # if ready to shoot
                        # start strike animation
                        cue.start_strike()  # begin cue stick animation
                
        mouse_pos = pygame.mouse.get_pos()  # get current mouse position
        
        # ai logic - ai takes its turn automatically
        if is_ai_turn and not shot_in_progress:  # if ai's turn and not shooting
            # check if balls are stopped
            all_stopped = True  # assume all stopped
            for ball in balls:  # check each ball
                if ball.alive and (abs(ball.vx) > 0 or abs(ball.vy) > 0):  # if ball moving
                    all_stopped = False  # not all stopped
                    break  # stop checking
            
            if all_stopped:  # if all balls stopped
                if cue_ball_in_hand:  # if ai needs to place cue ball
                    ai_place_ball(balls)  # ai places cue ball
                    cue_ball_in_hand = False  # done placing
                else:  # normal shot
                    ai_timer += 1  # increment delay timer
                    if ai_timer > 60:  # wait 1 second (60 frames)
                        # determine ai group
                        ai_group = None  # assume no group
                        if p1_group:  # if groups assigned
                            ai_group = "stripes" if p1_group == "solids" else "solids"  # ai gets opposite of p1
                            
                        angle, power = get_ai_shot(balls, config["difficulty"], ai_group)  # calculate ai shot
                        balls[0].vx = math.cos(angle) * (power * cue_power_multiplier)  # set cue ball x velocity
                        balls[0].vy = math.sin(angle) * (power * cue_power_multiplier)  # set cue ball y velocity
                        shot_in_progress = True  # mark shot as in progress
                        potted_this_turn = []  # reset potted balls list
                        ai_timer = 0  # reset timer
        
        if cue_ball_in_hand and not is_ai_turn:  # if human placing cue ball
            # move cue ball with mouse (constrained to table)
            balls[0].x = max(left_bound + ball_radius, min(mouse_pos[0], right_bound - ball_radius))  # clamp x to table
            balls[0].y = max(top_bound + ball_radius, min(mouse_pos[1], BOTTOM_BOUND - ball_radius))  # clamp y to table
            balls[0].vx = 0  # make sure ball has no velocity
            balls[0].vy = 0  # make sure ball has no velocity
        
        # physics updates - collision detection and ball movement
        check_collisions(balls, cue_ball_in_hand)  # check for ball collisions
        
        if not cue_ball_in_hand:  # if not placing cue ball
            potted = check_pockets(balls)  # check if any balls potted
            if shot_in_progress:  # if currently shooting
                potted_this_turn.extend(potted)  # add to list of balls potted this turn
        
        # check if all balls stopped - determines when turn is over
        all_stopped = True  # assume all stopped
        for ball in balls:  # check each ball
            if ball.alive and (abs(ball.vx) > 0 or abs(ball.vy) > 0):  # if ball moving
                all_stopped = False  # not all stopped
                break  # stop checking
        
        if shot_in_progress and all_stopped:  # if shot was taken and all balls stopped
            shot_in_progress = False  # shot is over
            # turn logic - determine what happens after shot
            
            # analyze potted balls - what was potted this turn
            potted_cue = "cue" in potted_this_turn  # was cue ball potted (foul)
            potted_8ball = "8ball" in potted_this_turn  # was 8-ball potted (game over)
            potted_stripes = [x for x in potted_this_turn if x == "stripe"]  # list of striped balls potted
            potted_solids = [x for x in potted_this_turn if x == "solid"]  # list of solid balls potted
            
            # assign groups if open table - first legal pot determines groups
            if p1_group is None and not potted_cue and not potted_8ball:  # if groups not assigned and legal pot
                if potted_solids and not potted_stripes:  # if only solids potted
                    p1_group = "solids" if player_turn == 1 else "stripes"  # current player gets solids
                elif potted_stripes and not potted_solids:  # if only stripes potted
                    p1_group = "stripes" if player_turn == 1 else "solids"  # current player gets stripes
            
            # determine if turn should switch
            switch_turn = True  # assume turn switches
            
            if potted_cue:  # if cue ball potted (scratch/foul)
                switch_turn = True  # always switch turn on foul
                cue_ball_in_hand = True  # opponent gets ball in hand
                balls[0].alive = True  # make sure cue ball is alive (will be placed)
            elif potted_8ball:  # if 8-ball potted
                # check if this is a legitimate win (all player's balls cleared)
                current_player_group = None  # assume no group
                if p1_group:  # if groups assigned
                    if player_turn == 1:  # if player 1's turn
                        current_player_group = p1_group  # get player 1's group
                    else:  # player 2's turn
                        current_player_group = "stripes" if p1_group == "solids" else "solids"  # get player 2's group
                
                # check win condition
                if current_player_group and check_win_condition(balls, current_player_group):  # if all balls cleared
                    # player wins!
                    winner_name = config["p1"] if player_turn == 1 else config["p2"]  # get winner name
                    result = show_win_screen(screen, winner_name, confetti_particles)  # show win screen
                    return result  # exit game loop
                else:  # potted 8-ball early
                    # potted 8-ball too early - player loses
                    # the other player wins
                    loser_turn = player_turn  # current player loses
                    winner_turn = 3 - player_turn  # other player wins
                    winner_name = config["p1"] if winner_turn == 1 else config["p2"]  # get winner name
                    result = show_win_screen(screen, winner_name, confetti_particles)  # show win screen
                    return result  # exit game loop
            else:  # normal shot (no foul, no 8-ball)
                # check if current player potted their own ball
                my_group = None  # assume no group
                if p1_group:  # if groups assigned
                    if player_turn == 1: my_group = p1_group  # get player 1 group
                    else: my_group = "stripes" if p1_group == "solids" else "solids"  # get player 2 group
                
                if my_group == "solids":  # if player has solids
                    if potted_solids: switch_turn = False  # if potted own ball, keep turn
                elif my_group == "stripes":  # if player has stripes
                    if potted_stripes: switch_turn = False  # if potted own ball, keep turn
                else:  # open table - no groups yet
                    if potted_solids or potted_stripes: switch_turn = False  # if potted any ball, keep turn
            
            if switch_turn:  # if turn should switch
                player_turn = 3 - player_turn  # switch between 1 and 2
            
        # update and draw balls - move and render all balls
        for ball in balls:  # for each ball
            if ball.alive:  # if ball is on table
                ball.move()  # update ball position
                ball.draw(screen)  # draw ball
            
        # update and draw cue if cue ball is stopped
        if balls[0].vx == 0 and balls[0].vy == 0 and balls[0].alive and not cue_ball_in_hand and not is_ai_turn and not shot_in_progress:  # if ready to aim
            cue.update(mouse_pos)  # update cue angle and power
            cue.draw(screen)  # draw cue stick
        
        # update strike animation
        if cue.is_striking:  # if currently striking
            strike_complete = cue.update_strike_animation()  # update animation
            cue.draw(screen)  # draw cue stick during animation
            if strike_complete:  # if strike animation finished
                vx, vy = cue.calculate_velocity()  # calculate ball velocity
                balls[0].vx = vx  # set cue ball x velocity
                balls[0].vy = vy  # set cue ball y velocity
                shot_in_progress = True  # mark shot in progress
                potted_this_turn = []  # reset potted balls list
            
        pygame.display.update()  # update display
    
    return "MENU"  # return to menu

def main():  # main entry point of program
    while True:  # loop to allow replaying
        config = menu()  # show menu and get game config
        if config is None:  # if player quit from menu
            break  # exit program
        
        result = run_game(config)  # run game with chosen config
        if result == "QUIT":  # if quit from game
            break  # exit program
            
    pygame.quit()  # shut down pygame

if __name__ == "__main__":  # if running as main program
    main()  # start the game
