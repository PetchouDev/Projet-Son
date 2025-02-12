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
from menus.score import Score

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

        # Objets du jeu
        self.mode = True
        self.player = Player(self.mode)
        self.platforms = generate_platforms(5)
        self.enemies = []
        self.bullets = []
        self.background = Background()
        self.ui = UI()
        self.pause = Pause()
        self.score = Score()

        # Autres paramètres
        self.enemy_spawn_timer = 0
        self.speed = SCROLL_SPEED
        self.volume = 0
        self.power_jump = 0
        self.power_charge = 0

        self.button_wait_1 = 0
        self.button_wait_2 = 0


        # Plateforme de départ
        self.test_platform = Platform(-100, HEIGHT - 100, 16)

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

    def update(self):
        """Mise à jour des objets du jeu"""
        if not self.game_started:
            self.background.update(self.screen, self.speed)
            self.player.draw(self.screen, self.speed)
            self.test_platform.draw(self.screen)
            return  # Ne rien mettre à jour si le jeu n'a pas commencé

        if not self.paused:
            self.player.update(self.power_charge, self.power_jump)
            self.background.update(self.screen, self.speed)

            # Mise à jour des plateformes
            for platform in self.platforms:
                platform.y += SCROLL_SPEED
                if platform.y > HEIGHT:
                    self.platforms.remove(platform)
                    self.platforms.append(generate_platforms(1)[0])

            # Mise à jour des bullets
            for bullet in self.bullets:
                bullet.update()
                if not bullet.active:
                    self.bullets.remove(bullet)

            # Mise à jour des ennemis
            for enemy in self.enemies:
                enemy.update()
                if not enemy.active:
                    self.enemies.remove(enemy)

            # Générer un nouvel ennemi à intervalles réguliers
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer > 100:
                self.enemies.append(generate_enemy())
                self.enemy_spawn_timer = 0

            # Collisions
            self.check_collisions()
        else: 
            self.player.update(0, 0, False)
            self.background.update(self.screen, 0)

    def check_collisions(self):
        """Gérer les collisions entre le joueur, les ennemis et les bullets"""
        for enemy in self.enemies:
            if enemy.x < self.player.x < enemy.x + 40 and enemy.y < self.player.y < enemy.y + 40:
                self.game_started = False  # Game Over

            for bullet in self.bullets:
                if enemy.x < bullet.x < enemy.x + 40 and enemy.y < bullet.y < enemy.y + 40:
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.score.increase(10)

        # Vérifier si le joueur tombe hors de l'écran
        if self.player.y > HEIGHT:
            self.game_started = False

    def draw(self):
        """Afficher les éléments graphiques"""

        if not self.game_started:
            self.ui.draw_start_menu(self.screen)  # Afficher l'écran de démarrage
        else:
            for platform in self.platforms:
                platform.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)

            self.player.draw(self.screen)
            self.score.draw(self.screen)

            if self.paused:
                self.pause.draw(self.screen)  # Afficher le menu pause

        pygame.display.flip()

    def run(self):
        """Boucle principale du jeu"""
        while self.running:

            data = self.serial_reader.get_data()
            gain = data["gain"]
            frequency = data["frequency"]
            button_pressed_1 = data["button_pressed_1"]
            button_pressed_2 = data["button_pressed_2"]
            self.volume = data["potentiometer_value"]
            if gain >= THRESHOLD:
                if not self.game_started:
                    self.game_started = True
                self.power_jump = gain
                self.power_charge = frequency
                
            self.handle_events(button_pressed_1, button_pressed_2)
            self.update()
            self.draw()
            self.speed += 0.05
            self.clock.tick(FPS)

        pygame.quit()