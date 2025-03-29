import socket
import threading
import json
import pygame  # Used for the clock in the game loop
from game_state import GameState

class GameServer:
    def __init__(self, host='127.0.0.1', port=12345, grid_size=15):
        self.host = host
        self.port = port
        self.grid_size = grid_size
        self.game_state = GameState(grid_size)
        self.clients = []
        self.clients_lock = threading.Lock()
        self.player_count = 0
        self.lock = threading.Lock()
        
        self.lobby_state = {
            'players': [None] * 4,
            'ready_states': [False] * 4,
            'sockets': [None] * 4,
            'addresses': [None] * 4
        }
        
        self.message_handlers = {
            'input': self.handle_input,
            
            'ready': self.handle_ready_toggle,
            'start_request': self.handle_start_request,
            'disconnect': self.handle_disconnect_message
        }
        
    def check_can_start(self):
        return (all(self.lobby_state["ready_states"]))
    
    def handle_start_request(self, message):
        with self.lock:
            if all(self.lobby_state["ready_states"]):
                self.broadcast_game_start()
                self.game_state = GameState(self.grid_size)
                
                
    def broadcast_game_start(self):
        start_msg = json.dumps({"type": "game_start"}) + "\n"
        for i, socket in enumerate(self.lobby_state["sockets"]):
            if socket:
                try:
                    socket.sendall(start_msg.encode())
                except Exception as e:
                    print(f"Failed to send start to player {i + 1}: {e}")
                    self.cleanup_player(i)

    def broadcast_game_state(self):
        state = {"type": "update"}
        state.update(self.game_state.get_state())
        message = json.dumps(state) + "\n"
        message = message.encode()
        
        for i, socket in enumerate(self.lobby_state["sockets"]):
            if socket:
                try:
                    # debug messages
                    # print(f"Sending game state to player {i + 1}")
                    socket.sendall(message)
                except Exception as e:
                    print(f"Failed to send game state to player {i + 1}: {e}")
                    pass
                    
    def broadcast_lobby_state(self):
        state = {
            'type': 'lobby_update',
            'players': self.lobby_state['players'],
            'ready_states': self.lobby_state['ready_states'],
            'can_start': all(self.lobby_state['ready_states'])
        }
        print(f"\nPreparing to broadcast: {state}")  # Debug print
        
        encoded = (json.dumps(state) + '\n').encode()
        # print(f"Sockets: {self.lobby_state['sockets']}")  # Debug sockets
        for i, socket in enumerate(self.lobby_state["sockets"]):
            if socket:
                try:
                    print(f"Sending lobby state to player {i + 1}")
                    socket.sendall(encoded)
                except Exception as e:
                    print(f"Failed to send to player {i + 1}: {e}") 
                    pass
        
    
    # returns assigned player id or -1 if if failed
    def initialize_lobby(self,client_socket,address) -> int:
        for i in range(4):
            if self.lobby_state['players'][i] is None:
                self.lobby_state['players'][i] = f"Player_{i+1}"
                self.lobby_state['sockets'][i] = client_socket
                self.lobby_state['ready_states'][i] = False
                self.lobby_state['addresses'][i] = address
                # player_id is equal to i
                self.send_lobby_init(client_socket, i)
                
                # broadcast to everyone when someone new joins
                self.broadcast_lobby_state()
                
                print(f"Sent lobby initialization to ", address)
                return i
            
        return -1
        
                    
    def handle_client(self,client_socket,address):
        print(f"Client {address} connected.")
        player_id = -1
        try:
            with self.lock:
                print(f"Currently there are {self.player_count} players")
                if self.player_count >= 4:
                    client_socket.close()
                    return
                    
                player_id = self.initialize_lobby(client_socket, address)
                if player_id == -1:
                    print(f"Too many players, reject {address}")
                    client_socket.close()
                    return
                
                self.player_count += 1
            file = client_socket.makefile('r')
            for line in file:
                try:
                    message = json.loads(line)
                    message_type = message.get("type")
                    
                    handler = self.message_handlers.get(message_type)
                    # debug
                    # print(message)
                    if handler:
                        
                        handler(message)
                    else:
                        # shouldn't hit error when using gui
                        print(f"Unhandled message type from client: {message_type}")
                except json.JSONDecodeError:
                    continue
        except ConnectionError:
            print(f"Client {address} disconnected abruptly")
        finally:
            self.handle_network_disconnect(player_id)
                        
    def send_lobby_init(self,socket,player_id):
        print(f"Broadcasting lobby state to all players")
        init_msg = {
            "type": "lobby_init",
            "your_id": player_id,
            "is_host": (player_id == 0), # todo: host logic
            "players": self.lobby_state['players'],
            "ready_states": self.lobby_state['ready_states'],
            "can_start": self.check_can_start()
        }
        if self.lobby_state['sockets'][player_id] is not None:
            socket.sendall(json.dumps(init_msg).encode() + b'\n')
            
    def handle_ready_toggle(self,message):
        player_id = message.get("player_id")
        with self.lock:
            current_ready_state = self.lobby_state["ready_states"][player_id]
            
            self.lobby_state["ready_states"][player_id] = not current_ready_state
            print(f"Updating ready state of player with id", player_id)
            print(f"Player with id", player_id, "ready:", current_ready_state)
            self.broadcast_lobby_state()
            if all(self.lobby_state["ready_states"]):
                # maybe start
                pass
            
    def handle_input(self,message):
        lobby_id = message.get("player_id")
        game_state_id = lobby_id + 1  # Convert to 1-4 for GameState
        move = message.get("move", {})
        dx = move.get("dx", 0)
        dy = move.get("dy", 0)
        self.game_state.move_player(game_state_id, dx, dy)
        
    # for abrupt disconnects
    def handle_network_disconnect(self, player_id: int):
        self.cleanup_player(player_id)
        
    def handle_disconnect_message(self,message):
        player_id = message.get('player_id')
        if player_id is not None:
            self.cleanup_player(player_id)
            
    def cleanup_player(self, player_id):
        with self.lock:
            address = self.lobby_state['addresses'][player_id]
            client_socket = self.lobby_state['sockets'][player_id]
            
            if player_id == -1:  # Never got assigned a slot
                return
            try:         
                # Clear the player's slot
                self.lobby_state['players'][player_id] = None
                self.lobby_state['sockets'][player_id] = None
                self.lobby_state['ready_states'][player_id] = False
                self.lobby_state['addresses'][player_id] = None
                self.player_count -= 1
                            
                print(f"Player {player_id} has left the game")
            except (ConnectionResetError):
                print(f"Client {address} disconnected abruptly")
            finally:
                if client_socket is not None:
                    client_socket.close()
                self.broadcast_lobby_state()

    def game_loop(self):
        clock = pygame.time.Clock()
        while True:
            self.broadcast_game_state()
            clock.tick(30)  # 30 updates per second

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(4)
        print(f"Server listening on {self.host}:{self.port}")

        game_thread = threading.Thread(target=self.game_loop)
        game_thread.daemon = True
        game_thread.start()

        try:
            while True:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            server_socket.close()