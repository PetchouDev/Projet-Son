import pygame
import random
from core.utils import get_image
from config import *

class Platform:
    def __init__(self, x, y, width=5):
        self.x = x
        self.y = y

        self.width = width

        self.sprite_sheet = pygame.image.load("voice-platformer/assets/platforms.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (self.sprite_sheet.get_width() * 4, self.sprite_sheet.get_height() * 4))
        self.sprite_size = (64, 64)
        self.display_size = (128, 128)

        self.left = get_image(self, 3, 0, self.display_size[0])
        self.middle = get_image(self, 4, 0, self.display_size[0])
        self.right = get_image(self, 5, 0, self.display_size[0])


    def draw(self, screen):
        i = 0
        screen.blit(self.left, (self.x - 64, self.y))
        while i < self.width:
            screen.blit(self.middle, (self.x + i * 128, self.y))
            i += 1
        screen.blit(self.right, (self.x + i * 128, self.y))

def generate_platforms(num_platforms):
    platforms = []
    for i in range(num_platforms - 2):
        x = random.randint(100, WIDTH - 100)
        y = HEIGHT - (i * 100) - 200
        platforms.append(Platform(x, y))
    return platforms