import threading
import random
from player import Player

class GameState:
    def __init__(self, grid_size=15):
        self.grid_size = grid_size
        self.players = {
            1: Player(1, (0, 0), (255, 0, 0)),
            2: Player(2, (grid_size - 1, 0), (0, 0, 255)),
            3: Player(3, (0, grid_size - 1), (255, 255, 0)),
            4: Player(4, (grid_size - 1, grid_size - 1), (0, 255, 255)),
        }
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
    
    def generate_random_flag_position(self):
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            pos = (x, y)
            
            # Check if position is not a base and not occupied by a player
            if (pos not in self.bases.values() and 
                not self.is_cell_occupied(pos)):
                return pos

    def is_cell_occupied(self, pos, exclude_player_id=None):
        for pid, player in self.players.items():
            if exclude_player_id is not None and pid == exclude_player_id:
                continue
            if player.pos == pos:
                return True
        return False

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

    def get_state(self):
        with self.state_lock:
            return {
                "players": [player.to_dict() for player in self.players.values()],
                "flag": self.flag_pos,
                "locked_cells": list(self.locked_cells),
            }