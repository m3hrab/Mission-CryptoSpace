import pygame
import random
import math
from config import *

class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
        self.vy = random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(50, 100)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.reset()

    def draw(self, surface):
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, PARTICLE_GLOW, (self.size, self.size), self.size)
        surface.blit(particle_surface, (int(self.x) - self.size, int(self.y) - self.size))

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, action=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
        self.base_color = DARK_GLOW
        self.text_color = NEON_WHITE
        self.action = action
        self.is_hovered = False
        self.glow_alpha = 0
        self.glow_speed = 5
        self.click_scale = 1.0
        self.click_duration = 100
        self.click_time = 0

    def update(self):
        if self.is_hovered:
            self.glow_alpha = min(self.glow_alpha + self.glow_speed, BUTTON_GLOW_INTENSITY)
        else:
            self.glow_alpha = max(self.glow_alpha - self.glow_speed, 0)
        if self.click_time and pygame.time.get_ticks() - self.click_time < self.click_duration:
            self.click_scale = 0.95
        else:
            self.click_scale = 1.0

    def draw(self, surface):
        scaled_rect = pygame.Rect(
            self.rect.x + self.rect.width * (1 - self.click_scale) / 2,
            self.rect.y + self.rect.height * (1 - self.click_scale) / 2,
            self.rect.width * self.click_scale,
            self.rect.height * self.click_scale
        )
        glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (0, 255, 255, int(self.glow_alpha)), (10, 10, self.rect.width, self.rect.height), border_radius=10)
        surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        pygame.draw.rect(surface, self.base_color, scaled_rect, border_radius=5)
        pygame.draw.rect(surface, NEON_CYAN, scaled_rect, 2, border_radius=5)
        text_surface = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surface, (scaled_rect.centerx - text_surface.get_width() // 2, scaled_rect.centery - text_surface.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered and self.action:
            self.click_time = pygame.time.get_ticks()
            self.action()
            return True
        return False

class UIManager:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.message = ""
        self.message_color = NEON_WHITE
        self.message_start = 0
        self.message_alpha = 255
        self.particles = [Particle() for _ in range(PARTICLE_COUNT)]
        self.flicker_state = True
        self.last_flicker = 0
        self.flicker_interval = 2000
        self.music_playing = False
        self.ambience_playing = False
        self.low_oxygen_channel = None
        self.tooltip = ""
        self.tooltip_alpha = 0
        self.tooltip_start = 0

    def set_message(self, message, color=NEON_WHITE):
        self.message = message
        self.message_color = color
        self.message_start = pygame.time.get_ticks()
        self.message_alpha = 255

    def set_tooltip(self, tooltip):
        self.tooltip = tooltip
        self.tooltip_start = pygame.time.get_ticks()
        self.tooltip_alpha = 0

    def play_menu_music(self):
        if not self.music_playing and os.path.exists(MENU_MUSIC):
            try:
                pygame.mixer.music.load(MENU_MUSIC)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except pygame.error:
                pass

    def stop_music(self):
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def play_gameplay_ambience(self):
        if not self.ambience_playing and os.path.exists(STATION_AMBIENCE):
            try:
                pygame.mixer.music.load(STATION_AMBIENCE)
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
                self.ambience_playing = True
            except pygame.error:
                pass

    def stop_gameplay_ambience(self):
        if self.ambience_playing:
            pygame.mixer.music.stop()
            self.ambience_playing = False

    def play_low_oxygen_alert(self):
        if not self.low_oxygen_channel and os.path.exists(LOW_OXYGEN_ALERT):
            try:
                sound = pygame.mixer.Sound(LOW_OXYGEN_ALERT)
                self.low_oxygen_channel = pygame.mixer.Channel(1)
                self.low_oxygen_channel.set_volume(0.6)
                self.low_oxygen_channel.play(sound, loops=-1)
            except pygame.error:
                pass

    def stop_low_oxygen_alert(self):
        if self.low_oxygen_channel:
            self.low_oxygen_channel.stop()
            self.low_oxygen_channel = None

    def play_sound(self, sound_file, volume):
        if os.path.exists(sound_file):
            try:
                sound = pygame.mixer.Sound(sound_file)
                channel = pygame.mixer.find_channel()
                if channel:
                    channel.set_volume(volume)
                    channel.play(sound)
            except pygame.error:
                pass

    def update(self):
        for particle in self.particles:
            particle.update()
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flicker >= self.flicker_interval:
            self.flicker_state = not self.flicker_state
            self.last_flicker = current_time
            self.flicker_interval = random.randint(1000, 3000)
        if self.message_start and current_time - self.message_start >= MESSAGE_DURATION - MESSAGE_FADE_DURATION:
            elapsed = current_time - (self.message_start + MESSAGE_DURATION - MESSAGE_FADE_DURATION)
            self.message_alpha = max(0, 255 - int(255 * elapsed / MESSAGE_FADE_DURATION))
        if self.tooltip:
            elapsed = current_time - self.tooltip_start
            if elapsed < TOOLTIP_FADE_DURATION:
                self.tooltip_alpha = min(255, int(255 * elapsed / TOOLTIP_FADE_DURATION))
            elif current_time - self.tooltip_start >= MESSAGE_DURATION - TOOLTIP_FADE_DURATION:
                elapsed = current_time - (self.tooltip_start + MESSAGE_DURATION - TOOLTIP_FADE_DURATION)
                self.tooltip_alpha = max(0, 255 - int(255 * elapsed / TOOLTIP_FADE_DURATION))
                if self.tooltip_alpha == 0:
                    self.tooltip = ""
        if self.gm.game_state == STATE_GAMEPLAY and not self.ambience_playing:
            self.play_gameplay_ambience()
        if self.gm.game_state == STATE_GAMEPLAY and self.gm.player.oxygen <= VIGNETTE_THRESHOLD and not self.low_oxygen_channel:
            self.play_low_oxygen_alert()
        elif self.gm.game_state != STATE_GAMEPLAY or self.gm.player.oxygen > VIGNETTE_THRESHOLD:
            self.stop_low_oxygen_alert()

    def draw_mini_map(self, surface):
        center = (WIDTH - MINI_MAP_RADIUS - 20, MINI_MAP_RADIUS + 20)
        map_surface = pygame.Surface((MINI_MAP_RADIUS * 2, MINI_MAP_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(map_surface, HOLO_GLOW, (MINI_MAP_RADIUS, MINI_MAP_RADIUS), MINI_MAP_RADIUS)
        surface.blit(map_surface, (center[0] - MINI_MAP_RADIUS, center[1] - MINI_MAP_RADIUS))
        pygame.draw.circle(surface, NEON_CYAN, center, MINI_MAP_RADIUS, 2)
        room_positions = {
            "control_room": (0, -MINI_MAP_RADIUS * 0.6),  # Top
            "lab_room": (0, 0),                          # Center
            "distress_room": (0, MINI_MAP_RADIUS * 0.6)  # Bottom
        }
        current_room_key = self.gm.current_room.name.lower().replace(" ", "_")
        for room_key, (dx, dy) in room_positions.items():
            pos = (center[0] + dx, center[1] + dy)
            color = NEON_GREEN if room_key == current_room_key else NEON_BLUE
            pygame.draw.circle(surface, color, pos, 8)  # Larger dots for visibility
        font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_SM)
        label = font.render("RADAR", True, NEON_WHITE)
        surface.blit(label, (center[0] - label.get_width() // 2, center[1] + MINI_MAP_RADIUS + 5))

    def draw_gameplay(self, surface):
        hud_rect = pygame.Rect(10, 10, 220, 100)
        panel = pygame.Surface((220, 100), pygame.SRCALPHA)
        panel.fill((40, 40, 60, HUD_PANEL_ALPHA))
        surface.blit(panel, hud_rect)
        pygame.draw.rect(surface, NEON_CYAN, hud_rect, 2, border_radius=10)
        font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_SM)
        oxygen_width = int(180 * (self.gm.player.oxygen / 100))
        pygame.draw.rect(surface, DARK_GLOW, (20, 20, 180, 20), 0, 5)
        pygame.draw.rect(surface, NEON_GREEN, (20, 20, oxygen_width, 20), 0, 5)
        pygame.draw.rect(surface, NEON_CYAN, (20, 20, 180, 20), 1, 5)
        oxygen_text = font.render(f"Oxygen: {int(self.gm.player.oxygen)}%", True, NEON_WHITE)
        surface.blit(oxygen_text, (20, 45))
        suit_width = int(180 * (self.gm.player.suit_integrity / 100))
        pygame.draw.rect(surface, DARK_GLOW, (20, 60, 180, 20), 0, 5)
        pygame.draw.rect(surface, NEON_LIGHT_BLUE, (20, 60, suit_width, 20), 0, 5)
        pygame.draw.rect(surface, NEON_CYAN, (20, 60, 180, 20), 1, 5)
        suit_text = font.render(f"Suit: {int(self.gm.player.suit_integrity)}%", True, NEON_WHITE)
        surface.blit(suit_text, (20, 85))
        if self.gm.player.oxygen <= VIGNETTE_THRESHOLD:
            vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(vignette, VIGNETTE_GLOW, (WIDTH // 2, HEIGHT // 2), WIDTH, WIDTH // 4)
            surface.blit(vignette, (0, 0))
        if self.message and self.message_alpha > 0:
            font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
            message_surface = font.render(self.message, True, self.message_color)
            message_surface.set_alpha(self.message_alpha)
            surface.blit(message_surface, (WIDTH // 2 - message_surface.get_width() // 2, HEIGHT - 30))
        if self.tooltip and self.tooltip_alpha > 0:
            font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
            tooltip_surface = font.render(self.tooltip, True, NEON_CYAN)
            tooltip_surface.set_alpha(self.tooltip_alpha)
            surface.blit(tooltip_surface, (WIDTH // 2 - tooltip_surface.get_width() // 2, HEIGHT - 100))
        self.draw_mini_map(surface)
        if self.gm.alarm_on and self.gm.alarm_visible:
            alarm = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alarm.fill(ALARM_GLOW)
            surface.blit(alarm, (0, 0))

    def draw_menu(self, buttons):
        self.gm.screen.fill(NEON_BLACK)
        for particle in self.particles:
            particle.draw(self.gm.screen)
        rect = pygame.Rect(WIDTH // 4, HEIGHT // 4 - 20, WIDTH // 2, HEIGHT // 2 + 100)
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((40, 40, 60, HUD_PANEL_ALPHA))
        self.gm.screen.blit(panel, rect)
        pygame.draw.rect(self.gm.screen, NEON_CYAN, rect, 3, border_radius=10)
        font_xl = pygame.font.Font(FONT_BOLD, FONT_SIZE_XL)
        title = font_xl.render("Crypternity", True, NEON_WHITE if self.flicker_state else NEON_CYAN)
        self.gm.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4 ))
        # font_md = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
        # subtitle = font_md.render("Martian Decipher", True, NEON_CYAN)
        # self.gm.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 4 + 30 + font_xl.get_height() + 10))
        for button in buttons:
            button.update()
            button.draw(self.gm.screen)
        self.play_menu_music()

    def draw_how_to_play(self, text_lines, back_button):
        self.gm.screen.fill(NEON_BLACK)
        for particle in self.particles:
            particle.draw(self.gm.screen)
        rect = pygame.Rect(WIDTH // 8, HEIGHT // 8, WIDTH * 6 // 8, HEIGHT * 6 // 8)
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((40, 40, 60, HUD_PANEL_ALPHA))
        self.gm.screen.blit(panel, rect)
        pygame.draw.rect(self.gm.screen, NEON_CYAN, rect, 3, border_radius=10)
        font = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
        y = HEIGHT // 8 + 30
        for line in text_lines:
            text = font.render(line, True, NEON_WHITE)
            self.gm.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 25
        back_button.update()
        back_button.draw(self.gm.screen)

    def draw_game_over(self, restart_button):
        self.gm.screen.fill(NEON_BLACK)
        for particle in self.particles:
            particle.draw(self.gm.screen)
        font_lg = pygame.font.Font(FONT_BOLD, FONT_SIZE_LG)
        font_md = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
        title = font_lg.render("MISSION FAILED", True, NEON_RED)
        self.gm.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
        message = font_md.render("Oxygen Depleted or Suit Breached!", True, NEON_WHITE)
        self.gm.screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 30))
        restart_button.update()
        restart_button.draw(self.gm.screen)
        exit_text = font_md.render("Press ESC to exit", True, NEON_WHITE)
        self.gm.screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 100))
        self.stop_music()

    def draw_win_screen(self, restart_button):
        self.gm.screen.fill(NEON_BLACK)
        for particle in self.particles:
            particle.draw(self.gm.screen)
        font_lg = pygame.font.Font(FONT_BOLD, FONT_SIZE_LG)
        font_md = pygame.font.Font(FONT_MEDIUM, FONT_SIZE_MD)
        title = font_lg.render("MISSION SUCCESS!", True, NEON_GREEN)
        self.gm.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
        message = font_md.render("Distress Signal Sent!", True, NEON_WHITE)
        self.gm.screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 30))
        restart_button.update()
        restart_button.draw(self.gm.screen)
        exit_text = font_md.render("Press ESC to exit", True, NEON_WHITE)
        self.gm.screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 100))
        self.stop_music()