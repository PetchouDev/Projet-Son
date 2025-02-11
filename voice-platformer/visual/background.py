import pygame
import random
from config import *

class Background:
    def __init__(self):
        self.bg = pygame.image.load("voice-platformer/assets/background.png")
        self.mountains = pygame.image.load("voice-platformer/assets/mountain.png")
        self.clouds = pygame.image.load("voice-platformer/assets/cloud.png")

        self.bg_y = 0
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.clouds = pygame.transform.scale(self.clouds, (WIDTH // 6, HEIGHT // 6)) 
        self.mountains = pygame.transform.scale(self.mountains, (WIDTH, HEIGHT // 3)) 

        self.cloud_positions = [(random.randint(0, WIDTH), random.randint(50, 200)) for _ in range(5)]
        self.mountain_positions = [(random.randint(0, WIDTH), 350) for _ in range(3)]

    def update(self):
        self.bg_y += 1
        if self.bg_y >= HEIGHT:
            self.bg_y = 0

        self.cloud_positions = [(x - 0.5 if x > -WIDTH // 6 else WIDTH, y) for x, y in self.cloud_positions]
        self.mountain_positions = [(x - 1 if x > -WIDTH else WIDTH, y) for x, y in self.mountain_positions]

    def draw(self, screen):
        screen.blit(self.bg, (0, self.bg_y))
        screen.blit(self.bg, (0, self.bg_y - HEIGHT))
        
        for x, y in self.cloud_positions:
            screen.blit(self.clouds, (x, y))
        
        for x, y in self.mountain_positions:
            screen.blit(self.mountains, (x, y))
