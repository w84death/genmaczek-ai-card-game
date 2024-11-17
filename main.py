# main.py
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QSound
from card import Card
from player import Player
from ai_player import AIPlayer
from logic import Game
from ui import GameUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("genMaczek - AI Card Battle Game")
        # Set fixed window size and disable resizing
        # self.setFixedSize(800, 600)
        self.setMaximumWidth(1024)
        self.setMaximumHeight(768)
        self.setWindowIcon(QIcon('icon.png'))  # Add your icon file here

        # Initialize players and game
        self.player = Player("You")
        self.ai_player = AIPlayer("AI Opponent", "http://localhost:11434")  # Ollama server
        self.deck = self.create_deck()
        self.game = Game(self.player, self.ai_player, self.deck)
        self.narrative_ai = AIPlayer("NarrativeAI", "http://localhost:11434")

        # Players draw initial hands
        self.player.draw_cards(self.deck)
        self.ai_player.draw_cards(self.deck)

        # Set up UI elements
        self.ui = GameUI(self, self.player, self.ai_player, self.narrative_ai)

    def init_ui(self):
        layout = QVBoxLayout()

        # Labels for health and stats
        self.player_label = QLabel(f"{self.player.name} Health: {self.player.health}")
        self.ai_label = QLabel(f"{self.ai_player.name} Health: {self.ai_player.health}")
        layout.addWidget(self.player_label)
        layout.addWidget(self.ai_label)

        # Area for cards
        self.card_buttons = []
        self.update_hand()

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_deck(self):
        base_cards = [
            Card("Laser Attack", attack=15, cost=2, description="Fires a piercing laser at the enemy."),
            Card("Shield Upgrade", defense=10, cost=2, description="Deploys a shield to absorb damage."),
            Card("Rocket Attack", attack=25, cost=5, description="Launches a powerful rocket at the opponent that can be blocked by shields."),
            Card("Repair", effect="heal", cost=4, description="Repairs damage to restore 10 health."),
            Card("Full Repair", effect="heal_full", cost=10, description="Fully restores 40 health."),
            Card("Stun", effect="skip_turn", cost=3, description="Stuns the enemy, causing them to skip a turn."),
            Card("Resource Generator", effect="add_resources", cost=2, description="Generates +5⬣ resources."),
            Card("Sabotage Attack", attack=4, cost=2, description="Minor attack that bypasses enemy shields.", piercing=True),
            Card("Intel Gathering", attack=2, cost=1, description="Gathers info while slightly damaging the enemy through shields.", piercing=True),
            # ...add more unique cards as needed...
        ]
        # Increase the deck size more significantly
        deck = base_cards * 8
        random.shuffle(deck)
        return deck

    def update_hand(self):
        # First return any existing cards (except skip card)
        self.player.end_turn(self.deck)
        self.ai_player.end_turn(self.deck)
        
        # Then draw new cards
        self.player.draw_cards(self.deck)
        self.ai_player.draw_cards(self.deck)
        
        # Update the UI
        self.ui.update_hand()
        self.ui.show_cards(True)

    def play_card(self, card):
        # Check if player is stunned at the start of their turn
        if self.player.skip_next_turn:
            self.player.skip_next_turn = False  # Reset stun
            self.ui.status_label.setText("Turn skipped - Stunned!")
            QApplication.processEvents()
            
            # AI gets to play twice when player is stunned
            self.ui.show_waiting_message()
            self.ai_turn()  # First AI turn
            self.ai_turn()  # Second AI turn
            self.update_stats()
            
            # Start new turn
            self.end_turn()
            return

        # Regular turn handling
        self.ui.show_cards(False)

        # Handle skip card
        if card.effect == "skip":
            self.ui.update_last_played(player_card=card)
            self.ai_turn()
            self.end_turn()
            return

        if not self.player.can_play_card(card):
            QMessageBox.warning(self, "Cannot Play Card", 
                              f"Not enough resources! (Cost: {card.cost}, Available: {self.player.resources})")
            self.ui.show_cards(True)  # Show cards again if play was invalid
            return

        # Player plays a card
        self.player.play_card(card, self.ai_player)
        self.ui.update_last_played(player_card=card)
        self.update_stats()

        # Generate narrative for player's action
        player_action = f"Player used {card.name} against AI."
        narrative = self.narrative_ai.generate_narrative(player_action)
        self.ui.update_narrative(narrative)

        # Check for win condition
        winner = self.game.check_winner()
        if winner:
            self.ui.show_game_over(winner)
            return

        # AI's turn
        if not self.ai_player.skip_next_turn:
            self.ai_turn()
        else:
            self.ai_player.skip_next_turn = False

        # End turn and start new one
        self.end_turn()

        # Check for win condition again
        winner = self.game.check_winner()
        if winner:
            self.ui.show_game_over(winner)
            return

        # Don't update hand if player is stunned for next turn
        if not self.player.skip_next_turn:
            self.update_hand()
            self.ui.show_cards(True)
        else:
            self.ui.status_label.setText("You are stunned for next turn!")
            QApplication.processEvents()

    def ai_turn(self):
        # Check if AI is stunned
        if self.ai_player.skip_next_turn:
            self.ai_player.skip_next_turn = False
            self.ui.status_label.setText("AI turn skipped - Stunned!")
            QApplication.processEvents()
            return

        # Prepare game state to send to AI
        game_state = {
            'player_health': self.player.health,
            'ai_health': self.ai_player.health,
            'ai_resources': self.ai_player.resources,
            'ai_hand': [card.to_dict() for card in self.ai_player.hand],
            'deck': self.deck  # needed for draw_cards
        }

        # Show waiting label and process UI events
        self.ui.show_waiting_message()
        QApplication.processEvents()  # Force UI update

        # Make AI move
        ai_card = self.ai_player.decide_move(game_state)

        if ai_card:
            # AI plays a card
            self.ai_player.play_card(ai_card, self.player)
            self.ui.update_last_played(ai_card=ai_card)
            self.update_stats()
            self.alert_window()  # Alert the window when AI responds

            # Generate narrative for AI's action
            ai_action = f"AI used {ai_card.name} against Player."
            narrative = self.narrative_ai.generate_narrative(ai_action)
            self.ui.update_narrative(narrative)
        else:
            # Handle case where AI didn't return a valid move
            print("AI did not play a card.")
            # Optionally, implement logic for AI to skip turn or draw a card
            pass

        # Check for win condition
        winner = self.game.check_winner()
        if winner:
            self.ui.show_game_over(winner)
            return

        # Next turn
        self.update_hand()
        QSound.play("sfx/ai_voice.wav")  # Play sound when AI ends its turn

    def end_turn(self):
        # Return unused cards to the deck
        self.player.end_turn(self.deck)
        self.ai_player.end_turn(self.deck)
        # Shuffle the deck after returning cards
        random.shuffle(self.deck)
        # Start new turn
        self.start_new_turn()

    def start_new_turn(self):
        # Add resources at start of turn
        self.player.resources += 1
        self.ai_player.resources += 1
        
        # Update UI
        self.update_hand()
        self.update_stats()

    def update_stats(self):
        self.ui.update_stats()

    def alert_window(self):
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()