# game_logic.py
class Game:
    def __init__(self, player, ai_player, deck):
        self.player = player
        self.ai_player = ai_player
        self.deck = deck
        self.current_turn = player  # or ai_player

    def next_turn(self):
        self.current_turn = self.ai_player if self.current_turn == self.player else self.player

    def check_winner(self):
        if self.player.health <= 0:
            return self.ai_player.name
        elif self.ai_player.health <= 0:
            return self.player.name
        elif len(self.deck) == 0:
            # If the deck is empty, the player with higher health wins
            if self.player.health > self.ai_player.health:
                return self.player.name
            elif self.ai_player.health > self.player.health:
                return self.ai_player.name
            else:
                return "No one"  # It's a tie
        return None
