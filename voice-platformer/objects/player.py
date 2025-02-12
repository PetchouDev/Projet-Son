import pygame
from config import *

class Player:
    def __init__(self, mode):
        self.image = pygame.image.load("voice-platformer/assets/player.png")
        self.x = WIDTH // 4
        self.y = HEIGHT - 100
        self.width = 50
        self.height = 50
        self.y_velocity = 0
        self.max_gain = 0
        self.loading = 0
        self.alive = True
        self.divide = 5
        if mode:
            self.mode += 1

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

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
