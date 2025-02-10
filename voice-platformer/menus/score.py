import pygame
from config import *

class Score:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.value = 0

    def increase(self, amount=1):
        self.value += amount

    def draw(self, screen):
        text = self.font.render(f"Score: {self.value}", True, WHITE)
        screen.blit(text, (10, 10))
