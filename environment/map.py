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
from team import Team

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
        unit.map = self
        self.get_tile(xy).unit = unit
        unit.location = xy
        self.units.append(unit)
    
    def remove_unit(self, unit):
        self.units.remove(unit)
        self.tiles[unit.location[0]][unit.location[1]].unit = None
        unit.location = None
    
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
    
    # 'team' is the team or iterable of teams for which locations should be counted as being passable.
    def neighboring_locations(self, xy, team):
        if not hasattr(team, '__iter__'):
            teams = [team]
        else:
            teams = team
        x, y = xy
        neighbors = []
        for loc in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if self.on_map(loc) and self.tiles[loc[0]][loc[1]].traversable and (self.tiles[loc[0]][loc[1]].unit is None or self.tiles[loc[0]][loc[1]].unit.team in teams):
                neighbors.append(loc)
        return neighbors

