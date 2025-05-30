import pygame
from config import *

def wrap_text(surface, text, font, color, rect):
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
    return y_offset

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, name="GameObject"):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name
        self.glow_alpha = 0
        self.glow_direction = 1

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        glow_surface.fill((*self.image.get_at((0,0))[:3], self.glow_alpha))
        surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))

    def update_glow(self):
        self.glow_alpha += GLOW_PULSE_SPEED * self.glow_direction
        if self.glow_alpha >= 100:
            self.glow_alpha = 100
            self.glow_direction = -1
        elif self.glow_alpha <= 0:
            self.glow_alpha = 0
            self.glow_direction = 1

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 25, 25, NEON_GREEN, "Player")
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
        self.rect.clamp_ip(pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100))
        current_time = pygame.time.get_ticks()
        if current_time - self.last_oxygen_tick >= 1000:
            if moved:
                self.suit_integrity -= SUIT_DAMAGE_RATE
                self.suit_integrity = max(0, self.suit_integrity)
            if self.suit_integrity < 100:
                self.oxygen -= OXYGEN_DEPLETION_RATE
            self.last_oxygen_tick = current_time
            if self.oxygen <= 0 or self.suit_integrity <= 0:
                self.oxygen = self.suit_integrity = 0
                self.is_alive = False
        self.update_glow()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.oxygen = 100.0
        self.suit_integrity = 100.0
        self.is_alive = True
        self.last_oxygen_tick = pygame.time.get_ticks()

class Door(GameObject):
    def __init__(self, x, y, width, height, target_room_key, target_x, target_y):
        super().__init__(x, y, width, height, NEON_BLUE, "Door")
        self.target_room_key = target_room_key
        self.target_x = target_x
        self.target_y = target_y
        self.is_locked = True
        self.unlocked_color = NEON_CYAN

    def interact(self, player, game_manager):
        if not self.is_locked:
            game_manager.ui_manager.set_game_message("Door Unlocked! Transitioning...", NEON_PURPLE)
            if self.target_room_key == "win_room":
                game_manager.start_final_cutscene()
            else:
                game_manager.set_current_room(self.target_room_key)
                player.rect.x = self.target_x
                player.rect.y = self.target_y
        else:
            game_manager.ui_manager.set_game_message("Door Locked.", NEON_RED)

    def unlock(self):
        self.is_locked = False
        self.image.fill(self.unlocked_color)

    def reset(self):
        self.is_locked = True
        self.image.fill(NEON_BLUE)

class Room:
    def __init__(self, name, interactive_objects):
        self.name = name
        self.interactive_objects = pygame.sprite.Group(interactive_objects)

    def draw(self, surface):
        surface.fill(DARK_CARBON)
        pygame.draw.rect(surface, CARBON_GRID, (50, 50, WIDTH - 100, HEIGHT - 100))
        for i in range(50, WIDTH - 50, 20):
            pygame.draw.line(surface, CARBON_GRID, (i, 50), (i, HEIGHT - 50), 1)
        for i in range(50, HEIGHT - 50, 20):
            pygame.draw.line(surface, CARBON_GRID, (50, i), (WIDTH - 50, i), 1)
        pygame.draw.rect(surface, NEON_CYAN, (50, 50, WIDTH - 100, HEIGHT - 100), 3)
        self.interactive_objects.draw(surface)
        for obj in self.interactive_objects:
            obj.update_glow()
        font = pygame.font.Font(None, FONT_SIZE_LG)
        text = font.render(self.name, True, WHITE)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))