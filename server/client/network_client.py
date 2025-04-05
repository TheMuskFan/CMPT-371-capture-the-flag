import queue
import socket
import threading
import json

class NetworkClient:
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
        
        
    def handle_game_start(self, message):
        with self.lock:
            self.game_start = True
        self.message_queue.put(message)

    def start_listener(self):
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()

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
    
    def get_messages(self):
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        
        return messages
            # self.process_message(message)
            
    def process_message(self,message):
        # print(f"Network client received message {message}")
        handler = self.message_handlers.get(message.get('type'))
        if handler:
            handler(message)
        else:
            print(f"Unhandled message type: {message.get('type')}")
        
    def handle_update(self, message):
        with self.lock:
            self.state.update({
                'players': message.get('players', []),
                'flag': tuple(message.get('flag', (0, 0))),
                'locked_cells': [tuple(c) for c in message.get('locked_cells', [])]
            })
            
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
            
    def handle_lobby_update(self, message):
        with self.lock:
            # Preserve existing ID/host
            self.lobby_state.update({
                'players': message.get('players', self.lobby_state['players']),
                'ready_states': message.get('ready_states', self.lobby_state['ready_states']),
                'can_start': message.get('can_start', self.lobby_state['can_start'])
            })
                
    def send_toggle_ready(self):
        print("Network Client: Sending toggle ready message")
        self.send_message(
            "ready",
            {"player_id": self.lobby_state["player_id"]}
        )
        
    def send_start_request(self):
        self.send_message(
            "start_request",
            {"player_id": self.lobby_state["player_id"]}
        )
            
    def send_disconnect(self):
        self.send_message(
            "disconnect",
            {"player_id": self.lobby_state["player_id"]}
        )
            
        
    def send_message(self,message_type,additional_data = None):
        message = {"type": message_type}
        
        if additional_data:
            message.update(additional_data)
            
        try:
            encoded_message = (json.dumps(message) + "\n").encode()
            self.client_socket.sendall(encoded_message)
            
        except Exception as e:
            print(f"Send {message_type} error: {e} \n")
        
    def send_input(self, player_id, dx, dy):
        self.send_message("input", {
            "player_id": player_id,
            "move": {"dx": dx, "dy": dy}
        })
        

    def get_state(self):
        with self.lock:
            return self.state.copy()

    def close(self):
        self.listening = False
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.client_socket.close()