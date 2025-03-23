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
        self.state = {
            "players": [],
            "flag": (0, 0),
            "locked_cells": [],
        }

    def start_listener(self):
        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()

    def listen(self):
        file = self.client_socket.makefile('r')
        for line in file:
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("type") == "update":
                with self.lock:
                    self.state["players"] = message.get("players", [])
                    self.state["flag"] = tuple(message.get("flag"))
                    self.state["locked_cells"] = [tuple(cell) for cell in message.get("locked_cells", [])]

    def send_input(self, player_id, dx, dy):
        message = {
            "type": "input",
            "player_id": player_id,
            "move": {"dx": dx, "dy": dy}
        }
        try:
            self.client_socket.sendall((json.dumps(message) + "\n").encode())
        except Exception as e:
            print("Send error:", e)

    def get_state(self):
        with self.lock:
            return self.state.copy()

    def close(self):
        self.client_socket.close()