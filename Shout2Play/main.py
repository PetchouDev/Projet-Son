from game import Game
import os

if __name__ == "__main__":

    # Changer le répertoire de travail pour le répertoire du fichier main.py (pour que les chemins relatifs fonctionnent)
    os.chdir(os.path.dirname(__file__))

    # Créer une instance de la classe Game et lancer le jeu
    game = Game()         
    game.run()
