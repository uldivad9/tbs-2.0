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
KEY_ECHO_START_DELAY = .2

# Time between key echos (in seconds)
KEY_ECHO_REPEAT_DELAY = .08

# height of health bar
HEALTH_BAR_HEIGHT = 4

# pixel margin on each side of health bar
HEALTH_BAR_HMARGIN = 1

# margin on each side of status icons
STATUS_ICON_HMARGIN = 1

# margin on top of status icons
STATUS_ICON_VMARGIN = 1

'''
CW - Control Window. The portion of the screen displaying controls like techs that can be used.
'''

# Top-left coordinates of the control window: (x,y)
CW_TOPLEFT = (1220, 700)

# Pixel size of the control window: (width, height)
CW_SIZE = (360,180)

# Number of pixels between the left edge of the constrol window and the first button, as well as between buttons
CW_BUTTON_HMARGIN = 10

# Number of pixels between the top edge of the control window and the first button
CW_BUTTON_VMARGIN = 10

# Button size: (width, height)
BUTTON_SIZE = (40,40)

# Buttons per row
BUTTONS_PER_ROW = 5

# Number of button rows
BUTTON_ROWS = 1

# Top-left pixel of the explanation area: (x,y)
ABILITY_DESCRIPTION_TOPLEFT = (CW_TOPLEFT[0] + 20, CW_TOPLEFT[1] + BUTTON_ROWS * BUTTON_SIZE[1] + CW_BUTTON_VMARGIN * 2)

# Pixel size of the explanation area: (width, height)
ABILITY_DESCRIPTION_SIZE = (320, 100)

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

'''
AI constants
'''

# Amount of time the AI waits before doing something
AI_DELAY = 0.1