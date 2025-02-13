import pygame
pygame.init()
# --- Configurations générales ---
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
#WIDTH, HEIGHT = 800,600
FPS = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# --- Paramètres de physique ---
GRAVITY = 1.2
JUMP_FACTOR = 2

SPAWN_JUMP= GRAVITY*JUMP_FACTOR*5
SCROLL_SPEED = 8
TILE_SIZE = 128

# --- Serial (Teensy) ---
SERIAL_PORT = "COM3"  # À ajuster
BAUD_RATE = 115200
# config.py - Fichier de configuration du jeu

# --- Paramètres Vocaux ---
THRESHOLD = 1  # Seuil pour la détection de la voix

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Paramètres des plateformes
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 50
PLATFORM_GAP = 150

# Paramètres des tirs
BULLET_SPEED = 10