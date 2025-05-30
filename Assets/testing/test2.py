import pygame
import sys
import time
import math

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
        self.oxygen_depletion_rate = 0.5
        self.is_alive = True

    def update(self, keys):
        """Updates player position and vital stats."""
        if not self.is_alive:
            return

        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Boundary checks
        self.rect.left = max(50, self.rect.left)
        self.rect.right = min(WIDTH - 50, self.rect.right)
        self.rect.top = max(50, self.rect.top)
        self.rect.bottom = min(HEIGHT - 50, self.rect.bottom)

        # Oxygen depletion
        current_time = pygame.time.get_ticks()
        if current_time - self.last_oxygen_tick >= 1000:
            if self.suit_integrity < 100: # Only deplete oxygen if suit is damaged
                self.oxygen -= self.oxygen_depletion_rate
            self.last_oxygen_tick = current_time
            if self.oxygen <= 0:
                self.oxygen = 0
                self.is_alive = False # Player dies if oxygen runs out

class Door(GameObject):
    """A door that can be locked or unlocked."""
    def __init__(self, x, y, width, height, target_room_key, target_x, target_y):
        super().__init__(x, y, width, height, BLUE, "Door")
        self.target_room_key = target_room_key
        self.target_x = target_x
        self.target_y = target_y
        self.is_locked = True
        self.unlocked_color = LIGHT_BLUE

    def interact(self, player_instance, game_manager):
        """Handles player interaction with the door."""
        if not self.is_locked:
            if self.target_room_key == "win_room":
                game_manager.start_final_cutscene()
            else:
                game_manager.set_current_room(self.target_room_key)
                player_instance.rect.x = self.target_x
                player_instance.rect.y = self.target_y
                print(f"Moved to {self.target_room_key}")
        else:
            print("Door is locked. Find a way to unlock it.")

    def unlock(self):
        """Unlocks the door."""
        self.is_locked = False
        self.image.fill(self.unlocked_color)

class Terminal(GameObject):
    """An interactive terminal with an RSA puzzle."""
    def __init__(self, x, y, puzzle_data, unlocks_door=None, is_final_terminal=False):
        super().__init__(x, y, 70, 100, RED, "Terminal")
        self.puzzle_data = puzzle_data
        self.is_locked = True
        self.input_text = ""
        self.message = ""
        self.unlocks_door = unlocks_door
        self.is_final_terminal = is_final_terminal
        self.solved_color = GREEN
        self.calculated_solution = self._calculate_solution()
        self.show_answer_cheat = False

    def _calculate_solution(self):
        """Calculates the RSA puzzle's solution."""
        try:
            p = self.puzzle_data['p']
            q = self.puzzle_data['q']
            e = self.puzzle_data['e']
            C = self.puzzle_data['C']

            n = p * q
            phi_n = (p - 1) * (q - 1)

            # Check if e and phi_n are coprime
            if math.gcd(e, phi_n) != 1:
                print(f"Error: e ({e}) and phi_n ({phi_n}) are not coprime. Cannot calculate d for this puzzle.")
                return None

            d = mod_inverse(e, phi_n)
            M = decrypt_rsa(C, d, n)
            return str(M)
        except Exception as ex:
            print(f"Error calculating RSA solution: {ex}")
            return None

    def interact(self, player_instance, game_manager):
        """Initiates the RSA puzzle interface."""
        game_manager.set_game_state(GAME_STATE_PUZZLE_RSA)
        game_manager.set_current_puzzle(self)
        if self.is_locked:
            self.message = (f"Authentication required. Decrypt:\n"
                            f"  p={self.puzzle_data['p']}, q={self.puzzle_data['q']}\n"
                            f"  e={self.puzzle_data['e']}\n"
                            f"  Ciphertext C={self.puzzle_data['C']}\n"
                            f"Enter plaintext M:")
            self.input_text = ""
        else:
            self.message = "Terminal already decrypted!\nPress ESC to return."
        self.show_answer_cheat = False

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
            self.message = "Puzzle error. Cannot solve."
            return

        player_solution = self.input_text.strip()
        if player_solution == self.calculated_solution:
            self.is_locked = False
            self.message = "Access Granted! System unlocked."
            self.image.fill(self.solved_color)
            if self.unlocks_door:
                self.unlocks_door.unlock()
                print(f"{self.unlocks_door.name} unlocked!")
            if self.is_final_terminal:
                game_manager.alarm_on = False # Turn off alarm when final terminal is solved
                print("Final terminal activated! Distress signal being sent...")
                game_manager.start_final_cutscene()
                return
            game_manager.set_game_state(GAME_STATE_GAMEPLAY)
        else:
            self.message = "Incorrect decryption. Try again."
        self.input_text = ""

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

        text_lines = self.message.split('\n')
        y_offset = puzzle_window_rect.top + 30
        for line in text_lines:
            text_surface = FONT_MD.render(line, True, WHITE)
            surface.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
            y_offset += 30

        if self.is_locked:
            input_rect = pygame.Rect(WIDTH // 4, HEIGHT - 150, WIDTH // 2, 40)
            pygame.draw.rect(surface, WHITE, input_rect, 2)
            input_surface = FONT_MD.render(self.input_text, True, WHITE)
            surface.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))

            if self.show_answer_cheat and self.calculated_solution is not None:
                cheat_text = FONT_SM.render(f"Solution: {self.calculated_solution}", True, (255, 255, 0))
                surface.blit(cheat_text, (input_rect.x, input_rect.y + 45))

        hint_surface = FONT_SM.render("Press ENTER to submit. Press 'P' for hint/solution. Press ESC to return to game.", True, WHITE)
        surface.blit(hint_surface, (WIDTH // 2 - hint_surface.get_width() // 2, HEIGHT - 80))

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
    """Manages cutscene playback."""
    def __init__(self):
        self.script = []
        self.start_time = 0
        self.index = 0
        self.char_index = 0
        self.last_char_time = 0
        self.finished_typing_current_line = False

    def start_cutscene(self, script):
        """Initializes a new cutscene."""
        self.script = script
        self.start_time = pygame.time.get_ticks()
        self.index = 0
        self.char_index = 0
        self.last_char_time = pygame.time.get_ticks()
        self.finished_typing_current_line = False

    def update(self, current_game_state, game_manager):
        """Updates cutscene state and advances lines."""
        if self.index >= len(self.script):
            if current_game_state == GAME_STATE_CUTSCENE_INTRO:
                game_manager.start_gameplay()
            elif current_game_state == GAME_STATE_CUTSCENE_OUTRO:
                game_manager.show_win_screen()
            return

        current_time = pygame.time.get_ticks()
        target_time_in_cutscene = self.script[self.index][1]

        if (current_time - self.start_time) / 1000.0 >= target_time_in_cutscene:
            if not self.finished_typing_current_line:
                if current_time - self.last_char_time >= CUTSCENE_CHAR_DELAY:
                    self.char_index = min(len(self.script[self.index][0]), self.char_index + 1)
                    self.last_char_time = current_time
                    if self.char_index == len(self.script[self.index][0]):
                        self.finished_typing_current_line = True
            else:
                if (current_time - self.start_time) / 1000.0 >= target_time_in_cutscene + 1.5:
                    self.index += 1
                    self.char_index = 0
                    self.finished_typing_current_line = False

    def handle_event(self, event, current_game_state, game_manager):
        """Handles input events for skipping cutscene lines."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.char_index < len(self.script[self.index][0]):
                self.char_index = len(self.script[self.index][0])
                self.finished_typing_current_line = True
            else:
                self.index += 1
                self.char_index = 0
                self.finished_typing_current_line = False
                if self.index >= len(self.script):
                    if current_game_state == GAME_STATE_CUTSCENE_INTRO:
                        game_manager.start_gameplay()
                    elif current_game_state == GAME_STATE_CUTSCENE_OUTRO:
                        game_manager.show_win_screen()

    def draw(self, surface):
        """Draws the current cutscene text."""
        surface.fill(BLACK)
        display_text = ""
        if self.index < len(self.script):
            full_line_text = self.script[self.index][0]
            display_text = full_line_text[:self.char_index]

        y_offset = HEIGHT // 3
        text_surface = FONT_MD.render(display_text, True, WHITE)
        surface.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))

        if self.index >= len(self.script) - 1 and self.finished_typing_current_line and (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_text = FONT_MD.render("Press ENTER to continue...", True, WHITE)
            surface.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT - 50))

class GameManager:
    """Manages the overall game state, assets, and flow."""
    def __init__(self):
        self.game_state = GAME_STATE_MENU
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.rooms = {}
        self.current_room = None
        self.current_puzzle = None
        self.cutscene_manager = CutsceneManager()
        self.running = True
        self.alarm_on = True
        self.alarm_flash_interval = 500
        self.last_alarm_flash_time = 0
        self.alarm_visible = False

        # Cutscene Data
        self.intro_cutscene_script = [
            ("You are an astronaut and cryptographic security analyst, alone aboard a Martian space station.", 0),
            ("The rest of the crew is on a mission in the Valles Marineris canyon.", 2),
            ("You were in charge of an experimental project: encrypting vital systems using advanced security algorithms.", 4),
            ("Suddenly, an alarm goes off: there's a breach in the station! Your spacesuit is damaged.", 6),
            ("But even stranger: the backup systems refuse to activate.", 8),
            ("A message appears on the main screen:", 10),
            ("        \"Authentication required. Decrypt the Sigma protocol.\"", 12),
            ("Your systems are locked down. Every door, every terminal, every life support system is protected by an encrypted code.", 14),
            ("You must decrypt these codes to survive: repair your suit, access emergency oxygen, activate the radio beacon.", 16),
            ("As a last hope, you pick up a faint signal: the Earth lander has crashed, but it contained fragments of encryption keys.", 18),
            ("It's up to you to find them, reassemble them, and send a clear distress message before it's too late.", 20),
            ("Your mission begins now...", 22)
        ]

        self.final_cutscene_script = [
            ("With the last code decrypted, the main systems flicker to life.", 0),
            ("A powerful signal beams towards Earth, carrying your distress message.", 2),
            ("The station's alarms quiet, replaced by the hum of stable life support.", 4),
            ("Though alone, you've secured the station and sent a beacon of hope.", 6),
            ("Help is on the way. Mission accomplished.", 8)
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
        # Define RSA puzzle data
        terminal1_puzzle_data = {'p': 11, 'q': 13, 'e': 7, 'C': 99} # M should be 50
        terminal2_puzzle_data = {'p': 17, 'q': 19, 'e': 5, 'C': 100} # M should be 100
        terminal3_puzzle_data = {'p': 23, 'q': 29, 'e': 3, 'C': 25} # M should be 25

        # Create interactive objects (Doors are defined before terminals that unlock them)
        door_control_to_lab = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "lab_room", 80, HEIGHT // 2)
        door_lab_to_control = Door(50, HEIGHT // 2 - 50, 30, 100, "control_room", WIDTH - 130, HEIGHT // 2)
        door_lab_to_distress = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "distress_room", 80, HEIGHT // 2)
        door_distress_to_lab = Door(50, HEIGHT // 2 - 50, 30, 100, "lab_room", WIDTH - 130, HEIGHT // 2)

        terminal_control = Terminal(200, 300, terminal1_puzzle_data, unlocks_door=door_control_to_lab)
        terminal_lab = Terminal(WIDTH - 300, 300, terminal2_puzzle_data, unlocks_door=door_lab_to_distress)
        terminal_distress = Terminal(WIDTH // 2 - 35, HEIGHT // 2 - 50, terminal3_puzzle_data, unlocks_door=None, is_final_terminal=True)

        self.rooms = {
            "control_room": Room("Control Room", [terminal_control, door_control_to_lab]),
            "lab_room": Room("Research Lab", [door_lab_to_control, terminal_lab, door_lab_to_distress]),
            "distress_room": Room("Distress Signal Room", [door_distress_to_lab, terminal_distress]),
            "win_room": Room("Win Screen", []) # A dummy room for win condition transition
        }
        self.current_room = self.rooms["control_room"]

        # Menu Buttons
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, "Start Mission", FONT_MD, DARK_GREY, GREY, WHITE, self.start_intro_cutscene)
        self.how_to_play_button_menu = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50, "How to Play", FONT_MD, DARK_GREY, GREY, WHITE, self.show_how_to_play_screen)
        self.exit_button_menu = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Exit", FONT_MD, DARK_RED, RED, WHITE, self.exit_game)
        self.back_button_how_to_play = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back to Main Menu", FONT_MD, DARK_GREY, GREY, WHITE, lambda: self.set_game_state(GAME_STATE_MENU))

    def set_game_state(self, new_state):
        """Changes the current game state."""
        self.game_state = new_state

    def set_current_room(self, room_key):
        """Sets the current active room."""
        self.current_room = self.rooms[room_key]

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
                self.cutscene_manager.handle_event(event, self.game_state, self)
            elif self.game_state == GAME_STATE_GAMEPLAY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        for obj in self.current_room.interactive_objects:
                            if self.player.rect.colliderect(obj.rect):
                                obj.interact(self.player, self)
                                break
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
            elif self.game_state in [GAME_STATE_GAME_OVER, GAME_STATE_WIN_SCREEN]:
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
            self.cutscene_manager.update(self.game_state, self)

    def draw(self, surface):
        """Draws all game elements based on the current game state."""
        surface.fill(BLACK)

        if self.game_state == GAME_STATE_MENU:
            self._draw_menu_screen(surface)
        elif self.game_state == GAME_STATE_HOW_TO_PLAY:
            self._draw_how_to_play_screen(surface)
        elif self.game_state in [GAME_STATE_CUTSCENE_INTRO, GAME_STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.draw(surface)
        elif self.game_state == GAME_STATE_GAMEPLAY:
            self._draw_gameplay_screen(surface)
        elif self.game_state == GAME_STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.draw_puzzle_screen(surface)
        elif self.game_state == GAME_STATE_GAME_OVER:
            self._draw_game_over_screen(surface)
        elif self.game_state == GAME_STATE_WIN_SCREEN:
            self._draw_win_screen(surface)

        pygame.display.flip()

    def _draw_menu_screen(self, surface):
        """Draws the main menu screen."""
        surface.fill(DARK_GREY)
        pygame.draw.rect(surface, BLACK, (WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100), border_radius=10)
        pygame.draw.rect(surface, CYAN, (WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100), 3, border_radius=10)

        title_text = FONT_XL.render("Crypternity", True, WHITE)
        subtitle_text = FONT_MD.render("Martian Decipher", True, CYAN)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 30))
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, title_rect.bottom + 10))
        surface.blit(title_text, title_rect)
        surface.blit(subtitle_text, subtitle_rect)

        self.start_button.draw(surface)
        self.how_to_play_button_menu.draw(surface)
        self.exit_button_menu.draw(surface)

    def _draw_how_to_play_screen(self, surface):
        """Draws the how-to-play instructions screen."""
        surface.fill(DARK_GREY)
        pygame.draw.rect(surface, BLACK, (WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8), border_radius=10)
        pygame.draw.rect(surface, CYAN, (WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8), 3, border_radius=10)

        y_offset_how_to_play = HEIGHT // 8 + 30
        for line in self.how_to_play_text:
            line_surface = FONT_MD.render(line, True, WHITE)
            surface.blit(line_surface, (WIDTH // 2 - line_surface.get_width() // 2, y_offset_how_to_play))
            y_offset_how_to_play += 25

        self.back_button_how_to_play.draw(surface)

    def _draw_gameplay_screen(self, surface):
        """Draws the main gameplay screen."""
        self.current_room.draw(surface)
        self.player.draw(surface)

        # Draw UI (oxygen, suit integrity)
        ui_panel_rect = pygame.Rect(5, 5, 140, 70)
        pygame.draw.rect(surface, DARK_GREY, ui_panel_rect, border_radius=5)
        pygame.draw.rect(surface, CYAN, ui_panel_rect, 2, border_radius=5)

        # Grid behind bars
        for i in range(ui_panel_rect.left + 5, ui_panel_rect.right - 5, 8):
            pygame.draw.line(surface, (40, 40, 40), (i, ui_panel_rect.top + 5), (i, ui_panel_rect.bottom - 5), 1)
        for i in range(ui_panel_rect.top + 5, ui_panel_rect.bottom - 5, 8):
            pygame.draw.line(surface, (40, 40, 40), (ui_panel_rect.left + 5, i), (ui_panel_rect.right - 5, i), 1)

        # Oxygen Bar
        oxygen_bar_width = int(120 * (self.player.oxygen / 100))
        pygame.draw.rect(surface, DARK_RED, (15, 15, 120, 20), 0, 3)
        pygame.draw.rect(surface, GREEN, (15, 15, oxygen_bar_width, 20), 0, 3)
        oxygen_text = FONT_SM.render(f"O2: {int(self.player.oxygen)}%", True, WHITE)
        surface.blit(oxygen_text, (25, 19))

        # Suit Integrity Bar
        suit_bar_width = int(120 * (self.player.suit_integrity / 100))
        pygame.draw.rect(surface, DARK_RED, (15, 45, 120, 20), 0, 3)
        pygame.draw.rect(surface, LIGHT_BLUE, (15, 45, suit_bar_width, 20), 0, 3)
        suit_text = FONT_SM.render(f"SUIT: {int(self.player.suit_integrity)}%", True, WHITE)
        surface.blit(suit_text, (25, 49))

        # Show interaction prompt
        interaction_prompt = ""
        for obj in self.current_room.interactive_objects:
            if self.player.rect.colliderect(obj.rect):
                interaction_prompt = f"Press 'E' to interact with {obj.name}"
                break
        if interaction_prompt:
            prompt_surface = FONT_MD.render(interaction_prompt, True, WHITE)
            surface.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT - 30))

        # Alarm Effect
        if self.alarm_on and self.alarm_visible:
            alarm_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alarm_overlay.fill(ALARM_COLOR)
            surface.blit(alarm_overlay, (0, 0))

    def _draw_game_over_screen(self, surface):
        """Draws the game over screen."""
        surface.fill(BLACK)
        game_over_text = FONT_LG.render("MISSION FAILED - GAME OVER", True, RED)
        instruction_text = FONT_MD.render("Oxygen Depleted or Suit Breached!", True, WHITE)
        exit_text = FONT_MD.render("Press ESC to exit", True, WHITE)
        surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        surface.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
        surface.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 50))

    def _draw_win_screen(self, surface):
        """Draws the win screen."""
        surface.fill(BLACK)
        win_text = FONT_LG.render("MISSION SUCCESS! Distress Signal Sent!", True, GREEN)
        instruction_text = FONT_MD.render("You decrypted the Sigma protocol and secured the station.", True, WHITE)
        exit_text = FONT_MD.render("Press ESC to exit", True, WHITE)
        surface.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
        surface.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
        surface.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 50))

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