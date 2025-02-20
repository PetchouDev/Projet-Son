import serial
import threading
import base64
import json
import time
#from config import *
from queue import Queue

# --- Classe pour lire les données de Teensy ---
class SerialMonitor(threading.Thread):
    def __init__(self, serial_port, baud_rate):
        """Initialise la connexion série pour lire les données de Teensy."""

        # Initialisation de la connexion série
        threading.Thread.__init__(self)
        self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
        self.queue = Queue()
        self.running = True

        # Variables pour stocker les données
        self.gain = 0
        self.frequency = 0
        self.button_pressed_shoot = False
        self.button_pressed_pause = False
        self.threshold = 70
        self.divider = 1000

    def start(self):
        """Démarre le thread de lecture des données."""
        super().start()

    def run(self):
        self.running = True
        while self.running:
            try:
                # Lecture des données de Teensy
                data = self.ser.readline().decode("utf-8").strip()
                if data:
                    # print(data)
                    data = base64.b64decode(data).decode("utf-8")
                    # print(data)
                    data = json.loads(data)
                    # print(data)

                    # Mise à jour des valeurs
                    self.process_data(data)

            except Exception as e:
                print(f"Erreur lors de la lecture des données : {e}")
                self.running = False

    def process_data(self, data):
        """Parse les données JSON et met à jour les valeurs."""
        for key in data.keys():
            try:
                self.__setattr__(key, data[key])
            except AttributeError:
                print(f"Clé inconnue")
            except Exception as e:
                print(f"Erreur lors de la lecture des données {key} de Teensy : {e}")

    def get_data(self):
        """Retourne un dictionnaire des dernières valeurs lues depuis Teensy."""
        return {
            "gain": self.gain,
            "frequency": self.frequency,
            "button_pressed_shoot": self.button_pressed_shoot, # mode
            "button_pressed_pause": self.button_pressed_pause, # pause
            "divider": self.divider,
            "threshold": self.threshold
        }
    
    def stop(self):
        """Arrête le thread de lecture."""
        self.running = False
        time.sleep(0.1)
        self.ser.close()
    
def open_serial() -> SerialMonitor:
    """Ouvre une connexion série avec Teensy."""
    try:
    
        return SerialMonitor("COM13", 115200)

    except Exception as e:
        print(f"Erreur lors de la recherche de ports série : {e}")

if __name__ == "__main__":
    monitor = open_serial()
    monitor.start()

    while True:
        time.sleep(1)

    input("Appuyez sur Entrée pour commencer la lecture...")
    times = []
    freqs = []
    gains = []
    i = 0 
    while True:
        data = monitor.get_data()
        print(data)
        times.append(time.time())
        freqs.append(data["frequency"])
        gains.append(data["gain"])
        time.sleep(0.01)
        print(i)
        i += 1
        if len(times) > 1000:
            break
    
    save = json.dumps({"times": times, "freqs": freqs, "gains": gains})
    with open("data.json", "w") as f:
        f.write(save)
    # Force kill the thread
    monitor.stop()
    del monitor

    print(max(freqs), min(freqs))
    print(max(gains), min(gains))

    import matplotlib.pyplot as plt
    plt.plot(times, freqs, label="Fréquence")
    plt.plot(times, gains, label="Gain")
    plt.legend()
    plt.show()
