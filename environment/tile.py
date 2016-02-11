class Tile:
    def __init__(self, x, y, traversable=True, unit = None):
        self.traversable = traversable
        self.unit = unit
        self.x = x
        self.y = y
        self.location = (x,y)