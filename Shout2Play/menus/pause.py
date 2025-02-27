import pygame

from config import *

class Pause:
    """
    Classe représentant l'état de pause du jeu.
    Elle permet de mettre le jeu en pause et d'afficher un message "PAUSE" à l'écran.
    """
    def __init__(self):
        """
        Initialise l'état de la pause (par défaut, non-pause).
        """
        self.paused = False

    def toggle_pause(self):
        """
        Inverse l'état de la pause.
        Si le jeu est en pause, il reprend. Sinon, il se met en pause.
        """
        self.paused = not self.paused

    def draw(self, screen):
        """
        Dessine un message "PAUSE" à l'écran lorsque le jeu est en pause.
        
        :param screen: l'écran sur lequel dessiner le message de pause
        """
        if self.paused:
            # Police et taille du texte
            font = pygame.font.Font(None, 50)
            text = font.render("PAUSE", True, WHITE)
            
            # Affichage du texte centré sur l'écran
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
