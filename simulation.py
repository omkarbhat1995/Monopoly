from collections import Counter
from dice import Dice
from board import Board
from deck import Deck
from player import Player

class MonopolySimulation:
    """Runs a batch simulation of independent games and aggregates telemetry data."""
    
    def __init__(self, total_games: int = 1_000, steps_per_game: int = 100):
        self.total_games = total_games
        self.steps_per_game = steps_per_game
        self.dice = Dice()
        self.player = Player()
        
        # Instantiate localized card decks
        self.chance_deck = Deck("chance")
        self.com_chest_deck = Deck("community_chest")
        
        # Initialize heat-map metrics for spaces 1-40
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0

    def run(self) -> None:
        """Executes the complete batch simulation across all scheduled games."""
        for _ in range(self.total_games):
            # Reset player and dice for a clean, standalone run
            self.player.reset_for_new_game()
            self.dice.reset_doubles()
            
            # Log initialization starting position (Space 1 - GO)
            self.visited_tracking[self.player.position] += 1
            self.total_positions_logged += 1

            for _ in range(self.steps_per_game):
                # Early termination if the player suffers financial insolvency
                if self.player.is_bankrupt:
                    break 
                
                dice_total, is_double = self.dice.roll()

                # Rule 1: Speeding Violation Check (3 consecutive doubles)
                if self.dice.consecutive_doubles == 3:
                    self.player.position = Board.JAIL
                    self.dice.reset_doubles()
                    self.visited_tracking[self.player.position] += 1
                    self.total_positions_logged += 1
                    continue

                # Rule 2: Basic Physical Movement Translation
                raw_new_pos = self.player.position + dice_total
                
                # Financial Flow: Collect $200 if passing GO
                if raw_new_pos > Board.SIZE:
                    self.player.change_cash(200)
                    
                new_position = Board.wrap_position(raw_new_pos)

                # Rule 3: Constant Trajectory Space Checks
                if new_position == Board.GO_TO_JAIL:
                    new_position = Board.JAIL
                
                elif new_position == Board.INCOME_TAX:
                    self.player.change_cash(-200)
                    
                elif new_position == Board.LUXURY_TAX:
                    self.player.change_cash(-100)
                
                # Rule 4: Card Deck Evaluation Interceptors
                elif new_position in Board.CHANCE_SPACES or new_position in Board.COMMUNITY_CHEST_SPACES:
                    # Log the initial landing on the card space itself
                    self.visited_tracking[new_position] += 1
                    self.total_positions_logged += 1
                    
                    # Draw and apply card transformation rules
                    if new_position in Board.CHANCE_SPACES:
                        card = self.chance_deck.draw_card()
                        new_position, forced_jail = self.chance_deck.resolve_card_movement(card, new_position)
                    else:
                        card = self.com_chest_deck.draw_card()
                        new_position, forced_jail = self.com_chest_deck.resolve_card_movement(card, new_position)
                    
                    # Special Case: "Go Back 3 Spaces" from Chance 3 lands on Community Chest 3
                    if card == "GO_BACK_3_SPACES" and new_position == 33:
                        self.visited_tracking[new_position] += 1
                        self.total_positions_logged += 1
                        cc_card = self.com_chest_deck.draw_card()
                        new_position, forced_jail = self.com_chest_deck.resolve_card_movement(cc_card, new_position)

                    if forced_jail:
                        self.dice.reset_doubles()

                # Update position and log final landing step
                self.player.position = new_position
                self.visited_tracking[self.player.position] += 1
                self.total_positions_logged += 1

        self._print_summary()

    def _print_summary(self) -> None:
        """Outputs statistical analytics sorted by color group for property management design."""
        print(f"\n--- SIMULATION COMPLETE ({self.total_games:,} GAMES x {self.steps_per_game} STEPS) ---")
        print(f"{'ID':<3} | {'Space Name':<35} | {'Group':<12} | {'Total Visits':<12} | {'Landed %':<10}")
        print("-" * 85)
        
        # Sort values descending based on landed-on counts
        sorted_visits = sorted(self.visited_tracking.items(), key=lambda item: item[1], reverse=True)
        
        for space, visits in sorted_visits:
            name, group = Board.get_space_info(space)
            colored_name = Board.format_colored_name(space)
            percentage = (visits / self.total_positions_logged) * 100
            
            # Pad the colored name string length to preserve terminal columns over hidden ANSI tags
            ansi_padding = 45 if group in ["BROWN", "ORANGE", "RAILROAD", "UTILITY"] else 35
            
            print(f"{space:02d}  | {colored_name:<{ansi_padding}} | {group:<12} | {visits:<12,} | {percentage:.2f}%")