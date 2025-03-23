class Player:
    def __init__(self, player_id, pos, color):
        self.id = player_id
        self.pos = pos
        self.color = color
        self.has_flag = False
        self.score = 0

    def to_dict(self):
        return {
            "id": self.id,
            "pos": self.pos,
            "color": self.color,
            "has_flag": self.has_flag,
            "score": self.score,
        }