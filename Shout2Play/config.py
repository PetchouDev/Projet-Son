import pygame

pygame.init()

# --- Configuration générale ---
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
WIDTH, HEIGHT = 800,600
FPS = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# --- Paramètres physiques ---
GRAVITY = 7
JUMP_FACTOR = 20
CAP_GRAVITY = GRAVITY*5

SPAWN_JUMP= GRAVITY*JUMP_FACTOR*10
SCROLL_SPEED = 8
TILE_SIZE = 128

# --- Serial (Teensy) ---
SERIAL_PORT = "COM13"  # À ajuster
BAUD_RATE = 115200

# --- Paramètres Vocaux ---
THRESHOLD = 2  # Seuil pour la détection de la voix

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