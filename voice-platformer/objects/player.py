import time
import pygame
from config import *

from core.utils import get_image

class Player:
    def __init__(self, mode=0):
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
        self.y_velocity = 0
        self.max_gain = 0
        self.loading = 0
        self.alive = True
        self.divide = 5
        if mode:
            self.divide += 1

    def change_mode(self, mode):
        self.divide = 5
        if mode:
            self.divide += 1

    def update(self, loading_bullet, jump_power, running=True):
        self.loading += loading_bullet/(self.mode)
        d_gain = max(0, jump_power - self.max_gain)
        if d_gain > 0.1:
            self.y_velocity = d_gain * JUMP_FACTOR
            self.max_gain = jump_power

        self.y_velocity -= GRAVITY
        self.y -= self.y_velocity

        if self.y >= HEIGHT - 100:
            self.y = HEIGHT - 100
            self.y_velocity = 0
            self.max_gain = 0

    def draw(self, screen, game_speed=1):
        self.animate_timer += 1 / FPS
        if self.animate_timer >= self.animate_delay * 8 / game_speed:
            self.animate_timer = 0
            self.animate_index = (self.animate_index + 1) % len(self.images)
        image = self.images[self.animate_index]

        screen.blit(image, (self.x, self.y + 6))
