import pygame

class GameRenderer:
    # Sets grid and screen dimensions
    # Defines player colors, flag color, base color
    # Creates the Pygame display window and clock for frame timing
    def __init__(self, grid_size=15, cell_size=50,
                 player_colors=None, flag_color=(0, 255, 0), base_color=(100, 100, 100)):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.screen_width = grid_size * cell_size
        self.screen_height = grid_size * cell_size
        self.player_colors = player_colors or {
            0: (255, 0, 0),
            1: (0, 0, 255),
            2: (255, 255, 0),
            3: (0, 255, 255)
        }
        self.flag_color = flag_color
        self.base_color = base_color

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Capture the Flag Client")
        self.clock = pygame.time.Clock()

    # Draws a light gray grid on the screen, dividing it into cells for easier position visualization.
    def draw_grid(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    # Renders each player on the grid using their ID color.
    # If a player is carrying the flag, a smaller flag-colored square is drawn inside their cell.
    def draw_players(self, players):
        for player in players:
            x, y = player["pos"]
            color = self.player_colors.get(player["id"], (255, 255, 255))

            # Draw player
            pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size,
                                                    self.cell_size, self.cell_size))
        
            # Draw flag indicator if player has it
            if player["has_flag"]:
                flag_rect = pygame.Rect(
                    x * self.cell_size + self.cell_size//4,
                    y * self.cell_size + self.cell_size//4,
                    self.cell_size//2, self.cell_size//2
                )
                pygame.draw.rect(self.screen, self.flag_color, flag_rect)

    # Draws the standalone flag on the grid if it’s not currently being carried.
    def draw_flag(self, flag_pos):
        x, y = flag_pos
        pygame.draw.rect(self.screen, self.flag_color,
                         (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
        
    # Draws the bases in each corner of the grid.
    def draw_bases(self):
        bases = {
            1: (0, 0),
            2: (self.grid_size - 1, 0),
            3: (0, self.grid_size - 1),
            4: (self.grid_size - 1, self.grid_size - 1)
        }
        for base in bases.values():
            x, y = base
            pygame.draw.rect(self.screen, self.base_color,
                             (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

    # Displays the current scores for all players on the top-left corner of the screen, sorted from highest to lowest.
    def draw_scores(self, players):
        font = pygame.font.Font(None, 36)
        sorted_players = sorted(players, key=lambda p: p["score"], reverse=True)
        for i, player in enumerate(sorted_players):
            text = font.render(f"Player {player['id']}: {player['score']}", True,
                               self.player_colors.get(player["id"], (255, 255, 255)))
            self.screen.blit(text, (10, 10 + i * 40))

    # Main rendering method:
    # - Clears the screen
    # - Draws grid, bases, and flag (only if not carried)
    # - Draws players and their scores
    # - Updates the display and caps frame rate at 30 FPS
    def render(self, players, flag_pos):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_bases()
        if not any(p["has_flag"] for p in players):
            self.draw_flag(flag_pos)
        self.draw_players(players)
        self.draw_scores(players)
        pygame.display.flip()
        self.clock.tick(30)