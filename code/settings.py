# general setup
TILE_SIZE = 64
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ANIMATION_SPEED = 10

# editor graphics 
EDITOR_DATA = {
    0: {'style': 'player', 'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': '../graphics/player/idle'},
    1: {'style': 'sky',    'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': None},

    2: {'style': 'terrain', 'type': 'tile', 'menu': 'terrain', 'menu_surf': '../graphics/menu/land.png',  'preview': '../graphics/preview/land.png',  'graphics': None},
    3: {'style': 'water',   'type': 'tile', 'menu': 'terrain', 'menu_surf': '../graphics/menu/water.png', 'preview': '../graphics/preview/water.png', 'graphics': '../graphics/terrain/water/animation'},

    4: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/gold.png',    'preview': '../graphics/preview/gold.png',    'graphics': '../graphics/items/gold'},
    5: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/silver.png',  'preview': '../graphics/preview/silver.png',  'graphics': '../graphics/items/silver'},
    6: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/diamond.png', 'preview': '../graphics/preview/diamond.png', 'graphics': '../graphics/items/diamond'},

    7: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/spikes.png',      'preview': '../graphics/preview/spikes.png',      'graphics': '../graphics/enemies/spikes'},
    8: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/tooth.png',       'preview': '../graphics/preview/tooth.png',       'graphics': '../graphics/enemies/tooth/idle'},
    9: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/shell_left.png',  'preview': '../graphics/preview/shell_left.png',  'graphics': '../graphics/enemies/shell_left/idle'},
    10: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/shell_right.png', 'preview': '../graphics/preview/shell_right.png', 'graphics': '../graphics/enemies/shell_right/idle'},
    11: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/crabby.png', 'preview': '../graphics/preview/crabby.png', 'graphics': '../graphics/enemies/crabby/idle'},
    12: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': '../graphics/menu/pinkstar.png', 'preview': '../graphics/preview/pinkstar.png', 'graphics': '../graphics/enemies/pinkstar/idle'},

    13: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/small_fg.png', 'preview': '../graphics/preview/small_fg.png', 'graphics': '../graphics/terrain/palm/small_fg'},
    14: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/large_fg.png', 'preview': '../graphics/preview/large_fg.png', 'graphics': '../graphics/terrain/palm/large_fg'},
    15: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/left_fg.png',  'preview': '../graphics/preview/left_fg.png',  'graphics': '../graphics/terrain/palm/left_fg'},
    16: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': '../graphics/menu/right_fg.png', 'preview': '../graphics/preview/right_fg.png', 'graphics': '../graphics/terrain/palm/right_fg'},

    17: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/small_bg.png', 'preview': '../graphics/preview/small_bg.png', 'graphics': '../graphics/terrain/palm/small_bg'},
    18: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/large_bg.png', 'preview': '../graphics/preview/large_bg.png', 'graphics': '../graphics/terrain/palm/large_bg'},
    19: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/left_bg.png',  'preview': '../graphics/preview/left_bg.png',  'graphics': '../graphics/terrain/palm/left_bg'},
    20: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': '../graphics/menu/right_bg.png', 'preview': '../graphics/preview/right_bg.png', 'graphics': '../graphics/terrain/palm/right_bg'},

    21: {'style': 'flag', 'type': 'tile', 'menu': 'coin', 'menu_surf': '../graphics/menu/flag.png', 'preview': '../graphics/preview/flag.png', 'graphics': '../graphics/flag'}
}

# 检查周围方块的八个方向
NEIGHBOR_DIRECTIONS = {
    'A': (0, -1),
    'B': (1, -1),
    'C': (1, 0),
    'D': (1, 1),
    'E': (0, 1),
    'F': (-1, 1),
    'G': (-1, 0),
    'H': (-1, -1)
}

LEVEL_LAYERS = {
    'clouds': 1,
    'ocean': 2,
    'bg': 3,
    'water': 4,
    'main': 5
}

# 玩家动画是循环的或一次性的, 可打断的或不可打断的
PLAYER_ANIMATION_STATUS = {
    'attack 0': {'times': 'once', 'interruptible': False},
    'attack 1': {'times': 'once', 'interruptible': False},
    'attack 2': {'times': 'once', 'interruptible': False},
    'fall': {'times': 'cyclic', 'interruptible': True},
    'idle': {'times': 'cyclic', 'interruptible': True},
    'jump': {'times': 'cyclic', 'interruptible': True},
    'run': {'times': 'cyclic', 'interruptible': True},
}

TOOTH_ANIMATION_STATUS = {
    'hit': {'times': 'once', 'interruptible': False},
    'idle': {'times': 'cyclic', 'interruptible': True},
    'run': {'times': 'cyclic', 'interruptible': True},
    'dead ground': {'times': 'once', 'interruptible': False},
    'dead hit': {'times': 'once', 'interruptible': False}
}

CRABBY_ANIMATION_STATUS = {
    'anticipation': {'times': 'once', 'interruptible': True},
    'attack': {'times': 'once', 'interruptible': True},
    'dead ground': {'times': 'once', 'interruptible': False},
    'dead hit': {'times': 'once', 'interruptible': False},
    'hit': {'times': 'once', 'interruptible': False},
    'idle': {'times': 'cyclic', 'interruptible': True},
    'run': {'times': 'cyclic', 'interruptible': True}
}

PINKSTAR_ANIMATION_STATUS = {
    'anticipation': {'times': 'once', 'interruptible': True},
    'attack': {'times': 'once', 'interruptible': False},
    'dead ground': {'times': 'once', 'interruptible': False},
    'dead hit': {'times': 'once', 'interruptible': False},
    'hit': {'times': 'once', 'interruptible': False},
    'idle': {'times': 'cyclic', 'interruptible': True},
    'run': {'times': 'cyclic', 'interruptible': True}
}

GAME_STATUS = {
    'overworld': 0,
    'level 1': 1,
    'level 2': 2,
    'level 3': 3,
    'level 4': 4,
    'level 5': 5,
    'level 6': 6,
}

# colors 
SKY_COLOR = '#ddc6a1'
SEA_COLOR = '#92a9ce'
HORIZON_COLOR = '#f5f1de'
HORIZON_TOP_COLOR = '#d1aa9d'
LINE_COLOR = 'black'
BUTTON_BG_COLOR = '#33323d'
BUTTON_LINE_COLOR = '#f5f1de'
# ui
FONT_COLOR = '#33323d'
HEALTH_BAR_COLOR = '#dc4949'
# overworld
PATH_COLOR = '#a04f45'

# game default settings
INIT_MAX_LEVEL = 0
INIT_MAX_HEALTH = 100
INIT_CUR_HEALTH = 100
INIT_COINS = 0
