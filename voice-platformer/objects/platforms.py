import pygame
import random
from core.utils import get_image
from config import *

class Platform:
    def __init__(self, x, y, width=5, id=0):
        self.x = x
        self.y = y
        self.id = id
        self.width = width

        self.sprite_sheet = pygame.image.load("voice-platformer/assets/platforms.png")
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (self.sprite_sheet.get_width() * 4, self.sprite_sheet.get_height() * 4))
        self.sprite_size = (64, 64)
        self.display_size = (TILE_SIZE, TILE_SIZE)
        self.has_enemy = False
        self.left = get_image(self, 3, 0, self.display_size[0])
        self.middle = get_image(self, 4, 0, self.display_size[0])
        self.right = get_image(self, 5, 0, self.display_size[0])
        self.size = TILE_SIZE*(self.width)
        self.player_on = False
        self.speed = 0.5

    def spawn_platform(self):
        if self.x < -TILE_SIZE*2:
            self.x += TILE_SIZE

    def draw(self, screen):
        i = 1
        screen.blit(self.left, (self.x, self.y))
        while i <= self.width:
            if i == self.width:
                screen.blit(self.right, (self.x + i * TILE_SIZE, self.y))
            else:
                screen.blit(self.middle, (self.x + i * TILE_SIZE, self.y))
            i += 1
        #self.draw_id(screen, WHITE)

    def draw_id(self, screen, color):
        font_path="voice-platformer/assets/font.otf"
        font = pygame.font.Font(font_path, 40)
        y = self.y-100
        rendered_text = font.render(str(self.id), True, color)
        screen.blit(rendered_text, (self.x - rendered_text.get_width() // 2, y))

    def update(self, speed):
        self.x -= self.speed*speed
    
def generate_platforms(before, game_speed=1):
    max_width = int(2+game_speed/SCROLL_SPEED)
    width=random.randint(1, max_width)
    min_x = before.x+before.size+(1/2+game_speed/SCROLL_SPEED)*TILE_SIZE
    x = random.randint(int(min_x), int(min_x+TILE_SIZE*(max_width+width)))
    y_borne1 = int(max(TILE_SIZE*3, before.y-TILE_SIZE*3))
    y_borne2 = int(min(HEIGHT-TILE_SIZE*0.5, before.y+TILE_SIZE*3))
    if y_borne1 > y_borne2:
        y = random.randint(y_borne2, y_borne1)
    else:
        y = random.randint(y_borne1, y_borne2)
    return Platform(x, y, width, id=before.id+1)