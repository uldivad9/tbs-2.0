import pygame
import time
import constants as cons
from util import *
import colors
import fonts
import random

"""
All animation classes should have:
active: whether the animation is still active or not.
waiting: whether the animation should lock most input.
locking: whether the animation should lock ALL input, including screen panning.
in_focus(focus_point): returns whether the animation should be drawn on the screen, given the focus_point.
draw(focus_point, surface): draw the animation on the given surface
activate(self): spawns 
update(): run every frame
cleanup(): run after the animation finishes.
"""

class Animation():
    def __init__(self):
        self.active = True
        self.waiting = False
        self.locking = False
        
        self.activate()
        
    def activate(self):
        self.start_time = time.clock()
        
    def in_focus(self, focus_point):
        pass
    
    def draw(self, surface, focus_point):
        pass
        
    def update(self):
        pass
        
    def cleanup(self):
        pass

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
        self.waiting = True
        self.locking = False
    
    def activate(self):
        self.start_time = time.clock()
    
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

class DeathAnimation():
    def __init__(self, origin=None, sprite=None, waittime = 1.3, fadetime=0.7):
        self.active = True
        self.waiting = True
        self.locking = False
        self.sprite = sprite
        self.origin = origin
        self.fadetime = fadetime
        self.waittime = waittime
        self.start_time = time.clock()
        self.finally_exploded = False
        
        self.explosions = []
        '''
        if random.random() > 0.6:
            spray_destination = random_point_in_radius((self.origin[0] + cons.TILESIZE / 2, self.origin[1] + cons.TILESIZE / 2), 70)
            spray = Explosion(origin = (self.origin[0] + cons.TILESIZE / 2, self.origin[1] + cons.TILESIZE / 2), radius=15, destination = spray_destination, spark_count=200, spark_size=1, end_spread = 0, start_spread = 3)
            self.explosions.append([random.random() * waittime/4, spray])
        '''
        for i in range(random.randint(2,4)):
            if random.random() > 0.5:
                # spurt of sparks
                spray_destination = random_point_in_radius((self.origin[0] + cons.TILESIZE / 2, self.origin[1] + cons.TILESIZE / 2), 60)
                spray = Explosion(origin = (self.origin[0] + cons.TILESIZE / 2, self.origin[1] + cons.TILESIZE / 2), radius=10, destination = spray_destination, spark_count=40, spark_size=2)
                self.explosions.append([random.random() * waittime, spray])
            else:
                # small explosion
                boom_origin = random_point_in_radius((self.origin[0] + cons.TILESIZE / 2, self.origin[1] + cons.TILESIZE / 2), 10)
                boom = Explosion(origin = boom_origin, radius=30, spark_count=60, spark_size=2)
                self.explosions.append([random.random() * waittime, boom])
            
        
        self.keyed = apply_color_key(self.sprite)
        
    def activate(self):
        self.start_time = time.clock()
        
    def in_focus(self, focus_point):
        return pixel_in_focus(self.origin, focus_point)
    
    def draw(self, surface, focus_point):
        elapsed_time = time.clock() - self.start_time
        
        if elapsed_time < self.waittime:
            if elapsed_time % 0.12 > 0.06:
                surface.blit(self.sprite, (self.origin[0] - focus_point[0] + 1, self.origin[1] - focus_point[1]))
            else:
                surface.blit(self.sprite, (self.origin[0] - focus_point[0] - 1, self.origin[1] - focus_point[1]))
        else:
            self.keyed.set_alpha(int(255 - 255 * (time.clock() - self.start_time - self.waittime) / self.fadetime))
            surface.blit(self.keyed, (self.origin[0] - focus_point[0], self.origin[1] - focus_point[1]))
        
    def update(self):
        spawn = []
        for explosion in self.explosions:
            if time.clock() - self.start_time > explosion[0]:
                spawn.append(explosion[1])
                explosion[0] = 99
        if time.clock() - self.start_time > self.fadetime + self.waittime:
            self.active = False
            self.cleanup()
        elif not self.finally_exploded and time.clock() - self.start_time > self.waittime:
            self.finally_exploded = True
            spawn.append(Explosion(origin = (self.origin[0] + cons.TILESIZE / 2, self.origin[1] + cons.TILESIZE / 2), radius=60, spark_count=300))
        return spawn
        
    def cleanup(self):
        self.waiting = False

class LaserAnimation():
    def __init__(self, point1, point2, source=None, color=colors.white, lifetime=0.3):
        self.point1 = point1
        self.point2 = point2
        self.original_color = color
        self.color = color
        self.active = True
        self.lifetime = float(lifetime)
        self.final_decay = 0.2
        self.decay_base = self.final_decay ** (1 / lifetime)
        self.start_time = time.clock()
        self.source = source
        if self.source is not None:
            self.previous_orientation = self.source.orientation
            self.source.orientation = angle_between(point1, point2)
        self.waiting = True
        self.locking = False
    
    def activate(self):
        self.start_time = time.clock()
        
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



class Explosion():
    def __init__(self, origin=None, radius=50, destination=None, spark_count=200, spark_size=3, start_spread=0, end_spread=1):
        self.active = True
        self.waiting = False
        self.locking = False
        self.origin = origin
        self.destination = destination if destination is not None else self.origin
        self.radius = radius
        self.start_time = time.clock()
        self.spark_count = spark_count
        self.spark_size = spark_size
        self.start_spread = start_spread
        self.end_spread = end_spread
        self.activate()
        
    def activate(self):
        '''
        each spark is of the form [start, end, start_time, lifetime]
        '''
        self.start_time = time.clock()
        self.sparks = []
        for i in range(self.spark_count):
            spark_origin = self.origin
            radius = random.randint(1,self.radius)
            endpoint = random_point_in_radius(self.destination, radius)
            spark_start = self.start_time + random.random() * self.start_spread
            self.sparks.append((spark_origin, endpoint, spark_start, cons.EXPLOSION_LIFETIME + random.random() * self.end_spread))
        
    def in_focus(self, focus_point):
        return pixel_in_focus(self.origin, focus_point)
    
    def draw(self, surface, focus_point):
        time_elapsed = time.clock() - self.start_time
        
        for spark in self.sparks:
            lifetime_elapsed = (time.clock() - spark[2]) / spark[3]
            if lifetime_elapsed < 0 or lifetime_elapsed > 1:
                continue
            distance_covered = 1 - (0.33 ** (2 * lifetime_elapsed))
            currentx = int(spark[0][0] + (spark[1][0] - spark[0][0]) * distance_covered)
            currenty = int(spark[0][1] + (spark[1][1] - spark[0][1]) * distance_covered)
            
            if lifetime_elapsed < 0.5:
                spark_color = blend_colors(colors.flame, colors.white, lifetime_elapsed * 2)
            else:
                spark_color = blend_colors(colors.black, colors.flame, lifetime_elapsed * 2 - 1)
                
            if self.spark_size > 1:
                pygame.draw.rect(surface, spark_color, pygame.Rect(currentx - focus_point[0], currenty - focus_point[1], self.spark_size, self.spark_size))
            else:
                surface.set_at((currentx - focus_point[0], currenty - focus_point[1]), spark_color)
        
    def update(self):
        self.sparks = [spark for spark in self.sparks if spark[3] > time.clock() - self.start_time]
        '''
        time_elapsed = (clock.time() - self.start_time)
        for spark in sparks:
            lifetime_elapsed = time_elapsed / spark.lifetime
            spark[0][0] = 
            spark[1][1] = 
        '''
        if len(self.sparks) == 0:
            self.active = False
        
    def cleanup(self):
        pass

class DamageText():
    def __init__(self, origin=None, amount=0):
        self.active = True
        self.waiting = False
        self.locking = False
        self.origin = origin # point at which the text should be centered
        self.amount = str(amount)
        self.start_time = time.clock()
        
    def activate(self):
        self.start_time = time.clock()
        
    def in_focus(self, focus_point):
        age = time.clock() - self.start_time
        rise_height = age * cons.DAMAGE_TEXT_SPEED * (1 - age / cons.DAMAGE_TEXT_LIFETIME / 2)
        return pixel_in_focus((self.origin[0], self.origin[1] - rise_height), focus_point)
    
    def draw(self, surface, focus_point):
        text = fonts.DAMAGE_TEXT_FONT.render(self.amount, True, colors.DAMAGE_TEXT_COLOR)
        rect = text.get_rect()
        width = rect.width
        height = rect.height
        age = time.clock() - self.start_time
        rise_height = age * cons.DAMAGE_TEXT_SPEED * (1 - age / cons.DAMAGE_TEXT_LIFETIME / 2)
        
        surface.blit(text, (self.origin[0] - width/2 - focus_point[0], self.origin[1] - height/2 - rise_height - focus_point[1]))
        
    def update(self):
        if time.clock() - self.start_time > cons.DAMAGE_TEXT_LIFETIME:
            self.active = False
            self.cleanup()
    
    def cleanup(self):
        pass

class TurnIndicator():
    def __init__(self, text):
        self.active = True
        self.waiting = False
        self.locking = True
        self.center = (800, 450)
        self.final = (400, 360)
        self.time1 = .18 # open vertically
        self.time2 = .25 # open horizontally
        self.time3 = .7 # wait and display text
        self.time4 = 1  # unused
        self.text = text
        self.activate()
    
    def activate(self):
        self.start_time = time.clock()
    
    def in_focus(self):
        return True
    
    def draw(self, surface):
        elapsed_time = time.clock() - self.start_time
        
        currentx, currenty = self.final
        text_reveal = 0
        
        if elapsed_time < self.time1: # open vertically
            currentx = self.center[0]
            currenty = int(self.center[1] + (self.final[1] - self.center[1]) * elapsed_time / self.time1)
        elif elapsed_time < self.time1 + self.time2: # open horizontally
            currentx = int(self.center[0] + (self.final[0] - self.center[0]) * (elapsed_time - self.time1) / self.time2)
            currenty = self.final[1]
            text_reveal = (elapsed_time - self.time1) / self.time2
        elif elapsed_time < self.time1 + self.time2 + self.time3: # display text
            currentx, currenty = self.final
            text_reveal = 1
        elif elapsed_time < self.time1 + self.time2 + self.time3 + self.time1:
            currentx = self.final[0]
            currenty = int(self.final[1] + (self.center[1] - self.final[1]) * (elapsed_time - self.time1 - self.time2 - self.time3) / self.time1)
        else:
            currenty = self.center[1]
            currentx = int(self.final[0] + (self.center[0] - self.final[0]) * (elapsed_time - self.time1 - self.time1 - self.time2 - self.time3) / self.time2)
        
        pygame.draw.rect(surface, colors.hologreen, pygame.Rect(currentx, currenty, 2 * (self.center[0] - currentx), 2 * (self.center[1] - currenty)))
        pygame.draw.line(surface, colors.holocyan, (currentx, currenty), (self.center[0] * 2 - currentx, currenty))
        pygame.draw.line(surface, colors.holocyan, (currentx, self.center[1] * 2 - currenty), (self.center[0] * 2 - currentx, self.center[1] * 2 - currenty))
        if text_reveal > 0:
            text = fonts.MAIN_MESSAGE_FONT.render(self.text, True, colors.holocyan)
            rect = text.get_rect()
            '''
            width = rect.width
            height = rect.height
            blit_location = (self.center[0] - width / 2, self.center[1] - height / 2)
            surface.blit(text.subsurface(pygame.Rect(0, 0, min(int(width * text_reveal), width), height)), blit_location)
            '''
            orig_width = rect.width
            width = rect.width * text_reveal
            height = rect.height
            subsurf = text.subsurface(pygame.Rect(orig_width/2 - width/2, 0, width, height))
            surface.blit(subsurf, (self.center[0] - width/2, self.center[1] - height/2))
        
    def update(self):
        if time.clock() - self.start_time > self.time1*2 + self.time2*2 + self.time3:
            self.active - False
            self.cleanup()
        
    def cleanup(self):
        self.active = False
        self.locking = False
