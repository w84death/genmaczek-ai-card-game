import random
from card import Card  # Add this import

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.force_power = 0
        self.defense = 0
        self.skip_card = Card.create_skip_card()
        self.hand = [self.skip_card]  # Start with skip card
        self._resources = 10  # Using private variable for resources
        self.skip_next_turn = False

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, value):
        self._resources = max(0, value)  # Ensure resources don't go negative

    def draw_cards(self, deck, num=3):
        """Draw cards from the deck"""
        cards_to_draw = min(num, len(deck))
        for _ in range(cards_to_draw):
            if deck:  # Check if deck is not empty
                card = deck.pop()  # Remove card from deck
                self.hand.append(card)

    def can_play_card(self, card):
        return self.resources >= card.cost

    def play_card(self, card, opponent):
        if self.can_play_card(card):
            self.resources -= card.cost
            
            # Handle attack with defense and piercing
            if card.attack > 0:
                damage = card.attack
                # Only check shields if the attack is not piercing
                if not card.piercing and opponent.defense > 0:
                    absorbed = min(opponent.defense, damage)
                    opponent.defense -= absorbed
                    damage -= absorbed
                # Apply remaining damage (or full damage if piercing)
                if damage > 0:
                    opponent.health -= damage
            
            # Add defense points
            self.defense += card.defense
            
            # Apply card effects
            if card.effect:
                card.apply_effect(self, opponent)
            
            self.hand.remove(card)
            if card != self.skip_card:
                pass

    def end_turn(self, deck):
        """Return unused cards to the deck"""
        # Keep skip card if present
        skip_cards = [card for card in self.hand if card.effect == "skip"]
        # Get other cards
        other_cards = [card for card in self.hand if card.effect != "skip"]
        # Return other cards to deck
        deck.extend(other_cards)
        # Reset hand to only have skip cards
        self.hand = skip_cards
