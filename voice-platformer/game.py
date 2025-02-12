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

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
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