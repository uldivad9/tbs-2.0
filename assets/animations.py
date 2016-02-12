import pygame
import time
import constants as cons
from util import pixel_in_focus, pixel_of_tile, abs_pixel_of_tile, distance

"""
All animation classes should have:
active: whether the animation is still active or not.
in_focus(focus_point): returns whether the animation should be drawn on the screen, given the focus_point.
draw(focus_point, surface): draw the animation on the given surface
update(): run every frame
cleanup(): run after the animation finishes.
"""

class MovementAnimation():
    def __init__(self, unit, sprite, start, end):
        self.start_time = time.clock()
        self.unit = unit
        self.active = True
        self.last_update = time.clock()
        self.start = start
        self.location = self.start
        self.end = end
        self.sprite = sprite
    
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
    
    def rounded_location(self):
        return (int(self.location[0]), int(self.location[1]))
    
    def draw(self, surface, focus_point):
        surface.blit(self.sprite, (int(self.location[0]) - focus_point[0], int(self.location[1]) - focus_point[1]))
    
    def update(self):
        current_time = time.clock()
        distance_traveled = (cons.MOVE_ANIM_SPEED + (current_time - self.start_time) * cons.MOVE_ANIM_ACCEL) * (current_time - self.last_update)
        self.last_update = time.clock()
        distance_to_end = distance(self.location, self.end)
        if distance_to_end <= distance_traveled:
            self.location = self.end
            self.cleanup()
        else:
            newx = self.location[0] + (self.end[0] - self.location[0]) * (distance_traveled / distance_to_end)
            newy = self.location[1] + (self.end[1] - self.location[1]) * (distance_traveled / distance_to_end)
            self.location = (newx, newy)
    
    def cleanup(self):
        self.unit.hidden = False
        self.active = False
        