import aiohttp
import asyncio
from player import Player
import json
import random

class AIPlayer(Player):
    def __init__(self, name, server_url):
        super().__init__(name)
        self.server_url = server_url
        self.session = None

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def decide_move(self, game_state, max_retries=3):
        if not self.hand:
            self.draw_cards(game_state['deck'], num=3)
        
        retries = 0
        last_error = None
        
        while retries < max_retries:
            game_state['ai_resources'] = self.resources
            message = self.create_prompt(game_state, last_error)

            payload = {
                "model": "granite3-dense",
                "prompt": message,
                "format": "json",
                "stream": False,
            }

            session = await self.get_session()
            try:
                async with session.post(f"{self.server_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get('response', '')
                        try:
                            ai_response = json.loads(content)
                            if ai_response and isinstance(ai_response, dict):
                                card_name = ai_response.get("card_name", "")
                                if card_name:
                                    if card_name.lower() == "skip_turn":
                                        print(f"AI skipping turn to gain 1 resource (Current: {self.resources})")
                                        return self.skip_card
                                    
                                    for card in self.hand:
                                        if card.name.lower() == card_name.lower():
                                            if self.can_play_card(card):
                                                print(f"AI playing {card.name}")
                                                return card
                                            else:
                                                last_error = f"Insufficient resources for {card.name}"
                                                break
                                    else:
                                        last_error = f"Card {card_name} not found in hand"
                        except json.JSONDecodeError:
                            last_error = "Failed to parse AI response as JSON"

            except Exception as e:
                last_error = f"Network error: {str(e)}"

            retries += 1
            if not last_error:
                last_error = "Response format error"
            await asyncio.sleep(0.5)  # Add small delay between retries
            
        print("AI failed to make a valid decision")
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
            prompt += f"Cards in hand: "
            for card in game_state['ai_hand']:
                prompt += f"\"{card['name']}\","
        prompt += "Choose a valid card, Respond in JSON format {{\"card_name\": \"[Card Name]\"}}."

        # print(prompt)
        return prompt

    async def generate_narrative(self, action):
        prompt = f"Provide a narrative commentary for the following action:\n{action}\n. Respond in JSON with narrative_commentary."
        payload = {
            "model": "granite3-dense",
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        
        session = await self.get_session()
        try:
            async with session.post(f"{self.server_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('response', '')
                    try:
                        narrative_response = json.loads(content)
                        commentary = narrative_response.get('narrative_commentary', '')
                        return commentary.strip()
                    except json.JSONDecodeError:
                        return "The battle continues..."
        except Exception:
            return "The battle continues..."
        
        return "The battle continues..."

    async def generate_introduction(self):
        prompt = "Provide a motivational, welcoming message for the player general at the start of the game."
        payload = {
            "model": "granite3-dense",
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        
        session = await self.get_session()
        try:
            async with session.post(f"{self.server_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('response', '')
                    try:
                        intro_response = json.loads(content)
                        message = intro_response.get('narrative_commentary', '')
                        return message.strip()
                    except json.JSONDecodeError:
                        return "Welcome to the battle, General!"
        except Exception:
            return "Welcome to the battle, General!"
        
        return "Welcome to the battle, General!"

    async def cleanup(self):
        if self.session:
            await self.session.close()
            self.session = None
