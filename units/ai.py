import pygame
from util import *

class AI():
    def __init__(self):
        pass
    
    # returns either a location to move to, or None if no move is made.
    def compute_move(unit, map):
        pass
    
    def compute_target(unit, map):
        pass

class BasicAI():
    def __init__(self, aggro_range = 10):
        self.aggro_range = aggro_range
    
    def compute_move(self, unit, map):
        if not unit.aggroed:
            # check if the unit should become aggroed
            nearby_locs = bfs(map, unit.location, self.aggro_range, blockable = False, include_units=True)
            for loc in nearby_locs:
                unit_there = map.get_tile(loc).unit
                if unit_there is not None and unit_there.team != unit.team:
                    # aggro due to nearby unit
                    unit.aggroed = True
                    break
        
        if not unit.aggroed:
            return None
        else:
            # locations of all player units
            distance = 9999
            target = None
            for other_unit in map.units:
                if other_unit.team != unit.team:
                    mhd = manhattan_distance(other_unit.location, unit.location)
                    if mhd < distance:
                        distance = mhd
                        target = other_unit.location
            # find the locations from which the target can be attacked
            locations_to_move = unit.base_ability.can_hit_target_from(map, target)
            # find the closest of these locations
            path = bfs_for_target(map, unit.location, locations_to_move, blockable=True, team=unit.team, include_units=False)
            if path is None or len(path) == 1:
                return None
            
            cutoff = min(len(path)-1, unit.get_speed())
            return path[cutoff], path[0:cutoff+1]
    
    def compute_attack(self, unit, map):
        if not unit.aggroed:
            return None
        else:
            potential_targets = unit.base_ability.get_locs_in_range(unit, map)
            for loc in potential_targets:
                target = map.get_tile(loc).unit
                if target is not None and target.team != unit.team:
                    return loc
        return None
