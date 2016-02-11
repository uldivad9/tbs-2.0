import pygame
from pygame.locals import *
import sys
import os
import time
import random

local_path = os.getcwd()
sys.path.append("{}/util".format(local_path))
sys.path.append("{}/environment".format(local_path))
import constants as cons
import map as maps

class MainWindow:

    def __init__(self, width=1600,height=900):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # The map currently in use.
        self.map = maps.map1
        
        # The top-left pixel of the portion of the map being displayed in the battle display.
        self.focus_point = [0,0]
        
    def main_loop(self):
        # fps calculation variables
        fps_time_counter = 0
        fps_time_start = 0
        time_per_100_frames = 0
        fps = 0
        
        # event handling variables
        input_locked_until = time.clock()
        last_key_pressed = None
        key_released = True
        last_time_pressed = time.clock()
        echoing = False
        
        
        # selection variables
        selected_tile = None
        selected_unit = None
        
        while True:
            if fps_time_counter == 100:
                fps_time_end = time.clock()
                time_per_100_frames = fps_time_end - fps_time_start
                fps = int(100.0 / (fps_time_end - fps_time_start))
                fps_time_counter = 0
                fps_time_start = time.clock()
            fps_time_counter += 1
            
            # Define functions to be used in event handling
            
            
            #~ Handle events
            for event in pygame.event.get():
                if time.clock() < input_locked_until:
                    key_released = True
                    echoing = False
                    break
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    # Mouse click
                    if event.button == 1:
                        # left click
                        click_pixels = event.pos
                        clicked_tile_x = None
                        clicked_tile_y = None
                        if click_pixels[0] >= cons.LEFTEDGEMARGIN and click_pixels[0] < cons.LEFTEDGEMARGIN + cons.BATTLE_DISPLAY_SIZE[0]:
                            clicked_tile_x = (self.focus_point[0] + click_pixels[0] - cons.LEFTEDGEMARGIN) / cons.TILESIZE
                        if click_pixels[1] >= cons.TOPEDGEMARGIN and click_pixels[1] < cons.TOPEDGEMARGIN + cons.BATTLE_DISPLAY_SIZE[1]:
                            clicked_tile_y = (self.focus_point[1] + click_pixels[1] - cons.TOPEDGEMARGIN) / cons.TILESIZE
                        if clicked_tile_x is not None and clicked_tile_y is not None:
                            selected_tile = self.map.tiles[clicked_tile_x][clicked_tile_y]
                            selected_unit = selected_tile.unit
                    elif event.button == 3:
                        # right click
                        pass
                elif event.type == KEYDOWN:
                    # Key press
                    key_released = False
                    echoing = False
                    last_key_pressed = event.key
                    last_time_pressed = time.clock()
                    if event.key == K_w or event.key == K_UP:
                        self.move_focus_up()
                    elif event.key == K_a or event.key == K_LEFT:
                        self.move_focus_left()
                    elif event.key == K_s or event.key == K_DOWN:
                        self.move_focus_down()
                    elif event.key == K_d or event.key == K_RIGHT:
                        self.move_focus_right()
                elif event.type == KEYUP:
                    # Key up
                    if event.key == last_key_pressed:
                        key_released = True
                        echoing = False
            if not key_released:
                current_time = time.clock()
                if (not echoing and current_time - last_time_pressed > cons.KEY_ECHO_START_DELAY) or (echoing and current_time - last_time_pressed > cons.KEY_ECHO_REPEAT_DELAY):
                    echoing = True
                    last_time_pressed = current_time
                    if last_key_pressed == K_w or last_key_pressed == K_UP:
                        self.move_focus_up()
                    elif last_key_pressed == K_a or last_key_pressed == K_LEFT:
                        self.move_focus_left()
                    elif last_key_pressed == K_s or last_key_pressed == K_DOWN:
                        self.move_focus_down()
                    elif last_key_pressed == K_d or last_key_pressed == K_RIGHT:
                        self.move_focus_right()
                
            
            
            #~ Redraw screen
            # Draw the portion of the map that is in focus
            
            focus_portion_base = self.map.background.subsurface(pygame.Rect(self.focus_point[0], self.focus_point[1],
                cons.BATTLE_DISPLAY_SIZE[0], cons.BATTLE_DISPLAY_SIZE[1]))
            
            focus_portion = pygame.Surface((cons.BATTLE_DISPLAY_SIZE[0], cons.BATTLE_DISPLAY_SIZE[1]))
            focus_portion.blit(focus_portion_base, (0,0)) # don't make a copy of this, it's slow as fuck
            
            # Draw grid line overlay
            for i in range(cons.TILESDOWN + 1):
                pygame.draw.line(focus_portion, pygame.Color('White'), (0, i*cons.TILESIZE), (cons.TILESIZE*cons.TILESACROSS, i*cons.TILESIZE))
            for i in range(cons.TILESACROSS+ 1):
                pygame.draw.line(focus_portion, pygame.Color('White'), (i*cons.TILESIZE, 0), (i*cons.TILESIZE, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[0] == 0:
                pygame.draw.line(focus_portion, pygame.Color('Red'), (0, 0), (0, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, pygame.Color('Red'), (1, 0), (1, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[0] == self.map.pixel_size[0] - cons.BATTLE_DISPLAY_SIZE[0]:
                pygame.draw.line(focus_portion, pygame.Color('Red'), (cons.TILESIZE*cons.TILESACROSS, 0), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, pygame.Color('Red'), (cons.TILESIZE*cons.TILESACROSS - 1, 0), (cons.TILESIZE*cons.TILESACROSS - 1, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[1] == 0:
                pygame.draw.line(focus_portion, pygame.Color('Red'), (0, 0), (cons.TILESIZE*cons.TILESACROSS, 0))
                pygame.draw.line(focus_portion, pygame.Color('Red'), (0, 1), (cons.TILESIZE*cons.TILESACROSS, 1))
            if self.focus_point[1] == self.map.pixel_size[1] - cons.BATTLE_DISPLAY_SIZE[1]:
                pygame.draw.line(focus_portion, pygame.Color('Red'), (0, cons.TILESIZE*cons.TILESDOWN), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, pygame.Color('Red'), (0, cons.TILESIZE*cons.TILESDOWN - 1), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN - 1))
            
            # Highlight selected tile
            if selected_tile is not None and self.tile_in_focus(selected_tile.location):
                topleft = self.pixel_of_tile(selected_tile.location)
                highlight_width = cons.TILESIZE
                highlight_thickness = 4
                # Create a alpha subsurface
                alpha_surface = pygame.Surface((highlight_width, highlight_width), pygame.SRCALPHA)
                for i in range(1, 1+highlight_thickness):
                    color = pygame.Color(0, 255, 0, 255 - 255*(i-1)/highlight_thickness)
                    pygame.draw.line(alpha_surface, color, (i, i), (i, highlight_width - i))
                    pygame.draw.line(alpha_surface, color, (i + 1, i), (highlight_width - i, i))
                    pygame.draw.line(alpha_surface, color, (i + 1, highlight_width - i), (highlight_width - i, highlight_width - i))
                    pygame.draw.line(alpha_surface, color, (highlight_width - i, i + 1), (highlight_width - i, highlight_width - i - 1))
                focus_portion.blit(alpha_surface, topleft)
            
            # Draw units in focus
            for unit in self.map.units:
                if self.tile_in_focus(unit.location):
                    focus_portion.blit(unit.sprite, self.pixel_of_tile(unit.location))
            
            self.screen.blit(focus_portion, (cons.LEFTEDGEMARGIN, cons.TOPEDGEMARGIN))
            
            # Draw fps indicator surface
            fps_surface = pygame.Surface((60, 40))
            font = pygame.font.Font(None, 20)
            text = font.render("FPS: {}".format(fps), True, pygame.Color('White'))
            fps_surface.blit(text, (0, 0))
            text = font.render("{}".format(time_per_100_frames), True, pygame.Color('White'))
            fps_surface.blit(text, (0, 20))
            self.screen.blit(fps_surface, (self.width - 60, 0))
            
            pygame.display.flip()
    
    # returns the top-left pixel coordinates of the given map tile.
    def pixel_of_tile(self, xy):
        x,y = xy[0], xy[1]
        return (x * cons.TILESIZE - self.focus_point[0], y * cons.TILESIZE - self.focus_point[1])
    
    # returns whether the given map tile is in focus (and therefore must be drawn).
    def tile_in_focus(self, xy):
        x,y = xy[0], xy[1]
        if self.pixel_in_focus((x * cons.TILESIZE, y*cons.TILESIZE)):
            return True
        elif self.pixel_in_focus(((x+1) * cons.TILESIZE - 1, y*cons.TILESIZE)):
            return True
        elif self.pixel_in_focus(((x+1) * cons.TILESIZE - 1, (y+1)*cons.TILESIZE)):
            return True
        elif self.pixel_in_focus(((x+1) * cons.TILESIZE - 1, y*cons.TILESIZE)):
            return True
        return False
    
    # returns whether a given pixel is in focus
    def pixel_in_focus(self, xy):
        x, y = xy[0], xy[1]
        return self.focus_point[0] <= x and self.focus_point[0] + cons.TILESACROSS * cons.TILESIZE > x and self.focus_point[1] <= y and self.focus_point[1] + cons.TILESDOWN * cons.TILESIZE > y
    
    def move_focus_up(self):
        self.focus_point[1] = max(0, self.focus_point[1] - cons.TILESIZE)
    
    def move_focus_left(self):
        self.focus_point[0] = max(0, self.focus_point[0] - cons.TILESIZE)
    
    def move_focus_down(self):
        self.focus_point[1] = min(self.map.pixel_size[1] - cons.BATTLE_DISPLAY_SIZE[1], 
            self.focus_point[1] + cons.TILESIZE)
    
    def move_focus_right(self):
        self.focus_point[0] = min(self.map.pixel_size[0] - cons.BATTLE_DISPLAY_SIZE[0], 
            self.focus_point[0] + cons.TILESIZE)

if __name__ == "__main__":
    window= MainWindow()
    window.main_loop()
