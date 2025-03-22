# TODO: Break the module down.

import pygame
import sys
import socket
import threading
import json

# --- Game Configuration ---
GRID_SIZE = 15
CELL_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE

# TODO: have a class handling initialization.
PLAYER_COLORS = {
    1: (255, 0, 0),    # Red
    2: (0, 0, 255),    # Blue
    3: (255, 255, 0),  # Yellow
    4: (0, 255, 255)   # Cyan
}

FLAG_COLOR = (0, 255, 0)
BASE_COLOR = (100, 100, 100)

# --- Global Game State (Updated from the Server) ---
players = []         # List of player dictionaries
flag_pos = (GRID_SIZE // 2, GRID_SIZE // 2)
locked_cells = []    # List of locked cell tuples

# --- Network Configuration ---
HOST = '127.0.0.1'
PORT = 12345
client_socket = None

# TODO: have a networking class to handle client networking actions.
def network_listener():
    """Continuously receive and process game state updates."""
    global players, flag_pos, locked_cells
    # Wrap the socket so we can read full lines.
    file = client_socket.makefile('r')
    for line in file:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("type") == "update":
            players = message.get("players", players)
            flag = message.get("flag", flag_pos)
            flag_pos = tuple(flag)
            locked_cells = [tuple(cell) for cell in message.get("locked_cells", locked_cells)]

def send_player_input(player_id, dx, dy):
    """Send a JSON message to the server with the player's input."""
    message = {
        "type": "input",
        "player_id": player_id,
        "move": {"dx": dx, "dy": dy}
    }
    # Append newline so the server can correctly frame the message.
    try:
        client_socket.sendall((json.dumps(message) + "\n").encode())
    except Exception as e:
        print("Send error:", e)

# --- Pygame Drawing Functions ---
def draw_grid(screen):
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

def draw_players(screen):
    for player in players:
        x, y = player["pos"]
        color = PLAYER_COLORS.get(player["id"], (255, 255, 255))
        pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_flag(screen):
    x, y = flag_pos
    pygame.draw.rect(screen, FLAG_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_bases(screen):
    bases = {
        1: (0, 0),
        2: (GRID_SIZE - 1, 0),
        3: (0, GRID_SIZE - 1),
        4: (GRID_SIZE - 1, GRID_SIZE - 1),
    }
    for base in bases.values():
        x, y = base
        pygame.draw.rect(screen, BASE_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_scores(screen):
    font = pygame.font.Font(None, 36)
    for i, player in enumerate(players):
        text = font.render(f"Player {player['id']}: {player['score']}", True, PLAYER_COLORS.get(player["id"], (255, 255, 255)))
        screen.blit(text, (10, 10 + i * 40))

# Break the main function into modules, so that we can just call couple of functions to initialize the client.
def main():
    global client_socket

    # Ask the user which player they control.
    player_id = None
    while player_id not in [1, 2, 3, 4]:
        try:
            player_id = int(input("Enter your player ID (1-4): "))
        except ValueError:
            continue

    # Connect to the server.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Start the network listener thread.
    listener_thread = threading.Thread(target=network_listener)
    listener_thread.daemon = True
    listener_thread.start()

    # Initialize Pygame.
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Capture the Flag Client")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                # Use WASD for movement.
                if event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_s:
                    dy = 1
                elif event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_d:
                    dx = 1
                if dx != 0 or dy != 0:
                    send_player_input(player_id, dx, dy)

        # Draw the current game state.
        screen.fill((0, 0, 0))
        draw_grid(screen)
        draw_bases(screen)
        draw_flag(screen)
        draw_players(screen)
        draw_scores(screen)
        
        # Update.
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    client_socket.close()
    sys.exit()

if __name__ == "__main__":
    main()