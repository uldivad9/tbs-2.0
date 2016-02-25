import pygame
from util import bfs, tuple_add, load_image
import status

"""
All ability classes should have:
user
get_locs_in_range()
get_locs_in_aoe()
activate()
"""

class Ability():
    def __init__(self, user=None, sprite=None):
        self.user = user
        self.sprite = sprite
    
    def get_locs_in_range(self):
        pass
    
    def can_hit_target_from(self, user, map, target_loc):
        pass
    
    def get_tiles_in_aoe(self, user, map, target_loc):
        pass
    
    def activate(self):
        pass
    
    def get_description(self):
        return "No data."

class BowAttack():
    def __init__(self, range=0, sprite=load_image('assets/icons/ability/missile_single_icon.png')):
        self.range = range
        self.sprite = sprite
    
    def get_locs_in_range(self, user, map):
        return bfs(map, user.location, self.range, blockable=False, include_units = True, include_start=False)
    
    def can_hit_target_from(self, user, map, target_loc):
        return bfs(map, target_loc, self.range, blockable=False, include_units = True, include_start=True)
    
    def get_tiles_in_aoe(self, user, map, target_loc):
        return [map.tiles[target_loc[0]][target_loc[1]]]
    
    def activate(self, user, map, target_loc):
        for tile in self.get_tiles_in_aoe(user, map, target_loc):
            if tile.unit is not None:
                tile.unit.take_damage(user.calc_standard_damage())
    
    def get_description(self):
        return "Damages a single target within range {}.".format(self.range)

class GunAttack():
    def __init__(self, range=0, sprite=load_image('assets/icons/ability/turret_icon.png')):
        self.range = range
        self.sprite = sprite
    
    def get_locs_in_range(self, user, map):
        inrange = set()
        x, y = user.location
        #north
        for i in range(1, self.range):
            next = (x, y-i)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        #east
        for i in range(1, self.range):
            next = (x+i, y)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        #south
        for i in range(1, self.range):
            next = (x, y+i)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        #west
        for i in range(1, self.range):
            next = (x-i, y)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        return inrange
    
    def can_hit_target_from(self, user, map, target_loc):
        inrange = set()
        x, y = target_loc
        #north
        for i in range(1, self.range):
            next = (x, y-i)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        #east
        for i in range(1, self.range):
            next = (x+i, y)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        #south
        for i in range(1, self.range):
            next = (x, y+i)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        #west
        for i in range(1, self.range):
            next = (x-i, y)
            tile = map.get_tile(next)
            if tile is None:
                break
            elif tile.unit is not None and tile.unit.team != user.team:
                inrange.add(next)
                break
            elif tile.traversable and not (tile.unit is not None and tile.unit.team != user.team):
                inrange.add(next)
            else:
                break
        return inrange
    
    def get_tiles_in_aoe(self, user, map, target_loc):
        if target_loc[0] > user.location[0]:
            aoe = [target_loc, tuple_add(target_loc, (1,0)), tuple_add(target_loc, (2,0))]
        elif target_loc[0] < user.location[0]:
            aoe = [target_loc, tuple_add(target_loc, (-1,0)), tuple_add(target_loc, (-2,0))]
        elif target_loc[1] > user.location[1]:
            aoe = [target_loc, tuple_add(target_loc, (0,1)), tuple_add(target_loc, (0,2))]
        elif target_loc[1] < user.location[1]:
            aoe = [target_loc, tuple_add(target_loc, (0,-1)), tuple_add(target_loc, (0,-2))]
        else:
            aoe = []
        return [map.get_tile(loc) for loc in aoe if map.on_map(loc)]
        
    def activate(self, user, map, target_loc):
        for tile in self.get_tiles_in_aoe(user, map, target_loc):
            if tile.unit is not None:
                tile.unit.take_damage(user.calc_standard_damage())
    
    def get_description(self):
        return "Damages three tiles in a line."

class CalibrateWeapons():
    def __init__(self, user=None, duration=1, power=1000, sprite=load_image('assets/icons/ability/calibrateweapons.png')):
        self.user = user
        self.duration = duration
        self.power = power
        self.sprite = sprite
    
    def get_locs_in_range(self, user, map):
        return [user.location]
    
    def can_hit_target_from(self, user, map, target_loc):
        return [target_loc]
    
    def get_tiles_in_aoe(self, user, map, target_loc):
        return [user.location]
    
    def activate(self, user, map, target_loc):
        # remove prior instances of calibrateweaponstatus
        user.statuses = [mystatus for mystatus in user.statuses if not isinstance(mystatus, status.CalibrateWeaponsStatus)]
        user.statuses.append(status.CalibrateWeaponsStatus(duration=self.duration, power=self.power))
    
    def get_description(self):
        return "Calibrates and strengthens the ship's weaponry for {} turns.".format(self.duration)
    
class EMP():
    def __init__(self, range=0, duration=1, sprite=load_image('assets/icons/ability/missile_large_icon.png')):
        self.range = range
        self.sprite = sprite
        self.duration = duration
    
    def get_locs_in_range(self, user, map):
        return bfs(map, user.location, self.range, blockable=False, include_units = True, include_start=False)
    
    def can_hit_target_from(self, user, map, target_loc):
        return bfs(map, target_loc, self.range, blockable=False, include_units = True, include_start=True)
    
    def get_tiles_in_aoe(self, user, map, target_loc):
        return [map.tiles[target_loc[0]][target_loc[1]]]
    
    def activate(self, user, map, target_loc):
        for tile in self.get_tiles_in_aoe(user, map, target_loc):
            if tile.unit is not None:
                tile.unit.statuses.append(status.Disabled(duration=self.duration))
                print("DISABLED")
                tile.unit.take_damage(user.calc_standard_damage() * 1.5)
    
    def get_description(self):
        return "Fires an EMP charge at a unit within {} range, dealing high damage and disabling it for {} turns.".format(self.range, self.duration)