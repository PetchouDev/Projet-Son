import serial
import threading
import base64
import json
import time
#from config import *
from queue import Queue
from serial.tools import list_ports

# --- Classe pour lire les données de Teensy ---
class SerialMonitor(threading.Thread):
    def __init__(self, serial_port, baud_rate):
        """Initialise la connexion série pour lire les données de Teensy."""

        super().__init__()
        self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
        self.stop_event = threading.Event()
        self.queue = Queue()

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
        """Boucle de lecture des données de Teensy."""
        while not self.stop_event.is_set():
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode("utf-8").strip()
                    if data:
                        try:
                            data = base64.b64decode(data).decode("utf-8")
                            data = json.loads(data)
                            self.process_data(data)
                        except Exception:
                            print(f"> {data}")  # Log si non JSON
                else:
                    time.sleep(0.1)  # Pause pour éviter de tourner à vide

            except Exception as e:
                print(f"Erreur de lecture série : {e}")
                break

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
    
    def send(self, message: str) -> None:
        """Envoie un message au Teensy."""
        try:
            print("Sending \"" + message + "\" to Teensy")
            message += "\n"
            self.ser.write(message.encode("utf-8"))
        except Exception as e:
            print(f"Erreur lors de l'envoi du message à Teensy : {e}")

    def stop(self):
        """Arrête proprement le thread."""
        if self.is_alive():
            self.stop_event.set()  # Déclenche l'arrêt
            self.join()  # Attend la fin du thread
        self.ser.close()  # Ferme le port série
        print("Connexion série fermée.")


def get_teensy_com_port():
    """Renvoie la liste des ports série disponibles au format (PORT, DEVICE_NAME)."""
    serial_items =  list_ports.comports()

    for device in serial_items:
        if "SER=9910160" in device.hwid:
            return device.device

    return None

def open_serial(default_port:str="", baudrate:int=115200) -> SerialMonitor:
    """Ouvre une connexion série avec Teensy."""
    try:
        port = get_teensy_com_port()
        if port is None:
            port = default_port
        if port is None:
            raise Exception("Port série non trouvé")
        
        print(f"Ouverture du port série {port} a {baudrate}bps...")
        
        return SerialMonitor(port, baudrate)

    except Exception as e:
        print(f"Erreur lors de la recherche de ports série : {e}")



if __name__ == "__main__":

    print(get_teensy_com_port())
    monitor = open_serial()
    monitor.start()

    while True:
        monitor.send(input("> "))
        time.sleep(0.1)

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
