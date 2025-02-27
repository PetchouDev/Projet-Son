import json
import time
import base64
import threading
from queue import Queue
from typing import Optional, Dict, Any

import serial
from serial.tools import list_ports


class SerialMonitor(threading.Thread):
    """
    Classe qui gère la lecture des données en série à partir d'un périphérique Teensy.
    Elle fonctionne dans un thread séparé pour effectuer une lecture continue des données.
    """
    def __init__(self, serial_port: str, baud_rate: int):
        """
        Initialise la connexion série pour lire les données de Teensy.
        
        :param serial_port: Le port série auquel est connecté le Teensy.
        :param baud_rate: La vitesse de transmission en bauds.
        """
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

    def run(self):
        """
        Boucle principale de lecture des données de Teensy.
        Lit les données du port série et les décode.
        """
        while not self.stop_event.is_set():
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode("utf-8").strip()
                    if data:
                        try:
                            data = base64.b64decode(data).decode("utf-8")
                            data = json.loads(data)
                            self.process_data(data)
                        except Exception as e:
                            print(f"Erreur de décodage ou traitement des données: {e}")
                            print(f"> {data}")  # Log si non JSON
                else:
                    time.sleep(0.05)  # Réduit la durée du sommeil pour améliorer la réactivité

            except Exception as e:
                print(f"Erreur de lecture série : {e}")
                break

    def process_data(self, data: Dict[str, Any]):
        """
        Parse les données JSON et met à jour les variables internes.
        
        :param data: Dictionnaire contenant les données reçues de Teensy.
        """
        for key in data.keys():
            try:
                self.__setattr__(key, data[key])
            except AttributeError:
                print(f"Clé inconnue: {key}")
            except Exception as e:
                print(f"Erreur lors de la lecture des données {key} de Teensy : {e}")

    def get_data(self) -> Dict[str, Any]:
        """
        Retourne un dictionnaire des dernières valeurs lues depuis Teensy.

        :return: Dictionnaire avec les valeurs actuelles du gain, de la fréquence, etc.
        """
        return {
            "gain": self.gain,
            "frequency": self.frequency,
            "button_pressed_shoot": self.button_pressed_shoot,
            "button_pressed_pause": self.button_pressed_pause,
            "divider": self.divider,
            "threshold": self.threshold
        }
    
    def send(self, message: str) -> None:
        """
        Envoie un message au Teensy via le port série.

        :param message: Le message à envoyer à Teensy.
        """
        try:
            print(f"Sending message to Teensy: {message}")
            self.ser.write(f"{message}\n".encode("utf-8"))
        except Exception as e:
            print(f"Erreur lors de l'envoi du message à Teensy : {e}")

    def stop(self):
        """
        Arrête proprement le thread de lecture et ferme le port série.
        """
        self.stop_event.set()  # Déclenche l'arrêt
        self.join()  # Attendre la fin du thread
        self.ser.close()  # Fermer le port série
        print("Connexion série fermée.")


def get_teensy_com_port() -> Optional[str]:
    """
    Recherche et retourne le port série du Teensy connecté.
    
    :return: Le port série sous forme de chaîne de caractères ou None si aucun périphérique n'est trouvé.
    """
    serial_items = list_ports.comports()
    for device in serial_items:
        if "SER=9910160" in device.hwid:
            return device.device
    return None


def open_serial(default_port: str = "", baudrate: int = 115200) -> SerialMonitor:
    """
    Ouvre une connexion série avec Teensy.

    :param default_port: Port série par défaut à utiliser si aucun périphérique Teensy n'est trouvé automatiquement.
    :param baudrate: Vitesse de transmission en bauds.
    :return: Instance de SerialMonitor pour la gestion de la communication série.
    """
    try:
        port = get_teensy_com_port() or default_port
        if not port:
            raise Exception("Port série non trouvé")
        
        print(f"Ouverture du port série {port} à {baudrate}bps...")
        return SerialMonitor(port, baudrate)
    except Exception as e:
        print(f"Erreur lors de la recherche de ports série : {e}")
        raise


if __name__ == "__main__":
    """
    Exécution principale du programme. Lit les données depuis Teensy, les enregistre dans un fichier JSON 
    et affiche un graphique avec les données lues.
    """
    monitor = open_serial()
    monitor.start()

    times = []
    freqs = []
    gains = []

    try:
        while len(times) <= 1000:
            data = monitor.get_data()
            print(data)

            times.append(time.time())
            freqs.append(data["frequency"])
            gains.append(data["gain"])

            time.sleep(0.01)  # Temps d'attente pour éviter d'être trop rapide

    except KeyboardInterrupt:
        print("Lecture interrompue.")

    # Sauvegarde des données en JSON
    with open("data.json", "w") as f:
        json.dump({"times": times, "freqs": freqs, "gains": gains}, f)

    # Importation des bibliothèques pour le graphique
    import matplotlib.pyplot as plt

    # Génération du graphique
    plt.plot(times, freqs, label="Fréquence")
    plt.plot(times, gains, label="Gain")
    plt.legend()
    plt.show()

    # Stoppe le thread de manière propre
    monitor.stop()
