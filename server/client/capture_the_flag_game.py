import pygame
import sys
from network_client import NetworkClient
from game_renderer import GameRenderer

class CaptureTheFlagGame:
    def __init__(self,network_client = None,player_id = None):
        self.network_client = network_client or NetworkClient()
        self.renderer = GameRenderer()
        self.running = True
        self.player_id = player_id

    def choose_player(self):
        while self.player_id not in [0, 1, 2, 3]:
            try:
                one_indexed = int(input("Enter your player ID (1-4): "))
                self.player_id = one_indexed - 1
            except ValueError:
                continue

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_s:
                    dy = 1
                elif event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_d:
                    dx = 1
                if dx != 0 or dy != 0:
                    self.network_client.send_input(self.player_id, dx, dy)

    def run(self):
        self.choose_player() 
        if not self.network_client.listening:
            self.network_client.start_listener()

        while self.running:
            self.process_events()
            state = self.network_client.get_state()
            players = state.get("players", [])
            flag_pos = state.get("flag", (self.renderer.grid_size // 2, self.renderer.grid_size // 2))
            self.renderer.render(players, flag_pos)

        self.cleanup()

    def cleanup(self):
        pygame.quit()
        self.network_client.close()
        sys.exit()