import time
import pygame
from config import *
from math import sqrt
from core.utils import get_image

class Player:
    def __init__(self, mode=False):
        self.sprite_sheet = pygame.image.load("voice-platformer/assets/ducky_player.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (self.sprite_sheet.get_width() * 2, self.sprite_sheet.get_height() * 2))
        self.sprite_size = (64, 64)
        self.display_size = (192, 192)
        self.images = [get_image(self, col, 1, self.display_size[0]) for col in range(6)]
        self.animate_delay = 0.1
        self.animate_timer = 0
        self.animate_index = 0

        self.x = WIDTH // 4
        self.y = HEIGHT - 100 - self.display_size[1]

        self.velocity_y = 0
        self.max_gain = 0
        self.loading = 0
        self.alive = True
        self.divide = 6
        #self.jump = 0
        if mode:
            self.divide += 1

        self.jump_factor = 1

    def change_mode(self, mode):
        self.divide = 6
        if mode:
            self.divide += 1

    def update(self, loading_bullet, jump_power, platforms, game_speed):
        if jump_power > THRESHOLD:
            self.loading += loading_bullet / self.divide
            self.loading = max(300, self.loading)
            if jump_power > self.max_gain:  # Seulement si la nouvelle puissance est plus forte
                if not self.alive:
                    jump_power = SPAWN_JUMP
                    self.alive = True
                    self.velocity_y = 0
                    self.y = HEIGHT
                    self.loading = 0
                    self.max_gain = 0
                    #self.jump = 0
                #if self.jump == 0:
                #    self.velocity_y = -(jump_power - self.max_gain) * JUMP_FACTOR * (1+self.max_gain/10)  # Applique la force du saut
                #else:
                #    self.velocity_y = -(jump_power - self.max_gain) * JUMP_FACTOR * (1+self.max_gain/10)
                self.velocity_y = -(jump_power - self.max_gain) * JUMP_FACTOR * (1+self.max_gain/10) * self.jump_factor
                self.jump_factor /= 1.5 # Réduit la puissance du prochain saut
                #self.jump +=1
                self.max_gain = jump_power  # Mémorise la puissance du saut
        
        # Appliquer la gravité si en l'air
        temp = max(min(self.velocity_y, GRAVITY*20), -GRAVITY*20)
        vector = temp * sqrt(sqrt(game_speed))
        final_pos = False #on ne traverse pas de plateforme
        if vector >= 0.0: #descendre
            final_pos = self.ground(platforms, vector)
        if not final_pos: #pas de plateforme traversée
                self.y = max(self.y + vector, -self.display_size[1]/2)
                self.max_gain *=0.98 # Réduit la puissance max
                self.velocity_y += GRAVITY  # Ajouter une constante de gravité
        else: #plateforme traversée
            self.y = final_pos - self.display_size[1]
            self.velocity_y = 0  # Arrêter tout mouvement vertical
            self.max_gain = 0  # Réinitialiser le gain pour un nouveau saut
            self.jump_power = 0
            #self.jump = 0

    def draw(self, screen, game_speed=1):
        if game_speed>0:
            self.animate_timer += 1 / 25
            if self.animate_timer >= self.animate_delay * 8 / game_speed:
                self.animate_timer = 0
                self.animate_index = (self.animate_index + 1) % len(self.images)
        image = self.images[self.animate_index]
        screen.blit(image, (self.x, self.y + 8))

    def ground(self, platforms, vector):
        for platform in platforms:
            print("====\nPlatform: ", platform.id)
            min_x = platform.x-4
            max_x = platform.x+platform.size+4
            print(platform.id, min_x, max_x, self.x, self.x+self.display_size[0])
            if self.x + self.display_size[0] > min_x and self.x < max_x:
                print("Good X")
                after = self.y + vector
                if self.y == platform.y - self.display_size[1] or (self.y + self.display_size[1] <= platform.y and after + self.display_size[1] >= platform.y):
                    print("On platform")
                    self.jump_factor = 1 # Réinitialise la puissance du saut
                    return platform.y
        return None