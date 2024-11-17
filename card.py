# card.py
class Card:
    def __init__(self, name, attack=0, defense=0, effect=None, cost=0, description="", piercing=False):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.effect = effect
        self.cost = cost  # Resource cost to play the card
        self.description = description  # Add this line
        self.piercing = piercing  # New property for shield penetration
        self.image_path = self._get_image_path()

    def __str__(self):
        return f"{self.name} (ATK: {self.attack}, DEF: {self.defense}, Effect: {self.effect})"

    def to_dict(self):
        return {
            'name': self.name,
            'attack': self.attack,
            'defense': self.defense,
            'effect': self.effect,
            'cost': self.cost
        }

    def apply_effect(self, player, opponent):
        if self.effect == "heal":
            player.health += 10  # Heal effect restores player's health
            player.health = min(player.health, 100)  # Cap health at 100
        elif self.effect == "heal_full":
            player.health += 40
            player.health = min(player.health, 100)  # Cap health at 100
        elif self.effect == "skip_turn":
            opponent.skip_next_turn = True  # Set opponent's next turn to be skipped
            print(f"{opponent.name} will skip their next turn!")  # Debug print
        elif self.effect == "add_resources":
            player.resources += 5  # Generate additional resources
        
        # ...add other effects as needed...

    def _get_image_path(self):
        # Convert card name to image filename
        image_map = {
            "Laser Attack": "laser_attack.jpg",
            "Shield Upgrade": "shield_block.jpg",
            "Rocket Attack": "rocket_attack.jpg",
            "Repair": "repair.jpg",
            "Full Repair": "full_repair.jpg",
            "Stun": "stun.jpg",
            "Resource Generator": "resource_gen.jpg",
            "Sabotage Attack": "sabotage.jpg",
            "Intel Gathering": "intelligence.jpg",
            "Skip Turn": "skip.jpg"
        }
        filename = image_map.get(self.name, "default.jpg")
        return f"cards/{filename}"

    @classmethod
    def create_skip_card(cls):
        return cls("Skip Turn", attack=0, defense=0, effect="skip", cost=0, description="Skip this turn and gain +1⬣ resource.")
