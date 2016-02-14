import pygame
from util import bfs

"""
All ability classes should have:
user
get_locs_in_range()
get_locs_in_aoe()
activate()
"""

class Ability():
    def __init__(self, user=None):
        self.user = user
    
    def get_locs_in_range(self):
        pass
    
    def get_tiles_in_aoe(self, map):
        pass
    
    def activate(self):
        pass

class BowAttack():
    def __init__(self, range=0):
        self.range = range
    
    def get_locs_in_range(self, user, map):
        return bfs(map, user.location, self.range, blockable=False, include_start=False)
    
    def get_tiles_in_aoe(self, user, map, target_loc):
        return [map.tiles[target_loc[0]][target_loc[1]]]
    
    def activate(self, user, map, target_loc):
        for tile in self.get_tiles_in_aoe(user, map, target_loc):
            if tile.unit is not None:
                tile.unit.take_damage(user.get_attack())