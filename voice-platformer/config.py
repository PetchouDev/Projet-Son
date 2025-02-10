# --- Configurations générales ---
WIDTH, HEIGHT = 800, 600
FPS = 30

# --- Paramètres de physique ---
GRAVITY = 0.5
JUMP_FACTOR = 5
SCROLL_SPEED = 3  # Ajustable avec le potentiomètre

# --- Serial (Teensy) ---
SERIAL_PORT = "COM3"  # À ajuster
BAUD_RATE = 115200
# config.py - Fichier de configuration du jeu

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