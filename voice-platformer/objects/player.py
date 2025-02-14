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

        self.max_gain = 0
        self.loading = 0
        self.divide = 6
        #self.jump = 0
        self.PID = PID(0.07,0.05,0.05, 0, self.y)
        self.falling = True
        self.is_jumping = False
        self.starting_jump_y = 0
        self.consigne = 0
        self.falling_speed = GRAVITY

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

            if self.is_jumping:
                if self.falling:
                    self.consigne = self.y-jump_power*JUMP_FACTOR/self.falling_speed*self.jump_factor
                    self.falling = False
                    self.falling_speed = GRAVITY
                    self.jump_factor /= 1.1
                    self.PID.set_consigne(max(-self.display_size[1],self.consigne), self.y, False)
                else:
                    self.consigne = self.starting_jump_y-jump_power*JUMP_FACTOR*self.jump_factor*2
                    self.PID.set_consigne(max(-self.display_size[1],self.consigne), self.y, False)
            else:
                self.consigne = self.y-jump_power*JUMP_FACTOR*2
                self.is_jumping = True
                self.falling = False
                self.starting_jump_y = self.y
                self.PID.set_consigne(max(-self.display_size[1],self.consigne), self.y, True)
        if self.is_jumping:
            if not self.falling and (self.y<self.PID.setpoint or abs(self.y-self.PID.setpoint)<2):
                self.falling = True
            
            if self.falling: #Personnage tombe
                next_pos = self.y+self.falling_speed
                final_pos = self.ground(platforms,next_pos-self.y)
                if not final_pos: #Pas de plateforme après chute
                    self.y = next_pos
                    self.falling_speed = min(self.falling_speed*1.2, CAP_GRAVITY)
                else: #Plateforme après chute
                    self.y = final_pos - self.display_size[1]
                    self.max_gain = 0
                    self.jump_factor = 1
                    self.falling = True
                    self.falling_speed = GRAVITY
                    self.is_jumping = False
            # Appliquer la gravité si en l'air
            else:
                next_pos = self.PID.update()
                final_pos = self.ground(platforms,next_pos-self.y)
                
            if not final_pos:  # Pas de plateforme traversée
                self.y = next_pos
                self.max_gain *= 0.98 # Réduit la puissance max
            else:  # Plateforme traversée
                self.y = final_pos - self.display_size[1]
                self.max_gain = 0  # Réinitialiser le gain pour un nouveau saut
                self.jump_factor = 1  # Réinitialiser la puissance du saut
                self.falling = True
                self.falling_speed = GRAVITY
                self.is_jumping = False
        else:
            next_pos = self.y+self.falling_speed
            final_pos = self.ground(platforms,next_pos-self.y)
            if not final_pos:  # Pas de plateforme traversée
                self.y = next_pos
                self.falling_speed = min(self.falling_speed*1.2, CAP_GRAVITY)
    def reset(self):
        self.y = HEIGHT - 100 - self.display_size[1]
        self.max_gain = 0
        self.loading = 0
        self.divide = 6
        self.jump_factor = 1
        self.PID.set_consigne(0, self.y, True)
        self.falling = True
        self.is_jumping = False
        self.starting_jump_y = 0
        self.consigne = 0
        self.falling_speed = GRAVITY           


    """def update2(self, loading_bullet, jump_power, platforms, game_speed):
        if self.velocity_y < 0:  # Bloque la mise à jour de la puissance tant que le joueur monte
            jump_power = self.max_gain

        if jump_power > THRESHOLD:
            self.loading += loading_bullet / self.divide
            self.loading = max(300, self.loading)

            if jump_power > self.max_gain and self.velocity_y >= 0:  # Seulement si le joueur ne monte plus
                if not self.alive:
                    jump_power = SPAWN_JUMP
                    self.alive = True
                    self.velocity_y = 0
                    self.y = HEIGHT
                    self.loading = 0
                    self.max_gain = 0

                self.velocity_y = -(jump_power - self.max_gain) * JUMP_FACTOR * (1+self.max_gain/10) * self.jump_factor
                self.jump_factor /= 1.5  # Réduit la puissance du prochain saut
                self.max_gain = jump_power  # Mémorise la puissance du saut

        # Appliquer la gravité si en l'air
        temp = max(min(self.velocity_y, GRAVITY*20), -GRAVITY*20)
        vector = temp * sqrt(sqrt(game_speed))
        final_pos = False  # On ne traverse pas de plateforme
        if vector >= 0.0:  # Descendre
            final_pos = self.ground(platforms, vector)
        if not final_pos:  # Pas de plateforme traversée
            self.y = self.y + vector
            self.max_gain *= 0.98  # Réduit la puissance max
            self.velocity_y += GRAVITY  # Ajouter une constante de gravité
        else:  # Plateforme traversée
            self.y = final_pos - self.display_size[1]
            self.velocity_y = 0  # Arrêter tout mouvement vertical
            self.max_gain = 0  # Réinitialiser le gain pour un nouveau saut
            self.jump_factor = 1  # Réinitialiser la puissance du saut
"""

    def draw(self, screen, game_speed=1):
        if game_speed>0:
            self.animate_timer += 1 / 40
            if self.animate_timer >= self.animate_delay * 8 / game_speed:
                self.animate_timer = 0
                self.animate_index = (self.animate_index + 1) % len(self.images)
        image = self.images[self.animate_index]
        screen.blit(image, (self.x, self.y + 8))

    def ground(self, platforms, vector):
        for platform in platforms:
            min_x = platform.x+TILE_SIZE/2
            max_x = platform.x+platform.size+4
            if self.x + self.display_size[0] > min_x and self.x < max_x:
                after = self.y + vector
                if (self.y + self.display_size[1] <= platform.y and after + self.display_size[1] >= platform.y):
                    return platform.y
        return None


class PID:
    def __init__(self, kp, ki, kd, consigne, initial_value=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = consigne
        self.last_error = 0
        self.integral = 0
        self.value = initial_value
        self.timer = 0
    def set_consigne(self, consigne, initial_value=0, new_jump=True):
        self.setpoint = consigne
        self.value = initial_value
        self.integral = 0
        self.last_error = 0
        if new_jump:
            self.timer = 0

    def update(self):
        self.timer += GRAVITY*0.75
        self.setpoint+=self.timer
        error = self.setpoint - self.value
        self.integral += error
        derivative = error - self.last_error
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.value += output  # Appliquer la correction
        
        self.last_error = error
        return self.value