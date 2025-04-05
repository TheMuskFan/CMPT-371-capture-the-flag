import threading
import random
from player import Player

class GameState:
    # Initializes the game state with a grid, player positions, team bases, 
    # and a randomly placed flag. Sets up player objects for each connected ID.
    def __init__(self, grid_size=15, connected_players_ids = None):
        self.grid_size = grid_size
        self.players = {}
        if connected_players_ids is None:
            connected_players_ids = []
        for pid in connected_players_ids:
            if pid == 1:
                start_pos = (0, 0)
                color = (255, 0, 0)  
            elif pid == 2:
                start_pos = (grid_size - 1, 0)
                color = (0, 0, 255)
            elif pid == 3:
                start_pos = (0, grid_size - 1)
                color = (255, 255, 0)
            elif pid == 4:
                start_pos = (grid_size - 1, grid_size - 1)
                color = (0, 255, 255)
            self.players[pid] = Player(pid, start_pos, color)
        self.flag_pos = (grid_size // 2, grid_size // 2)
        self.bases = {
            1: (0, 0),
            2: (grid_size - 1, 0),
            3: (0, grid_size - 1),
            4: (grid_size - 1, grid_size - 1),
        }
        self.locked_cells = set()
        self.state_lock = threading.Lock()
        self.flag_pos = self.generate_random_flag_position()
    
    # Randomly selects a grid cell for the flag that isn’t a player’s base 
    # or currently occupied by a player.
    def generate_random_flag_position(self):
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            pos = (x, y)
            
            # Check if position is not a base and not occupied by a player
            if (pos not in self.bases.values() and 
                not self.is_cell_occupied(pos)):
                return pos

    # Checks if a grid cell is occupied by any player, 
    # optionally excluding a specific player from the check (e.g., when moving that player).
    def is_cell_occupied(self, pos, exclude_player_id=None):
        for pid, player in self.players.items():
            if exclude_player_id is not None and pid == exclude_player_id:
                continue
            if player.pos == pos:
                return True
        return False

    # Handles a player's move:
    # - Validates move within bounds and checks for collisions or locked cells.
    # - If carrying a flag, the flag moves with the player.
    # - Allows stealing the flag from adjacent players.
    # - Lets players capture the flag by stepping on it.
    # Returns the flag to base to score a point, and resets the flag.
    def move_player(self, player_id, dx, dy):
        with self.state_lock:
            player = self.players.get(player_id)
            if not player:
                return
            x, y = player.pos
            new_x, new_y = x + dx, y + dy

            if (0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size and
                (new_x, new_y) not in self.locked_cells and
                not self.is_cell_occupied((new_x, new_y), exclude_player_id=player_id)):

                # If player has flag, move flag with them
                if player.has_flag:
                    # Remove lock from previous flag position
                    if self.flag_pos in self.locked_cells:
                        self.locked_cells.remove(self.flag_pos)
                    self.flag_pos = (new_x, new_y)

                player.pos = (new_x, new_y)

                # Check if player stole flag from another player
                if not player.has_flag:
                    for other_id, other_player in self.players.items():
                        if other_id != player_id and other_player.has_flag:
                            ox, oy = other_player.pos
                            px, py = player.pos
                            if abs(px - ox) + abs(py - oy) == 1:  # Check if adjacent
                                other_player.has_flag = False
                                player.has_flag = True
                                break

                # Capture flag if stepping on its cell.
                if (new_x, new_y) == self.flag_pos and not any(p.has_flag for p in self.players.values()):
                    player.has_flag = True
                    self.locked_cells.add((new_x, new_y))

                # If player returns flag to base, update score.
                if player.has_flag and (new_x, new_y) == self.bases[player_id]:
                    player.score += 1
                    player.has_flag = False
                    self.flag_pos = self.generate_random_flag_position()  # Flag respawns randomly
                    self.locked_cells.clear()

    # Returns a dictionary representing the current game state: 
    # player positions, flag location, and locked cells. Used for broadcasting to clients.
    def get_state(self):
        with self.state_lock:
            return {
                "players": [player.to_dict() for player in self.players.values()],
                "flag": self.flag_pos,
                "locked_cells": list(self.locked_cells),
            }