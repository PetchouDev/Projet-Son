import pygame
from config import *

class UI:
    def __init__(self, font_path="voice-platformer/assets/font.otf"):
        self.font = pygame.font.Font(font_path, 36)

    def draw_start_menu(self, screen):
        text = self.font.render("Appuyez sur Start (Teensy) pour jouer", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    def draw_pause_menu(self, screen):
        text = self.font.render("PAUSE - Appuyez sur Start pour reprendre", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    def draw_game_over(self, screen, score):
        text = self.font.render(f"GAME OVER - Score: {score}", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
