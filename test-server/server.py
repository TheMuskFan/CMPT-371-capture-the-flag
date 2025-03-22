# TODO: Break the module down.

import socket
import threading
import json
import pygame

# Initialize Pygame, using pygame's clock timing.
pygame.init()

# --- Game Configuration ---
GRID_SIZE = 15  
PLAYER_COLORS = {
    1: (255, 0, 0),    # Red
    2: (0, 0, 255),    # Blue
    3: (255, 255, 0),  # Yellow
    4: (0, 255, 255)   # Cyan
}
FLAG_COLOR = (0, 255, 0)
BASE_COLOR = (100, 100, 100)

# TODO: Break the module down.
# Create a Player class representing each object.
players = {
    1: {"id": 1, "pos": (0, 0), "color": PLAYER_COLORS[1], "has_flag": False, "score": 0},
    2: {"id": 2, "pos": (GRID_SIZE - 1, 0), "color": PLAYER_COLORS[2], "has_flag": False, "score": 0},
    3: {"id": 3, "pos": (0, GRID_SIZE - 1), "color": PLAYER_COLORS[3], "has_flag": False, "score": 0},
    4: {"id": 4, "pos": (GRID_SIZE - 1, GRID_SIZE - 1), "color": PLAYER_COLORS[4], "has_flag": False, "score": 0},
}
flag_pos = (GRID_SIZE // 2, GRID_SIZE // 2)

# Players' starting positions.
# TODO: Create a class that can handle this setup.
bases = {
    1: (0, 0),
    2: (GRID_SIZE - 1, 0),
    3: (0, GRID_SIZE - 1),
    4: (GRID_SIZE - 1, GRID_SIZE - 1),
}

locked_cells = set()

# --- Locks for Thread Safety ---
state_lock = threading.Lock()

clients = []
clients_lock = threading.Lock()

# --- Game Logic Functions ---
def is_cell_occupied(pos, exclude_player_id=None):
    """Return True if any player (other than exclude_player_id) occupies the cell."""
    for pid, player in players.items():
        if exclude_player_id is not None and pid == exclude_player_id:
            continue
        if player["pos"] == pos:
            return True
    return False

# TODO: Have server actions (move_player, broadcast_state, etc) in its own module/class.
def move_player(player_id, dx, dy):
    """Update the position of the given player and handle flag capture/score."""
    with state_lock:
        player = players.get(player_id)
        if not player:
            return
        x, y = player["pos"]
        new_x, new_y = x + dx, y + dy

        # Check boundaries, locked cells, and occupancy.
        if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and 
            (new_x, new_y) not in locked_cells and 
            not is_cell_occupied((new_x, new_y), exclude_player_id=player_id)):
            player["pos"] = (new_x, new_y)

            # Capture the flag if stepping on its cell.
            if (new_x, new_y) == flag_pos and not player["has_flag"]:
                player["has_flag"] = True
                locked_cells.add((new_x, new_y))
            
            # If the player returns the flag to their base, update score.
            if player["has_flag"] and (new_x, new_y) == bases[player_id]:
                player["score"] += 1
                player["has_flag"] = False
                locked_cells.clear()

# --- Networking Functions ---
def broadcast_game_state():
    """Send the current game state to all connected clients."""
    with state_lock:
        state = {
            "type": "update",
            "players": list(players.values()),
            "flag": flag_pos,
            "locked_cells": list(locked_cells),
        }
    # Append newline as a message delimiter.
    message = json.dumps(state) + "\n"
    message = message.encode()
    with clients_lock:
        for client in clients:
            try:
                client.sendall(message)
            except Exception as e:
                print("Error broadcasting to a client:", e)

def client_thread(client_socket, address):
    """Handle messages from a single client."""
    print(f"Client {address} connected.")
    with clients_lock:
        clients.append(client_socket)
    try:
        # Wrap the socket to read full lines.
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
                move_player(player_id, dx, dy)
    except Exception as e:
        print("Error with client", address, e)
    finally:
        print(f"Client {address} disconnected.")
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()

def game_loop():
    """Broadcast game state at ~30 updates per second using Pygame clock."""
    clock = pygame.time.Clock()
    while True:
        broadcast_game_state()
        clock.tick(30)  # Limit to 30 updates per second

def start_server():
    HOST = '127.0.0.1'
    PORT = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow immediate reuse of address after shutdown.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)
    
    print(f"Server listening on {HOST}:{PORT}")
    
    # Start the game update loop.
    game_thread = threading.Thread(target=game_loop)
    game_thread.daemon = True
    game_thread.start()

    try:
        while True:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=client_thread, args=(client_socket, address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()