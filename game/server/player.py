class Player:
    # Initializes a player with a unique ID, starting position, color, no flag, and a score of zero.
    def __init__(self, player_id, pos, color):
        self.id = player_id
        self.pos = pos
        self.color = color
        self.has_flag = False
        self.score = 0

    # Returns the player's data as a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "pos": self.pos,
            "color": self.color,
            "has_flag": self.has_flag,
            "score": self.score,
        }