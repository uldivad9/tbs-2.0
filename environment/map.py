import pygame
import random
import sys
import os
local_path = os.getcwd()
sys.path.append("{}/environment".format(local_path))
from tile import Tile
sys.path.append("{}/units".format(local_path))
import constants as cons
import units

class Map:
    def __init__(self, background_surface, tiles):
        self.tiles = tiles
        if background_surface.get_size() != (cons.TILESIZE * len(tiles) + 1, cons.TILESIZE * len(tiles[0]) + 1):
            print("BACKGROUND/TILES SIZE MISMATCH")
        self.background = background_surface
        self.pixel_size = background_surface.get_size()
        self.units = []
        
    def add_unit(self, unit, x, y):
        unit.location = (x,y)
        self.get_tile(x,y).unit = unit
        self.units.append(unit)
        
    def get_tile(self, x, y):
        if x < 0 or x >= len(self.tiles) or y < 0 or y >= len(self.tiles[0]):
            return None
        return self.tiles[x][y]

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

tiles1 = []
for x in range(30):
    tiles1.append([])
    for y in range(40):
        tiles1[x].append(Tile(x,y))
background_size = get_background_size(tiles1)
map1 = Map(generate_space(background_size[0], background_size[1], 60), tiles1)
map1.add_unit(units.Leonidas.clone(), 15, 15)