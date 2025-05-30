import pygame
from config import *
from helpers import wrap_text

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, FONT_SIZE_MD)
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.action = action
        self.glow_alpha = 0
        self.glow_direction = 1

    def draw(self, surface):
        self.glow_alpha += GLOW_PULSE_SPEED * self.glow_direction
        if self.glow_alpha >= 100:
            self.glow_alpha = 100
            self.glow_direction = -1
        elif self.glow_alpha <= 0:
            self.glow_alpha = 0
            self.glow_direction = 1
        glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        glow_surface.fill((*self.current_color[:3], self.glow_alpha))
        surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, NEON_CYAN, self.rect, 2, border_radius=5)
        text_surface = self.font.render(self.text, True, WHITE)
        surface.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2, self.rect.centery - text_surface.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.current_color = self.hover_color if self.rect.collidepoint(event.pos) else self.color
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos) and self.action:
            self.action()
            return True
        return False

class UIManager:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.game_message = ""
        self.message_color = WHITE
        self.message_start_time = 0
        self.fade_alpha = 0
        self.fade_direction = 0

    def set_game_message(self, message, color=WHITE):
        self.game_message = message
        self.message_color = color
        self.message_start_time = pygame.time.get_ticks()

    def draw_gameplay(self, surface):
        ui_panel = pygame.Rect(5, 5, 140, 70)
        pygame.draw.rect(surface, DARK_CARBON, ui_panel, border_radius=5)
        pygame.draw.rect(surface, NEON_CYAN, ui_panel, 2, border_radius=5)
        for i in range(ui_panel.left + 5, ui_panel.right - 5, 8):
            pygame.draw.line(surface, CARBON_GRID, (i, ui_panel.top + 5), (i, ui_panel.bottom - 5), 1)
        for i in range(ui_panel.top + 5, ui_panel.bottom - 5, 8):
            pygame.draw.line(surface, CARBON_GRID, (ui_panel.left + 5, i), (ui_panel.right - 5, i), 1)
        oxygen_width = int(120 * (self.gm.player.oxygen / 100))
        pygame.draw.rect(surface, DARK_RED, (15, 15, 120, 20), 0, 3)
        pygame.draw.rect(surface, NEON_GREEN, (15, 15, oxygen_width, 20), 0, 3)
        oxygen_text = pygame.font.Font(None, FONT_SIZE_SM).render(f"O2: {int(self.gm.player.oxygen)}%", True, WHITE)
        surface.blit(oxygen_text, (25, 19))
        suit_width = int(120 * (self.gm.player.suit_integrity / 100))
        pygame.draw.rect(surface, DARK_RED, (15, 45, 120, 20), 0, 3)
        pygame.draw.rect(surface, NEON_CYAN, (15, 45, suit_width, 20), 0, 3)
        suit_text = pygame.font.Font(None, FONT_SIZE_SM).render(f"SUIT: {int(self.gm.player.suit_integrity)}%", True, WHITE)
        surface.blit(suit_text, (25, 49))
        if self.game_message and (pygame.time.get_ticks() - self.message_start_time < MESSAGE_DURATION):
            prompt = pygame.font.Font(None, FONT_SIZE_MD).render(self.game_message, True, self.message_color)
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 30))
        else:
            interaction_prompt = ""
            for obj in self.gm.current_room.interactive_objects:
                if self.gm.player.rect.colliderect(obj.rect):
                    interaction_prompt = f"Press 'E' to interact with {obj.name}"
                    break
            if interaction_prompt:
                prompt = pygame.font.Font(None, FONT_SIZE_MD).render(interaction_prompt, True, WHITE)
                surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 30))
        if self.gm.alarm_on and self.gm.alarm_visible:
            alarm = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alarm.fill(ALARM_GLOW)
            surface.blit(alarm, (0, 0))

    def draw_menu(self, buttons):
        surface = self.gm.screen
        surface.fill(DARK_CARBON)
        pygame.draw.rect(surface, CARBON_GRID, (WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100), border_radius=10)
        pygame.draw.rect(surface, NEON_CYAN, (WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100), 3, border_radius=10)
        self._draw_centered_text(surface, "Crypternity", FONT_SIZE_XL, NEON_CYAN, HEIGHT // 4 + 30)
        self._draw_centered_text(surface, "Martian Decipher", FONT_SIZE_MD, NEON_PURPLE, HEIGHT // 4 + 30 + FONT_SIZE_XL + 10)
        for button in buttons:
            button.draw(surface)

    def draw_how_to_play(self, back_button):
        surface = self.gm.screen
        surface.fill(DARK_CARBON)
        rect = pygame.Rect(WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8)
        pygame.draw.rect(surface, CARBON_GRID, rect, border_radius=10)
        pygame.draw.rect(surface, NEON_CYAN, rect, 3, border_radius=10)
        text_lines = [
            "--- HOW TO PLAY ---",
            "Move: Arrow Keys or WASD",
            "Interact: Press 'E' near objects",
            "Solve Puzzles: Calculate M, enter, press ENTER",
            "  (M = C^d mod n)",
            "  (n = p*q, phi_n = (p-1)*(q-1), d = mod_inverse(e, phi_n))",
            "Press 'P': Show/hide solution (cheat)",
            "Exit Puzzle/Instructions: Press 'ESC'",
            "Unlock Doors: Decrypt terminals",
            "Survive: Monitor Oxygen & Suit Integrity",
            "Goal: Send distress signal"
        ]
        y_offset = HEIGHT // 8 + 30
        for line in text_lines:
            self._draw_centered_text(surface, line, FONT_SIZE_MD, WHITE, y_offset)
            y_offset += 25
        back_button.draw(surface)

    def draw_game_over(self, restart_button):
        surface = self.gm.screen
        surface.fill(DARK_CARBON)
        self._draw_centered_text(surface, "MISSION FAILED", FONT_SIZE_LG, NEON_RED, HEIGHT // 2 - 80)
        self._draw_centered_text(surface, "Oxygen Depleted or Suit Breached", FONT_SIZE_MD, WHITE, HEIGHT // 2 - 30)
        restart_button.draw(surface)
        self._draw_centered_text(surface, "Press ESC to exit", FONT_SIZE_MD, WHITE, HEIGHT // 2 + 100)

    def draw_win_screen(self, restart_button):
        surface = self.gm.screen
        surface.fill(DARK_CARBON)
        self._draw_centered_text(surface, "MISSION SUCCESS!", FONT_SIZE_LG, NEON_GREEN, HEIGHT // 2 - 80)
        self._draw_centered_text(surface, "Distress Signal Sent!", FONT_SIZE_MD, WHITE, HEIGHT // 2 - 30)
        restart_button.draw(surface)
        self._draw_centered_text(surface, "Press ESC to exit", FONT_SIZE_MD, WHITE, HEIGHT // 2 + 100)

    def _draw_centered_text(self, surface, text, font_size, color, y_offset):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))