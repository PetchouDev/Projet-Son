import random

import pygame

from config import *
from core.utils import get_image


class Enemy:
    """
    Classe représentant un ennemi dans le jeu, avec son apparence, sa position
    et ses comportements d'animation et d'interaction avec les projectiles.
    """
    def __init__(self, x, y):
        """
        Initialise l'ennemi avec ses paramètres de position, sprite et animation.
        
        :param x: la position horizontale de l'ennemi
        :param y: la position verticale de l'ennemi
        """
        self.sprite_sheet = pygame.image.load("assets/ducky_enemy.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, 
                                                   (self.sprite_sheet.get_width() * 2, 
                                                    self.sprite_sheet.get_height() * 2))
        self.sprite_size = (64, 64)
        self.display_size = (192, 192)
        self.images = [pygame.transform.flip(get_image(self, col, 2, self.display_size[0]), True, False) 
                       for col in range(4)]
        
        self.animate_delay = 0.2
        self.animate_timer = 0
        self.animate_index = 0

        self.x = x
        self.y = y - self.display_size[1]
        self.width = 192
        self.height = 192
        self.speed = 0.5

    def draw(self, screen, game_speed=1):
        """
        Dessine l'ennemi à l'écran avec une animation en fonction de la vitesse du jeu.
        
        :param screen: l'écran sur lequel dessiner l'ennemi
        :param game_speed: la vitesse du jeu (pour ajuster la vitesse de l'animation)
        """
        if game_speed > 0:
            self.animate_timer += 1 / 50
            if self.animate_timer >= self.animate_delay * 8 / game_speed:
                self.animate_timer = 0
                self.animate_index = (self.animate_index + 1) % len(self.images)
        
        image = self.images[self.animate_index]
        screen.blit(image, (self.x, self.y + 6))

    def update(self, speed, bullets):
        """
        Met à jour la position de l'ennemi et vérifie les collisions avec les projectiles.
        
        :param speed: la vitesse du jeu (affecte le déplacement de l'ennemi)
        :param bullets: liste des projectiles du joueur
        :return: un projectile si l'ennemi est touché, sinon None
        """
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        x, y = rect.center
        for bullet in bullets:
            bullet_rect = bullet.image.get_rect(topleft=(bullet.x, bullet.y)).center
            
            if ((x - bullet_rect[0])**2 + (y - bullet_rect[1])**2)**0.5 < 64:
                # L'ennemi est touché par un projectile
                bullet.break_egg()
                print("Touched")
                return bullet

        self.x -= self.speed * speed
        return None

def generate_enemy(platform):
    """
    Génère un ennemi sur une plateforme donnée à une position aléatoire.
    
    :param platform: la plateforme sur laquelle l'ennemi sera généré
    :return: une instance de l'ennemi généré
    """
    return Enemy(
                    random.randint(int(platform.x + TILE_SIZE / 2), 
                    int(platform.x + (platform.width - 0.5) * TILE_SIZE)), 
                    platform.y
                )
