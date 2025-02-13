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
        self.display_size = (TILE_SIZE, TILE_SIZE)

        self.left = get_image(self, 3, 0, self.display_size[0])
        self.middle = get_image(self, 4, 0, self.display_size[0])
        self.right = get_image(self, 5, 0, self.display_size[0])

        self.speed = 0.5

    def spawn_platform(self):
        if self.x < -self.display_size[0]*2:
            self.x += self.display_size[0]*2

    def draw(self, screen):
        i = 0
        screen.blit(self.left, (self.x - TILE_SIZE/2, self.y))
        while i < self.width:
            screen.blit(self.middle, (self.x + i * TILE_SIZE, self.y))
            i += 1
        screen.blit(self.right, (self.x + i * TILE_SIZE, self.y))

    def update(self, speed):
        self.x -= self.speed*speed

def generate_platforms(before):
    min_x = before.x+(before.width+2)*TILE_SIZE
    x = random.randint(int(min_x), int(min_x+TILE_SIZE*4))
    y_borne1 = int(max(TILE_SIZE*2, before.y-TILE_SIZE*4))
    y_borne2 = int(min(HEIGHT-TILE_SIZE*1, before.y+TILE_SIZE*4))
    if y_borne1 > y_borne2:
        y = random.randint(y_borne2, y_borne1)
    else:
        y = random.randint(y_borne1, y_borne2)
    return Platform(x, y, width=random.randint(1, 4))