import pygame
from config import *

class Bullet:
    def __init__(self, x, y, speed=10):
        self.image = pygame.image.load("voice-platformer/assets/bullet.png")
        self.x = x
        self.y = y
        self.width = 10
        self.speed = speed
        self.active = True

    def update(self):
        self.x += self.speed
        if self.x > 1.25*WIDTH:
            self.active = False
                
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def generate_bullet(x, y):
    return Bullet(x, y)
