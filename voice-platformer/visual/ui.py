import pygame
from config import *

class UI:
    def __init__(self, font_path="voice-platformer/assets/font.otf"):
        self.font = pygame.font.Font(font_path, 40)

    def draw_text(self, screen, text, color, y_offset=0):
        lines = self.split_text(text, screen.get_width() - 40)  # Ajuste la largeur max
        y = HEIGHT * 0.4 + y_offset - (len(lines) * self.font.get_height()) // 2
        for line in lines:
            rendered_text = self.font.render(line, True, color)
            screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y))
            y += self.font.get_height()

    def split_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def draw_start_menu(self, screen):
        self.draw_text(screen, "SHOUT 2 PLAY", WHITE)
    
    def draw_pause_menu(self, screen):
        self.draw_text(screen, "PAUSE - Criez pour reprendre", WHITE)
    
    def draw_game_over(self, screen, score):
        self.draw_text(screen, f"GAME OVER - Score: {score}", RED)
