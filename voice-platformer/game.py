import pygame
import sys
from time import time
from config import *
from objects.player import Player
from objects.platforms import Platform, generate_platforms
from objects.bullets import Bullet, generate_bullet
from objects.enemies import Enemy, generate_enemy
from communicate.serialMonitor import open_serial, SerialMonitor
from visual.background import Background
from visual.ui import UI
from menus.pause import Pause
from random import random
import tkinter as tk
from tkinter import simpledialog
# Initialisation de Pygame
pygame.init()

class Game:
    def __init__(self):
        # Initialisation de la fenêtre
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Shout 2 Play")
        # Autres initialisations
        self.clock = pygame.time.Clock()
        self.serial_reader: SerialMonitor = open_serial(SERIAL_PORT, BAUD_RATE)
        self.running = True
        self.game_started = False
        self.paused = False
        self.kills = 0

        # Meilleur score
        save = open("highscores.txt", "r", encoding="utf-8")
        scores = save.read()
        user, score = scores.strip().split(":")
        self.best_score = int(score)
        self.best_user = user
        save.close()
        del save
        del scores
        del user
        del score

        # Objets du jeu
        self.mode = False
        self.enemies = []
        self.player = Player(self.mode)
        
        pygame.display.set_icon(self.player.images[0])
        self.speed = SCROLL_SPEED
        self.calibrate = 70
        self.platforms = [Platform(-100, HEIGHT - 100, WIDTH//TILE_SIZE+2)]
        self.construct_platform(6)
        self.bullets = []
        self.touched_bullets = []
        self.background = Background()
        self.ui = UI()
        self.pause = Pause()
        self.last_state_shoot = 0
        self.last_state_pause = 0
        # Autres paramètres
        self.enemy_spawn_timer = 0
        self.volume = 0
        self.power_jump = 0
        self.power_charge = 0
        self.loose = 0
        self.button_wait_1 = 0
        self.button_wait_2 = 0
        self.shoot_wait = 0
        self.pause_wait = 0 

    def construct_platform(self, n):
        for i in range(n):
            platform = generate_platforms(self.platforms[-1], self.speed)
            self.platforms.append(platform)
            if random() < 0.6:
                if len(self.enemies) < 6:
                    if platform.width > 1:
                        self.enemies.append(generate_enemy(platform))

    def handle_events(self):
        """Gestion des événements clavier et souris"""
        if pygame.event.get(pygame.QUIT):
            self.running = False
            return
        keys = pygame.key.get_pressed()
        data = self.serial_reader.get_data()
        # print(data)
        self.power_jump = (data["gain"]-self.calibrate)/1.5
        self.power_charge = data["frequency"]
        shoot = data["button_pressed_shoot"] or keys[pygame.K_z]
        pause = data["button_pressed_pause"] or keys[pygame.K_ESCAPE]
        if ((shoot and self.last_state_shoot != shoot)) and time() - self.shoot_wait and self.player.loading > 100 and not self.paused:  # 1 seconde entre chaque appui
            self.shoot()
            self.shoot_wait = time()
        self.last_state_shoot = shoot
        if ((pause and self.last_state_pause != pause)) and time() - self.pause_wait > 1:  # 1 seconde entre chaque appui
            self.paused = not self.paused
            if self.paused:
                self.serial_reader.send("pause")
            else:
                self.serial_reader.send("resume")
            self.pause_wait = time()
        self.last_state_pause = pause
        if data["divider"]:
            self.player.change_mode(data["divider"])
        if data["threshold"]:
            self.calibrate = data["threshold"]
        if keys[pygame.K_RETURN]:  # Appui sur Enter
            if self.paused:  
                self.paused = not self.paused  # Démarrer le jeu
            elif self.game_started:
                self.game_started = False
        if keys[pygame.K_SPACE]:
            self.power_jump = 10
        
        if self.shoot_wait > 0:
            self.shoot_wait -= 1/FPS
        if self.pause_wait > 0:
            self.pause_wait -= 1/FPS

    def update_draw(self):
        """Mise à jour des objets du jeu"""
        if not self.game_started and not self.paused:
            self.background.update(self.screen, self.speed)
            self.player.draw(self.screen, self.speed)
            self.platforms[0].update(self.speed)
            self.platforms[0].spawn_platform()
            self.platforms[0].draw(self.screen)
            self.ui.draw_start_menu(self.screen, self.best_score, self.best_user)

        if not self.paused and self.game_started:
            if self.speed < SCROLL_SPEED*3:
                self.speed *= 1.05
                if self.speed > SCROLL_SPEED*3:
                    self.speed = SCROLL_SPEED*3
            self.speed += 0.015
            self.player.update(self.power_charge, self.power_jump, self.platforms, self.speed)
            
            self.power_jump = 0
            self.background.update(self.screen, self.speed)
            
            if self.player.y > HEIGHT*1.4:
                self.game_started = False
                self.serial_reader.send("init")
                #self.best_score = max(self.best_score, max(0, ))
                score = int(self.speed-SCROLL_SPEED*3+self.kills*10)
                if score > self.best_score:
                    self.best_score = score
                    root = tk.Tk()
                    root.withdraw()  # Hide the main window
                    username = simpledialog.askstring("Shout 2 Play", "New best score!\nWhat is your name? ", parent=root)
                    self.best_user = username
                    root.destroy()

                    with open("highscores.txt", "w", encoding="utf-8") as file:
                        file.write(f"{username}: {score}\n")
                self.kills = 0
                self.player.reset()
                self.enemies = []
                self.bullets = []
                self.touched_bullets = []
                self.speed = SCROLL_SPEED
                self.platforms = [Platform(-TILE_SIZE*3, HEIGHT - 100, WIDTH//TILE_SIZE+2)]
                self.loose = 1
                self.construct_platform(6)
            self.player.draw(self.screen, self.speed)

            # Mise à jour des plateformes
            for platform in self.platforms:
                platform.update(self.speed)
                platform.draw(self.screen)
                if platform.x+platform.size < -WIDTH:
                    self.platforms.remove(platform)
                    self.construct_platform(1)
            # Mise à jour des bullets
            for bullet in self.bullets:
                bullet.update(self.speed * 0.5)
                bullet.draw(self.screen)
                if not bullet.active:
                    self.bullets.remove(bullet)

            for bullet in self.touched_bullets:
                bullet.update(self.speed * 0.5)
                bullet.draw(self.screen)
                if not bullet.active:
                    self.touched_bullets.remove(bullet)

            # Mise à jour des ennemis
            for enemy in self.enemies:
                if not enemy:
                    self.enemies.remove(enemy)
                    continue
                died_from = enemy.update(self.speed, self.bullets) # Vérifier si l'ennemi est touché
                if died_from:
                    self.enemies.remove(enemy) 
                    self.bullets.remove(died_from)
                    self.touched_bullets.append(died_from) # Afficher l'oeuf au plat au 1er plan
                    self.kills += 1
                    self.serial_reader.send("die.wav")
                    continue
                enemy.draw(self.screen, self.speed)
                #pygame.draw.line(self.screen, (255, 0, 0),( WIDTH//2, HEIGHT), (enemy.x, enemy.y), 2)
                # draw rect
                # pygame.draw.rect(self.screen, (255, 0, 0), enemy.images[enemy.animate_index].get_rect(topleft=(enemy.x, enemy.y)), 2)
                if enemy.x < -enemy.display_size[0]*2:
                    self.enemies.remove(enemy)


                #draw rect 
                # pygame.draw.rect(self.screen, (255, 0, 0), bullet.image.get_rect(topleft=(bullet.x, bullet.y)), 2)

            # print(self.speed)
            self.ui.draw_score(self.screen, max(0, int(self.speed-SCROLL_SPEED*3+self.kills*10)))  # Afficher le score
            self.ui.loading_bar(self.screen, self.player.loading)
        elif self.paused: 
            self.background.update(self.screen, 0)
            self.player.draw(self.screen, 0)
            for platform in self.platforms:
                platform.draw(self.screen)
            gray_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            gray_surface.fill((100, 100, 100, 100))  # Couleur grise semi-transparente
            self.screen.blit(gray_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            self.ui.draw_score(self.screen, max(0, int(self.speed-SCROLL_SPEED*3+self.kills*10)))  # Afficher le score
            self.ui.loading_bar(self.screen, self.player.loading)
            self.ui.draw_stat(self.screen, int(self.calibrate), int(self.player.divide), int(self.power_jump + self.calibrate))
            self.ui.draw_pause_menu(self.screen)  # Dessiner le menu pause
            """ quit_button_rect = self.ui.draw_quit_button(self.screen)  # Dessiner le bouton quitter et obtenir son rectangle
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if quit_button_rect.collidepoint(mouse_pos) and mouse_click[0]:
                self.running = False """
            # print(self.power_charge, self.power_jump, THRESHOLD, self.power_jump>THRESHOLD)
            self.ui.freq_to_note(self.screen, self.power_charge, self.power_jump>THRESHOLD)
        pygame.display.flip()

    def shoot(self):
        self.bullets.append(Bullet(self.player.x, self.player.y, self.speed))
        self.player.loading = max(self.player.loading-100, 0)
        self.serial_reader.send("shoot.wav")
        
    def run(self):
        """Boucle principale du jeu"""
        self.serial_reader.start()

        self.serial_reader.send("init")

        while self.running:

            self.handle_events()

            if self.power_jump >= THRESHOLD:
                if not self.game_started:
                    self.game_started = True
                    self.serial_reader.send("resume")
                    if self.loose == 1:
                        self.power_jump = 10
                        self.speed = SCROLL_SPEED
            self.update_draw()
            self.clock.tick(FPS)


        self.stop()

    
    def stop(self):
        """Arrête le jeu"""
        print("Fermeture du jeu")
        self.serial_reader.send("stop")
        self.serial_reader.stop()
        del self.serial_reader
        sys.exit()

        pygame.quit()