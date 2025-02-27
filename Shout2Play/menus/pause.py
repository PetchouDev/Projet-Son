import pygame
from config import *

class Pause:
    def __init__(self):
        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused

    def draw(self, screen):
        if self.paused:
            font = pygame.font.Font(None, 50)
            text = font.render("PAUSE", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
