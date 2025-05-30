import pygame
from config import *
from helpers import wrap_text  # Added import for wrap_text

class CutsceneManager:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.current_cutscene = None
        self.current_line = 0
        self.current_text = ""
        self.text_progress = 0
        self.last_char_time = 0
        self.font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)

    def start_cutscene(self, cutscene_lines):
        self.current_cutscene = cutscene_lines
        self.current_line = 0
        self.current_text = ""
        self.text_progress = 0
        self.last_char_time = pygame.time.get_ticks()
        self.gm.set_game_state(STATE_CUTSCENE_INTRO if cutscene_lines == INTRO_CUTSCENE else STATE_CUTSCENE_OUTRO)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.current_line < len(self.current_cutscene) - 1:
                self.current_line += 1
                self.current_text = ""
                self.text_progress = 0
                self.last_char_time = pygame.time.get_ticks()
            else:
                if self.current_cutscene == INTRO_CUTSCENE:
                    self.gm.start_gameplay()
                else:
                    self.gm.show_win_screen()
                self.current_cutscene = None

    def update(self):
        if self.current_cutscene and self.current_line < len(self.current_cutscene):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_char_time >= CUTSCENE_CHAR_DELAY:
                if self.text_progress < len(self.current_cutscene[self.current_line]):
                    self.current_text += self.current_cutscene[self.current_line][self.text_progress]
                    self.text_progress += 1
                    self.last_char_time = current_time
                else:
                    self.last_char_time = current_time

    def draw(self, surface):
        surface.fill(NEON_BLACK)
        if self.current_cutscene and self.current_line < len(self.current_cutscene):
            rect = pygame.Rect(WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8)
            pygame.draw.rect(surface, DARK_GLOW, rect)
            pygame.draw.rect(surface, NEON_CYAN, rect, 3)
            message_rect = pygame.Rect(rect.x + 20, rect.y + 30, rect.width - 40, rect.height - 60)
            y = wrap_text(surface, self.current_text, self.font, NEON_WHITE, message_rect)
            prompt = self.font.render("Press SPACE to continue", True, NEON_CYAN)
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))