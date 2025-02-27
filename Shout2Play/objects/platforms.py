import random

import pygame

from core.utils import get_image
from config import *


class Platform:
    """
    Classe représentant une plateforme dans le jeu, avec des caractéristiques
    comme la position, la largeur et les images associées à la plateforme.
    """
    def __init__(self, x, y, width=5, id=0):
        """
        Initialise la plateforme avec les paramètres de position, taille, et identifiant.
        
        :param x: la position horizontale de la plateforme
        :param y: la position verticale de la plateforme
        :param width: la largeur de la plateforme
        :param id: l'identifiant unique de la plateforme
        """
        self.x = x
        self.y = y
        self.id = id
        self.width = width

        # Chargement de la sprite sheet de la plateforme
        self.sprite_sheet = pygame.image.load("assets/platforms.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, 
                                                   (self.sprite_sheet.get_width() * 4, 
                                                    self.sprite_sheet.get_height() * 4))
        
        # Définition des tailles des sprites et des plateformes
        self.sprite_size = (64, 64)
        self.display_size = (TILE_SIZE, TILE_SIZE)
        
        # Initialisation de l'état de la plateforme
        self.has_enemy = False
        self.left = get_image(self, 3, 0, self.display_size[0])
        self.middle = get_image(self, 4, 0, self.display_size[0])
        self.right = get_image(self, 5, 0, self.display_size[0])
        self.size = TILE_SIZE * self.width
        self.player_on = False
        self.speed = 0.5

    def spawn_platform(self):
        """
        Vérifie si la plateforme doit être réinitialisée, si elle est hors de l'écran.
        """
        if self.x < -TILE_SIZE * 2:
            self.x += TILE_SIZE

    def draw(self, screen):
        """
        Dessine la plateforme à l'écran.
        
        :param screen: l'écran sur lequel dessiner la plateforme
        """
        i = 1
        # Dessiner la première image (bord gauche)
        screen.blit(self.left, (self.x, self.y))
        
        # Dessiner le reste de la plateforme (milieu ou droite)
        while i <= self.width:
            if i == self.width:
                screen.blit(self.right, (self.x + i * TILE_SIZE, self.y))
            else:
                screen.blit(self.middle, (self.x + i * TILE_SIZE, self.y))
            i += 1

    def draw_id(self, screen, color):
        """
        Dessine l'identifiant de la plateforme (utile pour le débogage).
        
        :param screen: l'écran sur lequel dessiner l'identifiant
        :param color: la couleur du texte
        """
        font_path = "voice-platformer/assets/font.otf"
        font = pygame.font.Font(font_path, 40)
        y = self.y - 100
        rendered_text = font.render(str(self.id), True, color)
        screen.blit(rendered_text, (self.x - rendered_text.get_width() // 2, y))

    def update(self, speed):
        """
        Met à jour la position de la plateforme en fonction de la vitesse.
        
        :param speed: la vitesse de déplacement
        """
        self.x -= self.speed * speed

def generate_platforms(before, game_speed=1):
    """
    Génère une nouvelle plateforme après une précédente plateforme.
    
    :param before: la plateforme précédemment générée
    :param game_speed: la vitesse du jeu, influençant la largeur et la position de la plateforme
    :return: une nouvelle instance de la classe Platform
    """
    max_width = int(2 + game_speed / SCROLL_SPEED)
    width = random.randint(1, max_width)
    
    # Calcul de la position horizontale minimale pour la nouvelle plateforme
    min_x = before.x + before.size + (1 / 2 + game_speed / (2 * SCROLL_SPEED)) * TILE_SIZE
    
    # Calcul des bornes pour la position verticale de la plateforme
    y_borne1 = int(max(TILE_SIZE * 2, before.y - TILE_SIZE * 3))
    y_borne2 = int(min(HEIGHT - TILE_SIZE * 0.5, before.y + TILE_SIZE * 3))
    
    # Sélection de la position verticale aléatoire
    if y_borne1 > y_borne2:
        y = random.randint(y_borne2, y_borne1)
    else:
        y = random.randint(y_borne1, y_borne2)
    
    # Calcul de la position horizontale de la nouvelle plateforme
    x = random.randint(int(min_x), int(min_x + TILE_SIZE * (max_width + width - abs(y - before.y) / TILE_SIZE)))
    
    # Création et renvoi de la nouvelle plateforme
    return Platform(x, y, width, id=before.id + 1)
