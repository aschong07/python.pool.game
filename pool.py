#imports
import pygame
import math

#pygame is intiated
pygame.init()

#Visuals:

#basic settings
WIDTH, HEIGHT = 900, 500 # window size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Pool Game_ECE160") #title of game
clock = pygame.time.Clock() #creates a clocked controled by FPS
FPS = 60

#colors im too lazy to pick colors rn sooooo
table_boarder =  #sets the boarder
#color of the balls
green =  
white =
red =
yellow = 
blue = 
black = 

#constants
ball_radius = 12 #balls radius
friction = 0.99 #slows down the ball
cue_power_multiplier = 0.12 #controls the strength of the shots
min_speed = 0.01 #stops the ball completely

#table boundaries
left_bound = 70
right_bound = WIDTH - 70 
top_bound = 50 
BOTTOM_BOUND = HEIGHT - 50

#pockets 
pocket_radius = 22 
POCKETS = [
    #3 pockets on top
    (LEFT_BOUND, TOP_BOUND),
    ((LEFT_BOUND + RIGHT_BOUND) // 2, TOP_BOUND),
    (RIGHT_BOUND, TOP_BOUND),
    #3 pockets on bottom
    (LEFT_BOUND, BOTTOM_BOUND),
    ((LEFT_BOUND + RIGHT_BOUND) // 2, BOTTOM_BOUND),
    (RIGHT_BOUND, BOTTOM_BOUND)
]

#the balls

#the ball itself 
class Ball: 
    def __init__(self, x, y, color):
        self.x = x         #Balls X Position
        self.y = y         #Balls Y Position
        self.vx = 0        #Velocity in X direction
        self.vy = 0        #Velocity in Y direction
        self.color = color  #Color of ball
        self.is_cue = is_cue #cue ball
        self.alive = true #still in game

#Table

#
    





