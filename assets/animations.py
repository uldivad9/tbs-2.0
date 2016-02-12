import pygame
import time
import constants as cons
from util import pixel_in_focus, pixel_of_loc, abs_pixel_of_loc, distance, angle_between

"""
All animation classes should have:
active: whether the animation is still active or not.
in_focus(focus_point): returns whether the animation should be drawn on the screen, given the focus_point.
draw(focus_point, surface): draw the animation on the given surface
spawn(): spawns 
update(): run every frame
cleanup(): run after the animation finishes.
"""

class MovementAnimation():
    def __init__(self, unit=None, sprite=None, destinations=[(0,0),(0,0)]):
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
        