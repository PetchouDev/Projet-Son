import sys
from time import time

import pygame
import tkinter as tk
from tkinter import simpledialog
from random import random

from config import *
from objects.player import Player
from objects.platforms import Platform, generate_platforms
from objects.bullets import Bullet, generate_bullet
from objects.enemies import Enemy, generate_enemy
from communicate.serialMonitor import open_serial, SerialMonitor
from visual.background import Background
from visual.ui import UI
from menus.pause import Pause

# Initialisation de Pygame
pygame.init()

class Game:
    """Classe représentant le jeu Shout 2 Play."""

    def __init__(self):
        """Initialisation des paramètres du jeu."""
        # Initialisation de la fenêtre du jeu
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Shout 2 Play")
        
        # Initialisation des objets nécessaires au jeu
        self.clock = pygame.time.Clock()
        self.serial_reader: SerialMonitor = open_serial(SERIAL_PORT, BAUD_RATE)
        self.running = True
        self.game_started = False
        self.paused = False
        self.kills = 0

        # Chargement du meilleur score depuis un fichier
        self.load_best_score()

        # Initialisation des objets du jeu
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

        # Initialisation des timers
        self.enemy_spawn_timer = 0
        self.volume = 0
        self.power_jump = 0
        self.power_charge = 0
        self.loose = 0
        self.button_wait_1 = 0
        self.button_wait_2 = 0
        self.shoot_wait = 0
        self.pause_wait = 0 

    def load_best_score(self):
        """Charge le meilleur score depuis le fichier 'highscores.txt'."""
        try:
            with open("highscores.txt", "r", encoding="utf-8") as save:
                scores = save.read()
                user, score = scores.strip().split(":")
                self.best_score = int(score)
                self.best_user = user
        except FileNotFoundError:
            self.best_score = 0
            self.best_user = "Inconnu"

    def construct_platform(self, n):
        """Construit des plateformes aléatoires pour le jeu."""
        for i in range(n):
            platform = generate_platforms(self.platforms[-1], self.speed)
            self.platforms.append(platform)
            if random() < 0.6:
                if len(self.enemies) < 6:
                    if platform.width > 1:
                        self.enemies.append(generate_enemy(platform))

    def handle_events(self):
        """Gère les événements clavier et de communication série."""
        if pygame.event.get(pygame.QUIT):
            self.running = False
            self.stop()
            return

        keys = pygame.key.get_pressed()
        data = self.serial_reader.get_data()

        # Mise à jour des valeurs en fonction des données du capteur
        self.power_jump = (data["gain"] - self.calibrate) / 1.5
        self.power_charge = data["frequency"]

        # Gestion de la touche de tir
        shoot = data["button_pressed_shoot"] or keys[pygame.K_z]
        pause = data["button_pressed_pause"] or keys[pygame.K_ESCAPE]

        # Logique de tir
        if ((shoot and self.last_state_shoot != shoot)) and time() - self.shoot_wait and self.player.loading > 100 and not self.paused:
            self.shoot()
            self.shoot_wait = time()
        
        self.last_state_shoot = shoot

        # Logique de mise en pause
        if ((pause and self.last_state_pause != pause)) and time() - self.pause_wait > 1:
            self.paused = not self.paused
            if self.paused:
                self.serial_reader.send("pause")
            else:
                self.serial_reader.send("resume")
            self.pause_wait = time()
        
        self.last_state_pause = pause

        # Gestion du mode de jeu via les capteurs
        if data["divider"]:
            self.player.change_mode(data["divider"])
        if data["threshold"]:
            self.calibrate = data["threshold"]

        # Gestion des entrées supplémentaires
        if keys[pygame.K_RETURN]:
            if self.paused:  
                self.paused = not self.paused
            elif self.game_started:
                self.game_started = False
        
        if keys[pygame.K_SPACE]:
            self.power_jump = 10

        # Décrément des timers
        if self.shoot_wait > 0:
            self.shoot_wait -= 1 / FPS
        if self.pause_wait > 0:
            self.pause_wait -= 1 / FPS

    def update_draw(self):
        """Met à jour l'affichage et les objets du jeu."""
        if not self.game_started and not self.paused:
            self.background.update(self.screen, self.speed)
            self.player.draw(self.screen, self.speed)
            self.platforms[0].update(self.speed)
            self.platforms[0].spawn_platform()
            self.platforms[0].draw(self.screen)
            self.ui.draw_start_menu(self.screen, self.best_score, self.best_user)

        if not self.paused and self.game_started:
            # Augmente la vitesse de défilement du jeu
            if self.speed < SCROLL_SPEED * 3:
                self.speed *= 1.05
                if self.speed > SCROLL_SPEED * 3:
                    self.speed = SCROLL_SPEED * 3
            self.speed += 0.015
            self.player.update(self.power_charge, self.power_jump, self.platforms, self.speed)
            self.power_jump = 0

            # Mise à jour de l'arrière-plan et des plateformes
            self.background.update(self.screen, self.speed)
            self.player.draw(self.screen, self.speed)

            # Vérification de la condition de fin du jeu
            if self.player.y > HEIGHT * 1.4:
                self.end_game()

            # Mise à jour des plateformes
            for platform in self.platforms:
                platform.update(self.speed)
                platform.draw(self.screen)
                if platform.x + platform.size < -WIDTH:
                    self.platforms.remove(platform)
                    self.construct_platform(1)

            # Mise à jour des balles
            self.update_bullets()

            # Mise à jour des ennemis
            self.update_enemies()

            # Affichage du score et de la barre de chargement
            self.ui.draw_score(self.screen, max(0, int(self.speed - SCROLL_SPEED * 3 + self.kills * 10)))
            self.ui.loading_bar(self.screen, self.player.loading)
        elif self.paused:
            self.draw_pause_screen()

        pygame.display.flip()

    def update_bullets(self):
        """Met à jour l'état des balles dans le jeu."""
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

    def update_enemies(self):
        """Met à jour l'état des ennemis dans le jeu."""
        for enemy in self.enemies:
            if not enemy:
                self.enemies.remove(enemy)
                continue
            died_from = enemy.update(self.speed, self.bullets)
            if died_from:
                self.enemies.remove(enemy) 
                self.bullets.remove(died_from)
                self.touched_bullets.append(died_from)  # Affiche l'œuf au plat au premier plan
                self.kills += 1
                self.serial_reader.send("die.wav")
                continue
            enemy.draw(self.screen, self.speed)
            if enemy.x < -enemy.display_size[0] * 2:
                self.enemies.remove(enemy)

    def draw_pause_screen(self):
        """Dessine l'écran de pause."""
        self.background.update(self.screen, 0)
        self.player.draw(self.screen, 0)
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Application d'un filtre de gris semi-transparent pour la pause
        gray_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        gray_surface.fill((100, 100, 100, 100))
        self.screen.blit(gray_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Affichage du score et de la barre de chargement pendant la pause
        self.ui.draw_score(self.screen, max(0, int(self.speed - SCROLL_SPEED * 3 + self.kills * 10)))
        self.ui.loading_bar(self.screen, self.player.loading)
        self.ui.draw_stat(self.screen, int(self.calibrate), int(self.player.divide), int(self.power_jump + self.calibrate))
        self.ui.draw_pause_menu(self.screen)

    def shoot(self):
        """Tire une balle depuis la position du joueur."""
        self.bullets.append(Bullet(self.player.x, self.player.y, self.speed))
        self.player.loading = max(self.player.loading - 100, 0)
        self.serial_reader.send("shoot.wav")

    def end_game(self):
        """Gère la fin du jeu et l'enregistrement du score."""
        self.game_started = False
        self.serial_reader.send("init")
        score = int(self.speed - SCROLL_SPEED * 3 + self.kills * 10)
        if score > self.best_score:
            self.best_score = score
            self.update_best_score(score)

        self.kills = 0
        self.player.reset()
        self.enemies = []
        self.bullets = []
        self.touched_bullets = []
        self.speed = SCROLL_SPEED
        self.platforms = [Platform(-TILE_SIZE * 3, HEIGHT - 100, WIDTH // TILE_SIZE + 2)]
        self.loose = 1
        self.construct_platform(6)

    def update_best_score(self, score):
        """Met à jour le meilleur score et demande le nom du joueur."""
        root = tk.Tk()
        root.withdraw()  # Cache la fenêtre principale
        username = simpledialog.askstring("Shout 2 Play", "Nouveau meilleur score!\nQuel est ton nom ?", parent=root)
        self.best_user = username
        root.destroy()

        # Enregistrement du score dans le fichier
        with open("highscores.txt", "w", encoding="utf-8") as file:
            file.write(f"{username}: {score}\n")

    def run(self):
        """Boucle principale du jeu."""
        self.serial_reader.start()
        self.serial_reader.send("init")

        while self.running:
            self.handle_events()

            # Démarrage du jeu si les conditions sont réunies
            if self.power_jump >= THRESHOLD:
                if not self.game_started and not self.paused:
                    self.game_started = True
                    self.serial_reader.send("resume")
                    if self.loose == 1:
                        self.power_jump = 10
                        self.speed = SCROLL_SPEED

            self.update_draw()
            self.clock.tick(FPS)

        self.stop()

    def stop(self):
        """Arrête le jeu et ferme les ressources."""
        print("Fermeture du jeu")
        self.serial_reader.send("stop")
        self.serial_reader.stop()
        del self.serial_reader
        sys.exit()
        pygame.quit()
