import serial
import threading
import base64
import json
#from config import *
from queue import Queue

SERIAL_PORT = "COM13"
BAUD_RATE = 115200

# --- Classe pour lire les données de Teensy ---
class SerialMonitor(threading.Thread):
    def __init__(self, serial_port, baud_rate):
        """Initialise la connexion série pour lire les données de Teensy."""

        # Initialisation de la connexion série
        super().__init__()
        self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
        self.running = True

        # Variables pour stocker les données
        self.gain = 0
        self.frequency = 0
        self.button_pressed_shoot = False
        self.button_pressed_pause = False
        self.potentiometer_value = 0

    def start(self):
        """Démarre le thread de lecture des données."""
        super().start()
    
    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.ser.readline().decode("utf-8").strip()
                if data:
                    print(f"Reçu: {data}")
                    self.process_data(data)
            except Exception as e:
                print(f"Erreur lors de la lecture des données : {e}")
                self.running = False
    def process_data(self, data):
        """Parse les données JSON et met à jour les valeurs."""
        if(data[0] == 'M'):
            self.button_pressed_shoot = True
            data = data[1:]
        elif(data[0] == 'P'):
            self.button_pressed_pause = True
            data = data[1:]
        try:
            parsed_data = json.loads(data)
            self.gain = float(parsed_data.get("G", 0.0))
            self.frequency = float(parsed_data.get("F", 0.0))
        except json.JSONDecodeError as e:
            print(f"Erreur de parsing JSON : {e}")

    def get_data(self):
        """Retourne un dictionnaire des dernières valeurs lues depuis Teensy."""
        return {
            "gain": self.gain,
            "frequency": self.frequency,
            "button_pressed_shoot": self.button_pressed_shoot,
            "button_pressed_pause": self.button_pressed_pause,
            "potentiometer_value": self.potentiometer_value
        }

    def stop(self):
        """Arrête le thread de lecture."""
        self.running = False
        self.ser.close()
    
def open_serial() -> SerialMonitor:
    """Ouvre une connexion série avec Teensy."""
    try:
    
        return SerialMonitor(SERIAL_PORT, BAUD_RATE)

    except Exception as e:
        print(f"Erreur lors de la recherche de ports série : {e}")

if __name__ == "__main__":
    monitor = open_serial()
    if monitor:
        monitor.start()