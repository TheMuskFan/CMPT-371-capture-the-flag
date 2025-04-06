import sys
import pygame
import pygame_gui
from game_client import GameClient
from game_renderer import GameRenderer

class CaptureTheFlagGame:
    # Sets up the game:
    # - Initializes the network client (or creates one if none provided)
    # - Creates a GameRenderer for visuals
    # - Sets the game loop to running
    # - Stores the player's ID
    def __init__(self, game_client = None, player_id = None):
        self.game_client = game_client or GameClient()
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
                    self.game_client.send_input(self.player_id, dx, dy)

    # Main game loop:
    # Ensures player ID is set
    # Starts the network listener (if not already running)
    # Loops while the game is active:
    # - Processes user input
    # - Gets game state from the server
    # - Renders players and flag with GameRenderer
    def run(self):
        self.choose_player() 
        if not self.game_client.listening:
            self.game_client.start_listener()

        while self.running:
            self.process_events()

            # Check if a server shutdown has been signaled.
            if self.game_client.server_down:
                self.show_server_down_alert()
                break
            
            state = self.game_client.get_state()
            players = state.get("players", [])
            flag_pos = state.get("flag", (self.renderer.grid_size // 2, self.renderer.grid_size // 2))
            self.renderer.render(players, flag_pos)

        self.cleanup()

    # Show server down GUI
    def show_server_down_alert(self):
        # Get the current screen size from the renderer.
        screen_size = self.renderer.screen.get_size()
        alert_width, alert_height = 400, 200
        # Calculate the centered position.
        alert_rect = pygame.Rect(
            (screen_size[0] - alert_width) // 2,
            (screen_size[1] - alert_height) // 2,
            alert_width,
            alert_height
        )
        
        # Create a UIManager using the size of the renderer's display.
        manager = pygame_gui.UIManager(screen_size)
        # Create the message window with the centered rectangle.
        alert_window = pygame_gui.windows.UIMessageWindow(
            rect=alert_rect,
            html_message="Server is shutting down. The game will now exit.",
            manager=manager
        )
        clock = pygame.time.Clock()
        alert_active = True

        while alert_active:
            time_delta = clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    alert_active = False
                manager.process_events(event)
            manager.update(time_delta)
            self.renderer.screen.fill((0, 0, 0))  # Clear the screen
            manager.draw_ui(self.renderer.screen)
            pygame.display.update()

            # Exit the loop once the alert window is closed.
            if not alert_window.alive():
                alert_active = False

    # Gracefully shuts down the game:
    # - Quits Pygame
    # - Closes the network connection
    # - Exits the program
    def cleanup(self):
        pygame.quit()
        self.game_client.close()
        sys.exit()