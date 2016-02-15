import pygame
from pygame.locals import *
import sys
import os
import time
import random

local_path = os.getcwd()
sys.path.append("{}/assets".format(local_path))
sys.path.append("{}/environment".format(local_path))
from util import *
from team import Team
import animations
import colors
import constants as cons
from map import Map
import abilities
from tile import Tile
import units

tiles1 = []
probe_locations = []
for x in range(40):
    tiles1.append([])
    for y in range(30):
        if x + y > 5 and random.random() < 0.27:
            tiles1[x].append(Tile(x,y, traversable=False))
        else:
            tiles1[x].append(Tile(x,y))
            if x + y > 5 and random.random() < 0.02:
                probe_locations.append((x,y))
background_size = get_background_size(tiles1)
map1 = Map(generate_space(background_size[0], background_size[1], 150), tiles1)
map1.add_unit(units.Leonidas.clone(team=Team.PLAYER), (0, 0))
map1.add_unit(units.Leonidas.clone(team=Team.PLAYER), (0, 1))
for loc in probe_locations:
    map1.add_unit(units.red_probe.clone(), loc)
    
class MainWindow:

    def __init__(self, width=1600,height=900):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(colors.BACKGROUND)
        
        # The map currently in use.
        self.map = map1
        # Global animations.
        self.global_animations = []
        
        # The top-left pixel of the portion of the map being displayed in the battle display.
        self.focus_point = [0,0]
        
        self.DEBUG_STOP = False
        
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
        
        # game flow variables
        self.active_player = Team.PLAYER
        self.moved = False # whether the unit has moved and is waiting on an attack input
        self.ready_units = []
        self.total_units = 0
        
        # selection variables
        self.selected_tile = None
        self.selected_unit = None
        self.active_unit = None
        self.locs_in_range = {}
        self.ai_unit = None
        self.ai_last_acted = time.clock()
        
        def count_units():
            self.ready_units = []
            self.total_units = 0
            for unit in self.map.units:
                self.total_units += 1
                if unit.ready:
                    self.ready_units.append(unit)
        
        # Define functions to be used in game flow and event handling
        def next_turn(team):
            self.active_player = team
            
            if self.active_player == Team.PLAYER:
                self.global_animations.append(animations.TurnIndicator("PLAYER TURN"))
            elif self.active_player == Team.ENEMY:
                self.global_animations.append(animations.TurnIndicator("ENEMY TURN"))
            
            for unit in self.map.units:
                if unit.team == self.active_player:
                    unit.ready = True
            count_units()
        
        next_turn(Team.PLAYER)
        
        def deselect():
            self.selected_tile = None
            self.selected_unit = None
            self.active_unit = None
            self.locs_in_range = {}
        
        def select(loc):
            self.selected_tile = self.map.get_tile(loc)
            
            if self.selected_tile.unit is not None:
                self.selected_unit = self.selected_tile.unit
                if self.selected_unit.ready and self.selected_unit.team == Team.PLAYER:
                    self.active_unit = self.selected_unit
                else:
                    self.active_unit = None
            else:
                self.selected_unit = None
            
            if self.active_unit is not None:
                self.locs_in_range = bfs(self.map, self.selected_tile.location, self.selected_unit.get_speed(), team=self.active_unit.team)
            else:
                self.locs_in_range = {}
        
        while True:
            if fps_time_counter == 100:
                fps_time_end = time.clock()
                time_per_100_frames = fps_time_end - fps_time_start
                fps = int(100.0 / (fps_time_end - fps_time_start))
                fps_time_counter = 0
                fps_time_start = time.clock()
            fps_time_counter += 1
            
            #~ Handle game flow
            waiting = False
            locking = False
            for animation in self.map.animations + self.global_animations:
                if animation.locking:
                    waiting = True
                    locking = True
                    echoing = False
                    key_released = True
                elif animation.waiting:
                    waiting = True
            
            if self.DEBUG_STOP:
                locking = True
            
            count_units()
            
            if not waiting and not locking:
                if len(self.ready_units) == 0:
                    # switch the active player.
                    if self.active_player == Team.PLAYER:
                        next_turn(Team.ENEMY)
                    else:
                        next_turn(Team.PLAYER)
                    self.ai_last_acted = time.clock()
            #~ AI
            if not waiting and not locking:
                if self.active_player == Team.ENEMY and time.clock() - self.ai_last_acted > cons.AI_DELAY:
                    self.ai_last_acted = time.clock()
                
                    if self.ai_unit is None or not self.ai_unit.ready:
                        self.ai_unit = self.ready_units[0]
                    
                    if not self.moved:
                        dptuple = self.ai_unit.ai.compute_move(self.ai_unit, self.map)
                        if dptuple is not None:
                            destination, path = dptuple
                            self.ai_unit.hidden = True
                            # Generate a MovementAnimation
                            pixel_path = [abs_pixel_of_loc(dest) for dest in simplify_path(path)]
                            self.map.animations.append(animations.MovementAnimation(unit=self.ai_unit, destinations=pixel_path))
                            # Actually move the selected unit to the selected tile.
                            self.map.move_unit(self.ai_unit, destination)
                        self.moved = True
                    else:
                        target = self.ai_unit.ai.compute_attack(self.ai_unit, self.map)
                        if target is not None:
                            laser_animation = animations.LaserAnimation(abs_pixel_of_loc(self.ai_unit.location), abs_pixel_of_loc(target), color=colors.blue_laser, source=self.ai_unit)
                            self.map.animations.append(laser_animation)
                            self.ai_unit.base_ability.activate(self.ai_unit, self.map, target)
                        self.moved = False
                        self.ai_unit.ready = False
                        
            
            #~ Handle events
            for event in pygame.event.get():
                if time.clock() < input_locked_until:
                    key_released = True
                    echoing = False
                    break
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if waiting or locking:
                        continue
                    # Mouse click
                    if event.button == 1:
                        # left click
                        click_pixels = event.pos
                        clicked_loc = loc_of_pixel(click_pixels, self.focus_point)
                        if not loc_in_focus(clicked_loc, self.focus_point):
                            continue
                        if self.active_unit is not None:
                            # A unit is currently active.
                            if not self.moved:
                                self.selected_tile = self.map.get_tile(clicked_loc)
                                if self.selected_tile.traversable and self.selected_tile.unit is None:
                                    #~ Move command
                                    # If the selected tile is traversable and empty:
                                    # Calculate the path from the location to the tile
                                    path = a_star(self.map, self.active_unit.location, clicked_loc, self.active_unit.team)
                                    if path is not None:
                                        # Simplify the path and turn it into a sequence of pixels
                                        pixel_path = [abs_pixel_of_loc(dest) for dest in simplify_path(path)]
                                        self.active_unit.hidden = True
                                        # Generate a MovementAnimation
                                        self.map.animations.append(animations.MovementAnimation(unit=self.active_unit, destinations=pixel_path))
                                        
                                        # Actually move the selected unit to the selected tile.
                                        self.map.move_unit(self.active_unit, clicked_loc)
                                        # Attack selection
                                        self.locs_in_range = bfs(self.map, self.active_unit.location, self.active_unit.get_range(), blockable = False, include_units = True, include_start = False)
                                        self.moved = True
                                    else:
                                        deselect()
                                elif self.selected_tile.unit is self.active_unit:
                                    # Don't actually move, but go to attack selection
                                    self.locs_in_range = bfs(self.map, self.active_unit.location, self.active_unit.get_range(), blockable = False, include_units = True, include_start = False)
                                    self.moved = True
                                else:
                                    # select a new tile and unit
                                    select(clicked_loc)
                            else: # moved == True
                                # Received attack input.
                                self.moved = False
                                self.active_unit.ready = False
                                
                                if clicked_loc in self.locs_in_range:
                                    # attack selected tile
                                    laser_animation = animations.LaserAnimation(abs_pixel_of_loc(self.selected_tile.location), abs_pixel_of_loc(clicked_loc), color=colors.blue_laser, source=self.active_unit)
                                    self.map.animations.append(laser_animation)
                                    
                                    self.active_unit.base_ability.activate(self.active_unit, self.map, clicked_loc)
                                    
                                deselect()
                        else: # self.active_unit is None
                            if self.selected_tile == self.map.get_tile(clicked_loc):
                                # If the same tile is clicked, deselect
                                deselect()
                            else:
                                # select a new tile and unit
                                select(clicked_loc)
                    elif event.button == 3:
                        # right click
                        pass
                elif event.type == KEYDOWN:
                    if locking:
                        continue
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
                    if locking:
                        continue
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
            
            grid_x_offset = self.focus_point[0] % cons.TILESIZE
            grid_y_offset = self.focus_point[1] % cons.TILESIZE
            # Draw grid line overlay
            for i in range(cons.TILESDOWN + 1):
                pygame.draw.line(focus_portion, colors.GRIDLINE, (-grid_x_offset, i*cons.TILESIZE - grid_y_offset), (cons.TILESIZE*cons.TILESACROSS - grid_x_offset, i*cons.TILESIZE - grid_y_offset))
            for i in range(cons.TILESACROSS+ 1):
                pygame.draw.line(focus_portion, colors.GRIDLINE, (i*cons.TILESIZE - grid_x_offset, -grid_y_offset), (i*cons.TILESIZE - grid_x_offset, cons.TILESIZE*cons.TILESDOWN - grid_y_offset))
            if self.focus_point[0] == 0:
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (0, 0), (0, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (1, 0), (1, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[0] == self.map.pixel_size[0] - cons.BD_SIZE[0]:
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (cons.TILESIZE*cons.TILESACROSS, 0), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (cons.TILESIZE*cons.TILESACROSS - 1, 0), (cons.TILESIZE*cons.TILESACROSS - 1, cons.TILESIZE*cons.TILESDOWN))
            if self.focus_point[1] == 0:
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (0, 0), (cons.TILESIZE*cons.TILESACROSS, 0))
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (0, 1), (cons.TILESIZE*cons.TILESACROSS, 1))
            if self.focus_point[1] == self.map.pixel_size[1] - cons.BD_SIZE[1]:
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (0, cons.TILESIZE*cons.TILESDOWN), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN))
                pygame.draw.line(focus_portion, colors.MAP_BOUNDARY_LINE, (0, cons.TILESIZE*cons.TILESDOWN - 1), (cons.TILESIZE*cons.TILESACROSS, cons.TILESIZE*cons.TILESDOWN - 1))
            
            self.screen.blit(focus_portion, (cons.BD_HMARGIN, cons.BD_VMARGIN))
            
            # Clip to BD
            self.screen.set_clip(pygame.Rect(cons.BD_HMARGIN, cons.BD_VMARGIN, cons.BD_SIZE[0], cons.BD_SIZE[1]))
            
            # Draw red lines around untraversable terrain and highlight inrange tiles
            tlx, tly = loc_of_pixel((cons.BD_HMARGIN, cons.BD_VMARGIN), self.focus_point)
            for x in range(cons.TILESACROSS + 1):
                for y in range(cons.TILESDOWN + 1):
                    loc = (tlx + x, tly + y)
                    if tlx + x >= len(self.map.tiles) or tly + y >= len(self.map.tiles[0]):
                        continue
                    current_tile = self.map.tiles[tlx + x][tly + y]
                    if not current_tile.traversable:
                        pxx, pxy = pixel_of_loc(current_tile.location, self.focus_point)
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx, pxy), (pxx + cons.TILESIZE, pxy))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx, pxy), (pxx, pxy + cons.TILESIZE))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx, pxy + cons.TILESIZE), (pxx + cons.TILESIZE, pxy + cons.TILESIZE))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx + cons.TILESIZE, pxy), (pxx + cons.TILESIZE, pxy + cons.TILESIZE))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx, pxy+20), (pxx + 20, pxy))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx, pxy+40), (pxx + 40, pxy))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx, pxy+60), (pxx + 60, pxy))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx + 20, pxy+60), (pxx + 60, pxy + 20))
                        pygame.draw.line(self.screen, colors.UNTRAVERSABLE_BOUNDARY_LINE, (pxx + 40, pxy+60), (pxx + 60, pxy + 40))
                    # highlight locs in range unless the currently selected unit is hidden.
                    if loc in self.locs_in_range and not (self.selected_unit is not None and self.selected_unit.hidden):
                        if not self.moved:
                            self.highlight_tile(loc, colors.MOVE_HIGHLIGHT, 3)
                        else:
                            self.highlight_tile(loc, colors.ATTACK_HIGHLIGHT, 3)
            

            
            # Highlight selected tile
            if self.selected_tile is not None and loc_in_focus(self.selected_tile.location, self.focus_point):
                self.highlight_tile(self.selected_tile.location, colors.SELECTION_HIGHLIGHT, 4)
            
            # Draw units in focus
            for unit in self.map.units:
                if unit.location is not None and not unit.hidden and loc_in_focus(unit.location, self.focus_point):
                    # if the unit is ready, draw a little rotating thing around it
                    if unit.ready:
                        angle = (time.clock() % 2) * math.pi
                        center = tuple_add(pixel_of_loc(unit.location, self.focus_point), (cons.TILESIZE/2, cons.TILESIZE/2))
                        pygame.draw.circle(self.screen, colors.white, tuple_int(point_at_angle(center, angle, 25)), 3)
                    rotated_sprite = pygame.transform.rotate(unit.sprite, unit.orientation)
                    rotated_width = rotated_sprite.get_width()
                    rotated_height = rotated_sprite.get_height()
                    px, py = pixel_of_loc(unit.location, self.focus_point)
                    self.screen.blit(rotated_sprite, (px + cons.TILESIZE / 2 - rotated_width / 2, py + cons.TILESIZE / 2 - rotated_height / 2))
                    
            
            #~ Update and draw animations
            self.map.animations = [animation for animation in self.map.animations if animation.active]
            new_animations = []
            for animation in self.map.animations:
                spawned = animation.update()
                if spawned is not None:
                    new_animations += spawned
                if animation.in_focus(self.focus_point):
                    animation.draw(self.screen, self.focus_point)
            for animation in new_animations:
                animation.activate()
                self.map.animations.append(animation)
            
            # Draw console
            CS_origin = (cons.BD_HMARGIN + cons.BD_SIZE[0] + cons.CS_HMARGIN, cons.CS_VMARGIN)
            self.screen.set_clip(CS_origin[0], CS_origin[1], cons.CS_SIZE[0], cons.CS_SIZE[1])
            
            CS_lines = []
            if self.selected_tile is None:
                CS_lines.append("No loc selected")
            else:
                CS_lines.append("Selected loc: {},{}".format(self.selected_tile.x, self.selected_tile.y))
            if self.selected_unit is None:
                CS_lines.append("No unit selected")
            else:
                CS_lines.append("Selected unit: {}".format(self.selected_unit.name))
                CS_lines.append("Location: {}".format(self.selected_unit.location))
            if self.active_unit is None:
                CS_lines.append("No active unit")
            else:
                CS_lines.append("Active unit: {}".format(self.active_unit.name))
                CS_lines.append("Location: {}".format(self.active_unit.location))
            if self.ai_unit is None:
                CS_lines.append("No AI unit")
            else:
                CS_lines.append("AI unit: {}".format(self.ai_unit.name))
                CS_lines.append("Location: {}".format(self.ai_unit.location))
            CS_lines.append("Ready units: {}".format(len(self.ready_units)))
            CS_lines.append("Total units: {}".format(self.total_units))
            CS_lines.append("{} animations active".format(len(self.map.animations)))
            
            console = generate_message_window(cons.CS_SIZE[0], cons.CS_SIZE[1], CS_lines)
            self.screen.blit(console, CS_origin)
            
            self.screen.set_clip(None)
            
            # Draw fps indicator surface
            fps_surface = pygame.Surface((60, 40))
            fps_surface.fill(colors.BACKGROUND)
            font = pygame.font.Font(None, 20)
            draw_text("FPS: {}".format(fps), fps_surface, (0,0), font, colors.TEXT)
            draw_text("{}".format(time_per_100_frames), fps_surface, (0,20), font, colors.TEXT)
            self.screen.blit(fps_surface, (self.width - 60, 0))
            
            # Draw global animations
            self.screen.set_clip(0, 0, 1600, 900)
            self.global_animations = [animation for animation in self.global_animations if animation.active]
            for animation in self.global_animations:
                animation.update()
                animation.draw(self.screen)
            
            pygame.display.flip()
    
    
    # Draws a inner highlight on the given tile.
    def highlight_tile(self, loc, color_in, thickness):
        topleft = pixel_of_loc(loc, self.focus_point)
        highlight_width = cons.TILESIZE
        highlight_thickness = thickness
        # Create a alpha subsurface
        alpha_surface = pygame.Surface((highlight_width, highlight_width), pygame.SRCALPHA)
        for i in range(1, 1+highlight_thickness):
            color = pygame.Color(color_in.r, color_in.g, color_in.b, 255 - 255*(i-1)/highlight_thickness)
            pygame.draw.line(alpha_surface, color, (i, i), (i, highlight_width - i))
            pygame.draw.line(alpha_surface, color, (i + 1, i), (highlight_width - i, i))
            pygame.draw.line(alpha_surface, color, (i + 1, highlight_width - i), (highlight_width - i, highlight_width - i))
            pygame.draw.line(alpha_surface, color, (highlight_width - i, i + 1), (highlight_width - i, highlight_width - i - 1))
        self.screen.blit(alpha_surface, topleft)

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
