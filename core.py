import pygame
from config import *
from ui_elements import UIManager, Button
from animations import CutsceneManager
from crypto import PuzzleGenerator
from helpers import wrap_text

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(NEON_GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = PLAYER_SPEED
        self.oxygen = 100.0
        self.suit_integrity = 100.0
        self.last_oxygen_tick = pygame.time.get_ticks()
        self.is_alive = True

    def update(self, keys):
        if not self.is_alive:
            return
        moved = False
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
        self.rect.left = max(50, self.rect.left)
        self.rect.right = min(WIDTH - 50, self.rect.right)
        self.rect.top = max(50, self.rect.top)
        self.rect.bottom = min(HEIGHT - 50, self.rect.bottom)
        if pygame.time.get_ticks() - self.last_oxygen_tick >= 1000:
            if moved:
                self.suit_integrity -= SUIT_DAMAGE_RATE
                self.suit_integrity = max(0, self.suit_integrity)
            if self.suit_integrity < 100:
                self.oxygen -= OXYGEN_DEPLETION
            self.last_oxygen_tick = pygame.time.get_ticks()
            if self.oxygen <= 0 or self.suit_integrity <= 0:
                self.is_alive = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def reset(self):
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.oxygen = 100.0
        self.suit_integrity = 100.0
        self.is_alive = True
        self.last_oxygen_tick = pygame.time.get_ticks()

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, target_room, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(NEON_BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = f"Door to {target_room.replace('_', ' ').title()}"
        self.target_room = target_room
        self.target_x = target_x
        self.target_y = target_y
        self.is_locked = True
        self.unlocked_color = NEON_LIGHT_BLUE
        self.pulse_alpha = 0
        self.pulse_start = 0
        self.font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_SM)

    def update_color(self):
        self.image.fill(self.unlocked_color if not self.is_locked else NEON_BLUE)

    def update(self):
        if not self.is_locked and self.pulse_start:
            elapsed = pygame.time.get_ticks() - self.pulse_start
            if elapsed < DOOR_PULSE_DURATION:
                self.pulse_alpha = int(100 * (1 - elapsed / DOOR_PULSE_DURATION))
            else:
                self.pulse_alpha = 0
                self.pulse_start = 0

    def interact(self, player, game_manager):
        game_manager.ui_manager.play_interact_sound()
        if not self.is_locked:
            game_manager.set_game_message("Door Unlocked! Transitioning...", NEON_ORANGE)
            if self.target_room == "win_room":
                game_manager.start_final_cutscene()
            else:
                game_manager.set_current_room(self.target_room)
                player.rect.x = self.target_x
                player.rect.y = self.target_y
        else:
            game_manager.set_game_message("Door Locked. Decrypt terminal.", NEON_RED)

    def unlock(self):
        self.is_locked = False
        self.update_color()
        self.pulse_start = pygame.time.get_ticks()
        if os.path.exists(UNLOCK_SOUND):
            try:
                sound = pygame.mixer.Sound(UNLOCK_SOUND)
                sound.set_volume(0.5)
                sound.play()
            except pygame.error:
                pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.pulse_alpha > 0:
            pulse_surface = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(pulse_surface, (0, 255, 255, self.pulse_alpha), (5, 5, self.rect.width, self.rect.height), border_radius=5)
            surface.blit(pulse_surface, (self.rect.x - 5, self.rect.y - 5))
        label = self.font.render(self.name, True, NEON_WHITE)
        surface.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.top - 20))

    def reset(self):
        self.is_locked = True
        self.update_color()
        self.pulse_alpha = 0
        self.pulse_start = 0

class Terminal(pygame.sprite.Sprite):
    def __init__(self, x, y, puzzle_generator, unlocks_door=None, is_final=False):
        super().__init__()
        self.image = pygame.Surface((70, 100))
        self.image.fill(NEON_RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = "Distress Terminal" if is_final else ("Control Terminal" if unlocks_door else "Terminal")
        self.puzzle_generator = puzzle_generator
        self.puzzle_data = {}
        self.is_locked = True
        self.input_text = ""
        self.current_message = ""
        self.default_message = ""
        self.unlocks_door = unlocks_door
        self.is_final = is_final
        self.solved_color = NEON_GREEN
        self.solution = None
        self.show_cheat = False
        self.message_time = 0
        self.cursor_blink = True
        self.last_blink = 0
        self.font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_SM)
        self.generate_puzzle()

    def generate_puzzle(self):
        self.puzzle_data = self.puzzle_generator.generate_puzzle()
        self.solution = self.puzzle_data['M_solution']
        self.update_message()

    def update_message(self):
        self.default_message = (
            f"Decrypt Sigma Protocol:\n"
            f"p={self.puzzle_data['p']}, q={self.puzzle_data['q']}\n"
            f"e={self.puzzle_data['e']}, C={self.puzzle_data['C']}\n"
            f"Enter plaintext M:"
        )
        self.current_message = self.default_message if self.is_locked else "Terminal decrypted! Press ESC."

    def update(self):
        if pygame.time.get_ticks() - self.last_blink >= 500:
            self.cursor_blink = not self.cursor_blink
            self.last_blink = pygame.time.get_ticks()
        if self.message_time and pygame.time.get_ticks() > self.message_time:
            self.update_message()
            self.message_time = 0

    def interact(self, game_manager):
        game_manager.ui_manager.play_interact_sound()
        game_manager.set_game_state(STATE_PUZZLE_RSA)
        game_manager.set_current_puzzle(self)
        self.input_text = ""
        self.show_cheat = False
        self.update_message()

    def handle_input(self, event, game_manager):
        if not self.is_locked:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.check_solution(game_manager)
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_p:
                self.show_cheat = not self.show_cheat
            else:
                self.input_text += event.unicode

    def check_solution(self, game_manager):
        if self.solution and self.input_text.strip() == self.solution:
            self.is_locked = False
            self.image.fill(self.solved_color)
            self.set_temp_message("Access Granted!", NEON_GREEN)
            if self.unlocks_door:
                self.unlocks_door.unlock()
                game_manager.set_game_message(f"{self.unlocks_door.name} unlocked!", NEON_ORANGE)
            if self.is_final:
                game_manager.alarm_on = False
                game_manager.set_game_message("Distress signal sent!", NEON_GREEN)
                game_manager.start_final_cutscene()
            else:
                game_manager.set_game_state(STATE_GAMEPLAY)
        else:
            self.set_temp_message("Incorrect. Try again.", NEON_RED)
        self.input_text = ""

    def set_temp_message(self, message, color):
        self.current_message = message
        self.message_time = pygame.time.get_ticks() + MESSAGE_DURATION

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        mini_screen = pygame.Surface((60, 20), pygame.SRCALPHA)
        mini_screen.fill((0, 0, 0, 100))
        if self.is_locked and self.cursor_blink:
            cursor = self.font.render("_", True, NEON_GREEN)
            mini_screen.blit(cursor, (5, 5))
        surface.blit(mini_screen, (self.rect.x + 5, self.rect.y + 10))
        label = self.font.render(self.name, True, NEON_WHITE)
        surface.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.top - 20))

    def draw_puzzle(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        rect = pygame.Rect(WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8)
        pygame.draw.rect(surface, DARK_GLOW, rect)
        pygame.draw.rect(surface, NEON_CYAN, rect, 3)
        font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
        message_rect = pygame.Rect(rect.x + 20, rect.y + 30, rect.width - 40, rect.height // 2)
        y = wrap_text(surface, self.current_message, font, NEON_WHITE, message_rect)
        if self.is_locked:
            input_rect = pygame.Rect(WIDTH // 4, HEIGHT - 150, WIDTH // 2, 40)
            pygame.draw.rect(surface, NEON_CYAN, input_rect, 2)
            input_text = font.render(self.input_text + ("_" if self.cursor_blink else ""), True, NEON_WHITE)
            surface.blit(input_text, (input_rect.x + 5, input_rect.y + 5))
            if self.show_cheat and self.solution:
                cheat_font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_SM)
                cheat_text = cheat_font.render(f"Solution: {self.solution}", True, NEON_YELLOW)
                surface.blit(cheat_text, (input_rect.x, input_rect.y + 45))
        hint_font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_SM)
        hint = hint_font.render("ENTER to submit, 'P' for hint, ESC to exit", True, NEON_WHITE)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))

    def reset(self):
        self.is_locked = True
        self.image.fill(NEON_RED)
        self.input_text = ""
        self.show_cheat = False
        self.message_time = 0
        self.generate_puzzle()

class Room:
    def __init__(self, name, objects):
        self.name = name
        self.objects = pygame.sprite.Group(objects)

    def draw(self, surface):
        surface.fill(NEON_BLACK)
        pygame.draw.rect(surface, DARK_GLOW, (50, 50, WIDTH - 100, HEIGHT - 100))
        for i in range(50, WIDTH - 50, 20):
            pygame.draw.line(surface, GRID_GLOW, (i, 50), (i, HEIGHT - 50), 1)
        for i in range(50, HEIGHT - 50, 20):
            pygame.draw.line(surface, GRID_GLOW, (50, i), (WIDTH - 50, i), 1)
        pygame.draw.rect(surface, NEON_CYAN, (50, 50, WIDTH - 100, HEIGHT - 100), 5)
        font = pygame.font.Font(FONT_BOLD, FONT_SIZE_LG)
        name_text = font.render(self.name, True, NEON_WHITE)
        surface.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 10))
        self.objects.draw(surface)
        for obj in self.objects:
            obj.draw(surface)  # Ensure custom draw for labels

class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.game_state = STATE_MENU
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.puzzle_generator = PuzzleGenerator()
        self.rooms = {}
        self.current_room = None
        self.current_puzzle = None
        self.ui_manager = UIManager(self)
        self.cutscene_manager = CutsceneManager(self)
        self.running = True
        self.alarm_on = True
        self.alarm_visible = False
        self.last_alarm_flash = 0
        self.setup_game()

    def setup_game(self):
        door_control_to_lab = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "lab_room", 80, HEIGHT // 2)
        door_lab_to_control = Door(50, HEIGHT // 2 - 50, 30, 100, "control_room", WIDTH - 130, HEIGHT // 2)
        door_lab_to_distress = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "distress_room", 80, HEIGHT // 2)
        door_distress_to_lab = Door(50, HEIGHT // 2 - 50, 30, 100, "lab_room", WIDTH - 130, HEIGHT // 2)
        terminal_control = Terminal(200, 300, self.puzzle_generator, door_control_to_lab)
        terminal_lab = Terminal(WIDTH - 300, 300, self.puzzle_generator, door_lab_to_distress)
        terminal_distress = Terminal(WIDTH // 2 - 35, HEIGHT // 2 - 50, self.puzzle_generator, is_final=True)
        self.all_doors = [door_control_to_lab, door_lab_to_control, door_lab_to_distress, door_distress_to_lab]
        self.all_terminals = [terminal_control, terminal_lab, terminal_distress]
        self.rooms = {
            "control_room": Room("Control Room", [terminal_control, door_control_to_lab]),
            "lab_room": Room("Research Lab", [door_lab_to_control, terminal_lab, door_lab_to_distress]),
            "distress_room": Room("Distress Signal Room", [door_distress_to_lab, terminal_distress]),
            "win_room": Room("Win Screen", [])
        }
        self.current_room = self.rooms["control_room"]
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, "Start Mission", self.start_intro_cutscene)
        self.how_to_play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50, "How to Play", self.show_how_to_play)
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Exit", self.exit_game)
        self.back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back to Menu", lambda: self.set_game_state(STATE_MENU))
        self.restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Main Menu", self.reset_game)

    def set_game_state(self, state):
        self.game_state = state
        if state != STATE_MENU:
            self.ui_manager.stop_menu_music()

    def set_current_room(self, room_key):
        self.current_room = self.rooms[room_key]
        self.ui_manager.set_message(f"Entering: {self.current_room.name}", NEON_CYAN)

    def set_current_puzzle(self, puzzle):
        self.current_puzzle = puzzle

    def start_intro_cutscene(self):
        self.set_game_state(STATE_CUTSCENE_INTRO)
        self.cutscene_manager.start_cutscene(INTRO_CUTSCENE)

    def start_gameplay(self):
        self.set_game_state(STATE_GAMEPLAY)
        self.player.last_oxygen_tick = pygame.time.get_ticks()
        self.ui_manager.set_message("Mission started! Press 'E' to interact", NEON_CYAN)

    def show_how_to_play(self):
        self.set_game_state(STATE_HOW_TO_PLAY)

    def exit_game(self):
        self.running = False
        self.ui_manager.stop_menu_music()

    def start_final_cutscene(self):
        self.set_game_state(STATE_CUTSCENE_OUTRO)
        self.cutscene_manager.start_cutscene(FINAL_CUTSCENE)

    def show_win_screen(self):
        self.set_game_state(STATE_WIN_SCREEN)

    def set_game_message(self, message, color=NEON_WHITE):
        self.ui_manager.set_message(message, color)

    def reset_game(self):
        self.player.reset()
        for door in self.all_doors:
            door.reset()
        for terminal in self.all_terminals:
            terminal.reset()
        self.current_room = self.rooms["control_room"]
        self.current_puzzle = None
        self.alarm_on = True
        self.alarm_visible = False
        self.last_alarm_flash = 0
        self.ui_manager.set_message("")
        self.set_game_state(STATE_MENU)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ui_manager.stop_menu_music()
                self.running = False
            elif self.game_state == STATE_MENU:
                self.start_button.handle_event(event)
                self.how_to_play_button.handle_event(event)
                self.exit_button.handle_event(event)
            elif self.game_state == STATE_HOW_TO_PLAY:
                self.back_button.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.set_game_state(STATE_MENU)
            elif self.game_state in [STATE_CUTSCENE_INTRO, STATE_CUTSCENE_OUTRO]:
                self.cutscene_manager.handle_event(event)
            elif self.game_state == STATE_GAMEPLAY:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    interacted = False
                    for obj in self.current_room.objects:
                        if self.player.rect.colliderect(obj.rect):
                            if isinstance(obj, Door):
                                obj.interact(self.player, self)
                            else:
                                obj.interact(self)
                            interacted = True
                            break
                    if not interacted:
                        self.set_game_message("Nothing to interact here.", NEON_YELLOW)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_how_to_play()
                tooltip_set = False
                for obj in self.current_room.objects:
                    if self.player.rect.colliderect(obj.rect):
                        action = "Unlock Door" if isinstance(obj, Door) else "Access Terminal"
                        self.ui_manager.set_tooltip(f"Interact [E]: {action}")
                        tooltip_set = True
                        break
                if not tooltip_set:
                    self.ui_manager.set_tooltip("")
            elif self.game_state == STATE_PUZZLE_RSA:
                if self.current_puzzle:
                    self.current_puzzle.handle_input(event, self)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.set_game_state(STATE_GAMEPLAY)
                    if self.current_puzzle:
                        self.current_puzzle.input_text = ""
                        self.current_puzzle.show_cheat = False
                        self.current_puzzle.update_message()
                        self.current_puzzle.message_time = 0
            elif self.game_state in [STATE_GAME_OVER, STATE_WIN_SCREEN]:
                self.restart_button.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.ui_manager.stop_menu_music()

    def update(self):
        self.ui_manager.update()
        if self.game_state == STATE_GAMEPLAY:
            self.player.update(pygame.key.get_pressed())
            if not self.player.is_alive:
                self.set_game_state(STATE_GAME_OVER)
            if self.alarm_on:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_alarm_flash >= ALARM_FLASH_INTERVAL:
                    self.alarm_visible = not self.alarm_visible
                    self.last_alarm_flash = current_time
            for obj in self.current_room.objects:
                obj.update()
        elif self.game_state in [STATE_CUTSCENE_INTRO, STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.update()
        elif self.game_state == STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.update()

    def draw(self):
        self.screen.fill(NEON_BLACK)
        if self.game_state == STATE_MENU:
            self.ui_manager.draw_menu([self.start_button, self.how_to_play_button, self.exit_button])
        elif self.game_state == STATE_HOW_TO_PLAY:
            self.ui_manager.draw_how_to_play(HOW_TO_PLAY_TEXT, self.back_button)
        elif self.game_state in [STATE_CUTSCENE_INTRO, STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.draw(self.screen)
        elif self.game_state == STATE_GAMEPLAY:
            self.current_room.draw(self.screen)
            self.player.draw(self.screen)
            self.ui_manager.draw_gameplay(self.screen)
        elif self.game_state == STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.draw_puzzle(self.screen)
        elif self.game_state == STATE_GAME_OVER:
            self.ui_manager.draw_game_over(self.restart_button)
        elif self.game_state == STATE_WIN_SCREEN:
            self.ui_manager.draw_win_screen(self.restart_button)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)