import pygame
from config import *

class Background:
    def __init__(self):
        self.bg = pygame.image.load("voice-platformer/assets/background.png")
        self.mountains = pygame.image.load("voice-platformer/assets/mountain.png")
        self.clouds = pygame.image.load("voice-platformer/assets/cloud.png")

        self.bg_x = 0
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.clouds_x = 0
        self.clouds = pygame.transform.scale(self.clouds, (WIDTH // 6, HEIGHT // 6)) 
        self.mountains_x = 0
        self.mountains = pygame.transform.scale(self.mountains, (WIDTH, HEIGHT // 3)) 

    def update(self):
        self.clouds_x -= 0.5
        self.mountains_x -= 1
        if self.clouds_x <= -WIDTH: self.clouds_x = 0
        if self.mountains_x <= -WIDTH: self.mountains_x = 0

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        screen.blit(self.clouds, (self.clouds_x, 50))
        screen.blit(self.clouds, (self.clouds_x + WIDTH, 50))
        screen.blit(self.mountains, (self.mountains_x, 350))
        screen.blit(self.mountains, (self.mountains_x + WIDTH, 350))
