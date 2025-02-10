import pygame
import random
from ..config import *

class Enemy:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/enemy.png")
        self.x = x
        self.y = y
        self.active = True

    def update(self):
        if self.x < -50:
            self.active = False

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def generate_enemy():
    return Enemy(WIDTH, random.randint(200, HEIGHT - 100))
