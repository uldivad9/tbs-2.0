from Queue import Queue
from bisect import bisect_left
import constants as cons
import pygame
import colors
import math

b = colors.white

# renders and blits the given text in the given color to the given location.
def draw_text(text="", surface=None, location=(0,0), font=None, color=colors.white):
    rendered = font.render(text, True, color)
    surface.blit(rendered, location)


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

#~ Methods for detecting whether pixels are in the display
# Returns true if the given pixel would be within the battle display.
def pixel_in_focus(xy, focus_point):
    x, y = xy
    return focus_point[0] <= x and focus_point[0] + cons.TILESACROSS * cons.TILESIZE > x and focus_point[1] <= y and focus_point[1] + cons.TILESDOWN * cons.TILESIZE > y

# Returns true if part of the given tile would be within the battle display.
def tile_in_focus(xy, focus_point):
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

# Returns the top-left pixel coordinates of the given map tile.
def pixel_of_tile(xy, focus_point):
    x,y = xy
    return (x * cons.TILESIZE - focus_point[0] + cons.BD_HMARGIN, y * cons.TILESIZE - focus_point[1] + cons.BD_VMARGIN)

def abs_pixel_of_tile(xy):
    x,y = xy
    return (x * cons.TILESIZE + cons.BD_HMARGIN, y * cons.TILESIZE + cons.BD_VMARGIN)

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

def a_star(map, start, goal):
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
        
        for next in map.neighboring_locations(current):
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