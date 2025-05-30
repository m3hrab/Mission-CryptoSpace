import pygame
import os

# Screen Settings
WIDTH = 960
HEIGHT = 540
FPS = 60

# Colors (Neon Sci-Fi Palette)
NEON_BLACK = (20, 20, 30)
NEON_CYAN = (0, 255, 255)
NEON_GREEN = (0, 255, 128)
NEON_RED = (255, 64, 64)
NEON_BLUE = (64, 128, 255)
NEON_LIGHT_BLUE = (150, 200, 255)
NEON_YELLOW = (255, 255, 64)
NEON_ORANGE = (255, 165, 64)
NEON_WHITE = (220, 220, 255)
NEON_PURPLE = (128, 0, 255)
ALARM_GLOW = (255, 64, 64, 80)
DARK_GLOW = (40, 40, 60)
DARK_CARBON = (20, 20, 30)
DARK_RED = (100, 0, 0)
YELLOW = (255, 255, 0)
GRID_GLOW = (60, 60, 80)
HOLO_GLOW = (0, 255, 255, 50)
PARTICLE_GLOW = (100, 255, 255, 100)
VIGNETTE_GLOW = (255, 64, 64, 50)
WHITE = (255, 255, 255)
CARBON_GRID = (30, 30, 50)

# Game States
STATE_MENU = "MENU"
STATE_CUTSCENE_INTRO = "CUTSCENE_INTRO"
STATE_GAMEPLAY = "GAMEPLAY"
STATE_PUZZLE_RSA = "PUZZLE_RSA"
STATE_CUTSCENE_OUTRO = "CUTSCENE_OUTRO"
STATE_GAME_OVER = "GAME_OVER"
STATE_WIN_SCREEN = "WIN_SCREEN"
STATE_HOW_TO_PLAY = "HOW_TO_PLAY"

# Font Paths
FONT_DIR = os.path.join("Assets", "Fonts", "Orbitron")
FONT_BLACK = os.path.join(FONT_DIR, "Orbitron-Black.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "Orbitron-Bold.ttf")
FONT_MEDIUM = os.path.join(FONT_DIR, "Orbitron-Medium.ttf")

# Audio Paths
AUDIO_DIR = os.path.join("Assets", "Audio")
MENU_MUSIC = os.path.join(AUDIO_DIR, "ambient_sci_fi.mp3")
STATION_AMBIENCE = os.path.join(AUDIO_DIR, "station_ambience.mp3")
CUTSCENE_THEME = os.path.join(AUDIO_DIR, "cutscene_theme.mp3")
INTERACT_SOUND = os.path.join(AUDIO_DIR, "interact_beep.mp3")
UNLOCK_SOUND = os.path.join(AUDIO_DIR, "unlock_pulse.mp3")
TERMINAL_TYPING = os.path.join(AUDIO_DIR, "terminal_typing.mp3")
TERMINAL_SUCCESS = os.path.join(AUDIO_DIR, "terminal_success.mp3")
TERMINAL_ERROR = os.path.join(AUDIO_DIR, "terminal_error.mp3")
LOW_OXYGEN_ALERT = os.path.join(AUDIO_DIR, "low_oxygen_alert.mp3")
PLAYER_DEATH = os.path.join(AUDIO_DIR, "player_death.mp3")

# Font Sizes
FONT_SIZE_SM = 12
FONT_SIZE_MD = 16
FONT_SIZE_LG = 22
FONT_SIZE_XL = 28

# Game Mechanics
PLAYER_SPEED = 3
OXYGEN_DEPLETION = 0.2
SUIT_DAMAGE_RATE = 0.085
MESSAGE_DURATION = 5000
MESSAGE_DURATION_WRONG = 6000  # Duration for terminal wrong input message
ALARM_FLASH_INTERVAL = 500
CUTSCENE_CHAR_DELAY = 30
DOOR_PULSE_DURATION = 1000
TOOLTIP_FADE_DURATION = 300
OXYGEN_DEPLETION_RATE = 0.05  # Oxygen depletion rate per second
SUIT_DAMAGE_RATE = 0.01  # Suit damage rate per second
GLOW_SPEED = 0.05  # Speed of neon glow pulse

# UI Settings
BUTTON_GLOW_INTENSITY = 50
PARTICLE_COUNT = 50
PARTICLE_SPEED = 0.5
MESSAGE_FADE_DURATION = 500
HUD_PANEL_ALPHA = 150
MINI_MAP_RADIUS = 60
VIGNETTE_THRESHOLD = 30

# Cutscene Scripts
INTRO_CUTSCENE = [
    "Aboard the Elysium-7 Martian station, you, a cryptographic analyst, stand alone.",
    "Your crew is stranded in Valles Marineris after a lander crash.",
    "An alarm blares: a hull breach has compromised your suit.",
    "Worse, the station's systems are locked by the Sigma protocol's encryption.",
    "Every door, terminal, and life support system requires decryption.",
    "Your mission: unlock the systems, repair your suit, and send a distress signal.",
    "Fragments of encryption keys are scattered across the station.",
    "Time is running out. Decrypt the codes. Survive. Save humanity."
]

FINAL_CUTSCENE = [
    "The final code unlocks the station's core systems.",
    "A distress signal pulses toward Earth, a beacon of hope.",
    "The alarms fade, replaced by the hum of restored life support.",
    "Alone but victorious, you've secured Elysium-7.",
    "Help is coming. Mission accomplished."
]

HOW_TO_PLAY_TEXT = [
    "--- HOW TO PLAY ---",
    "",
    "Move: Arrow Keys or WASD",
    "Interact: Press 'E' near objects",
    "Solve Puzzles: Calculate M, enter, press ENTER",
    "  (M = C^d mod n, where n = p*q, d = mod_inverse(e, (p-1)*(q-1)))",
    "Press 'P': Toggle puzzle solution (cheat)",
    "Exit Puzzle/Instructions: Press 'ESC'",
    "Unlock Doors: Decrypt terminals to access new areas",
    "Survive: Monitor Oxygen & Suit Integrity",
    "Goal: Decrypt Sigma protocol, send distress signal"
]