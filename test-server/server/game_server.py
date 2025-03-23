import socket
import threading
import json
import pygame  # Used for the clock in the game loop
from game_state import GameState

class GameServer:
    def __init__(self, host='127.0.0.1', port=12345, grid_size=15):
        self.host = host
        self.port = port
        self.game_state = GameState(grid_size)
        self.clients = []
        self.clients_lock = threading.Lock()

    def broadcast_game_state(self):
        state = {"type": "update"}
        state.update(self.game_state.get_state())
        message = json.dumps(state) + "\n"
        message = message.encode()
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.sendall(message)
                except Exception as e:
                    print("Error broadcasting:", e)

    def handle_client(self, client_socket, address):
        print(f"Client {address} connected.")
        with self.clients_lock:
            self.clients.append(client_socket)
        try:
            file = client_socket.makefile('r')
            for line in file:
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if message.get("type") == "input":
                    player_id = message.get("player_id")
                    move = message.get("move", {})
                    dx = move.get("dx", 0)
                    dy = move.get("dy", 0)
                    self.game_state.move_player(player_id, dx, dy)
        except Exception as e:
            print(f"Error with client {address}: {e}")
        finally:
            print(f"Client {address} disconnected.")
            with self.clients_lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()

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