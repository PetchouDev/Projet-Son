import pygame
import random
from config import *

class Platform:
    def __init__(self, x, y, width=100, height=20):
        self.x = x
        self.y = y

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def generate_platforms(num_platforms):
    platforms = []
    for i in range(num_platforms):
        x = random.randint(100, WIDTH - 100)
        y = HEIGHT - (i * 100) - 200
        platforms.append(Platform(x, y))
    return platforms