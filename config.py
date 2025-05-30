# Screen dimensions
WIDTH = 960
HEIGHT = 540
FPS = 60

# Neon sci-fi color palette
NEON_GREEN = (0, 255, 128)    # Player, solved terminal, win text
NEON_RED = (255, 64, 64)      # Terminal, game over, alarm
NEON_BLUE = (64, 128, 255)    # Locked door
NEON_CYAN = (0, 255, 255)     # Unlocked door, UI borders
NEON_PURPLE = (128, 0, 255)   # UI accents, messages
DARK_CARBON = (20, 20, 30)    # Background (space station metal)
CARBON_GRID = (30, 30, 50)    # Grid lines
ALARM_GLOW = (255, 64, 64, 100)  # Semi-transparent alarm overlay
DARK_RED = (100, 0, 0)        # UI bars (background)
WHITE = (255, 255, 255)       # Text
YELLOW = (255, 255, 0)        # Cheat text/warnings

# Game states
STATE_MENU = "MENU"
STATE_CUTSCENE_INTRO = "CUTSCENE_INTRO"
STATE_GAMEPLAY = "GAMEPLAY"
STATE_PUZZLE_RSA = "PUZZLE_RSA"
STATE_CUTSCENE_OUTRO = "CUTSCENE_OUTRO"
STATE_GAME_OVER = "GAME_OVER"
STATE_WIN_SCREEN = "WIN_SCREEN"
STATE_HOW_TO_PLAY = "HOW_TO_PLAY"

# Animation and timing
CUTSCENE_CHAR_DELAY = 20       # Milliseconds per character (faster for polish)
MESSAGE_DURATION = 5000        # 5 seconds for messages
ALARM_FLASH_INTERVAL = 400     # Faster alarm flash for urgency
GLOW_PULSE_SPEED = 0.05       # Speed of neon glow pulse
FADE_SPEED = 5                # Speed of screen fade transitions

# Font sizes
FONT_SIZE_SM = 18
FONT_SIZE_MD = 28
FONT_SIZE_LG = 36
FONT_SIZE_XL = 60

# Player settings
PLAYER_SPEED = 3
OXYGEN_DEPLETION_RATE = 0.05
SUIT_DAMAGE_RATE = 0.01