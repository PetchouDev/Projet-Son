import pygame
from config import *

class Background:
    def __init__(self):
        self.bg = pygame.image.load("assets/background.png")
        self.mountains = pygame.image.load("assets/mountains.png")
        self.clouds = pygame.image.load("assets/clouds.png")

        self.bg_x = 0
        self.clouds_x = 0
        self.mountains_x = 0

    def update(self):
        self.clouds_x -= 0.5
        self.mountains_x -= 1
        if self.clouds_x <= -WIDTH: self.clouds_x = 0
        if self.mountains_x <= -WIDTH: self.mountains_x = 0

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        screen.blit(self.clouds, (self.clouds_x, 50))
        screen.blit(self.clouds, (self.clouds_x + WIDTH, 50))
        screen.blit(self.mountains, (self.mountains_x, 300))
        screen.blit(self.mountains, (self.mountains_x + WIDTH, 300))
