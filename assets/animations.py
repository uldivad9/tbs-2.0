import pygame
import time
import constants as cons
from util import pixel_in_focus, pixel_of_loc, abs_pixel_of_loc, distance, angle_between
import colors

"""
All animation classes should have:
active: whether the animation is still active or not.
in_focus(focus_point): returns whether the animation should be drawn on the screen, given the focus_point.
draw(focus_point, surface): draw the animation on the given surface
spawn(): spawns 
update(): run every frame
cleanup(): run after the animation finishes.
"""

class Animation():
    def __init__(self, spawn=[]):
        self.spawn = spawn
        self.active = True
        
    def spawn():
        return self.spawn
        
    def in_focus(self, focus_point):
        pass
    
    def draw(self, surface, focus_point):
        pass
        
    def update(self):
        pass
        
    def cleanup(self):
        pass

class MovementAnimation():
    def __init__(self, unit=None, sprite=None, destinations=[(0,0),(0,0)], spawn=[]):
        self.unit = unit
        self.active = True
        self.last_update = time.clock()
        self.destinations = destinations
        self.destination_index = 0
        if sprite is None and unit is not None:
            self.sprite = unit.sprite
        self.sprite_orientation = 0
        self.next_destination()
        self.location = self.start
        self.spawn = spawn
    
    def spawn():
        return self.spawn
    
    def in_focus(self, focus_point):
        x,y = self.rounded_location()
        if pixel_in_focus((x, y), focus_point):
            return True
        elif pixel_in_focus((x + cons.TILESIZE, y), focus_point):
            return True
        elif pixel_in_focus((x + cons.TILESIZE, y + cons.TILESIZE), focus_point):
            return True
        elif pixel_in_focus((x, y + cons.TILESIZE), focus_point):
            return True
        return False
    
    def next_destination(self):
        self.start_time = time.clock()
        self.start = self.destinations[self.destination_index]
        self.destination_index += 1
        self.end = self.destinations[self.destination_index]
        # get new orientation
        self.sprite_orientation = angle_between(self.start, self.end)
    
    def rounded_location(self):
        return (int(self.location[0]), int(self.location[1]))
    
    def draw(self, surface, focus_point):
        surface.blit(pygame.transform.rotate(self.sprite, self.sprite_orientation), (int(self.location[0]) - focus_point[0], int(self.location[1]) - focus_point[1]))
    
    def update(self):
        current_time = time.clock()
        distance_traveled = (cons.MOVE_ANIM_SPEED + (current_time - self.start_time) * cons.MOVE_ANIM_ACCEL) * (current_time - self.last_update)
        self.last_update = time.clock()
        distance_to_end = distance(self.location, self.end)
        if distance_to_end <= distance_traveled:
            self.location = self.end
            if self.destination_index == len(self.destinations) - 1:
                self.cleanup()
            else:
                self.next_destination()
        else:
            newx = self.location[0] + (self.end[0] - self.location[0]) * (distance_traveled / distance_to_end)
            newy = self.location[1] + (self.end[1] - self.location[1]) * (distance_traveled / distance_to_end)
            self.location = (newx, newy)
    
    def cleanup(self):
        if self.unit is not None:
            self.unit.orientation = self.sprite_orientation
            self.unit.hidden = False
        self.active = False

class LaserAnimation():
    def __init__(self, point1, point2, source=None, color=colors.white, lifetime=0.3, spawn=[]):
        self.point1 = point1
        self.point2 = point2
        self.original_color = color
        self.color = color
        self.spawn = spawn
        self.active = True
        self.lifetime = float(lifetime)
        self.final_decay = 0.2
        self.decay_base = self.final_decay ** (1 / lifetime)
        self.start_time = time.clock()
        self.source = source
        if self.source is not None:
            self.previous_orientation = self.source.orientation
            self.source.orientation = angle_between(point1, point2)
    
    def spawn():
        return self.spawn
        
    def in_focus(self, focus_point):
        return (pixel_in_focus(self.point1, focus_point) or pixel_in_focus(self.point2, focus_point))
        # TODO improve this
    
    def draw(self, surface, focus_point):
        p1 = (self.point1[0] - focus_point[0] + cons.TILESIZE / 2, self.point1[1] - focus_point[1] + cons.TILESIZE / 2)
        p2 = (self.point2[0] - focus_point[0] + cons.TILESIZE / 2, self.point2[1] - focus_point[1] + cons.TILESIZE / 2)
        if time.clock() - self.start_time < 0.2:
            pygame.draw.line(surface, self.color, p1, p2, 5)
        elif time.clock() - self.start_time < 0.25:
            pygame.draw.line(surface, self.color, p1, p2, 3)
        else:
            pygame.draw.line(surface, self.color, p1, p2, 1)
        
    def update(self):
        # TODO update self.color
        strength_factor = self.decay_base ** (time.clock() - self.start_time)
        new_r = int(self.original_color.r * strength_factor)
        new_g = int(self.original_color.g * strength_factor)
        new_b = int(self.original_color.b * strength_factor)
        
        self.color = pygame.Color(new_r, new_g, new_b)
        
        if time.clock() > self.start_time + self.lifetime:
            self.active = False
            self.cleanup()
        
    def cleanup(self):
        if self.source is not None:
            self.source.orientation = self.previous_orientation