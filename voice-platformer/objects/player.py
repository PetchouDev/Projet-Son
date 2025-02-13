import time
import pygame
from config import *

from core.utils import get_image

class Player:
    def __init__(self, mode=False):
        self.sprite_sheet = pygame.image.load("voice-platformer/assets/ducky_player.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (self.sprite_sheet.get_width() * 2, self.sprite_sheet.get_height() * 2))
        self.sprite_size = (64, 64)
        self.display_size = (192, 192)
        self.images = [get_image(self, col, 1, self.display_size[0]) for col in range(6)]
        self.animate_delay = 0.1
        self.animate_timer = 0
        self.animate_index = 0

        self.x = WIDTH // 4
        self.y = HEIGHT - 100 - self.display_size[1]
        self.width = 50
        self.height = 50
        self.velocity_y = 0
        self.objective = self.y
        self.monte = False
        self.was_on_ground = 1
        self.max_gain = 0
        self.loading = 0
        self.alive = True
        self.divide = 6
        if mode:
            self.divide += 1

    def change_mode(self, mode):
        self.divide = 6
        if mode:
            self.divide += 1

    def update(self, loading_bullet, jump_power, platforms, game_speed=1):
        if jump_power > THRESHOLD:
            self.loading += loading_bullet / self.divide
            if self.was_on_ground:
                jump_power *= 0.7
            if jump_power > self.max_gain:  # Seulement si la nouvelle puissance est plus forte
                if self.was_on_ground:
                    jump_power *= 1.2
                self.velocity_y = -(jump_power - self.max_gain) * JUMP_FACTOR*3  # Applique la force du saut
                self.max_gain = jump_power  # Mémorise la puissance du saut
                self.monte = True  # Indique qu'on est en l'air
                self.was_on_ground = False
        
        # Appliquer la gravité si en l'air
        if self.velocity_y != 0:
            self.y += max(min(self.velocity_y, game_speed*50), -game_speed*50) * game_speed
        final_pos = self.ground(platforms)
        if not final_pos or self.monte:
            self.max_gain *=0.995  # Réduit la puissance max
            self.velocity_y += 6*GRAVITY  # Ajouter une constante de gravité
            if self.velocity_y > 0:
                self.monte = False
        else:
            self.was_on_ground = True
            self.y = final_pos - self.display_size[1]
            self.velocity_y = 0  # Arrêter tout mouvement vertical
            self.max_gain = 0  # Réinitialiser le gain pour un nouveau saut


    def draw(self, screen, game_speed=1):
        if game_speed>0:
            self.animate_timer += 1 / 25
            if self.animate_timer >= self.animate_delay * 8 / game_speed:
                self.animate_timer = 0
                self.animate_index = (self.animate_index + 1) % len(self.images)
        image = self.images[self.animate_index]
        screen.blit(image, (self.x, self.y + 6))

    def ground(self, platforms):
        for platform in platforms:
            if pygame.Rect(self.x, self.y, self.display_size[0], self.display_size[1]).colliderect(platform.x+TILE_SIZE/2, platform.y, (platform.width) * TILE_SIZE, TILE_SIZE):
                return platform.y
        return None