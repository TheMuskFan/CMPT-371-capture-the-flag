import pygame
import pygame_menu
import sys
from game.client.game_client import GameClient
from lobby import Lobby
from enum import Enum, auto
from capture_the_flag_game import CaptureTheFlagGame

# Represents the current screen/state of the app:
# MENU: Main menu screen
# LOBBY: Waiting in the lobby
# GAME: Active gameplay
# ERROR: Error occurred, returns to menu
class AppState(Enum):
    MENU = auto()
    LOBBY = auto()
    GAME = auto()
    ERROR = auto()

class GameMenu:
    # Sets up the Pygame window, initializes the menu, and creates the main menu UI.
    # Also initializes app state and network client variables.
    def __init__(self,screen_width = 750,screen_height=750):
        pygame.init()
        
        self.surface = pygame.display.set_mode((screen_width,screen_height))
        pygame.display.set_caption("Capture the Flag")
        
        self.state = AppState.MENU
        self.game_client = None
        self.error_message = ""
        self.connection_in_progress = False
        
        self.create_main_menu()
    
    # Builds the main menu with:
    # - Server IP and Port input fields
    # - "Connect" and "Quit" buttons
    # - Optional error label if connection failed
    def create_main_menu(self):
        
        self.menu = pygame_menu.Menu(
            "Capture the Flag", 
            self.surface.get_width(),
            self.surface.get_height(),
            theme=pygame_menu.themes.THEME_DARK
        )
        
        # for resetting the widgets on the menu's inputs
        # self.menu.clear()
        
        # Add text input for server IP
        self.ip_input = self.menu.add.text_input(
            "Server IP:", 
            default="127.0.0.1", 
            maxchar=20, 
        )
        
        # Add text input for server port
        self.port_input = self.menu.add.text_input(
            "Server Port:", 
            default="12345", 
            maxchar=10, 
        )
        
        # self.menu.add.button('Connect', self.prepare_connection_details)
        self.menu.add.button('Connect', self.connect_to_server)
        # pygame_menu.events.EXIT also works
        self.menu.add.button('Quit', self.quit_game)
        
        if self.error_message:
            error_label = self.menu.add.label(
                self.error_message,
                font_color=(255, 100, 100),
                font_size=18
            )
            error_label.set_max_width(700)
    
    # Reads IP and port from input fields, then:
    # - Attempts to connect to the server
    # - Starts the network listener
    # - Changes app state to LOBBY if successful
    # - Shows error message on failure and refreshes menu
    def connect_to_server(self):
        if self.connection_in_progress:
            return
        
        host = self.ip_input.get_value()
        
        try:
            port = int(self.port_input.get_value())
        except ValueError:
            print("Invalid port number")
            self.error_message = "Invalid port number"
            self.create_main_menu()
            return
        
        try:
            self.game_client = GameClient(host,port)
            self.game_client.initialized = True
            self.game_client.start_listener()
            self.state = AppState.LOBBY
            self.connection_in_progress = True
            self.menu.disable()
        except Exception as e:
            self.error_message = f"Connection failed: {str(e)}"
            self.create_main_menu()
    
    # Closes the network connection if active, shuts down Pygame, and exits the program.
    def quit_game(self):
        if self.game_client:
            self.game_client.close()
        pygame.quit()
        sys.exit()

    # Central loop that switches between app states:
    # - MENU: Displays the main menu
    # - LOBBY: Runs the Lobby screen and checks the next transition
    # - GAME: Starts the game session
    # - ERROR: Triggers error handling
    def run(self):
        while True:
            events = pygame.event.get()
            
            if self.state == AppState.MENU:
                self.menu.update(events)
                self.menu.enable()
                self.menu.draw(self.surface)
            
            elif self.state == AppState.LOBBY:
                self.menu.disable()
                lobby = Lobby(self.game_client)
                result, player_id = lobby.run()
                
                # result is either "game" or "menu"
                if result == "game":
                    self.state = AppState.GAME
                else:
                    self.connection_in_progress = False
                    self.state = AppState.MENU
                    self.menu.enable()
                    
            elif self.state == AppState.GAME:
                game = CaptureTheFlagGame(self.game_client, player_id)
                game.run()
                
            elif self.state == AppState.ERROR:
                # this should just go back to the menu
                self.handle_error_state()
                
            pygame.display.flip()
    
    # Resets the app state to the menu and re-initializes the main menu after an error.
    def handle_error_state(self):
        self.state = AppState.MENU
        self.create_main_menu()
            