import pygame
from ..config import *

class Player:
    def __init__(self, mode):
        self.image = pygame.image.load("assets/player.png")
        self.x = WIDTH // 4
        self.y = HEIGHT - 100
        self.width = 50
        self.height = 50
        self.y_velocity = 0
        self.max_gain = 0
        self.loading = 0
        self.alive = True
        self.mode = 5+mode


    def update(self, gain, loading_bullet):
        self.loading += loading_bullet/(self.mode)
        d_gain = max(0, gain - self.max_gain)
        if d_gain > 0.1:
            self.y_velocity = d_gain * JUMP_FACTOR
            self.max_gain = gain

        self.y_velocity -= GRAVITY
        self.y -= self.y_velocity

        if self.y >= HEIGHT - 100:
            self.y = HEIGHT - 100
            self.y_velocity = 0
            self.max_gain = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
