import time
import pygame
import pygame_menu
from enum import Enum,auto

# Represents the current state of the lobby screen:
# - WAITING: Still in the lobby.
# - START_GAME: Ready to transition into the game.
# - EXIT: Player wants to leave the lobby and return to main menu.
class LobbyState(Enum):
    WAITING = auto()    # Still in lobby
    START_GAME = auto() # Transition to game
    EXIT = auto()  # Return to main menu

class Lobby:

    # Sets up the Pygame lobby UI, initializes player state tracking, and builds a menu interface with:
    # Player info frames: "Ready", "Start Game", and "Leave Lobby" buttons
    def __init__(self,network_client,screen_width = 750, screen_height = 750):
        pygame.init()
        
        self.last_update_time = 0
        self.update_interval = 0.1
        
        self.network_client = network_client
        self.lobby_state = LobbyState.WAITING
        self.surface = pygame.display.set_mode((screen_width, screen_height))
        
        self.players = [None] * 4
        self.ready_states = [False] * 4
        self.is_ready = False
        self.starting_game = False
        
        self.menu = pygame_menu.Menu(
            title="Game Lobby",
            width=screen_width,
            height=screen_height,
            theme=pygame_menu.themes.THEME_DARK
        )
        
        self.player_widgets = []
        self.player_labels = []
        for i in range(4):
            frame = self.menu.add.frame_v(
                width = 300,
                height = 60,
                background_color=(50, 50, 50),
                padding = 0
            )
            
            row = self.menu.add.frame_h(
                width=290,
                height=50,
                background_color=(50, 50, 50)
            )
            
            player_label = self.menu.add.label(
                f"Player {i+1}:",
                font_color=(200, 200, 200),
                font_size=20
            )
            player_label.set_max_height(40)
            
            status = self.menu.add.label(
                "(Empty)", 
                font_color=(150, 150, 150),
                font_size=20
            )
            status.set_max_height(40)
            
            row.pack(player_label, align=pygame_menu.locals.ALIGN_LEFT)
            row.pack(status, align=pygame_menu.locals.ALIGN_RIGHT)
            frame.pack(row)
            
            self.player_widgets.append((frame, status))
            self.player_labels.append(player_label)
            self.menu.add.vertical_margin(10)
            
        self.ready_button = self.menu.add.button(
            "Ready",
            self.toggle_ready,
            background_color=(0, 180, 0)
        )
        
        self.start_button = self.menu.add.button(
            "Start Game",
            self.start_game,
            background_color=(0, 100, 200)
        )
        
        self.menu.add.button(
            'Leave Lobby', 
            self.leave_lobby,
            font_size=25
        )
    
    # Syncs the displayed lobby UI with the latest state from the server:
    # Updates player names, ready states, colors, and button visibility (like Start Game)
    def update_ui(self):
        lobby_state = self.network_client.lobby_state
        current_player_id = lobby_state["player_id"]
        
        for i in range(4):
            frame,status = self.player_widgets[i]
            player = lobby_state["players"][i]
            is_ready = lobby_state["ready_states"][i]
            
            # label_text = f"Player {i+1}:"
            if i == current_player_id and player is not None:
                label_text = f"Player {i+1}: (YOU)"
                self.player_labels[i].set_title(label_text)
            
            if player is None:
                status.set_title("Empty")
                status.update_font({'color': (150, 150, 150)}) 
                frame.set_background_color((150, 150, 150))
            else:
                status.set_title("Ready" if is_ready else "Not Ready")
                # new frame is green if ready, else red if not ready
                new_frame_color = ((50,150, 50) if is_ready else (150,50,50))
                frame.set_background_color(new_frame_color)
                
                status.update_font({'color': (0, 255, 0) if is_ready else (255, 0, 0)}) 
            
        if lobby_state["can_start"]:
            self.start_button.show()
            self.start_button.set_background_color((0,200,200))
        else:
            self.start_button.hide()
    
    # Toggles the current player's "ready" status and sends an update to the server.
    def toggle_ready(self):
        print(f"Ready button clicked.")
        self.is_ready = not self.is_ready
        self.network_client.send_toggle_ready()

    # Sends a request to the server to start the game.
    # Only visible if the client is the host and conditions are met.
    def start_game(self):
        self.network_client.send_start_request()
    
    # Changes the local lobby state to EXIT and notifies the server of disconnection.
    def leave_lobby(self):
        self.lobby_state = LobbyState.EXIT
        self.network_client.send_disconnect()
        
    # Returns what the next screen should be ("game" or "menu"), based on the current lobby state.
    def get_next_state(self):
        if self.lobby_state == LobbyState.START_GAME:
            return "game"
            # return LobbyState.GAME
        elif self.lobby_state == LobbyState.EXIT:
            # return LobbyState.EXIT
            return "menu"
        
        return self.lobby_state
    
    # Main loop for the lobby screen:
    # Continuously checks events, updates UI, and handles game start trigger.
    # Runs at 30 FPS until the state changes from WAITING.
    def run(self):
        clock = pygame.time.Clock()
        
        while self.lobby_state == LobbyState.WAITING:
            events = pygame.event.get()
            
            self.update_ui()
            # for debug
            # print(self.network_client.lobby_state)
            if self.network_client.game_start:
                self.lobby_state = LobbyState.START_GAME
            
            self.menu.update(events)
            self.menu.draw(self.surface)
            pygame.display.flip()
            clock.tick(30)
        
        return self.get_next_state(), self.network_client.lobby_state["player_id"]
  