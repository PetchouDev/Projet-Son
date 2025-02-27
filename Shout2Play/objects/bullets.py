import pygame

from core.utils import get_image
from config import *

class Bullet:
    """
    Classe représentant une balle (ou un oeuf) tirée par le joueur.
    Elle gère l'image, la position, le mouvement, ainsi que les interactions avec les ennemis.
    """
    def __init__(self, x, y, speed=10):
        """
        Initialise un oeuf à la position spécifiée avec une certaine vitesse.

        :param x: la position horizontale de l'oeuf
        :param y: la position verticale de l'oeuf
        :param speed: la vitesse de l'oeuf
        """
        # Taille des sprites
        self.sprite_size = (64, 64)

        # Chargement des images pour l'oeuf et l'oeuf cuit
        self.egg_sheet = pygame.image.load("assets/egg.png")
        self.egg_image = get_image(self, 0, 0, 64, self.egg_sheet)
        self.touch_image_sheet = pygame.image.load("assets/egg_cooked.png")
        self.touch_image = get_image(self, 0, 0, 192, self.touch_image_sheet)

        # Image actuelle de l'oeuf
        self.image = self.egg_image

        # Position et état de l'oeuf
        self.x = x + 64  # Position de l'oeuf par rapport au joueur
        self.y = y + 64  # Position de l'oeuf par rapport au joueur
        self.width = 64  # Largeur de l'oeuf
        self.speed = speed  # Vitesse de l'oeuf
        self.touched = False  # Si l'oeuf a été touché par un ennemi
        self.active = True  # Si l'oeuf est encore actif

    def update(self, game_speed):
        """
        Met à jour la position de l'oeuf en fonction de sa vitesse et du jeu.

        :param game_speed: la vitesse du jeu qui influence le mouvement
        """
        if self.touched:
            self.x -= game_speed  # Déplace l'oeuf à gauche une fois qu'il est touché
        else:
            self.x += self.speed  # Déplace l'oeuf à droite tant qu'il n'est pas touché
        
        # Si l'oeuf sort de l'écran à droite ou à gauche, il devient inactif
        if self.x > 1.25 * WIDTH:  # Oeuf sortant à droite
            self.active = False
        elif self.x + self.width < -100:  # Oeuf sortant à gauche
            self.active = False

    def draw(self, screen):
        """
        Dessine l'oeuf sur l'écran.

        :param screen: l'écran sur lequel dessiner l'oeuf
        """
        screen.blit(self.image, (self.x, self.y))

    def break_egg(self):
        """
        Gère la logique lorsque l'oeuf touche un ennemi (devient "cuit").
        """
        self.touched = True  # Marque l'oeuf comme touché
        self.speed = 0  # Arrête l'oeuf
        self.image = self.touch_image  # Change l'image pour l'oeuf cuit
        print("touched_break_egg")

def generate_bullet(x, y):
    """
    Crée un nouvel oeuf à la position spécifiée.
    
    :param x: la position horizontale initiale de l'oeuf
    :param y: la position verticale initiale de l'oeuf
    :return: une instance de Bullet
    """
    return Bullet(x, y)
