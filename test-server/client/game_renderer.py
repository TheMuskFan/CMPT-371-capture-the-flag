import pygame

class GameRenderer:
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

    def draw_grid(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

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

    def draw_flag(self, flag_pos):
        x, y = flag_pos
        pygame.draw.rect(self.screen, self.flag_color,
                         (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
        

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

    def draw_scores(self, players):
        font = pygame.font.Font(None, 36)
        for i, player in enumerate(players):
            text = font.render(f"Player {player['id']}: {player['score']}", True,
                               self.player_colors.get(player["id"], (255, 255, 255)))
            self.screen.blit(text, (10, 10 + i * 40))

    def render(self, players, flag_pos):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_bases()
        self.draw_flag(flag_pos)
        self.draw_players(players)
        self.draw_scores(players)
        pygame.display.flip()
        self.clock.tick(30)