import serial
import threading
from config import *
from queue import Queue

class SerialSender:
    def __init__(self):
        """Initialise la connexion série pour envoyer des commandes à Teensy."""
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        except serial.SerialException as e:
            print(f"Erreur de connexion série lors de l'initialisation : {e}")
    
    def send_command(self, command):
        """Envoie une commande au Teensy via la connexion série."""
        try:
            self.ser.write(f"{command}\n".encode())  # Ajout de \n pour signaler la fin de la commande
        except Exception as e:
            print(f"Erreur d'envoi Serial: {e}")

    def play_music(self, track_name):
        """Demande au Teensy de jouer un fichier MP3 spécifique."""
        self.send_command(f"PLAY:{track_name}")

    def stop_music(self):
        """Demande au Teensy d'arrêter la musique."""
        self.send_command("STOP")

    def set_volume(self, level):
        """Ajuste le volume en fonction du niveau reçu."""
        self.send_command(f"VOLUME:{level}")

# --- Classe pour lire les données de Teensy ---
class SerialReader:
    def __init__(self):
        """Initialise la connexion série et lance un thread pour lire les données."""
        self.serial_queue = Queue()  # Utilisé pour gérer les données lues
        self.running = True
        self.gain = 0
        self.frequency = 0
        self.button_pressed_1 = False
        self.button_pressed_2 = False
        self.potentiometer_value = 0

        # Démarrer le thread de lecture en arrière-plan
        threading.Thread(target=self.read_serial, daemon=True).start()

    def read_serial(self):
        """Lecture continue des données envoyées par Teensy."""
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            while self.running:
                line = ser.readline().decode().strip()  # Lire la ligne et la nettoyer des caractères inutiles
                if line:
                    # Décomposer les données par la virgule
                    data = line.split(",")
                    if len(data) == 2:
                        identifier, value = data[0], data[1]
                        # Traiter la donnée selon l'identifiant
                        self.process_data(identifier, value)
        except serial.SerialException as e:
            print(f"Erreur de connexion série : {e}")
        finally:
            if ser.is_open:
                ser.close()  # Fermeture propre du port série à la fin

    def process_data(self, identifier, value):
        """Traite les données en fonction de l'identifiant (simule un switch-case)."""
        switch = {
            "gain": self.set_gain,
            "frequency": self.set_frequency,
            "button_1": self.set_button_1,
            "button_2": self.set_button_2,
            "potentiometer": self.set_potentiometer
        }
        # Appel de la fonction associée à l'identifiant
        if identifier in switch:
            switch[identifier](value)
        else:
            print(f"Identifiant non reconnu : {identifier}")

    def set_gain(self, value):
        """Met à jour le gain selon la valeur reçue."""
        try:
            self.gain = float(value)
            print(f"Gain mis à jour : {self.gain}")
        except ValueError:
            print(f"Erreur de conversion pour Gain : {value}")

    def set_frequency(self, value):
        """Met à jour la fréquence selon la valeur reçue."""
        try:
            self.frequency = float(value)
            print(f"Fréquence mise à jour : {self.frequency}")
        except ValueError:
            print(f"Erreur de conversion pour Frequency : {value}")

    def set_button_1(self, value):
        """Met à jour l'état du bouton (True ou False) selon la valeur reçue."""
        try:
            self.button_pressed_1 = bool(int(value))
            print(f"État du bouton : {self.button_pressed_1}")
        except ValueError:
            print(f"Erreur de conversion pour Button : {value}")

    def set_button_2(self, value):
        try:
            self.button_pressed_2 = bool(int(value))
            print(f"État du bouton : {self.button_pressed_2}")
        except ValueError:
            print(f"Erreur de conversion pour Button : {value}")

    def set_potentiometer(self, value):
        """Met à jour la valeur du potentiomètre selon la valeur reçue."""
        try:
            self.potentiometer_value = int(value)
            print(f"Potentiomètre mis à jour : {self.potentiometer_value}")
        except ValueError:
            print(f"Erreur de conversion pour Potentiometer : {value}")

    def get_data(self):
        """Retourne un dictionnaire des dernières valeurs lues depuis Teensy."""
        return {
            "gain": self.gain,
            "frequency": self.frequency,
            "button_pressed_1": self.button_pressed_1,
            "button_pressed_2": self.button_pressed_2,
            "potentiometer_value": self.potentiometer_value
        }