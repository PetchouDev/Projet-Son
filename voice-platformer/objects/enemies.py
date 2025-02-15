import pygame
import random
from config import *

from core.utils import get_image

class Enemy:
    def __init__(self, x, y):
        self.sprite_sheet = pygame.image.load("voice-platformer/assets/ducky_enemy.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (self.sprite_sheet.get_width() * 2, self.sprite_sheet.get_height() * 2))
        self.sprite_size = (64, 64)
        self.display_size = (192, 192)
        self.images = [pygame.transform.flip(get_image(self, col, 2, self.display_size[0]), True, False) for col in range(4)]
        self.animate_delay = 0.2
        self.animate_timer = 0
        self.animate_index = 0

        self.x = x
        self.y = y - self.display_size[1]
        self.width = 192
        self.height = 192
        self.speed = 0.5

    def draw(self, screen, game_speed=1):
        if game_speed>0:
            self.animate_timer += 1 / 50
            if self.animate_timer >= self.animate_delay * 8 / game_speed:
                self.animate_timer = 0
                self.animate_index = (self.animate_index + 1) % len(self.images)
        image = self.images[self.animate_index]
        screen.blit(image, (self.x, self.y + 6))

    def update(self, speed, bullets):

        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        x, y = rect.center
        for bullet in bullets:
            bullet_rect = bullet.image.get_rect(topleft=(bullet.x, bullet.y)).center
            
            """print(self.x, self.y)
            print(bullet.x, bullet.y)
            print(bullet_rect)
            print(x, y)
            print(x + 64, x + self.width - 32)
            print(y + 32, y + self.height + 32)
            print(rect.colliderect(bullet.image.get_rect(topleft=(bullet.x, bullet.y))))
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            print(f"Enemy Rect: {rect.topleft} -> {rect.bottomright}, Center: {rect.center}")
            print(f"Distance: {((x - bullet_rect[0])**2 + (y - bullet_rect[1])**2)**.5}")
            print("#####################")

            pygame.draw.rect(screen, (0, 255, 0), rect, 2)  # Ennemi en vert
            pygame.draw.rect(screen, (255, 0, 0), bullet.image.get_rect(topleft=(bullet.x, bullet.y)), 2)  # Bullet en rouge
            """
            if ((x - bullet_rect[0])**2 + (y - bullet_rect[1])**2)**.5 < 64:
                # L'oeuf touche l'ennemi => l'ennemi meurt
                bullet.break_egg()
                print("touched")
                #input("...")
                return bullet

        self.x -= self.speed*speed
        return None

def generate_enemy(platform):
    return Enemy(random.randint(int(platform.x+TILE_SIZE/2), int(platform.x+(platform.width-0.5)*(TILE_SIZE))), platform.y) 