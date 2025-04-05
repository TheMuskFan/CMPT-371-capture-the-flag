import queue
import socket
import threading
import json

class NetworkClient:
    # Initializes the client, connects to the server, sets up state and message handling, 
    # and prepares for communication.
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.lock = threading.Lock()
        self.message_queue = queue.Queue()
        self.listening = False
        self.game_start = False
        
        self.state = {
            "players": [],
            "flag": (0, 0),
            "locked_cells": [],
        }
        
        self.lobby_state = {
            "players": [None] * 4,
            "ready_states": [False] * 4,
            "can_start": False,
            "player_id": None,
            "host": False,
        }
        
        self.message_handlers = {
            'update': self.handle_update,
            'lobby_update': self.handle_lobby_update,
            'lobby_init': self.handle_lobby_init,
            'game_start': self.handle_game_start
        }
        
    # Sets the game_start flag and queues the message for further processing.
    def handle_game_start(self, message):
        with self.lock:
            self.game_start = True
        self.message_queue.put(message)

    # Starts a background thread that listens for server messages.
    def start_listener(self):
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()

    # Continuously reads messages from the server, parses them, and hands them off to the handler.
    def listen(self):
        self.listening = True
        file = self.client_socket.makefile('r')
        while self.listening:
            try:
                line = file.readline()
                
                if not line:
                    break
                
                message = json.loads(line)
                self.process_message(message)
            except (json.JSONDecodeError,ConnectionError):
                continue
    
    # Returns all messages currently in the queue — used by the game to process new events.
    def get_messages(self):
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        
        return messages
            # self.process_message(message)
    
    # Routes incoming messages to the appropriate handler based on their type.
    def process_message(self,message):
        handler = self.message_handlers.get(message.get('type'))
        if handler:
            handler(message)
        else:
            print(f"Unhandled message type: {message.get('type')}")
    
    # Updates the in-game state (players, flag, locked cells) from the server.
    def handle_update(self, message):
        with self.lock:
            self.state.update({
                'players': message.get('players', []),
                'flag': tuple(message.get('flag', (0, 0))),
                'locked_cells': [tuple(c) for c in message.get('locked_cells', [])]
            })
    
    # Processes initial lobby info: assigns player ID, checks if host, and updates player list and ready states.
    def handle_lobby_init(self, message):
        # Includes getting ID and host
        with self.lock:
            self.lobby_state = {
                "players": message.get("players", [None]*4),
                "ready_states": message.get("ready_states", [False]*4),
                "player_id": message["your_id"],
                "can_start": message.get("can_start", False),
                "host": message.get("is_host", False)
            }
    
    # Updates lobby state (players, ready states, and whether the game can start).
    def handle_lobby_update(self, message):
        with self.lock:
            # Preserve existing ID/host
            self.lobby_state.update({
                'players': message.get('players', self.lobby_state['players']),
                'ready_states': message.get('ready_states', self.lobby_state['ready_states']),
                'can_start': message.get('can_start', self.lobby_state['can_start'])
            })

    # Sends a "ready/unready" toggle for the current player to the server.
    def send_toggle_ready(self):
        print("Network Client: Sending toggle ready message")
        self.send_message(
            "ready",
            {"player_id": self.lobby_state["player_id"]}
        )
    
    # Asks the server to start the game (host only).
    def send_start_request(self):
        self.send_message(
            "start_request",
            {"player_id": self.lobby_state["player_id"]}
        )
    
    # Informs the server the player is leaving the game.
    def send_disconnect(self):
        self.send_message(
            "disconnect",
            {"player_id": self.lobby_state["player_id"]}
        )

    # Sends a structured message to the server, merging any extra data.
    def send_message(self,message_type,additional_data = None):
        message = {"type": message_type}
        
        if additional_data:
            message.update(additional_data)
            
        try:
            encoded_message = (json.dumps(message) + "\n").encode()
            self.client_socket.sendall(encoded_message)
            
        except Exception as e:
            print(f"Send {message_type} error: {e} \n")
    
    # Sends movement input (directional) to the server for the specified player.
    def send_input(self, player_id, dx, dy):
        self.send_message("input", {
            "player_id": player_id,
            "move": {"dx": dx, "dy": dy}
        })
    
    # Returns a copy of the current game state (used for rendering or logic on the client side).
    def get_state(self):
        with self.lock:
            return self.state.copy()
    
    # Stops listening and closes the socket connection safely.
    def close(self):
        self.listening = False
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.client_socket.close()