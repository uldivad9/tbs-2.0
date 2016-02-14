'''
BD - Battle Display. The portion of the screen displaying a portion of the world, with units and terrain and stuff.
'''

# Margin size to the left and right, in pixels
BD_HMARGIN = 2

# Margin size to the top and bottom, in pixels
BD_VMARGIN = 2

# Size of each tile, in pixels
TILESIZE = 60

# Number of tiles in a column
TILESDOWN = 14

# Number of tiles in a row
TILESACROSS = 20

# Pixel size of the battle display: (width, height)
BD_SIZE = (TILESIZE * TILESACROSS + 1, TILESIZE * TILESDOWN + 1)

'''
CS - Console. The portion of the screen displaying information about the selected unit.
'''

# Number of pixels between the left edge of the battle display and the console.
CS_HMARGIN = 2

# Number of pixels between the top edge of the window and the battle display.
CS_VMARGIN = 60

# Pixel size of the console: (width, height)
CS_SIZE = (380, 380)

# Time before key echos (in seconds)
KEY_ECHO_START_DELAY = .3

# Time between key echos (in seconds)
KEY_ECHO_REPEAT_DELAY = .10

'''
Animation constants
'''

# Speed, in pixels per second, of a MovementAnimation
MOVE_ANIM_SPEED = 500

# Acceleration factor, in pixels per second squared, of a MovementAnimation
MOVE_ANIM_ACCEL = 2000

# Starting speed, in pixels per second, of a DamageText
DAMAGE_TEXT_SPEED = 50

# Lifetime, in seconds, of a DamageText
DAMAGE_TEXT_LIFETIME = 0.5

# Lifetime, in seconds, of an Explosion
EXPLOSION_LIFETIME = 0.5