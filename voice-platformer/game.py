import pygame
from time import time
from config import *
from objects.player import Player
from objects.platforms import generate_platforms
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

    def handle_events(self, button_pressed_1, button_pressed_2):
        """Gestion des événements clavier et souris"""
        if button_pressed_1 and time() - self.button_wait_1 > 0.5:
            self.player.change_mode(not self.player.divide)
            self.button_wait_2 = time()
        if button_pressed_2 and time() - self.button_wait_2 > 0.5:
            self.pause = not self.pause
            self.button_wait_2 = time()
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
            self.background.update(screen, self.speed)
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
            self.clock.tick(FPS)

        input("Appuyez sur Entrée pour quitter...")
        pygame.quit()







def game_loop():
    pygame.display.set_caption("Voice-Controlled Platformer")
    clock = pygame.time.Clock()
    serial_reader = SerialReader()
    serial_sender = SerialSender()
    player = Player(0)
    platforms = generate_platforms(5)
    enemies = []
    bullets = []
    speed = 10
    background = Background()
    ui = UI()
    pause = Pause()
    score = Score()

    running = True
    game_started = False
    enemy_spawn_timer = 0

    while running:
        #speed += 0.01
        data = serial_reader.get_data()
        gain = data["gain"]
        frequency = data["frequency"]
        button_pressed = data["button_pressed"]
        potentiometer_value = data["potentiometer_value"]
        screen.fill((0, 0, 0))
        background.update(screen, speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_started:
            ui.draw_start_menu(screen)
        else:
            if not pause.paused:
                # Mise à jour des objets
                player.update(gain)
                if player.loading > 100:
                    player.loading = 0
                    bullets.append(generate_bullet(player.x, player.y))
                    serial_sender.send_command("PLAY:shoot")

                for platform in platforms:
                    platform.y += SCROLL_SPEED
                    if platform.y > HEIGHT:
                        platforms.remove(platform)
                        platforms.append(generate_platforms(1)[0])

                for bullet in bullets:
                    bullet.update()
                    if not bullet.active:
                        bullets.remove(bullet)

                for enemy in enemies:
                    enemy.update()
                    if not enemy.active:
                        enemies.remove(enemy)

                enemy_spawn_timer += 1
                if enemy_spawn_timer > 100:
                    enemies.append(generate_enemy())
                    enemy_spawn_timer = 0

                # Collisions bullet-enemy
                for enemy in enemies:
                    if enemy.x < player.x < enemy.x + 40 and enemy.y < player.y < enemy.y + 40:
                        game_started = False
                        serial_sender.send_command("PLAY:loose")
                        
                    for bullet in bullets:
                        if enemy.x < bullet.x < enemy.x + 40 and enemy.y < bullet.y < enemy.y + 40:
                            enemies.remove(enemy)
                            bullets.remove(bullet)
                            score.increase(10)
                            serial_sender.send_command("PLAY:die")

                # Vérification de la mort du joueur
                if player.y > HEIGHT:
                    game_started = False
                    serial_sender.send_command("PLAY:loose")

                score.draw(screen)

            # Affichage
            for platform in platforms:
                platform.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            player.draw(screen)
            pause.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()