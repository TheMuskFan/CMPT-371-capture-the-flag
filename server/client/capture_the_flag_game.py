import pygame
import sys
from network_client import NetworkClient
from game_renderer import GameRenderer

class CaptureTheFlagGame:
    # Sets up the game:
    # - Initializes the network client (or creates one if none provided)
    # - Creates a GameRenderer for visuals
    # - Sets the game loop to running
    # - Stores the player's ID
    def __init__(self,network_client = None,player_id = None):
        self.network_client = network_client or NetworkClient()
        self.renderer = GameRenderer()
        self.running = True
        self.player_id = player_id

    # Ensures the player ID is valid (between 0 and 3).
    # If it’s not already set, prompts the user to input their ID (1-4), 
    # then converts it to 0-indexed.
    def choose_player(self):
        while self.player_id not in [0, 1, 2, 3]:
            try:
                one_indexed = int(input("Enter your player ID (1-4): "))
                self.player_id = one_indexed - 1
            except ValueError:
                continue

    # Handles Pygame events:
    # Quits the game if the window is closed
    # Detects movement input (W, A, S, D) and sends it to the server using the network client
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_s:
                    dy = 1
                elif event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_d:
                    dx = 1
                if dx != 0 or dy != 0:
                    self.network_client.send_input(self.player_id, dx, dy)

    # Main game loop:
    # Ensures player ID is set
    # Starts the network listener (if not already running)
    # Loops while the game is active:
    # - Processes user input
    # - Gets game state from the server
    # - Renders players and flag with GameRenderer
    def run(self):
        self.choose_player() 
        if not self.network_client.listening:
            self.network_client.start_listener()

        while self.running:
            self.process_events()
            state = self.network_client.get_state()
            players = state.get("players", [])
            flag_pos = state.get("flag", (self.renderer.grid_size // 2, self.renderer.grid_size // 2))
            self.renderer.render(players, flag_pos)

        self.cleanup()

    # Gracefully shuts down the game:
    # - Quits Pygame
    # - Closes the network connection
    # - Exits the program
    def cleanup(self):
        pygame.quit()
        self.network_client.close()
        sys.exit()