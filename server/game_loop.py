import pygame
import sys

# Constants
GRID_SIZE = 15  # 15x15 grid
CELL_SIZE = 50  # Each cell is 50x50 pixels
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
PLAYER_COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]  # Red, Blue, Yellow, Cyan
FLAG_COLOR = (0, 255, 0)
BASE_COLOR = (100, 100, 100)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Capture the Flag - 4 Players")
clock = pygame.time.Clock()

# Grid setup
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Players
players = [
    {"id": 1, "pos": (0, 0), "color": PLAYER_COLORS[0], "has_flag": False, "score": 0},  # Top-left
    {"id": 2, "pos": (GRID_SIZE - 1, 0), "color": PLAYER_COLORS[1], "has_flag": False, "score": 0},  # Top-right
    {"id": 3, "pos": (0, GRID_SIZE - 1), "color": PLAYER_COLORS[2], "has_flag": False, "score": 0},  # Bottom-left
    {"id": 4, "pos": (GRID_SIZE - 1, GRID_SIZE - 1), "color": PLAYER_COLORS[3], "has_flag": False, "score": 0},  # Bottom-right
]

# Flag
flag_pos = (GRID_SIZE // 2, GRID_SIZE // 2)
grid[flag_pos[0]][flag_pos[1]] = "flag"

# Bases
bases = {
    1: (0, 0),  # Player 1's base
    2: (GRID_SIZE - 1, 0),  # Player 2's base
    3: (0, GRID_SIZE - 1),  # Player 3's base
    4: (GRID_SIZE - 1, GRID_SIZE - 1),  # Player 4's base
}

# Locked cells (initially empty)
locked_cells = set()

def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

def draw_players():
    for player in players:
        x, y = player["pos"]
        pygame.draw.rect(screen, player["color"], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_flag():
    x, y = flag_pos
    pygame.draw.rect(screen, FLAG_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_bases():
    for player_id, (x, y) in bases.items():
        pygame.draw.rect(screen, BASE_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_scores():
    font = pygame.font.Font(None, 36)
    for i, player in enumerate(players):
        text = font.render(f"Player {player['id']}: {player['score']}", True, player["color"])
        screen.blit(text, (10, 10 + i * 40))

def is_cell_occupied(x, y):
    """Check if a cell is occupied by another player."""
    for player in players:
        if player["pos"] == (x, y):
            return True
    return False

def move_player(player, dx, dy):
    x, y = player["pos"]
    new_x, new_y = x + dx, y + dy

    # Check if the new position is within the grid, not locked, and not occupied
    if (
        0 <= new_x < GRID_SIZE
        and 0 <= new_y < GRID_SIZE
        and (new_x, new_y) not in locked_cells
        and not is_cell_occupied(new_x, new_y)
    ):
        player["pos"] = (new_x, new_y)

         # Check if player stole flag from another player
        if not player["has_flag"]:
            for other_player in players:
                if other_player["id"] != player["id"] and other_player["has_flag"]:
                    ox, oy = other_player["pos"]
                    px, py = player["pos"]
                    if abs(px - ox) + abs(py - oy) == 1:    # Check if adjacent
                        other_player["has_flag"] = False
                        player["has_flag"] = True
                        print(f"Player {player['id']} stole the flag from Player {other_player['id']}")
                        break
                    
        # Check if the player captures the flag
        if (new_x, new_y) == flag_pos and not player["has_flag"]:
            player["has_flag"] = True
            locked_cells.add((new_x, new_y))  # Lock the flag cell
        
        # Check if the player returns the flag to their base
        if player["has_flag"] and (new_x, new_y) == bases[player["id"]]:
            player["score"] += 1
            player["has_flag"] = False
            locked_cells.clear()  # Unlock all cells


def main_game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle player movement
            if event.type == pygame.KEYDOWN:
                for player in players:
                    if player["id"] == 1:  # Player 1 controls (WASD)
                        if event.key == pygame.K_w:
                            move_player(player, 0, -1)
                        elif event.key == pygame.K_s:
                            move_player(player, 0, 1)
                        elif event.key == pygame.K_a:
                            move_player(player, -1, 0)
                        elif event.key == pygame.K_d:
                            move_player(player, 1, 0)
                    elif player["id"] == 2:  # Player 2 controls (Arrow keys)
                        if event.key == pygame.K_UP:
                            move_player(player, 0, -1)
                        elif event.key == pygame.K_DOWN:
                            move_player(player, 0, 1)
                        elif event.key == pygame.K_LEFT:
                            move_player(player, -1, 0)
                        elif event.key == pygame.K_RIGHT:
                            move_player(player, 1, 0)
                    elif player["id"] == 3:  # Player 3 controls (IJKL)
                        if event.key == pygame.K_i:
                            move_player(player, 0, -1)
                        elif event.key == pygame.K_k:
                            move_player(player, 0, 1)
                        elif event.key == pygame.K_j:
                            move_player(player, -1, 0)
                        elif event.key == pygame.K_l:
                            move_player(player, 1, 0)
                    elif player["id"] == 4:  # Player 4 controls (TFGH)
                        if event.key == pygame.K_t:
                            move_player(player, 0, -1)
                        elif event.key == pygame.K_g:
                            move_player(player, 0, 1)
                        elif event.key == pygame.K_f:
                            move_player(player, -1, 0)
                        elif event.key == pygame.K_h:
                            move_player(player, 1, 0)

        # Draw everything
        screen.fill((0, 0, 0))
        draw_grid()
        draw_bases()
        draw_flag()
        draw_players()
        draw_scores()

        # Update the display
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_game_loop()