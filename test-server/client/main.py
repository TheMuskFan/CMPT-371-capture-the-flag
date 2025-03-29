from capture_the_flag_game import CaptureTheFlagGame
from network_client import NetworkClient
from game_menu import GameMenu
from lobby import Lobby

if __name__ == "__main__":
    menu = GameMenu()
    menu.run()

    # Game is runnable by itself (with server)
    # game = CaptureTheFlagGame()
    # game.run()