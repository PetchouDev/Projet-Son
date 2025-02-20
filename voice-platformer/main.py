from game import Game
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    game = Game()         
    game.run()
     