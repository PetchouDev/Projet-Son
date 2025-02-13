import pygame
import random
from config import *

from core.utils import get_image

class Enemy:
    def __init__(self, x, y):
        self.sprite_sheet = pygame.image.load("voice-platformer/assets/ducky_enemy.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (self.sprite_sheet.get_width() * 2, self.sprite_sheet.get_height() * 2))
        self.sprite_size = (64, 64)
        self.display_size = (192, 192)
        self.images = [pygame.transform.flip(get_image(self, col, 2, self.display_size[0]), True, False) for col in range(4)]
        self.animate_delay = 0.2
        self.animate_timer = 0
        self.animate_index = 0

        self.x = x
        self.y = y - self.display_size[1]
        self.width = 50
        self.height = 50
        self.speed = 0.5

    def draw(self, screen, game_speed=1):
        if game_speed>0:
            self.animate_timer += 1 / 25
            if self.animate_timer >= self.animate_delay * 8 / game_speed:
                self.animate_timer = 0
                self.animate_index = (self.animate_index + 1) % len(self.images)
        image = self.images[self.animate_index]
        screen.blit(image, (self.x, self.y + 6))

    def update(self, speed):
        self.x -= self.speed*speed

def generate_enemy(platform):
    return Enemy(random.randint(int(platform.x+TILE_SIZE/2), int(platform.x+(platform.width-0.5)*(TILE_SIZE))), platform.y) 