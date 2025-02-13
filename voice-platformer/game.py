import pygame
from time import time
from config import *
from objects.player import Player
from objects.platforms import Platform, generate_platforms
from objects.bullets import Bullet, generate_bullet
from objects.enemies import Enemy, generate_enemy
from communicate.serial import SerialReader, SerialSender
from visual.background import Background
from visual.ui import UI
from menus.pause import Pause

# Initialisation de Pygame
pygame.init()

class Game:
    def __init__(self):
        # Initialisation de la fenêtre
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Shout 2 Play")
        
        # Autres initialisations
        self.clock = pygame.time.Clock()
        self.serial_reader = SerialReader()
        self.serial_sender = SerialSender()
        self.running = True
        self.game_started = False
        self.paused = False
        self.score = 0
        self.kills = 0

        # Objets du jeu
        self.mode = False
        self.enemies = []
        self.player = Player(self.mode)
        self.platforms = [Platform(-100, HEIGHT - 100, WIDTH//TILE_SIZE+2)]
        for i in range(9):
            platform = generate_platforms(self.platforms[-1])
            self.platforms.append(platform)
            if len(self.enemies) < 5:
                if platform.width > 1:
                    self.enemies.append(generate_enemy(platform))
        self.bullets = []
        self.background = Background()
        self.ui = UI()
        self.pause = Pause()

        # Autres paramètres
        self.enemy_spawn_timer = 0
        self.speed = SCROLL_SPEED
        self.volume = 0
        self.power_jump = 0
        self.power_charge = 0
        self.loose = 0

        self.button_wait_1 = 0
        self.button_wait_2 = 0

    def handle_events(self, button_pressed_1, button_pressed_2):
        """Gestion des événements clavier et souris"""
        if button_pressed_1:
            self.player.change_mode(not self.player.divide)
        if button_pressed_2:
            self.pause = not self.pause
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Appui sur Enter
                    if not self.game_started:  
                        self.game_started = True  # Démarrer le jeu
                    elif self.paused:
                        self.paused = False  # Reprendre la partie
                
                elif event.key == pygame.K_ESCAPE:  # Appui sur Échap
                    if self.game_started:
                        self.paused = not self.paused  # Pause ou reprise

    def update_draw(self):
        """Mise à jour des objets du jeu"""
        if not self.game_started:
            self.background.update(self.screen, self.speed)
            self.player.draw(self.screen, self.speed)
            self.platforms[0].update(self.speed)
            self.platforms[0].spawn_platform()
            self.platforms[0].draw(self.screen)
            self.ui.draw_start_menu(self.screen)

        if not self.paused and self.game_started:
            self.speed += 0.015
            self.player.update(self.power_charge, self.power_jump, self.platforms, self)
            self.power_jump = 0
            self.background.update(self.screen, self.speed)
            self.player.draw(self.screen, self.speed)
            if self.player.y > HEIGHT*1.1:
                self.game_started = False
                self.score = 0
                self.player.x = WIDTH // 4
                self.enemies = []
                self.bullets = []
                self.speed = SCROLL_SPEED
                self.platforms = [Platform(-100, HEIGHT - 100, WIDTH//TILE_SIZE+2)]
                self.loose += 1
                for i in range(9):
                    self.platforms.append(generate_platforms(self.platforms[-1]))
            # Mise à jour des plateformes
            for platform in self.platforms:
                platform.update(self.speed)
                platform.draw(self.screen)
                if platform.x+platform.width*TILE_SIZE < -WIDTH:
                    self.platforms.remove(platform)
                    new_platform = generate_platforms(self.platforms[-1])
                    self.platforms.append(new_platform)
                    if len(self.enemies) < 5:
                        if new_platform.width > 1:
                            self.enemies.append(generate_enemy(platform))

                    
            # Mise à jour des bullets
            for bullet in self.bullets:
                bullet.update()
                platform.draw(self.screen)
                if not bullet.active:
                    self.bullets.remove(bullet)

            # Mise à jour des ennemis
            for enemy in self.enemies:
                if not enemy:
                    self.enemies.remove(enemy)
                    continue
                enemy.update(self.speed)
                enemy.draw(self.screen, self.speed)
                if enemy.x < -enemy.display_size[0]*2:
                    self.enemies.remove(enemy)

            self.ui.draw_score(self.screen, int((self.speed-SCROLL_SPEED)/2+self.kills*10))  # Afficher le score
        elif self.paused: 
            self.player.update(0, 0, self.platforms, self)
            self.background.update(self.screen, 0)

            self.player.draw(self.screen, self.speed)
            for platform in self.platforms:
                platform.draw(self.screen)
            self.ui.draw_score(self.screen, self.score)  # Afficher le score
        pygame.display.flip()

    def run(self):
        """Boucle principale du jeu"""
        while self.running:

            data = self.serial_reader.get_data()
            gain = data["gain"]
            #activation barre espace
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gain = 10
            frequency = data["frequency"]
            button_pressed_1 = data["button_pressed_1"]
            button_pressed_2 = data["button_pressed_2"]
            self.volume = data["potentiometer_value"]
            if gain >= THRESHOLD:
                if not self.game_started:
                    self.game_started = True
                    if self.loose > 0:
                        gain = 20
                self.power_jump = gain
                self.power_charge = frequency
                
            self.handle_events(button_pressed_1, button_pressed_2)
            self.update_draw()
            self.clock.tick(FPS)

        pygame.quit()