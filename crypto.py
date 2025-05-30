import random
import math
from config import *
from helpers import GameObject, wrap_text  # Add this import
import pygame

class PuzzleGenerator:
    def __init__(self):
        self.primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    def _get_random_prime(self, exclude=None):
        available_primes = [p for p in self.primes if p != exclude]
        return random.choice(available_primes)

    def extended_gcd(self, a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    def mod_inverse(self, e, phi_n):
        gcd, x, _ = self.extended_gcd(e, phi_n)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % phi_n + phi_n) % phi_n

    def generate_puzzle(self):
        while True:
            p = self._get_random_prime()
            q = self._get_random_prime(exclude=p)
            n = p * q
            phi_n = (p - 1) * (q - 1)
            e_candidates = [i for i in range(2, phi_n) if math.gcd(i, phi_n) == 1]
            if not e_candidates:
                continue
            e = random.choice(e_candidates)
            try:
                M = random.randint(10, n // 2)
                C = pow(M, e, n)
                return {'p': p, 'q': q, 'e': e, 'C': C, 'M_solution': str(M)}
            except ValueError:
                continue

class Terminal(GameObject):
    def __init__(self, x, y, puzzle_generator, unlocks_door=None, is_final_terminal=False):
        super().__init__(x, y, 70, 100, NEON_RED, "Terminal")
        self.puzzle_generator = puzzle_generator
        self.puzzle_data = {}
        self.is_locked = True
        self.input_text = ""
        self.current_message = ""
        self.default_message = ""
        self.unlocks_door = unlocks_door
        self.is_final_terminal = is_final_terminal
        self.solved_color = NEON_GREEN
        self.calculated_solution = None
        self.show_answer_cheat = False
        self.message_start_time = 0
        self.generate_new_puzzle()

    def generate_new_puzzle(self):
        self.puzzle_data = self.puzzle_generator.generate_puzzle()
        self.calculated_solution = self.puzzle_data['M_solution']
        self._update_default_message()

    def _update_default_message(self):
        self.default_message = (f"AUTHENTICATION REQUIRED\n"
                               f"p={self.puzzle_data['p']}, q={self.puzzle_data['q']}\n"
                               f"e={self.puzzle_data['e']}\n"
                               f"Ciphertext C={self.puzzle_data['C']}\n"
                               f"Enter plaintext M:")
        self.current_message = self.default_message if self.is_locked else "Terminal decrypted!\nPress ESC to exit."

    def interact(self, player, game_manager):
        game_manager.set_game_state(STATE_PUZZLE_RSA)
        game_manager.set_current_puzzle(self)
        self.input_text = ""
        self.show_answer_cheat = False
        self._update_default_message()

    def handle_input(self, event, game_manager):
        if self.is_locked and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.check_solution(game_manager)
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_p:
                self.show_answer_cheat = not self.show_answer_cheat
            else:
                self.input_text += event.unicode

    def check_solution(self, game_manager):
        if self.calculated_solution is None:
            self.set_temp_message("Puzzle error.", NEON_RED)
            return
        if self.input_text.strip() == self.calculated_solution:
            self.is_locked = False
            self.set_temp_message("ACCESS GRANTED!", NEON_GREEN)
            self.image.fill(self.solved_color)
            if self.unlocks_door:
                self.unlocks_door.unlock()
                game_manager.ui_manager.set_game_message(f"{self.unlocks_door.name} unlocked!", NEON_PURPLE)
            if self.is_final_terminal:
                game_manager.alarm_on = False
                game_manager.ui_manager.set_game_message("Distress signal sent!", NEON_GREEN)
                game_manager.start_final_cutscene()
            else:
                game_manager.set_game_state(STATE_GAMEPLAY)
        else:
            self.set_temp_message("ACCESS DENIED!", NEON_RED)
        self.input_text = ""

    def set_temp_message(self, message, color):
        self.current_message = message
        self.message_start_time = pygame.time.get_ticks()

    def reset_input(self):
        self.input_text = ""
        self.show_answer_cheat = False
        self.current_message = self.default_message
        self.message_start_time = 0

    def update(self):
        if self.message_start_time and pygame.time.get_ticks() - self.message_start_time > MESSAGE_DURATION:
            self._update_default_message()
            self.message_start_time = 0

    def draw_puzzle_screen(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        window_rect = pygame.Rect(WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8)
        pygame.draw.rect(surface, DARK_CARBON, window_rect)
        pygame.draw.rect(surface, NEON_CYAN, window_rect, 3)
        message_rect = pygame.Rect(window_rect.x + 20, window_rect.y + 30, window_rect.width - 40, window_rect.height // 2)
        wrap_text(surface, self.current_message, pygame.font.Font(None, FONT_SIZE_MD), WHITE, message_rect)
        if self.is_locked:
            input_rect = pygame.Rect(WIDTH // 4, HEIGHT - 150, WIDTH // 2, 40)
            pygame.draw.rect(surface, NEON_CYAN, input_rect, 2)
            input_surface = pygame.font.Font(None, FONT_SIZE_MD).render(self.input_text, True, WHITE)
            surface.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
            if self.show_answer_cheat:
                cheat_text = pygame.font.Font(None, FONT_SIZE_SM).render(f"Solution: {self.calculated_solution}", True, YELLOW)
                surface.blit(cheat_text, (input_rect.x, input_rect.y + 45))
        hint_text = pygame.font.Font(None, FONT_SIZE_SM).render("ENTER to submit, 'P' for hint, ESC to exit", True, WHITE)
        surface.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 80))

    def reset(self):
        self.is_locked = True
        self.image.fill(NEON_RED)
        self.input_text = ""
        self.show_answer_cheat = False
        self.message_start_time = 0
        self.generate_new_puzzle()