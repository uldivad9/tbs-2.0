import pygame
import random
import sys
import os
local_path = os.getcwd()
sys.path.append("{}/..".format(local_path))
import constants as cons

class Map:
    def __init__(self, background_surface, tiles):
        self.tiles = tiles
        if background_surface.get_size() != (cons.TILESIZE * len(tiles) + 1, cons.TILESIZE * len(tiles[0]) + 1):
            print("BACKGROUND/TILES SIZE MISMATCH")
        self.background = background_surface
        self.pixel_size = background_surface.get_size()

def get_background_size(tiles):
    return (cons.TILESIZE * len(tiles) + 1, cons.TILESIZE * len(tiles[0]) + 1)

# Generates a Surface consisting of black space and a bunch of stars.
def generate_space(x, y, num_stars):
    space = pygame.Surface((x, y))
    pxarray = pygame.PixelArray(space)
    
    for i in range(num_stars):
        radius = random.randint(3,15) # TODO: better star radius distribution
        centerx = int(random.random() * x)
        centery = int(random.random() * y)
        for xval in range(max(0, centerx - radius), min(x-1, centerx + radius)):
            for yval in range(max(0, centery - radius), min(y-1, centery + radius)):
                distance_squared = (xval - centerx) ** 2 + (yval - centery) ** 2
                if distance_squared >= radius:
                    continue
                else:
                    intensity = float(radius - distance_squared) / radius
                    rgb_value = int(255 * intensity)
                    pxarray[xval, yval] = (rgb_value, rgb_value, rgb_value)
    return space

tiles1 = [[None] * 30] * 40
background_size = get_background_size(tiles1)
map1 = Map(generate_space(background_size[0], background_size[1], 60), tiles1)