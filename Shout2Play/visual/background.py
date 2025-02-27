import random

import pygame

from config import *


class Background:
    """
    Classe représentant l'arrière-plan du jeu, qui inclut des nuages et des éléments de fond.
    Gère la mise à jour et le rendu des éléments visuels du fond.
    """
    def __init__(self):
        """
        Initialise les éléments de fond, y compris les nuages et les images d'arrière-plan.
        """
        # Création des nuages avec une échelle et une vitesse par défaut
        self.clouds = [elements(f"cloud{i+1}", (25, 150), 0.75) for i in range(7)]
        
        # Création des éléments de fond
        self.backgrounds = [back_element(f"background{i+1}", i/6) for i in range(3)]

    def update(self, screen, speed):
        """
        Met à jour les éléments de fond et les nuages en fonction de la vitesse fournie.
        
        :param screen: l'écran sur lequel dessiner l'arrière-plan
        :param speed: la vitesse de défilement des éléments
        """
        # Mise à jour et dessin des éléments de fond
        for background in self.backgrounds:
            background.update(speed)
            background.draw(screen)

        # Mise à jour et dessin des nuages
        for cloud in self.clouds:
            cloud.update(speed)
            cloud.draw(screen)


class elements:
    """
    Classe représentant un élément mobile comme un nuage ou un objet dans le fond du jeu.
    """
    def __init__(self, image, y_scale=(50, 200), speed=1):
        """
        Initialise un élément avec une image, une échelle de position verticale et une vitesse de défilement.
        
        :param image: le nom de l'image de l'élément
        :param y_scale: la plage verticale de l'élément
        :param speed: la vitesse à laquelle l'élément se déplace
        """
        # Chargement et mise à l'échelle de l'image de l'élément
        self.picture = pygame.image.load(f"assets/{image}.png")
        self.picture = pygame.transform.scale(self.picture, (WIDTH // 6, HEIGHT // 6))
        
        # Position de l'élément (horizontale et verticale)
        self.position = [random.randint(WIDTH, WIDTH * 2), random.randint(y_scale[0], y_scale[1])]
        
        # Échelle verticale de l'élément
        self.y_scale = y_scale
        
        # Vitesse de défilement de l'élément
        self.speed = speed

    def update(self, speed):
        """
        Met à jour la position de l'élément en fonction de la vitesse donnée.
        
        :param speed: la vitesse de défilement
        """
        if self.position[0] > -WIDTH:
            self.position[0] -= self.speed * speed
        else:
            # L'élément se réinitialise lorsque sa position dépasse l'écran
            self.position = self.respawn()

    def draw(self, screen):
        """
        Dessine l'élément sur l'écran à sa position actuelle.
        
        :param screen: l'écran sur lequel dessiner l'élément
        """
        screen.blit(self.picture, tuple(self.position))

    def respawn(self):
        """
        Réinitialise la position de l'élément à une nouvelle position aléatoire.
        
        :return: la nouvelle position de l'élément
        """
        return [random.randint(WIDTH, WIDTH * 2), random.randint(self.y_scale[0], self.y_scale[1])]


class back_element:
    """
    Classe représentant un élément de fond (par exemple, une image d'arrière-plan qui défile).
    """
    def __init__(self, image, speed=0.5):
        """
        Initialise un élément de fond avec une image et une vitesse de défilement.
        
        :param image: le nom de l'image de l'élément de fond
        :param speed: la vitesse de défilement de l'élément de fond
        """
        # Chargement et mise à l'échelle de l'image de fond
        self.picture = pygame.image.load(f"assets/{image}.png")
        self.picture = pygame.transform.scale(self.picture, (WIDTH, HEIGHT))
        
        # Position initiale de l'élément de fond
        self.position = [0, 0]
        
        # Vitesse de défilement de l'élément de fond
        self.speed = speed

    def update(self, speed):
        """
        Met à jour la position de l'élément de fond en fonction de la vitesse donnée.
        
        :param speed: la vitesse de défilement
        """
        amount = self.speed * speed
        if self.position[0] > -WIDTH:
            self.position[0] -= amount
        else:
            # L'élément de fond se réinitialise lorsqu'il dépasse l'écran
            self.position = [self.position[0] + WIDTH - amount, 0]

    def respawn(self):
        """
        Réinitialise la position de l'élément de fond à la position initiale.
        
        :return: la position réinitialisée de l'élément de fond
        """
        return [WIDTH, 0]

    def draw(self, screen):
        """
        Dessine l'élément de fond sur l'écran à sa position actuelle.
        
        :param screen: l'écran sur lequel dessiner l'élément de fond
        """
        screen.blit(self.picture, tuple(self.position))
        screen.blit(self.picture, (self.position[0] + WIDTH, self.position[1]))
