import pygame
from config import *

class UI:
    def __init__(self, font_path="voice-platformer/assets/font.otf"):
        self.font = pygame.font.Font(font_path, 40)
        self.font2 = pygame.font.Font(font_path, 25)
        self.note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.notes = []
        self.note_labels = []
        self.lastfreq = 0
        for octave in range(9):  # De l'octave 0 à 8
            for i, base_freq in enumerate([16.35, 17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50, 29.14, 30.87]):
                freq_octave = base_freq * (2 ** octave)
                if freq_octave > 7902.13:  # Limite supérieure
                    break
                self.notes.append(freq_octave)
                self.note_labels.append(f"{self.note_names[i]}{octave}")
        
    def draw_text(self, screen, text, color, y_offset=0):
        lines = self.split_text(text, screen.get_width() - 40)  # Ajuste la largeur max
        y = HEIGHT * 0.4 + y_offset - (len(lines) * self.font.get_height()) // 2
        for line in lines:
            rendered_text = self.font.render(line, True, color)
            screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y))
            y += self.font.get_height()
    
    def draw_start_text(self, screen, text, score, color, y_offset=0):
        lines = self.split_text(text, screen.get_width() - 40)  # Ajuste la largeur max
        lines2 = self.split_text(score, screen.get_width() - 40)  # Ajuste la largeur max
        y = HEIGHT * 0.4 + y_offset - (len(lines) * self.font.get_height()) // 2
        for line in lines:
            rendered_text = self.font.render(line, True, color)
            screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y))
            y += self.font.get_height()
        for line2 in lines2:
            rendered_text = self.font2.render(line2, True, color)
            screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y))
            y += self.font2.get_height()

    def freq_to_note(self, screen, freq, active=False, color=WHITE):
        if active:
            self.lastfreq = freq
        else:
            freq = self.lastfreq
        closest_index = min(range(len(self.notes)), key=lambda i: abs(self.notes[i] - freq))  # Trouver l'index de la note la plus proche
        closest = self.notes[closest_index]
        note = self.note_labels[closest_index]
            
        # Calculer l'écart relatif en fonction de la moitié de la distance avec la note précédente ou suivante
        if closest_index == 0:
            reference_gap = (self.notes[1] - self.notes[0]) / 2
        elif closest_index == len(self.notes) - 1:
            reference_gap = (self.notes[-1] - self.notes[-2]) / 2
        else:
            lower_gap = (closest - self.notes[closest_index - 1]) / 2
            upper_gap = (self.notes[closest_index + 1] - closest) / 2
            reference_gap = lower_gap if freq < closest else upper_gap
            
        relative_diff = (freq - closest) / reference_gap * 100  # Calcul de l'écart relatif
        lines = ["Accordeur intégré", f"Fréquence: {freq:.2f} Hz", f"Note proche: {note}"]
        if self.lastfreq == 0:
            lines = ["Accordeur intégré", f"Fréquence: // Hz", f"Note proche: //"]
            relative_diff = 0
        y = HEIGHT * 0.55 - (len(lines) * self.font2.get_height()) // 2
        for line in lines:
            if line == lines[0]:
                rendered_text = self.font.render(line, True, color)
                screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y))
                y += self.font.get_height()*1.2
            else:
                rendered_text = self.font2.render(line, True, color)
                screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y))
                y += self.font2.get_height()  
        # Dessiner la barre grise
        bar_width = WIDTH // 2
        bar_height = HEIGHT / 20
        bar_x = (WIDTH - bar_width) // 2
        bar_y = y + bar_height/2
        pygame.draw.rect(screen, (186, 186, 186), (bar_x, bar_y, bar_width, bar_height))
            
        # Dessiner la barre verte
        green_width = WIDTH // 20
        green_x = (WIDTH - green_width) // 2
        pygame.draw.rect(screen, (127, 221, 76), (green_x, bar_y, green_width, bar_height))
        
        # Dessiner le curseur rouge
        cursor_width = 5
        cursor_x = bar_x + (bar_width // 2) + (relative_diff / 100) * (bar_width // 2)
        cursor_x = max(bar_x, min(cursor_x, bar_x + bar_width))  # Limite dans la barre
        pygame.draw.rect(screen, (255, 0, 0), (cursor_x-cursor_width/2, bar_y - 10, cursor_width, bar_height + 20))
            
    
    def draw_score(self, screen, score, color=WHITE):
        text = f"Score: {score}"
        lines = self.split_text(text, screen.get_width() - 40)  # Ajuste la largeur max
        y = HEIGHT * 0.02 - (len(lines) * self.font2.get_height()) // 2
        for line in lines:
            rendered_text = self.font2.render(line, True, color)
            screen.blit(rendered_text, (WIDTH*0.02, y))
            y += self.font2.get_height()

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
    
    def draw_start_menu(self, screen, best_score):
        self.draw_start_text(screen, "SHOUT 2 PLAY", f"Best Score : {best_score}", WHITE)
    
    def draw_pause_menu(self, screen):
        self.draw_text(screen, "PAUSE", WHITE)
    
    def draw_game_over(self, screen, score):
        self.draw_text(screen, f"GAME OVER - Score: {score}", RED)
    
    def loading_bar(self, screen, loading):
        #pygame.draw.rect(screen, WHITE, (WIDTH*0.1, HEIGHT*0.9, WIDTH*0.8, 20))
        #pygame.draw.rect(screen, GREEN, (WIDTH*0.1, HEIGHT*0.9, WIDTH*0.8 * loading / max_loading, 20))
        bar_width = WIDTH/10 # Largeur totale de la barre
        bar_height = HEIGHT/20   # Hauteur de la barre
        x, y = WIDTH*0.02, HEIGHT*0.04   # Position de la barre
        
        # Dessiner le fond de la barre
        pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_width, bar_height))
        
        # Dessiner la progression
        fill_width = (loading%100)/100 * bar_width
        pygame.draw.rect(screen, (0, 150, 255), (x, y, fill_width, bar_height))

        text = self.font2.render(f"Munitions : {int(loading/100)}", True, (255, 255, 255))
        screen.blit(text, (x + bar_width + 10, y))
