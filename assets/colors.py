import pygame

# These values are color definitions and should not be significantly changed.

red = pygame.Color('Red')
darkred = pygame.Color(159, 0, 15)
darkpurple = pygame.Color(120, 0, 80)
green = pygame.Color('Green')
darkgreen = pygame.Color(0, 120, 40)
black = pygame.Color('Black')
white = pygame.Color('White')
space = pygame.Color(11, 15, 17)
hologreen = pygame.Color(14, 38, 39)
holocyan = pygame.Color(40, 236, 230)
gunmetal = pygame.Color(44, 53, 57)
flame = pygame.Color(246, 40, 23)


#########################################

blue_laser = pygame.Color(10, 150, 250)

#########################################

# Mess around with these to match colors to UI elements.

BACKGROUND = space
GRIDLINE = gunmetal
MAP_BOUNDARY_LINE = red
UNTRAVERSABLE_BOUNDARY_LINE = darkred
SELECTION_HIGHLIGHT = white
MOVE_HIGHLIGHT = darkgreen
ATTACK_HIGHLIGHT = darkpurple
WINDOW = hologreen
TEXT = holocyan
DAMAGE_TEXT_COLOR = red