import pygame
import sys
import time
import math
import random

# --- Constants ---
# Screen dimensions
WIDTH, HEIGHT = 960, 540
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)   # Player color, solved terminal, win text
RED = (255, 0, 0)     # Terminal color, game over text, alarm
BLUE = (0, 0, 255)    # Door color
GREY = (100, 100, 100) # Room walls/floor
DARK_GREY = (50, 50, 50) # Darker shade for backgrounds
ALARM_COLOR = (255, 0, 0, 80) # Semi-transparent red for alarm effect
DARK_RED = (150, 0, 0) # For UI bars
LIGHT_BLUE = (150, 200, 255) # For unlocked door
CYAN = (0, 255, 255)  # For UI borders/accents
YELLOW = (255, 255, 0) # For cheat text/warnings
ORANGE = (255, 165, 0) # For messages

# Game States
GAME_STATE_MENU = "MENU"
GAME_STATE_CUTSCENE_INTRO = "CUTSCENE_INTRO"
GAME_STATE_GAMEPLAY = "GAMEPLAY"
GAME_STATE_PUZZLE_RSA = "PUZZLE_RSA"
GAME_STATE_CUTSCENE_OUTRO = "CUTSCENE_OUTRO"
GAME_STATE_GAME_OVER = "GAME_OVER"
GAME_STATE_WIN_SCREEN = "WIN_SCREEN"
GAME_STATE_HOW_TO_PLAY = "HOW_TO_PLAY"

# Cutscene timing
CUTSCENE_CHAR_DELAY = 30 # Milliseconds per character

# UI Constants
MESSAGE_DURATION = 5000 # 5 seconds for temporary messages

# --- Pygame Initialization ---
pygame.init()

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crypternity: Martian Decipher")
CLOCK = pygame.time.Clock()

# --- Fonts ---
FONT_SM = pygame.font.Font(None, 18)
FONT_MD = pygame.font.Font(None, 28)
FONT_LG = pygame.font.Font(None, 36)
FONT_XL = pygame.font.Font(None, 60) # Extra large for titles

# --- Utility Functions ---
def wrap_text(surface, text, font, color, rect):
    """Draws text that wraps within a given rectangle."""
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() <= rect.width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    y_offset = rect.y
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, y_offset))
        y_offset += font.get_height() + 5
    return y_offset # Return the end y-coordinate for next text block

# --- RSA Utility Functions ---
def extended_gcd(a, b):
    """Calculates gcd(a, b) and coefficients x, y such that ax + by = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi_n):
    """Calculates the modular multiplicative inverse of e modulo phi_n."""
    gcd, x, y = extended_gcd(e, phi_n)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist (e and phi_n are not coprime)")
    else:
        return (x % phi_n + phi_n) % phi_n

def decrypt_rsa(ciphertext, private_key_d, n):
    """Decrypts RSA ciphertext using the private key (d, n)."""
    return pow(ciphertext, private_key_d, n)

class PuzzleGenerator:
    """Generates valid RSA puzzle parameters."""
    def __init__(self):
        self.primes = [
            11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
        ]

    def _get_random_prime(self, exclude=None):
        """Returns a random prime from the list, excluding a specific one."""
        if exclude is None:
            return random.choice(self.primes)
        available_primes = [p for p in self.primes if p != exclude]
        return random.choice(available_primes)

    def generate_puzzle(self):
        """Generates a new, valid RSA puzzle."""
        while True:
            p = self._get_random_prime()
            q = self._get_random_prime(exclude=p)

            n = p * q
            phi_n = (p - 1) * (q - 1)

            # Choose e such that 1 < e < phi_n and gcd(e, phi_n) = 1
            e_candidates = [i for i in range(2, phi_n) if math.gcd(i, phi_n) == 1]
            if not e_candidates: # Should not happen with typical primes, but good check
                continue
            e = random.choice(e_candidates)

            try:
                # Ensure d exists
                d = mod_inverse(e, phi_n)

                # Choose a plaintext M such that 0 < M < n
                M = random.randint(10, n // 2) # Keep M reasonably small

                # Calculate ciphertext C
                C = pow(M, e, n)

                return {'p': p, 'q': q, 'e': e, 'C': C, 'M_solution': str(M)}
            except ValueError:
                # If mod_inverse fails (shouldn't if e_candidates are properly chosen), retry
                continue

# --- Base Classes ---
class GameObject(pygame.sprite.Sprite):
    """Base class for all game objects."""
    def __init__(self, x, y, width, height, color, name="GameObject"):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name

    def draw(self, surface):
        """Draws the object on the given surface."""
        surface.blit(self.image, self.rect)

class Button(GameObject):
    """A clickable button."""
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color, action=None):
        super().__init__(x, y, width, height, color, "Button")
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.current_color = color

    def draw(self, surface):
        """Draws the button with its current state."""
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, CYAN, self.rect, 2, border_radius=5) # Border
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handles mouse events for the button."""
        if event.type == pygame.MOUSEMOTION:
            self.current_color = self.hover_color if self.rect.collidepoint(event.pos) else self.color
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
                return True
        return False

# --- Game Entities ---
class Player(GameObject):
    """The player character."""
    def __init__(self, x, y):
        super().__init__(x, y, 25, 25, GREEN, "Player")
        self.speed = 3
        self.oxygen = 100.0
        self.suit_integrity = 100.0
        self.last_oxygen_tick = pygame.time.get_ticks()
        self.oxygen_depletion_rate = 0.05 # Reduced rate for clarity
        self.suit_damage_rate = 0.01 # Small constant damage when moving
        self.is_alive = True

    def update(self, keys):
        """Updates player position and vital stats."""
        if not self.is_alive:
            return

        moved = False
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            moved = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
            moved = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            moved = True

        # Boundary checks
        self.rect.left = max(50, self.rect.left)
        self.rect.right = min(WIDTH - 50, self.rect.right)
        self.rect.top = max(50, self.rect.top)
        self.rect.bottom = min(HEIGHT - 50, self.rect.bottom)

        current_time = pygame.time.get_ticks()

        # Suit integrity and Oxygen depletion
        if current_time - self.last_oxygen_tick >= 1000: # Every second
            if moved: # Player takes minimal suit damage when moving
                self.suit_integrity -= self.suit_damage_rate
                self.suit_integrity = max(0, self.suit_integrity)

            if self.suit_integrity < 100: # Only deplete oxygen if suit is damaged
                self.oxygen -= self.oxygen_depletion_rate
            self.last_oxygen_tick = current_time

            if self.oxygen <= 0:
                self.oxygen = 0
                self.is_alive = False # Player dies if oxygen runs out
            if self.suit_integrity <= 0:
                self.suit_integrity = 0
                self.is_alive = False # Player dies if suit integrity reaches 0

    def reset(self):
        """Resets player state for a new game."""
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.oxygen = 100.0
        self.suit_integrity = 100.0
        self.is_alive = True
        self.last_oxygen_tick = pygame.time.get_ticks()


class Door(GameObject):
    """A door that can be locked or unlocked."""
    def __init__(self, x, y, width, height, target_room_key, target_x, target_y):
        super().__init__(x, y, width, height, BLUE, "Door")
        self.target_room_key = target_room_key
        self.target_x = target_x
        self.target_y = target_y
        self.initial_locked_state = True # Store initial state for reset
        self.is_locked = self.initial_locked_state
        self.unlocked_color = LIGHT_BLUE
        self._update_color()

    def _update_color(self):
        """Sets the door's color based on its locked state."""
        self.image.fill(self.unlocked_color if not self.is_locked else BLUE)

    def interact(self, player_instance, game_manager):
        """Handles player interaction with the door."""
        if not self.is_locked:
            game_manager.set_game_message("Door Unlocked! Transitioning...", ORANGE)
            if self.target_room_key == "win_room":
                game_manager.start_final_cutscene()
            else:
                game_manager.set_current_room(self.target_room_key)
                player_instance.rect.x = self.target_x
                player_instance.rect.y = self.target_y
        else:
            game_manager.set_game_message("Door Locked. Find a way to unlock it.", RED)

    def unlock(self):
        """Unlocks the door."""
        self.is_locked = False
        self._update_color()

    def reset(self):
        """Resets the door to its initial locked state."""
        self.is_locked = self.initial_locked_state
        self._update_color()

class Terminal(GameObject):
    """An interactive terminal with an RSA puzzle."""
    def __init__(self, x, y, puzzle_generator, unlocks_door=None, is_final_terminal=False):
        super().__init__(x, y, 70, 100, RED, "Terminal")
        self.puzzle_generator = puzzle_generator
        self.puzzle_data = {} # To be generated on game start
        self.is_locked = True
        self.input_text = ""
        self.current_message = ""
        self.default_message = "" # Stores the default puzzle info
        self.unlocks_door = unlocks_door
        self.is_final_terminal = is_final_terminal
        self.solved_color = GREEN
        self.calculated_solution = None
        self.show_answer_cheat = False
        self.last_message_time = 0
        self.message_display_time = 0

        self.generate_new_puzzle() # Generate puzzle data on initialization

    def generate_new_puzzle(self):
        """Generates a new RSA puzzle for this terminal."""
        self.puzzle_data = self.puzzle_generator.generate_puzzle()
        self.calculated_solution = self.puzzle_data['M_solution']
        self._update_default_message()

    def _update_default_message(self):
        """Updates the default puzzle message."""
        self.default_message = (f"Authentication required. Decrypt:\n"
                                f"  p={self.puzzle_data['p']}, q={self.puzzle_data['q']}\n"
                                f"  e={self.puzzle_data['e']}\n"
                                f"  Ciphertext C={self.puzzle_data['C']}\n"
                                f"Enter plaintext M:")
        if self.is_locked:
            self.current_message = self.default_message
        else:
            self.current_message = "Terminal already decrypted!\nPress ESC to return."


    def interact(self, player_instance, game_manager):
        """Initiates the RSA puzzle interface."""
        game_manager.set_game_state(GAME_STATE_PUZZLE_RSA)
        game_manager.set_current_puzzle(self)
        if self.is_locked:
            self.current_message = self.default_message
            self.input_text = ""
        else:
            self.current_message = "Terminal already decrypted!\nPress ESC to return."
        self.show_answer_cheat = False
        self.last_message_time = 0 # Reset message timer

    def handle_input(self, event, game_manager):
        """Handles input for the puzzle screen."""
        if self.is_locked:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.check_solution(game_manager)
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_p: # Cheat key for showing solution
                    self.show_answer_cheat = not self.show_answer_cheat
                else:
                    self.input_text += event.unicode

    def check_solution(self, game_manager):
        """Checks the player's entered solution."""
        if self.calculated_solution is None:
            self.set_temp_message("Puzzle error. Cannot solve.", RED)
            return

        player_solution = self.input_text.strip()
        if player_solution == self.calculated_solution:
            self.is_locked = False
            self.set_temp_message("Access Granted! System unlocked.", GREEN)
            self.image.fill(self.solved_color)
            if self.unlocks_door:
                self.unlocks_door.unlock()
                game_manager.set_game_message(f"{self.unlocks_door.name} unlocked!", ORANGE)
            if self.is_final_terminal:
                game_manager.alarm_on = False # Turn off alarm when final terminal is solved
                game_manager.set_game_message("Final terminal activated! Distress signal being sent...", GREEN)
                game_manager.start_final_cutscene()
                return
            game_manager.set_game_state(GAME_STATE_GAMEPLAY)
        else:
            self.set_temp_message("Incorrect decryption. Try again.", RED)
        self.input_text = ""

    def set_temp_message(self, message, color):
        """Sets a temporary message that reverts to default after a delay."""
        self.current_message = message
        self.message_display_time = pygame.time.get_ticks() + MESSAGE_DURATION

    def update(self):
        """Updates the terminal's state, specifically for temporary messages."""
        if self.message_display_time > 0 and pygame.time.get_ticks() > self.message_display_time:
            self.current_message = self.default_message
            self.message_display_time = 0

    def draw_puzzle_screen(self, surface):
        """Draws the RSA puzzle interface."""
        # Thematic puzzle overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Puzzle window border
        puzzle_window_rect = pygame.Rect(WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8)
        pygame.draw.rect(surface, DARK_GREY, puzzle_window_rect)
        pygame.draw.rect(surface, CYAN, puzzle_window_rect, 3) # Thematic border

        # Display current message, handling temporary messages
        message_rect = pygame.Rect(puzzle_window_rect.x + 20, puzzle_window_rect.y + 30, puzzle_window_rect.width - 40, puzzle_window_rect.height // 2)
        y_after_message = wrap_text(surface, self.current_message, FONT_MD, WHITE, message_rect)

        if self.is_locked:
            input_rect = pygame.Rect(WIDTH // 4, HEIGHT - 150, WIDTH // 2, 40)
            pygame.draw.rect(surface, WHITE, input_rect, 2)
            input_surface = FONT_MD.render(self.input_text, True, WHITE)
            surface.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))

            if self.show_answer_cheat and self.calculated_solution is not None:
                cheat_text = FONT_SM.render(f"Solution: {self.calculated_solution}", True, YELLOW)
                surface.blit(cheat_text, (input_rect.x, input_rect.y + 45))

        hint_surface = FONT_SM.render("Press ENTER to submit. Press 'P' for hint/solution. Press ESC to return to game.", True, WHITE)
        surface.blit(hint_surface, (WIDTH // 2 - hint_surface.get_width() // 2, HEIGHT - 80))

    def reset(self):
        """Resets the terminal to its initial locked state and generates a new puzzle."""
        self.is_locked = True
        self.image.fill(RED)
        self.input_text = ""
        self.show_answer_cheat = False
        self.last_message_time = 0
        self.message_display_time = 0
        self.generate_new_puzzle()


class Room:
    """Represents a game room."""
    def __init__(self, name, interactive_objects):
        self.name = name
        self.interactive_objects = pygame.sprite.Group(interactive_objects)

    def draw(self, surface):
        """Draws the room background and its interactive objects."""
        # Thematic room background
        surface.fill(DARK_GREY) # Simulating a darker, metallic floor
        pygame.draw.rect(surface, BLACK, (50, 50, WIDTH - 100, HEIGHT - 100)) # Central area for movement

        # Futuristic grid pattern
        for i in range(50, WIDTH - 50, 20):
            pygame.draw.line(surface, (30, 30, 30), (i, 50), (i, HEIGHT - 50), 1)
        for i in range(50, HEIGHT - 50, 20):
            pygame.draw.line(surface, (50, 50, 50), (50, i), (WIDTH - 50, i), 1)

        pygame.draw.rect(surface, GREY, (50, 50, WIDTH - 100, HEIGHT - 100), 5) # Room border

        self.interactive_objects.draw(surface)

        room_name_surface = FONT_LG.render(self.name, True, WHITE)
        surface.blit(room_name_surface, (WIDTH // 2 - room_name_surface.get_width() // 2, 10))


class CutsceneManager:
    """Manages cutscene playback with text wrapping and manual progression."""
    def __init__(self):
        self.script = []
        self.current_line_index = 0
        self.current_char_index = 0
        self.last_char_time = 0
        self.finished_typing_current_line = False
        self.skip_button = Button(WIDTH - 150, HEIGHT - 60, 120, 40, "Skip", FONT_MD, DARK_GREY, GREY, WHITE, self.skip_cutscene)
        self.next_button = Button(WIDTH - 280, HEIGHT - 60, 120, 40, "Next", FONT_MD, DARK_GREY, GREY, WHITE, self.next_line)
        self.game_manager_ref = None # Reference to GameManager for state changes

    def set_game_manager(self, gm):
        self.game_manager_ref = gm

    def start_cutscene(self, script):
        """Initializes a new cutscene."""
        self.script = script
        self.current_line_index = 0
        self.current_char_index = 0
        self.last_char_time = pygame.time.get_ticks()
        self.finished_typing_current_line = False

    def next_line(self):
        """Advances to the next line or finishes typing current line."""
        if self.current_line_index >= len(self.script):
            self._finish_cutscene()
            return

        if not self.finished_typing_current_line:
            self.current_char_index = len(self.script[self.current_line_index])
            self.finished_typing_current_line = True
        else:
            self.current_line_index += 1
            self.current_char_index = 0
            self.last_char_time = pygame.time.get_ticks()
            self.finished_typing_current_line = False
            if self.current_line_index >= len(self.script):
                self._finish_cutscene()

    def skip_cutscene(self):
        """Skips to the end of the current cutscene."""
        self.current_line_index = len(self.script)
        self._finish_cutscene()

    def _finish_cutscene(self):
        """Handles actions after the cutscene finishes."""
        if self.game_manager_ref:
            if self.game_manager_ref.game_state == GAME_STATE_CUTSCENE_INTRO:
                self.game_manager_ref.start_gameplay()
            elif self.game_manager_ref.game_state == GAME_STATE_CUTSCENE_OUTRO:
                self.game_manager_ref.show_win_screen()

    def update(self):
        """Updates cutscene state (character typing animation)."""
        if self.current_line_index < len(self.script) and not self.finished_typing_current_line:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_char_time >= CUTSCENE_CHAR_DELAY:
                self.current_char_index = min(len(self.script[self.current_line_index]), self.current_char_index + 1)
                self.last_char_time = current_time
                if self.current_char_index == len(self.script[self.current_line_index]):
                    self.finished_typing_current_line = True

    def handle_event(self, event):
        """Handles input events for cutscene buttons."""
        self.skip_button.handle_event(event)
        self.next_button.handle_event(event)
        # Allow return key to also act as 'Next'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.next_line()

    def draw(self, surface):
        """Draws the current cutscene text and buttons."""
        surface.fill(BLACK)
        display_text = ""
        if self.current_line_index < len(self.script):
            full_line_text = self.script[self.current_line_index]
            display_text = full_line_text[:self.current_char_index]

        text_rect = pygame.Rect(50, HEIGHT // 3, WIDTH - 100, HEIGHT // 3)
        wrap_text(surface, display_text, FONT_MD, WHITE, text_rect)

        # Draw buttons
        self.skip_button.draw(surface)
        self.next_button.draw(surface)

class UIManager:
    """Manages all UI drawing logic."""
    def __init__(self, game_manager):
        self.gm = game_manager
        self.game_message = ""
        self.game_message_color = WHITE
        self.message_start_time = 0

    def set_game_message(self, message, color=WHITE):
        """Sets a temporary message to be displayed at the bottom of the screen."""
        self.game_message = message
        self.game_message_color = color
        self.message_start_time = pygame.time.get_ticks()

    def draw_gameplay_ui(self, surface):
        """Draws the UI for the gameplay screen."""
        # UI panel
        ui_panel_rect = pygame.Rect(5, 5, 140, 70)
        pygame.draw.rect(surface, DARK_GREY, ui_panel_rect, border_radius=5)
        pygame.draw.rect(surface, CYAN, ui_panel_rect, 2, border_radius=5)

        # Grid behind bars
        for i in range(ui_panel_rect.left + 5, ui_panel_rect.right - 5, 8):
            pygame.draw.line(surface, (40, 40, 40), (i, ui_panel_rect.top + 5), (i, ui_panel_rect.bottom - 5), 1)
        for i in range(ui_panel_rect.top + 5, ui_panel_rect.bottom - 5, 8):
            pygame.draw.line(surface, (40, 40, 40), (ui_panel_rect.left + 5, i), (ui_panel_rect.right - 5, i), 1)

        # Oxygen Bar
        oxygen_bar_width = int(120 * (self.gm.player.oxygen / 100))
        pygame.draw.rect(surface, DARK_RED, (15, 15, 120, 20), 0, 3)
        pygame.draw.rect(surface, GREEN, (15, 15, oxygen_bar_width, 20), 0, 3)
        oxygen_text = FONT_SM.render(f"O2: {int(self.gm.player.oxygen)}%", True, WHITE)
        surface.blit(oxygen_text, (25, 19))

        # Suit Integrity Bar
        suit_bar_width = int(120 * (self.gm.player.suit_integrity / 100))
        pygame.draw.rect(surface, DARK_RED, (15, 45, 120, 20), 0, 3)
        pygame.draw.rect(surface, LIGHT_BLUE, (15, 45, suit_bar_width, 20), 0, 3)
        suit_text = FONT_SM.render(f"SUIT: {int(self.gm.player.suit_integrity)}%", True, WHITE)
        surface.blit(suit_text, (25, 49))

        # Show interaction prompt or temporary message
        if self.game_message and (pygame.time.get_ticks() - self.message_start_time < MESSAGE_DURATION):
            prompt_surface = FONT_MD.render(self.game_message, True, self.game_message_color)
            surface.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT - 30))
        else:
            interaction_prompt = ""
            for obj in self.gm.current_room.interactive_objects:
                if self.gm.player.rect.colliderect(obj.rect):
                    interaction_prompt = f"Press 'E' to interact with {obj.name}"
                    break
            if interaction_prompt:
                prompt_surface = FONT_MD.render(interaction_prompt, True, WHITE)
                surface.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT - 30))

        # Alarm Effect
        if self.gm.alarm_on and self.gm.alarm_visible:
            alarm_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alarm_overlay.fill(ALARM_COLOR)
            surface.blit(alarm_overlay, (0, 0))

    def _draw_centered_text(self, surface, text, font, color, y_offset):
        """Helper to draw centered text on a surface."""
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))

    def draw_menu_screen(self, surface, buttons):
        """Draws the main menu screen."""
        surface.fill(DARK_GREY)
        pygame.draw.rect(surface, BLACK, (WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100), border_radius=10)
        pygame.draw.rect(surface, CYAN, (WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100), 3, border_radius=10)

        self._draw_centered_text(surface, "Crypternity", FONT_XL, WHITE, HEIGHT // 4 + 30)
        self._draw_centered_text(surface, "Martian Decipher", FONT_MD, CYAN, HEIGHT // 4 + 30 + FONT_XL.get_height() + 10)

        for button in buttons:
            button.draw(surface)

    def draw_how_to_play_screen(self, surface, text_lines, back_button):
        """Draws the how-to-play instructions screen."""
        surface.fill(DARK_GREY)
        pygame.draw.rect(surface, BLACK, (WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8), border_radius=10)
        pygame.draw.rect(surface, CYAN, (WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8), 3, border_radius=10)

        y_offset_how_to_play = HEIGHT // 8 + 30
        for line in text_lines:
            self._draw_centered_text(surface, line, FONT_MD, WHITE, y_offset_how_to_play)
            y_offset_how_to_play += 25

        back_button.draw(surface)

    def draw_game_over_screen(self, surface, restart_button):
        """Draws the game over screen."""
        surface.fill(BLACK)
        self._draw_centered_text(surface, "MISSION FAILED - GAME OVER", FONT_LG, RED, HEIGHT // 2 - 80)
        self._draw_centered_text(surface, "Oxygen Depleted or Suit Breached!", FONT_MD, WHITE, HEIGHT // 2 - 30)
        restart_button.draw(surface)
        self._draw_centered_text(surface, "Press ESC to exit", FONT_MD, WHITE, HEIGHT // 2 + 100)


    def draw_win_screen(self, surface, restart_button):
        """Draws the win screen."""
        surface.fill(BLACK)
        self._draw_centered_text(surface, "MISSION SUCCESS! Distress Signal Sent!", FONT_LG, GREEN, HEIGHT // 2 - 80)
        self._draw_centered_text(surface, "You have saved humanity!", FONT_MD, WHITE, HEIGHT // 2 - 30)
        restart_button.draw(surface)
        self._draw_centered_text(surface, "Press ESC to exit", FONT_MD, WHITE, HEIGHT // 2 + 100)


class GameManager:
    """Manages the overall game state, assets, and flow."""
    def __init__(self):
        self.game_state = GAME_STATE_MENU
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.puzzle_generator = PuzzleGenerator()
        self.rooms = {}
        self.current_room = None
        self.current_puzzle = None
        self.cutscene_manager = CutsceneManager()
        self.cutscene_manager.set_game_manager(self) # Pass reference
        self.ui_manager = UIManager(self) # Pass reference
        self.running = True
        self.alarm_on = True
        self.alarm_flash_interval = 500
        self.last_alarm_flash_time = 0
        self.alarm_visible = False

        # Cutscene Data
        self.intro_cutscene_script = [
            "You are an astronaut and cryptographic security analyst, alone aboard a Martian space station.",
            "The rest of the crew is on a mission in the Valles Marineris canyon.",
            "You were in charge of an experimental project: encrypting vital systems using advanced security algorithms.",
            "Suddenly, an alarm goes off: there's a breach in the station! Your spacesuit is damaged.",
            "But even stranger: the backup systems refuse to activate.",
            "A message appears on the main screen:",
            "        \"Authentication required. Decrypt the Sigma protocol.\"",
            "Your systems are locked down. Every door, every terminal, every life support system is protected by an encrypted code.",
            "You must decrypt these codes to survive: repair your suit, access emergency oxygen, activate the radio beacon.",
            "As a last hope, you pick up a faint signal: the Earth lander has crashed, but it contained fragments of encryption keys.",
            "It's up to you to find them, reassemble them, and send a clear distress message before it's too late.",
            "Your mission begins now..."
        ]

        self.final_cutscene_script = [
            "With the last code decrypted, the main systems flicker to life.",
            "A powerful signal beams towards Earth, carrying your distress message.",
            "The station's alarms quiet, replaced by the hum of stable life support.",
            "Though alone, you've secured the station and sent a beacon of hope.",
            "Help is on the way. Mission accomplished."
        ]

        self.how_to_play_text = [
            "--- HOW TO PLAY ---",
            "Move: Arrow Keys or WASD",
            "Interact: Press 'E' near objects",
            "Solve Puzzles: Calculate M, enter, press ENTER",
            "  (M = C^d mod n)",
            "  (n = p*q, phi_n = (p-1)*(q-1), d = mod_inverse(e, phi_n))",
            "Press 'P': Show/hide solution for puzzle (cheat)",
            "Exit Puzzle/Instructions: Press 'ESC'",
            "Unlock Doors: Decrypt terminals to open new paths",
            "Survive: Keep an eye on Oxygen & Suit Integrity!",
            "Goal: Decrypt the Sigma protocol and send distress signal."
        ]

        self._setup_game_elements()

    def _setup_game_elements(self):
        """Initializes game rooms, terminals, and doors."""
        # Create interactive objects (Doors are defined before terminals that unlock them)
        self.door_control_to_lab = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "lab_room", 80, HEIGHT // 2)
        self.door_lab_to_control = Door(50, HEIGHT // 2 - 50, 30, 100, "control_room", WIDTH - 130, HEIGHT // 2)
        self.door_lab_to_distress = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "distress_room", 80, HEIGHT // 2)
        self.door_distress_to_lab = Door(50, HEIGHT // 2 - 50, 30, 100, "lab_room", WIDTH - 130, HEIGHT // 2)

        self.terminal_control = Terminal(200, 300, self.puzzle_generator, unlocks_door=self.door_control_to_lab)
        self.terminal_lab = Terminal(WIDTH - 300, 300, self.puzzle_generator, unlocks_door=self.door_lab_to_distress)
        self.terminal_distress = Terminal(WIDTH // 2 - 35, HEIGHT // 2 - 50, self.puzzle_generator, unlocks_door=None, is_final_terminal=True)

        self.all_doors = [self.door_control_to_lab, self.door_lab_to_control, self.door_lab_to_distress, self.door_distress_to_lab]
        self.all_terminals = [self.terminal_control, self.terminal_lab, self.terminal_distress]

        self.rooms = {
            "control_room": Room("Control Room", [self.terminal_control, self.door_control_to_lab]),
            "lab_room": Room("Research Lab", [self.door_lab_to_control, self.terminal_lab, self.door_lab_to_distress]),
            "distress_room": Room("Distress Signal Room", [self.door_distress_to_lab, self.terminal_distress]),
            "win_room": Room("Win Screen", []) # A dummy room for win condition transition
        }
        self.current_room = self.rooms["control_room"]

        # Menu Buttons
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, "Start Mission", FONT_MD, DARK_GREY, GREY, WHITE, self.start_intro_cutscene)
        self.how_to_play_button_menu = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50, "How to Play", FONT_MD, DARK_GREY, GREY, WHITE, self.show_how_to_play_screen)
        self.exit_button_menu = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Exit", FONT_MD, DARK_RED, RED, WHITE, self.exit_game)
        self.back_button_how_to_play = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back to Main Menu", FONT_MD, DARK_GREY, GREY, WHITE, lambda: self.set_game_state(GAME_STATE_MENU))
        self.restart_button_game_over = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Main Menu", FONT_MD, DARK_GREY, GREY, WHITE, self.reset_game)


    def set_game_state(self, new_state):
        """Changes the current game state."""
        self.game_state = new_state

    def set_current_room(self, room_key):
        """Sets the current active room."""
        self.current_room = self.rooms[room_key]
        self.ui_manager.set_game_message(f"Entering: {self.current_room.name}", CYAN)

    def set_current_puzzle(self, puzzle_obj):
        """Sets the currently active terminal puzzle."""
        self.current_puzzle = puzzle_obj

    def start_intro_cutscene(self):
        """Starts the introductory cutscene."""
        self.set_game_state(GAME_STATE_CUTSCENE_INTRO)
        self.cutscene_manager.start_cutscene(self.intro_cutscene_script)

    def start_gameplay(self):
        """Transitions to gameplay state."""
        self.set_game_state(GAME_STATE_GAMEPLAY)
        self.player.last_oxygen_tick = pygame.time.get_ticks() # Reset oxygen timer
        self.ui_manager.set_game_message("Mission started! Decrypt terminals (Press 'E' to interact)", CYAN)

    def show_how_to_play_screen(self):
        """Transitions to the how-to-play screen."""
        self.set_game_state(GAME_STATE_HOW_TO_PLAY)

    def exit_game(self):
        """Sets the game to stop running."""
        self.running = False

    def start_final_cutscene(self):
        """Starts the final cutscene."""
        self.set_game_state(GAME_STATE_CUTSCENE_OUTRO)
        self.cutscene_manager.start_cutscene(self.final_cutscene_script)

    def show_win_screen(self):
        """Transitions to the win screen."""
        self.set_game_state(GAME_STATE_WIN_SCREEN)

    def set_game_message(self, message, color=WHITE):
        """Wrapper for UIManager's set_game_message."""
        self.ui_manager.set_game_message(message, color)

    def reset_game(self):
        """Resets all game elements to their initial state for a new game."""
        self.player.reset()
        for door in self.all_doors:
            door.reset()
        for terminal in self.all_terminals:
            terminal.reset() # This also generates new puzzles
        self.current_room = self.rooms["control_room"]
        self.current_puzzle = None
        self.alarm_on = True
        self.alarm_visible = False
        self.last_alarm_flash_time = 0
        self.ui_manager.set_game_message("") # Clear any messages
        self.set_game_state(GAME_STATE_MENU)

    def handle_events(self):
        """Handles all Pygame events based on the current game state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == GAME_STATE_MENU:
                self.start_button.handle_event(event)
                self.how_to_play_button_menu.handle_event(event)
                self.exit_button_menu.handle_event(event)
            elif self.game_state == GAME_STATE_HOW_TO_PLAY:
                self.back_button_how_to_play.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.set_game_state(GAME_STATE_MENU)
            elif self.game_state in [GAME_STATE_CUTSCENE_INTRO, GAME_STATE_CUTSCENE_OUTRO]:
                self.cutscene_manager.handle_event(event)
            elif self.game_state == GAME_STATE_GAMEPLAY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        interacted = False
                        for obj in self.current_room.interactive_objects:
                            if self.player.rect.colliderect(obj.rect):
                                obj.interact(self.player, self)
                                interacted = True
                                break
                        if not interacted:
                            self.set_game_message("Nothing to interact with here.", YELLOW)
                    if event.key == pygame.K_ESCAPE:
                        self.show_how_to_play_screen()
            elif self.game_state == GAME_STATE_PUZZLE_RSA:
                if self.current_puzzle:
                    self.current_puzzle.handle_input(event, self)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.set_game_state(GAME_STATE_GAMEPLAY)
                    if self.current_puzzle:
                        self.current_puzzle.input_text = ""
                        self.current_puzzle.show_answer_cheat = False
                        self.current_puzzle.current_message = self.current_puzzle.default_message # Reset message
                        self.current_puzzle.message_display_time = 0
            elif self.game_state == GAME_STATE_GAME_OVER:
                self.restart_button_game_over.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            elif self.game_state == GAME_STATE_WIN_SCREEN:
                self.restart_button_game_over.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Updates game logic based on the current game state."""
        if self.game_state == GAME_STATE_GAMEPLAY:
            keys = pygame.key.get_pressed()
            self.player.update(keys)

            if not self.player.is_alive:
                self.set_game_state(GAME_STATE_GAME_OVER)

            # Alarm flashing logic
            if self.alarm_on:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_alarm_flash_time >= self.alarm_flash_interval:
                    self.alarm_visible = not self.alarm_visible
                    self.last_alarm_flash_time = current_time

        elif self.game_state in [GAME_STATE_CUTSCENE_INTRO, GAME_STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.update()
        elif self.game_state == GAME_STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.update() # Update to handle message timing

    def draw(self, surface):
        """Draws all game elements based on the current game state."""
        surface.fill(BLACK) # Clear screen

        if self.game_state == GAME_STATE_MENU:
            self.ui_manager.draw_menu_screen(surface, [self.start_button, self.how_to_play_button_menu, self.exit_button_menu])
        elif self.game_state == GAME_STATE_HOW_TO_PLAY:
            self.ui_manager.draw_how_to_play_screen(surface, self.how_to_play_text, self.back_button_how_to_play)
        elif self.game_state in [GAME_STATE_CUTSCENE_INTRO, GAME_STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.draw(surface)
        elif self.game_state == GAME_STATE_GAMEPLAY:
            self.current_room.draw(surface)
            self.player.draw(surface)
            self.ui_manager.draw_gameplay_ui(surface)
        elif self.game_state == GAME_STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.draw_puzzle_screen(surface)
        elif self.game_state == GAME_STATE_GAME_OVER:
            self.ui_manager.draw_game_over_screen(surface, self.restart_button_game_over)
        elif self.game_state == GAME_STATE_WIN_SCREEN:
            self.ui_manager.draw_win_screen(surface, self.restart_button_game_over)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw(SCREEN)
            CLOCK.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameManager()
    game.run()