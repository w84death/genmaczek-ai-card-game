import requests
from player import Player  # Import the Player class
import json  # Add this import
import random  # Add this import if not already present

class AIPlayer(Player):
    def __init__(self, name, server_url):
        super().__init__(name)
        self.server_url = server_url

    def decide_move(self, game_state, max_retries=3):
        # Draw new cards if hand is empty
        if not self.hand:
            self.draw_cards(game_state['deck'], num=3)
        
        # Keep track of retries
        retries = 0
        last_error = None  # Track the last error
        
        while retries < max_retries:
            game_state['ai_resources'] = self.resources
            message = self.create_prompt(game_state, last_error)  # Pass the error to prompt

            # Add random seed for each attempt
            payload = {
                "model": "llama3.2",
                "prompt": message,
                "format": "json",
                "stream": False,
            }
            response = requests.post(
                f"{self.server_url}/api/generate",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get('response', '')
                try:
                    ai_response = json.loads(content)
                    if ai_response and isinstance(ai_response, dict):
                        card_name = ai_response.get("card_name", "")
                        if card_name:  # If we got a valid card name
                            # Check if AI wants to skip turn
                            if card_name.lower() == "skip_turn":
                                print(f"AI skipping turn to gain 1 resource (Current: {self.resources})")
                                return self.skip_card
                            
                            # Try to play a card
                            for card in self.hand:
                                if card.name.lower() == card_name.lower():
                                    if self.can_play_card(card):
                                        print(f"AI playing {card.name} (Cost: {card.cost}, Resources: {self.resources})")
                                        return card
                                    else:
                                        last_error = f"Insufficient resources to play {card.name} (Cost: {card.cost}, Available: {self.resources}). Consider skipping turn to gain resources."
                                        break
                            else:
                                last_error = f"Card {card_name} not found in hand"
                except json.JSONDecodeError:
                    last_error = "Failed to parse AI response as JSON"

            retries += 1
            print(f"Retrying AI decision ({retries}/{max_retries}). Reason: {last_error}")
        
        print("AI failed to make a valid decision after all retries, skipping turn")
        return self.skip_card

    def end_turn(self, deck):
        # Return only non-skip cards to the deck
        unused_cards = [card for card in self.hand if card != self.skip_card and card.effect != "skip"]
        deck.extend(unused_cards)
        # Reset hand to only have the skip card
        self.hand = [self.skip_card]

    def create_prompt(self, game_state, last_error=None):
        prompt = "{"
        prompt += "\"ai_hand\": [\n"
        for card in game_state['ai_hand']:
            prompt += f"    {{\"name\": \"{card['name']}\", \"attack\": {card['attack']}, \"defense\": {card['defense']}, \"effect\": \"{card['effect']}\", \"cost\": {card['cost']}}},\n"
        prompt += f"  ]\n" \
              f"}}\n" \
              f"You have {game_state['ai_resources']} resources and {game_state['ai_health']} health. Opponent health is {game_state['player_health']}. " \
              f"Cards left: {len(game_state['deck'])}. "
        
        if last_error:
            prompt += f"Previous attempt failed because: {last_error}. "
            prompt += f"Choose card from: "
            for card in game_state['ai_hand']:
                prompt += f"\"{card['name']}\","
        prompt += "Your turn, respond in JSON."

        # print(prompt)
        return prompt
