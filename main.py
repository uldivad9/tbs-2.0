import pygame
from pygame.locals import *
import sys
import os
import time
import random

local_path = os.getcwd()
sys.path.append("{}/assets".format(local_path))
sys.path.append("{}/environment".format(local_path))
from util import draw_text, a_star, tile_in_focus, pixel_of_tile, abs_pixel_of_tile
import animations
import colors
import constants as cons
import map as maps

class MainWindow:

    def __init__(self, width=1600,height=900):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(colors.space)
        
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
                        if click_pixels[0] >= cons.BD_HMARGIN and click_pixels[0] < cons.BD_HMARGIN + cons.BD_SIZE[0]:
                            clicked_tile_x = (self.focus_point[0] + click_pixels[0] - cons.BD_HMARGIN) / cons.TILESIZE
                        if click_pixels[1] >= cons.BD_VMARGIN and click_pixels[1] < cons.BD_VMARGIN + cons.BD_SIZE[1]:
                            clicked_tile_y = (self.focus_point[1] + click_pixels[1] - cons.BD_VMARGIN) / cons.TILESIZE
                        if clicked_tile_x is None or clicked_tile_y is None:
                            continue
                        clicked_tile = (clicked_tile_x, clicked_tile_y)
                        if selected_unit is not None:
                            # A unit is currently selected.
                            selected_tile = self.map.get_tile(clicked_tile)
                            if selected_tile.traversable and selected_tile.unit is None:
                                # If the selected tile is traversable and empty:
                                # Calculate the path from the location to the tile
                                path = a_star(self.map, selected_unit.location, clicked_tile)
                                selected_unit.hidden = True
                                # Generate a MovementAnimation
                                self.map.animations.append(animations.MovementAnimation(selected_unit, selected_unit.sprite, abs_pixel_of_tile(selected_unit.location), abs_pixel_of_tile(clicked_tile)))
                                
                                # Actually move the selected unit to the selected tile.
                                self.map.move_unit(selected_unit, (clicked_tile_x, clicked_tile_y))
                                
                                
                                
                                selected_tile = None
                                selected_unit = None
                            elif selected_tile.unit is selected_unit:
                                # deselect the tile and unit
                                selected_tile = None
                                selected_unit = None
                            else:
                                # select a new tile and unit
                                selected_tile = self.map.get_tile(clicked_tile)
                                selected_unit = selected_tile.unit
                        else:
                            if selected_tile == self.map.get_tile(clicked_tile):
                                # If the same tile is clicked, deselect
                                selected_tile = None
                                selected_unit = None
                            else:
                                # select a new tile and unit
                                selected_tile = self.map.get_tile(clicked_tile)
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
            focus_portion = self.map.background.subsurface(pygame.Rect(self.focus_point[0], self.focus_point[1],
                cons.BD_SIZE[0], cons.BD_SIZE[1]))
            
            # Draw grid line overlay
            for i in range(cons.TILESDOWN + 1):
                pygame.draw.line(focus_portion, colors.white, (0, i*cons.TILESIZE), (cons.TILESIZE*cons.TILESACROSS, i*cons.TILESIZE))
            for i in range(cons.TILESACROSS+ 1):
                pygame.draw.line(focus_portion, colors.white, (i*cons.TILESIZE, 0), (i*cons.TILESIZE, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[0] == 0:
                pygame.draw.line(focus_portion, colors.red, (0, 0), (0, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, colors.red, (1, 0), (1, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[0] == self.map.pixel_size[0] - cons.BD_SIZE[0]:
                pygame.draw.line(focus_portion, colors.red, (cons.TILESIZE*cons.TILESACROSS, 0), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, colors.red, (cons.TILESIZE*cons.TILESACROSS - 1, 0), (cons.TILESIZE*cons.TILESACROSS - 1, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[1] == 0:
                pygame.draw.line(focus_portion, colors.red, (0, 0), (cons.TILESIZE*cons.TILESACROSS, 0))
                pygame.draw.line(focus_portion, colors.red, (0, 1), (cons.TILESIZE*cons.TILESACROSS, 1))
            if self.focus_point[1] == self.map.pixel_size[1] - cons.BD_SIZE[1]:
                pygame.draw.line(focus_portion, colors.red, (0, cons.TILESIZE*cons.TILESDOWN), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, colors.red, (0, cons.TILESIZE*cons.TILESDOWN - 1), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN - 1))
            
            self.screen.blit(focus_portion, (cons.BD_HMARGIN, cons.BD_VMARGIN))
            
            # Clip to BD
            self.screen.set_clip(pygame.Rect(cons.BD_HMARGIN, cons.BD_VMARGIN, cons.BD_SIZE[0], cons.BD_SIZE[1]))
            
            # Highlight selected tile
            if selected_tile is not None and tile_in_focus(selected_tile.location, self.focus_point):
                topleft = pixel_of_tile(selected_tile.location, self.focus_point)
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
                self.screen.blit(alpha_surface, topleft)
            
            # Draw units in focus
            for unit in self.map.units:
                if unit.location is not None and not unit.hidden and tile_in_focus(unit.location, self.focus_point):
                    self.screen.blit(unit.sprite, pixel_of_tile(unit.location, self.focus_point))
            
            #~ Update and draw animations
            self.map.animations = [animation for animation in self.map.animations if animation.active]
            for animation in self.map.animations:
                animation.update()
                if animation.in_focus(self.focus_point):
                    animation.draw(self.screen, self.focus_point)
            
            # Draw console
            CS_origin = (cons.BD_HMARGIN + cons.BD_SIZE[0] + cons.CS_HMARGIN, cons.CS_VMARGIN)
            self.screen.set_clip(CS_origin[0], CS_origin[1], cons.CS_SIZE[0], cons.CS_SIZE[1])
            
            console = pygame.Surface((cons.CS_SIZE[0], cons.CS_SIZE[1]))
            console.fill(colors.hologreen)
            font = pygame.font.Font(None, 20)
            if selected_tile is None:
                text = font.render("No tile selected", True, colors.holocyan)
            else:
                text = font.render("Selected tile: {},{}".format(selected_tile.x, selected_tile.y), True, colors.holocyan)
            console.blit(text, (10,10))
            if selected_unit is None:
                draw_text("No unit selected", console, (10,30), font, colors.holocyan)
            else:
                draw_text("Selected unit: {}".format(selected_unit.name), console, (10,30), font, colors.holocyan)
                draw_text("Location: {}".format(selected_unit.location), console, (10,50), font, colors.holocyan)
            draw_text("{} animations active".format(len(self.map.animations)), console, (10,70), font, colors.holocyan)
            if len(self.map.animations) > 0:
                draw_text("animation at {}".format(self.map.animations[0].location), console, (10,90), font, colors.holocyan)
                draw_text("start: {}".format(self.map.animations[0].start), console, (10,110), font, colors.holocyan)
                draw_text("end: {}".format(self.map.animations[0].end), console, (10,130), font, colors.holocyan)
                
            
            self.screen.blit(console, CS_origin)
            
            self.screen.set_clip(None)
            
            # Draw fps indicator surface
            fps_surface = pygame.Surface((60, 40))
            font = pygame.font.Font(None, 20)
            draw_text("FPS: {}".format(fps), fps_surface, (0,0), font, colors.white)
            draw_text("{}".format(time_per_100_frames), fps_surface, (0,20), font, colors.white)
            self.screen.blit(fps_surface, (self.width - 60, 0))
            
            pygame.display.flip()
    
    
    def move_focus_up(self):
        self.focus_point[1] = max(0, self.focus_point[1] - cons.TILESIZE)
    
    def move_focus_left(self):
        self.focus_point[0] = max(0, self.focus_point[0] - cons.TILESIZE)
    
    def move_focus_down(self):
        self.focus_point[1] = min(self.map.pixel_size[1] - cons.BD_SIZE[1], 
            self.focus_point[1] + cons.TILESIZE)
    
    def move_focus_right(self):
        self.focus_point[0] = min(self.map.pixel_size[0] - cons.BD_SIZE[0], 
            self.focus_point[0] + cons.TILESIZE)

if __name__ == "__main__":
    window= MainWindow()
    window.main_loop()
