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
        # Keep the skip card
        skip_card = self.skip_card
        # Clear current hand completely
        self.hand.clear()
        # Put skip card back
        self.hand.append(skip_card)
        
        # Get available cards that are not skip cards
        available_cards = [card for card in deck if card.effect != "skip"]
        
        # Determine how many cards we can draw
        cards_to_draw = min(num, len(available_cards))
        
        if cards_to_draw > 0:
            # Draw exactly cards_to_draw cards
            drawn_cards = random.sample(available_cards, cards_to_draw)
            self.hand.extend(drawn_cards)
            
            # Remove drawn cards from the deck
            for card in drawn_cards:
                deck.remove(card)
        
        # print(f"{self.name} drew {len(self.hand)-1} cards (plus skip card)")  # Debug print

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
        # Return only non-skip cards to the deck
        cards_to_return = [card for card in self.hand if card != self.skip_card]
        deck.extend(cards_to_return)
        # Reset hand to only have the skip card
        self.hand = [self.skip_card]
        # print(f"{self.name} returned {len(cards_to_return)} cards to deck")  # Debug print
