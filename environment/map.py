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
        self.animations = []
        
    def add_unit(self, unit, xy):
        self.get_tile(xy).unit = unit
        unit.location = xy
        self.units.append(unit)
        
    def get_tile(self, xy):
        x, y = xy
        if not self.on_map(xy):
            return None
        return self.tiles[x][y]
    
    def move_unit(self, unit, xy):
        if unit.location is not None:
            self.get_tile(unit.location).unit = None
            
        self.get_tile(xy).unit = unit
        unit.location = xy
    
    def on_map(self, xy):
        x, y = xy
        return x >= 0 and x < len(self.tiles) and y >= 0 and y < len(self.tiles[0])
    
    def adjacent_locations(self, xy):
        x, y = xy
        neighbors = []
        for loc in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if self.on_map(loc):
                neighbors.append(loc)
        return neighbors
    
    def neighboring_locations(self, xy):
        x, y = xy
        neighbors = []
        for loc in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if self.on_map(loc) and self.tiles[loc[0]][loc[1]].traversable:
                neighbors.append(loc)
        return neighbors

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
for x in range(40):
    tiles1.append([])
    for y in range(30):
        if x + y > 5 and random.random() < 0.3:
            tiles1[x].append(Tile(x,y, traversable=False))
        else:
            tiles1[x].append(Tile(x,y))
background_size = get_background_size(tiles1)
map1 = Map(generate_space(background_size[0], background_size[1], 60), tiles1)
map1.add_unit(units.Leonidas.clone(), (0, 0))

'''
sys.path.append("{}/util".format(local_path))
import util
util.a_star(map1, (0,0), (1,0))
'''