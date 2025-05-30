import pygame
from config import *
from ui_elements import Button
from helpers import wrap_text

class CutsceneManager:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.script = []
        self.current_line_index = 0
        self.current_char_index = 0
        self.last_char_time = 0
        self.finished_typing = False
        self.skip_button = Button(WIDTH - 150, HEIGHT - 60, 120, 40, "Skip", NEON_PURPLE, NEON_CYAN, self.skip)
        self.next_button = Button(WIDTH - 280, HEIGHT - 60, 120, 40, "Next", NEON_PURPLE, NEON_CYAN, self.next_line)
        self.fade_alpha = 255
        self.fade_direction = -FADE_SPEED

    def start_cutscene(self, script):
        self.script = script
        self.current_line_index = 0
        self.current_char_index = 0
        self.last_char_time = pygame.time.get_ticks()
        self.finished_typing = False
        self.fade_alpha = 255
        self.fade_direction = -FADE_SPEED

    def next_line(self):
        if not self.finished_typing:
            self.current_char_index = len(self.script[self.current_line_index])
            self.finished_typing = True
        else:
            self.current_line_index += 1
            self.current_char_index = 0
            self.last_char_time = pygame.time.get_ticks()
            self.finished_typing = False
            if self.current_line_index >= len(self.script):
                self._finish_cutscene()

    def skip(self):
        self.current_line_index = len(self.script)
        self._finish_cutscene()

    def _finish_cutscene(self):
        if self.gm.game_state == STATE_CUTSCENE_INTRO:
            self.gm.start_gameplay()
        elif self.gm.game_state == STATE_CUTSCENE_OUTRO:
            self.gm.show_win_screen()

    def update(self):
        if self.current_line_index < len(self.script) and not self.finished_typing:
            if pygame.time.get_ticks() - self.last_char_time >= CUTSCENE_CHAR_DELAY:
                self.current_char_index += 1
                self.last_char_time = pygame.time.get_ticks()
                if self.current_char_index >= len(self.script[self.current_line_index]):
                    self.finished_typing = True
        self.fade_alpha = max(0, min(255, self.fade_alpha + self.fade_direction))

    def handle_event(self, event):
        self.skip_button.handle_event(event)
        self.next_button.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.next_line()

    def draw(self, surface):
        surface.fill(DARK_CARBON)
        if self.current_line_index < len(self.script):
            display_text = self.script[self.current_line_index][:self.current_char_index]
            text_rect = pygame.Rect(50, HEIGHT // 3, WIDTH - 100, HEIGHT // 3)
            wrap_text(surface, display_text, pygame.font.Font(None, FONT_SIZE_MD), WHITE, text_rect)
        self.skip_button.draw(surface)
        self.next_button.draw(surface)
        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.fade_alpha))
            surface.blit(fade, (0, 0))