import random
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QWidget, 
                           QHBoxLayout, QGroupBox, QFrame, QProgressBar, QStackedLayout, QTextEdit)
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QPainter, QColor, QPainterPath, QTextOption, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer
from PyQt5.QtMultimedia import QSound

class GameUI:
    def __init__(self, main_window, player, ai_player, narrative_ai):
        # Load custom font
        QFontDatabase.addApplicationFont("fonts/Teko-Regular.ttf")
        self.font_family = "Teko"

        self.main_window = main_window
        self.player = player
        self.ai_player = ai_player
        self.narrative_ai = narrative_ai  # Store this if you need it for narratives

        # Initialize avatars
        self.player_avatar = f"avatars/player_{random.randint(0, 4)}.jpg"
        self.ai_avatar = f"avatars/ai_{random.randint(0, 4)}.jpg"

        # Replace QLabel with QTextEdit for narrative
        self.narrative_text = QTextEdit()
        self.narrative_text.setReadOnly(True)
        self.narrative_text.setStyleSheet(f"""
            QTextEdit {{
                color: white;
                font-size: 16px;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px;
                border-radius: 10px;
                font-family: {self.font_family};
            }}
        """)
        self.narrative_text.setWordWrapMode(QTextOption.WordWrap)

        # Create main container with padding
        main_container = QWidget()
        main_container.setStyleSheet("padding: 20px;")
        
        # Create stacked layout for multiple screens
        self.stacked_layout = QStackedLayout()
        self.layout = QVBoxLayout(main_container)
        
        # Create and add intro layout
        self.intro_widget = self.create_intro_layout()
        self.stacked_layout.addWidget(self.intro_widget)
        
        # Create game layout
        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout(self.game_widget)
        self.create_game_layout()  # Move existing game layout code here
        self.stacked_layout.addWidget(self.game_widget)
        
        # Create game over layout
        self.game_over_widget = self.create_game_over_layout()
        self.stacked_layout.addWidget(self.game_over_widget)
        
        # Add stacked layout to main layout
        self.layout.addLayout(self.stacked_layout)
        
        # Start with intro screen
        self.show_layout('intro')

        # Connect the start button after it's defined
        self.start_btn.clicked.connect(self.start_game)

        # Set layout
        self.main_window.setCentralWidget(main_container)
        
        # After both defense labels are created
        self.update_resource_display()  # Move this call here
        self.update_defense_display()  # Move call here, after both labels exist

    def create_intro_layout(self):
        intro_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("genMaczek")
        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                font-family: {self.font_family};
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Story introduction
        story_label = QLabel("Welcome, General! Your strategic prowess will be tested in this epic battle. Lead your forces to victory and outsmart your opponent!")
        story_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 18px;
                padding: 10px;
                font-family: {self.font_family};
            }}
        """)
        story_label.setAlignment(Qt.AlignCenter)
        story_label.setWordWrap(True)
        layout.addWidget(story_label)

        # Start button
        self.start_btn = QPushButton("Start Game")
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 200, 0, 150);
                color: white;
                border: 2px solid white;
                border-radius: 10px;
                padding: 15px;
                font-size: 24px;
                font-weight: bold;
                font-family: {self.font_family};
            }}
            QPushButton:hover {{
                background-color: rgba(0, 255, 0, 200);
            }}
        """)
        self.start_btn.setFixedWidth(200)
        self.start_btn.clicked.connect(lambda: self.show_layout('game'))
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)
        
        intro_widget.setLayout(layout)
        return intro_widget

    def create_game_over_layout(self):
        game_over_widget = QWidget()
        layout = QVBoxLayout()
        
        self.result_label = QLabel()
        self.result_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 36px;
                font-weight: bold;
                padding: 20px;
                font-family: {self.font_family};
            }}
        """)
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(200, 0, 0, 150);
                color: white;
                border: 2px solid white;
                border-radius: 10px;
                padding: 15px;
                font-size: 24px;
                font-weight: bold;
                font-family: {self.font_family};
            }}
            QPushButton:hover {{
                background-color: rgba(255, 0, 0, 200);
            }}
        """)
        quit_btn.setFixedWidth(200)
        quit_btn.clicked.connect(self.main_window.close)
        layout.addWidget(quit_btn, alignment=Qt.AlignCenter)
        
        game_over_widget.setLayout(layout)
        return game_over_widget

    def show_layout(self, layout_name):
        if layout_name == 'intro':
            self.stacked_layout.setCurrentIndex(0)
        elif layout_name == 'game':
            QSound.play("sfx/click.wav")
            self.stacked_layout.setCurrentIndex(1)
        elif layout_name == 'game_over':
            self.stacked_layout.setCurrentIndex(2)

    def show_game_over(self, winner):
        if winner == self.player.name:
            self.result_label.setText("Victory!")
            self.result_label.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    font-size: 36px;
                    font-weight: bold;
                    padding: 20px;
                }
            """)
        else:
            self.result_label.setText("Defeat!")
            self.result_label.setStyleSheet("""
                QLabel {
                    color: #ff0000;
                    font-size: 36px;
                    font-weight: bold;
                    padding: 20px;
                }
            """)
        self.show_layout('game_over')

    def create_game_layout(self):
        # Set background image
        palette = self.main_window.palette()
        bg_image = QPixmap("bg.jpg")
        # bg_image = bg_image.scaled(main_window.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(bg_image))
        self.main_window.setPalette(palette)
        self.main_window.setAutoFillBackground(True)

        # Create top stats bar with player and AI info
        top_bar = QHBoxLayout()
        
        # Player stats group (left side)
        player_group = QGroupBox("● PLAYER")
        player_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: rgba(0, 100, 200, 150);
                border-radius: 10px;
                padding: 20px 10px 10px 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: {self.font_family};
            }}
        """)
        player_layout = QVBoxLayout()

        # Create a horizontal layout for avatar and stats
        avatar_stats_layout = QHBoxLayout()

        # Add avatar to the left
        avatar_stats_layout.addWidget(self.create_avatar(self.player_avatar))

        # Create a vertical layout for stats
        stats_layout = QVBoxLayout()

        # Define styles for stats labels with consistent width
        stats_label_style = f"""
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: 14px;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 5px;
                padding: 5px;
                font-family: {self.font_family};
            }}
        """

        # Define player defense label
        self.player_defense_label = QLabel()
        self.player_defense_label.setStyleSheet(stats_label_style)
        stats_layout.addWidget(self.player_defense_label)

        # Define player resource label
        self.resource_label = QLabel()
        self.resource_label.setStyleSheet(stats_label_style)
        stats_layout.addWidget(self.resource_label)

        # Add stats layout to the right side of the horizontal layout
        avatar_stats_layout.addLayout(stats_layout)

        # Add the horizontal layout to the main player layout
        player_layout.addLayout(avatar_stats_layout)

        # Define last played card label
        self.player_last_card = QLabel("Last played: None")
        last_played_style = f"""
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: 12px;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 3px;
                padding: 3px;
                margin: 0px;
                font-family: {self.font_family};
            }}
        """
        self.player_last_card.setStyleSheet(last_played_style)
        player_layout.addWidget(self.player_last_card)

        # Define player health bar
        self.player_health_bar = QProgressBar()
        self.player_health_bar.setMaximum(100)
        self.player_health_bar.setValue(self.player.health)
        self.player_health_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                text-align: center;
                background-color: rgba(0, 0, 0, 100);
            }
            QProgressBar::chunk {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        player_layout.addWidget(self.player_health_bar)

        player_group.setLayout(player_layout)
        top_bar.addWidget(player_group)

        # Center status section
        center_group = QGroupBox("DECK STATUS")  # Added container with title
        center_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: rgba(50, 50, 50, 150);
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: {self.font_family};
            }}
        """)
        center_status = QVBoxLayout()
        
        # Deck label as header
        deck_header = QLabel("CARDS REMAINING")
        deck_header.setStyleSheet(f"""
            QLabel {{
                color: white;
                padding: 5px;
                font-weight: bold;
                font-size: 14px;
                font-family: {self.font_family};
            }}
        """)
        deck_header.setAlignment(Qt.AlignCenter)
        center_status.addWidget(deck_header)
        
        # Cards remaining count
        self.cards_remaining_label = QLabel(f"{len(self.main_window.deck)}")
        self.cards_remaining_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: rgba(0, 0, 0, 100);
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 32px;
                font-family: {self.font_family};
            }}
        """)
        self.cards_remaining_label.setAlignment(Qt.AlignCenter)
        center_status.addWidget(self.cards_remaining_label)
        
        # Status label with consistent styling
        self.status_label = QLabel("Your turn")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: rgba(0, 0, 0, 100);
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                font-family: {self.font_family};
            }}
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        center_status.addWidget(self.status_label)
        
        center_status.setAlignment(Qt.AlignCenter)
        center_group.setLayout(center_status)  # Add layout to group
        top_bar.addWidget(center_group)       # Add group to top bar

        # AI stats group (right side)
        ai_group = QGroupBox("▶ AI OPPONENT")
        ai_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: rgba(200, 50, 50, 150);
                border-radius: 10px;
                padding: 20px 10px 10px 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: {self.font_family};
            }}
        """)
        ai_layout = QVBoxLayout()

        # Create a horizontal layout for avatar and stats
        ai_avatar_stats_layout = QHBoxLayout()

        # Add avatar to the left
        ai_avatar_stats_layout.addWidget(self.create_avatar(self.ai_avatar))

        # Create a vertical layout for stats
        ai_stats_layout = QVBoxLayout()

        # Add AI defense label
        self.ai_defense_label = QLabel()
        self.ai_defense_label.setStyleSheet(stats_label_style)
        ai_stats_layout.addWidget(self.ai_defense_label)

        # AI resource label
        self.ai_resource_label = QLabel()
        self.ai_resource_label.setStyleSheet(stats_label_style)
        ai_stats_layout.addWidget(self.ai_resource_label)

        # Add stats layout to the horizontal layout
        ai_avatar_stats_layout.addLayout(ai_stats_layout)

        # Add the horizontal layout to the main AI layout
        ai_layout.addLayout(ai_avatar_stats_layout)

        # Add last played card label
        self.ai_last_card = QLabel("Last played: None")
        self.ai_last_card.setStyleSheet(last_played_style)
        ai_layout.addWidget(self.ai_last_card)

        # Add AI health bar
        self.ai_health_bar = QProgressBar()
        self.ai_health_bar.setMaximum(100)
        self.ai_health_bar.setValue(self.ai_player.health)
        self.ai_health_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                text-align: center;
                background-color: rgba(0, 0, 0, 100);
            }
            QProgressBar::chunk {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        ai_layout.addWidget(self.ai_health_bar)
        
        ai_group.setLayout(ai_layout)
        top_bar.addWidget(ai_group)

        # Create a widget for the game area (everything except footer)
        game_area = QWidget()
        game_layout = QVBoxLayout(game_area)
        game_layout.addLayout(top_bar)
        
        # Initialize card buttons list before creating containers
        self.card_buttons = []
        
        # Create cards container with explicit size policy
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.cards_container.setMinimumHeight(170)  # Give it minimum height
        game_layout.addWidget(self.cards_container)
        
        # Initial update of the hand to show cards
        self.update_hand()
        
        # Add waiting label
        self.waiting_label = QLabel("Waiting for AI move...")
        self.waiting_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 20px;
                border-radius: 15px;
                font-weight: bold;
                font-family: {self.font_family};
            }}
        """)
        self.waiting_label.setAlignment(Qt.AlignCenter)
        self.waiting_label.hide()
        game_layout.addWidget(self.waiting_label)
        
        # Add game area to main layout with stretch
        self.game_layout.addWidget(game_area, stretch=1)
        
        self.game_layout.addWidget(self.narrative_text)

        # Add footer (will stay at bottom)
        footer = QLabel("Produced by Krzysztof Krystian Jankowski, © 2024. Powered by IBM Granite 3.0")
        footer.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
                font-family: {self.font_family};
            }}
        """)
        footer.setAlignment(Qt.AlignCenter)
        self.game_layout.addWidget(footer)

    def create_avatar(self, image_path, size=128):
        def create_circular_pixmap(pixmap, size):
            # Create circular mask
            rounded = QPixmap(size, size)
            rounded.fill(QColor("transparent"))
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create circular path
            path = QPainterPath()
            path.addEllipse(QRectF(0, 0, size, size))
            painter.setClipPath(path)
            
            # Draw the scaled image
            scaled_pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Center the image if it's not square
            x = (size - scaled_pixmap.width()) // 2
            y = (size - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            return rounded

        avatar_frame = QFrame()
        avatar_frame.setFixedSize(size, size)
        avatar_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 64px;
                padding: 5px;
            }
        """)
        
        avatar_label = QLabel(avatar_frame)
        pixmap = QPixmap(image_path)
        # Create circular avatar
        circular_pixmap = create_circular_pixmap(pixmap, size-10)
        avatar_label.setPixmap(circular_pixmap)
        avatar_label.setAlignment(Qt.AlignCenter)
        
        return avatar_frame

    def update_resource_display(self):
        self.resource_label.setText(f"⬣ {self.player.resources}")
        self.ai_resource_label.setText(f"⬣ {self.ai_player.resources}")

    def update_deck_count(self, count):
        """Update the deck count display"""
        self.cards_remaining_label.setText(str(count))
        # Add some visual feedback
        self.cards_remaining_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: rgba(0, 0, 0, 100);
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 32px;
                border: 2px solid rgba(255, 255, 255, 150);
                font-family: {self.font_family};
            }}
        """)
        # Reset style after brief delay
        QTimer.singleShot(200, lambda: self.cards_remaining_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: rgba(0, 0, 0, 100);
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 32px;
                font-family: {self.font_family};
            }}
        """))

    def update_hand(self):
        # Clear existing buttons and layout
        self.card_buttons = []
        
        # Clear previous layout
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add new card buttons
        for card in self.player.hand:
            card_widget = self.create_card_widget(card)
            self.card_buttons.append(card_widget)
            self.cards_layout.addWidget(card_widget)

        # Update deck count
        self.update_deck_count(len(self.main_window.deck))  # Add this line

    def create_card_widget(self, card):
        # Create container widget for the card
        card_widget = QWidget()
        card_widget.setFixedSize(150, 200)
        card_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 200);
                border-radius: 6px;
                padding: 0;
            }
            QWidget:hover {
                background-color: rgba(0, 0, 240, 200);
            }
        """)

        # Create main layout for the card widget
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Create a container for the image and cost label
        image_container = QWidget()
        image_container.setFixedSize(150, 150)
        image_container.setStyleSheet("background: transparent;")

        # Use a stacked layout to overlay the cost icon on the image
        stacked_layout = QStackedLayout(image_container)
        stacked_layout.setContentsMargins(0, 0, 0, 0)
        stacked_layout.setStackingMode(QStackedLayout.StackAll)

        # Image label
        image_label = QLabel()
        pixmap = QPixmap(card.image_path)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        # Cost icon label
        cost_label = QLabel(f"⬣ {card.cost}")
        cost_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: white;
                background-color: black;
                padding: 4px;
                border-radius: 3px;
                font-family: {self.font_family};
            }}
        """)
        cost_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        cost_label.setFixedSize(50, 30)

        # Add widgets to stacked layout - reversed order
        stacked_layout.addWidget(cost_label)  # Add cost label first
        stacked_layout.addWidget(image_label) # Add image label second

        # Add image container to card layout
        card_layout.addWidget(image_container)

        # Name label
        name_label = QLabel(card.name)
        name_label.setAlignment(Qt.AlignCenter)

        # Name label
        name_label = QLabel(card.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 12px;
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 2px;
                font-family: {self.font_family};
            }}
        """)

        # Description label
        description_label = QLabel(card.description)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 4px;
                font-family: {self.font_family};
            }}
        """)
        description_label.setFixedHeight(40)

        # Add labels to card layout
        card_layout.addWidget(name_label)
        card_layout.addWidget(description_label)

        # Make the whole card clickable
        card_widget.mousePressEvent = lambda e, c=card: self.main_window.play_card(c)

        return card_widget

    def update_stats(self):
        # Update health bars
        self.player_health_bar.setValue(self.player.health)
        self.ai_health_bar.setValue(self.ai_player.health)
        # Update resources with emoji icons
        self.update_resource_display()
        self.update_defense_display()  # Add this line
        self.ai_defense_label.setText(f"🛡️ {self.ai_player.defense}")

    def show_waiting_message(self):
        self.waiting_label.setVisible(True)
        self.status_label.setText("AI is thinking...")
        for btn in self.card_buttons:
            btn.setVisible(False)

    def show_cards(self, visible=True):
        self.status_label.setText("Your turn!")
        for btn in self.card_buttons:
            btn.setVisible(visible)
        self.cards_container.setVisible(visible)
        self.waiting_label.setVisible(not visible)

    def update_last_played(self, player_card=None, ai_card=None):
        if player_card:
            self.player_last_card.setText(f"Last played: {player_card.name}")
        if ai_card:
            self.ai_last_card.setText(f"Last played: {ai_card.name}")

    def update_defense_display(self):
        self.player_defense_label.setText(f"🛡️ {self.player.defense}")
        self.ai_defense_label.setText(f"🛡️ {self.ai_player.defense}")

    def update_narrative(self, text):
        # Append new narrative to the text box
        self.narrative_text.append(text)

    def start_game(self):
        self.show_layout('game')
        # Introduction is now handled asynchronously
        # The introduction text will appear once ready
