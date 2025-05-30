import pygame
import os

# Screen Settings
WIDTH = 960
HEIGHT = 540
FPS = 60

# Colors (Neon Sci-Fi Palette)
NEON_BLACK = (20, 20, 30)       # Background
NEON_CYAN = (0, 255, 255)      # Accents, borders
NEON_GREEN = (0, 255, 128)     # Player, solved terminals
NEON_RED = (255, 64, 64)       # Terminals, alarms
NEON_BLUE = (64, 128, 255)     # Locked doors
NEON_LIGHT_BLUE = (150, 200, 255)  # Unlocked doors
NEON_YELLOW = (255, 255, 64)   # Cheat text, warnings
NEON_ORANGE = (255, 165, 64)   # Messages
NEON_WHITE = (220, 220, 255)   # Text
ALARM_GLOW = (255, 64, 64, 80) # Semi-transparent alarm effect
DARK_GLOW = (40, 40, 60)       # UI panels
GRID_GLOW = (60, 60, 80)       # Room grid lines
HOLO_GLOW = (0, 255, 255, 50)  # Holographic HUD effect
PARTICLE_GLOW = (100, 255, 255, 100)  # Menu particle effect
VIGNETTE_GLOW = (255, 64, 64, 50)  # Low oxygen vignette

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
MENU_MUSIC = os.path.join(AUDIO_DIR, "ambient_sci_fi.mp3")  # Placeholder
INTERACT_SOUND = os.path.join(AUDIO_DIR, "interact_beep.mp3")  # Placeholder
UNLOCK_SOUND = os.path.join(AUDIO_DIR, "unlock_pulse.mp3")  # Placeholder

# Font Sizes
FONT_SIZE_SM = 12
FONT_SIZE_MD = 16
FONT_SIZE_LG = 24
FONT_SIZE_XL = 36

# Game Mechanics
PLAYER_SPEED = 3
OXYGEN_DEPLETION = 0.075  # Increased by 50% for challenge
SUIT_DAMAGE_RATE = 0.015  # Increased by 50% for challenge
MESSAGE_DURATION = 5000  # 5 seconds
ALARM_FLASH_INTERVAL = 500  # Milliseconds
CUTSCENE_CHAR_DELAY = 30    # Milliseconds per character
DOOR_PULSE_DURATION = 1000  # Milliseconds for unlock animation
TOOLTIP_FADE_DURATION = 300  # Milliseconds for tooltip fade

# UI Settings
BUTTON_GLOW_INTENSITY = 50  # Alpha for button hover glow
PARTICLE_COUNT = 50        # Number of background particles in menu
PARTICLE_SPEED = 0.5       # Speed of particles
MESSAGE_FADE_DURATION = 500  # Milliseconds for message fade
HUD_PANEL_ALPHA = 150      # Transparency of HUD panel (lower for less obstruction)
MINI_MAP_RADIUS = 60       # Radius of circular mini-map
VIGNETTE_THRESHOLD = 30    # Oxygen % for vignette effect

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