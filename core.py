import pygame
from config import *
from ui_elements import UIManager, Button
from animations import CutsceneManager
from crypto import PuzzleGenerator, Terminal
from helpers import GameObject, Door, Room, Player

class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Crypternity: Martian Decipher")
        self.clock = pygame.time.Clock()
        self.game_state = STATE_MENU
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.puzzle_generator = PuzzleGenerator()
        self.rooms = {}
        self.current_room = None
        self.current_puzzle = None
        self.cutscene_manager = CutsceneManager(self)
        self.ui_manager = UIManager(self)
        self.running = True
        self.alarm_on = True
        self.alarm_visible = False
        self.last_alarm_flash_time = 0
        self._setup_game_elements()

    def _setup_game_elements(self):
        # Doors
        self.door_control_to_lab = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "lab_room", 80, HEIGHT // 2)
        self.door_lab_to_control = Door(50, HEIGHT // 2 - 50, 30, 100, "control_room", WIDTH - 130, HEIGHT // 2)
        self.door_lab_to_distress = Door(WIDTH - 80, HEIGHT // 2 - 50, 30, 100, "distress_room", 80, HEIGHT // 2)
        self.door_distress_to_lab = Door(50, HEIGHT // 2 - 50, 30, 100, "lab_room", WIDTH - 130, HEIGHT // 2)

        # Terminals
        self.terminal_control = Terminal(200, 300, self.puzzle_generator, unlocks_door=self.door_control_to_lab)
        self.terminal_lab = Terminal(WIDTH - 300, 300, self.puzzle_generator, unlocks_door=self.door_lab_to_distress)
        self.terminal_distress = Terminal(WIDTH // 2 - 35, HEIGHT // 2 - 50, self.puzzle_generator, unlocks_door=None, is_final_terminal=True)

        self.all_doors = [self.door_control_to_lab, self.door_lab_to_control, self.door_lab_to_distress, self.door_distress_to_lab]
        self.all_terminals = [self.terminal_control, self.terminal_lab, self.terminal_distress]

        # Rooms
        self.rooms = {
            "control_room": Room("Control Room", [self.terminal_control, self.door_control_to_lab]),
            "lab_room": Room("Research Lab", [self.door_lab_to_control, self.terminal_lab, self.door_lab_to_distress]),
            "distress_room": Room("Distress Signal Room", [self.door_distress_to_lab, self.terminal_distress]),
            "win_room": Room("Win Screen", [])
        }
        self.current_room = self.rooms["control_room"]

        # Menu buttons
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, "Start Mission", NEON_PURPLE, NEON_CYAN, self.start_intro_cutscene)
        self.how_to_play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50, "How to Play", NEON_PURPLE, NEON_CYAN, self.show_how_to_play)
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50, "Exit", NEON_RED, DARK_RED, self.exit_game)
        self.back_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Back to Menu", NEON_PURPLE, NEON_CYAN, lambda: self.set_game_state(STATE_MENU))
        self.restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Main Menu", NEON_PURPLE, NEON_CYAN, self.reset_game)

    def set_game_state(self, new_state):
        self.game_state = new_state

    def set_current_room(self, room_key):
        self.current_room = self.rooms[room_key]
        self.ui_manager.set_game_message(f"Entering: {self.current_room.name}", NEON_CYAN)

    def set_current_puzzle(self, puzzle_obj):
        self.current_puzzle = puzzle_obj

    def start_intro_cutscene(self):
        self.set_game_state(STATE_CUTSCENE_INTRO)
        self.cutscene_manager.start_cutscene([
            "ASTRONAUT: You awake in solitude aboard the Ares Station on Mars.",
            "ALARM: A critical breach has compromised the station's systems!",
            "MISSION: Decrypt the Sigma protocol to restore life support.",
            "CHALLENGE: Solve RSA puzzles to unlock doors and terminals.",
            "SURVIVE: Monitor your oxygen and suit integrity.",
            "OBJECTIVE: Activate the distress beacon before time runs out."
        ])

    def start_gameplay(self):
        self.set_game_state(STATE_GAMEPLAY)
        self.player.last_oxygen_tick = pygame.time.get_ticks()
        self.ui_manager.set_game_message("Mission started! Decrypt terminals (Press 'E')", NEON_CYAN)

    def show_how_to_play(self):
        self.set_game_state(STATE_HOW_TO_PLAY)

    def exit_game(self):
        self.running = False

    def start_final_cutscene(self):
        self.set_game_state(STATE_CUTSCENE_OUTRO)
        self.cutscene_manager.start_cutscene([
            "SUCCESS: All terminals decrypted. Systems online.",
            "BEACON: Distress signal sent to Earth.",
            "ARES STATION: Life support stabilized.",
            "ASTRONAUT: You have secured humanity's hope."
        ])

    def show_win_screen(self):
        self.set_game_state(STATE_WIN_SCREEN)

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
        self.last_alarm_flash_time = 0
        self.ui_manager.set_game_message("")
        self.set_game_state(STATE_MENU)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
                    for obj in self.current_room.interactive_objects:
                        if self.player.rect.colliderect(obj.rect):
                            obj.interact(self.player, self)
                            interacted = True
                            break
                    if not interacted:
                        self.ui_manager.set_game_message("Nothing to interact with.", YELLOW)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_how_to_play()
            elif self.game_state == STATE_PUZZLE_RSA:
                if self.current_puzzle:
                    self.current_puzzle.handle_input(event, self)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.set_game_state(STATE_GAMEPLAY)
                    if self.current_puzzle:
                        self.current_puzzle.reset_input()
            elif self.game_state in [STATE_GAME_OVER, STATE_WIN_SCREEN]:
                self.restart_button.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        if self.game_state == STATE_GAMEPLAY:
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            if not self.player.is_alive:
                self.set_game_state(STATE_GAME_OVER)
            if self.alarm_on:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_alarm_flash_time >= ALARM_FLASH_INTERVAL:
                    self.alarm_visible = not self.alarm_visible
                    self.last_alarm_flash_time = current_time
        elif self.game_state in [STATE_CUTSCENE_INTRO, STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.update()
        elif self.game_state == STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.update()

    def draw(self):
        self.screen.fill(DARK_CARBON)
        if self.game_state == STATE_MENU:
            self.ui_manager.draw_menu([self.start_button, self.how_to_play_button, self.exit_button])
        elif self.game_state == STATE_HOW_TO_PLAY:
            self.ui_manager.draw_how_to_play(self.back_button)
        elif self.game_state in [STATE_CUTSCENE_INTRO, STATE_CUTSCENE_OUTRO]:
            self.cutscene_manager.draw(self.screen)
        elif self.game_state == STATE_GAMEPLAY:
            self.current_room.draw(self.screen)
            self.player.draw(self.screen)
            self.ui_manager.draw_gameplay(self.screen)
        elif self.game_state == STATE_PUZZLE_RSA:
            if self.current_puzzle:
                self.current_puzzle.draw_puzzle_screen(self.screen)
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