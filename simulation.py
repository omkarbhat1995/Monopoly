from collections import Counter
from dice import Dice
from board import Board

class MonopolySimulation:
    """Runs a batch simulation of independent games and aggregates telemetry data."""
    def __init__(self, total_games: int = 1_000_000, steps_per_game: int = 100):
        self.total_games = total_games
        self.steps_per_game = steps_per_game
        self.dice = Dice()
        
        # Initialize heat-map metrics for spaces 1-40
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0

    def run(self) -> None:
        """Executes 1 million independent games of 100 steps each."""
        for _ in range(self.total_games):
            # Reset player state back to GO for a brand new game
            current_position = 1
            self.dice.reset_doubles()
            
            # Record the initial game setup state
            self.visited_tracking[current_position] += 1
            self.total_positions_logged += 1

            # Run a standalone 100-step match
            for _ in range(self.steps_per_game):
                dice_total, is_double = self.dice.roll()

                # Rule 1: 3 consecutive doubles triggers a Speeding Violation
                if self.dice.consecutive_doubles == 3:
                    current_position = Board.JAIL
                    self.dice.reset_doubles()
                    self.visited_tracking[current_position] += 1
                    self.total_positions_logged += 1
                    continue

                # Rule 2: Compute standard physical movement execution
                new_position = Board.wrap_position(current_position + dice_total)

                # Rule 3: Check if landing space is the 'Go to Jail' space
                if new_position == Board.GO_TO_JAIL:
                    new_position = Board.JAIL

                current_position = new_position
                self.visited_tracking[current_position] += 1
                self.total_positions_logged += 1

        self._print_summary()

    def _print_summary(self) -> None:
        """Outputs statistical tracking analysis data based on total landings."""
        print(f"--- SIMULATION COMPLETE ({self.total_games:,} GAMES x {self.steps_per_game} STEPS) ---")
        print(f"{'Space':<18} | {'Total Visits':<15} | {'Landed %':<10}")
        print("-" * 50)
        
        # Sort values descending based on landed-on metric counts
        sorted_visits = sorted(self.visited_tracking.items(), key=lambda item: item[1], reverse=True)
        
        # Display the percentage breakdown
        for space, visits in sorted_visits:
            label = f"Space {space:02d}{Board.get_special_label(space)}"
            percentage = (visits / self.total_positions_logged) * 100
            print(f"{label:<18} | {visits:<15,} | {percentage:.2f}%")