from Queue import Queue
from bisect import bisect_left
import constants as cons
import pygame
import colors
import math
import random

# loads the given image and applies a color key to remove full transparency.
def load_image(path):
    img = pygame.image.load(path)
    return apply_color_key(img)

# renders and blits the given text in the given color to the given location.
def draw_text(text="", surface=None, location=(0,0), font=None, color=colors.white):
    rendered = font.render(text, True, color)
    surface.blit(rendered, location)

# returns a blend between colors c1 and c2. If c1_ratio = 1, the output color is c1. If c1_ratio = 0, the output color is c2.
def blend_colors(c1, c2, c1_ratio):
    if c1_ratio > 1:
        c1_ratio = 1
    elif c1_ratio < 0:
        c1_ratio = 0
    return pygame.Color(int(c1.r * c1_ratio + c2.r * (1 - c1_ratio)), int(c1.g * c1_ratio + c2.g * (1 - c1_ratio)), int(c1.b * c1_ratio + c2.b * (1 - c1_ratio)))

# returns the distance between a and b.
def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

# returns the manhattan distance between a and b.
def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# returns the angle from point a to point b.
def angle_between(a, b):
    angle = math.atan2(b[0]-a[0], b[1]-a[1])
    return (math.degrees(angle) + 180) % 360

# adds 2-element tuples element-wise and returns the results.
def tuple_add(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])

def tuple_int(t):
    return (int(t[0]), int(t[1]))

# returns the point at a specified distance and angle away from a given point.
def point_at_angle(center, angle, radius):
    return (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))

# returns a random point in that is the given radius away from the given center.
def random_point_in_radius(center, radius):
    angle = random.random() * 2 * math.pi
    return point_at_angle(center, angle, radius)

# returns the image with a color key applied. speeds up fps a lot when used on images with fully-transparent pixels.
def apply_color_key(img):
    key = (255, 0, 255)
    keyed = pygame.Surface(img.get_size(), depth = 24)
    keyed.fill(key, keyed.get_rect())
    keyed.set_colorkey(key)
    keyed.blit(img, (0,0))
    return keyed

# 
def get_background_size(tiles):
    return (cons.TILESIZE * len(tiles) + 1, cons.TILESIZE * len(tiles[0]) + 1)

#~ Methods for detecting whether pixels are in the display
# Returns true if the given pixel would be within the battle display.
def pixel_in_focus(xy, focus_point):
    x, y = xy
    return focus_point[0] <= x and focus_point[0] + cons.TILESACROSS * cons.TILESIZE > x and focus_point[1] <= y and focus_point[1] + cons.TILESDOWN * cons.TILESIZE > y

# Returns true if part of the given tile would be within the battle display.
def loc_in_focus(xy, focus_point):
    x,y = xy[0], xy[1]
    if pixel_in_focus((x * cons.TILESIZE, y*cons.TILESIZE), focus_point):
        return True
    elif pixel_in_focus(((x+1) * cons.TILESIZE, y*cons.TILESIZE), focus_point):
        return True
    elif pixel_in_focus(((x+1) * cons.TILESIZE, (y+1)*cons.TILESIZE), focus_point):
        return True
    elif pixel_in_focus((x * cons.TILESIZE, (y+1)*cons.TILESIZE), focus_point):
        return True
    return False

# returns the coordinates of the tile that the given pixel belongs to.
def loc_of_pixel(xy, focus_point):
    x,y = xy
    return ((x - cons.BD_HMARGIN + focus_point[0]) / cons.TILESIZE, (y - cons.BD_VMARGIN + focus_point[1]) / cons.TILESIZE)

# Returns the top-left pixel coordinates of the given map tile.
def pixel_of_loc(xy, focus_point):
    x,y = xy
    return (x * cons.TILESIZE - focus_point[0] + cons.BD_HMARGIN, y * cons.TILESIZE - focus_point[1] + cons.BD_VMARGIN)

# Returns the absolute pixel coordinates (not relative to the focus point) of the given map tile. As if the entire map were being displayed.
def abs_pixel_of_loc(xy):
    x,y = xy
    return (x * cons.TILESIZE + cons.BD_HMARGIN, y * cons.TILESIZE + cons.BD_VMARGIN)

#~ BFS
def bfs(map, start, range, blockable = True, team = None, include_units = False, include_start = True):
    frontier = Queue()
    frontier.put(start, 0)
    cost_so_far = {start:0}
    
    while not frontier.empty():
        current = frontier.get()
        
        if blockable:
            neighbors = map.neighboring_locations(current, team)
        else:
            neighbors = map.adjacent_locations(current)
        for next in neighbors:
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far and new_cost <= range:
                cost_so_far[next] = new_cost
                frontier.put(next)
    
    if not include_units:
        to_remove = []
        for location in cost_so_far:
            if map.get_tile((location[0], location[1])).unit is not None:
                to_remove.append(location)
        for remove in to_remove:
            cost_so_far.pop(remove)
        
    if not include_start and include_units:
        cost_so_far.pop(start)
    elif include_start and not include_units:
        cost_so_far[start] = 0
    return cost_so_far

# Performs a bfs, returning the first location in 'targets' that is found.
def bfs_for_target(map, start, targets, blockable = True, team = None, include_units = False):
    if start in targets:
        return [start]
    frontier = Queue()
    frontier.put(start, 0)
    cost_so_far = {start:0}
    came_from = {}
    came_from[start] = None
    
    while not frontier.empty():
        current = frontier.get()
        if current in targets and (include_units or map.get_tile(current).unit is None):
            path = [current]
            while (current != start):
                current = came_from[current]
                path.insert(0, current)
            return path
        
        if blockable:
            neighbors = map.neighboring_locations(current, team)
        else:
            neighbors = map.adjacent_locations(current)
        for next in neighbors:
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far:
                cost_so_far[next] = new_cost
                frontier.put(next)
                came_from[next] = current
    return None

#~ A* algorithm methods
class PriorityQueue(Queue):
    def _init(self, maxsize):
        self.maxsize = maxsize
        # Python 2.5 uses collections.deque, but we can't because
        # we need insert(pos, item) for our priority stuff
        self.queue = []

    def put(self, item, priority=0, block=True, timeout=None):
        """Puts an item onto the queue with a numeric priority (default is zero).

        Note that we are "shadowing" the original Queue.Queue put() method here.
        """
        Queue.put(self, (priority, item), block, timeout)

    def _put(self, item):
        """Override of the Queue._put to support prioritisation."""
        # Priorities must be integers!
        priority = int(item[0])

        # Using a tuple (priority+1,) finds us the correct insertion
        # position to maintain the existing ordering.
        self.queue.insert(bisect_left(self.queue, (priority+1,)), item)

    def get(self):
        """Override of Queue._get().  Strips the priority."""
        return self.queue.pop(0)[1]

def a_star_heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star(map, start, goal, team=None):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    found = False
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            found = True
            break
        
        for next in map.neighboring_locations(current, team):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + a_star_heuristic(goal, next)
                # Break priority ties by trying tiles with closer heuristic values
                frontier.put(next, priority*1000 + a_star_heuristic(goal, next))
                #frontier.put(next, priority)
                came_from[next] = current
    
    if not found:
        return None
    
    # return the path from start to goal.
    path = [current]
    while (current != start):
        current = came_from[current]
        path.insert(0, current)
    return path

# takes a tile-by-tile path and reduces it to start/end/turn points.
def simplify_path(path):
    key_points = []
    for i, dest in enumerate(path):
        if i == 0 or i == len(path) - 1:
            key_points.append(dest)
        elif not (2 * path[i][0] == path[i-1][0] + path[i+1][0] and 2 * path[i][1] == path[i-1][1] + path[i+1][1]):
            key_points.append(dest)
    return key_points

#~ Pre-drawn objects
# Generates a Surface consisting of black space and a bunch of stars.
def generate_space(x, y, num_stars):
    space = pygame.Surface((x, y))
    pxarray = pygame.PixelArray(space)
    
    for i in range(num_stars):
        radius = random.randint(3,15) # TODO: better star radius distribution
        centerx = int(random.random() * x)
        centery = int(random.random() * y)
        for xval in range(max(0, centerx - radius), min(x-1, centerx + radius)):
            for yval in range(max(0, centery - radius), min(y-1, centery + radius)):
                distance_squared = (xval - centerx) ** 2 + (yval - centery) ** 2
                if distance_squared >= radius:
                    continue
                else:
                    intensity = float(radius - distance_squared) / radius
                    rgb_value = int(255 * intensity)
                    pxarray[xval, yval] = (rgb_value, rgb_value, rgb_value)
    return space

# Wraps the given text in the given font so that it fits in a window of the given width.
# 'text' should be a list of strings. The output will be a list of strings as well, where each string of 'text' is broken up into multiple wrapped strings.
def word_wrap(text, font, width):
    wrapped = []
    for string in text:
        words = string.split(' ')
        concat = ''
        for word in words:
            #print(word)
            if concat == '':
                next = word
            else:
                next = concat + ' ' + word
            if font.size(next)[0] > width:
                if concat == '':
                    # a single word is too long for the entire width. qq.
                    wrapped.append(next)
                    concat = ''
                else:
                    wrapped.append(concat)
                    concat = word
            else:
                concat = next
        wrapped.append(concat)
    return wrapped

# Generates a message window of the given dimensions and containing the given array of lines.
def generate_message_window(width, height, text):
    console = pygame.Surface((width, height))
    console.fill(colors.WINDOW)
    font = pygame.font.Font(None, 20)
    current = 10
    for line in word_wrap(text, font, width):
        draw_text(line, console, (10, current), font, colors.TEXT)
        current += 20
    return console