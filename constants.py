import ctypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN_MIDDLE = (float(SCREEN_WIDTH) / 2, float(SCREEN_HEIGHT) / 2)
SCREEN_MIDDLE_INT = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

FULL_WIDTH = user32.GetSystemMetrics(0)
FULL_HEIGHT = user32.GetSystemMetrics(1)
FULL_SIZE = (FULL_WIDTH, FULL_HEIGHT)
FULL_MIDDLE = (float(FULL_WIDTH) / 2, float(FULL_HEIGHT) / 2)
FULL_MIDDLE_INT = (FULL_WIDTH // 2, FULL_HEIGHT // 2)

SCREEN_LEFT = (FULL_WIDTH - SCREEN_WIDTH) // 2
SCREEN_TOP = (FULL_HEIGHT - SCREEN_HEIGHT) // 2
SCREEN_TOP_LEFT = (SCREEN_LEFT, SCREEN_TOP)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 254, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 200, 0)
LOCK_COLOR = (150, 0, 150)

TRANSPARENT = (0, 255, 0)

GRAVITY = 0.5

FPS = 60

PIXEL = 1

TILE_WIDTH = 20
TILE_HEIGHT = 20

LAYERS = 2
LAYER_BLOCKS = 0
LAYER_BUTTONS = 1

LEVEL_WIDTH = 25  # measured in tiles, not pixels
LEVEL_HEIGHT = 25
