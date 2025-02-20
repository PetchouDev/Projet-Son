import pygame
from core.utils import get_image
from config import *

class Bullet:
    def __init__(self, x, y, speed=10):
        self.sprite_size = (64, 64)
        self.egg_sheet = pygame.image.load("assets/egg.png")
        self.egg_image = get_image(self, 0, 0, 64, self.egg_sheet)
        self.touch_image_sheet = pygame.image.load("assets/egg_cooked.png")
        self.touch_image = get_image(self, 0, 0, 192, self.touch_image_sheet)

        self.image = self.egg_image

        self.x = x + 64 # Position de l'oeuf par rapport au joueur
        self.y = y + 64 # Position de l'oeuf par rapport au joueur
        self.width = 64
        self.speed = speed
        self.touched = False
        self.active = True

    def update(self, game_speed):
        if self.touched:
            self.x -= game_speed
        else:
            self.x += self.speed
        if self.x > 1.25*WIDTH: # Oeuf qui n'a pas touché d'ennemi sort de l'écran (à droite)
            self.active = False
        elif self.x +  self.width < -100: # Oeuf qui a touché un ennemi sort de l'écran (à gauche)
            self.active = False
                
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def break_egg(self):
        self.touched = True
        self.speed = 0
        self.image = self.touch_image
        print("touched_break_egg")

        

def generate_bullet(x, y):
    return Bullet(x, y)
