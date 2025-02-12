import pygame
import random
from config import *

class Background:
    def __init__(self):

        self.clouds = [elements(f"cloud{i+1}", (25, 150), 0.75) for i in range(7)]
        self.backgrounds = [back_element(f"background{i+1}", i/6) for i in range(3)]

    def update(self, screen, speed):
        for background in self.backgrounds:
            background.update(speed)
            background.draw(screen)
        for cloud in self.clouds:
            cloud.update(speed)
            cloud.draw(screen)

        
class elements:
    def __init__(self, image, y_scale=(50, 200), speed=1):
        self.picture = pygame.image.load(f"voice-platformer/assets/{image}.png")
        self.picture = pygame.transform.scale(self.picture, (WIDTH // 6, HEIGHT // 6))
        self.position = [random.randint(WIDTH, WIDTH*2), random.randint(y_scale[0], y_scale[1])]
        self.y_scale = y_scale
        self.speed = speed

    def update(self, speed):
        if self.position[0] > -WIDTH:
            self.position[0] -= self.speed*speed
        else:
            self.position = self.respawn()

    def draw(self, screen):
        screen.blit(self.picture, tuple(self.position))

    def respawn(self):
        return [random.randint(WIDTH, WIDTH*2), random.randint(self.y_scale[0], self.y_scale[1])]

class back_element:
    def __init__(self, image, speed=0.5):
        self.picture = pygame.image.load(f"voice-platformer/assets/{image}.png")
        self.picture = pygame.transform.scale(self.picture, (WIDTH, HEIGHT))
        self.position = [0, 0]
        self.speed = speed

    def update(self, speed):
        amount = self.speed* speed
        if self.position[0] > -WIDTH:
            self.position[0] -= amount
        else:
            self.position = [self.position[0]+WIDTH-amount, 0]
    
    def respawn(self):
        return [WIDTH, 0]
    
    def draw(self, screen):
        screen.blit(self.picture, tuple(self.position))
        screen.blit(self.picture, (self.position[0] + WIDTH, self.position[1]))
    