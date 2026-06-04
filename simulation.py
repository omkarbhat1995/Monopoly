from collections import Counter
from dice import Dice
from board import Board

class MonopolySimulation:
    """Runs the simulation engine and aggregates telemetry data."""
    
    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_position = 1
        self.dice = Dice()
        
        # Initialize heat-map metrics for spaces 1-40
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.visited_tracking[self.current_position] += 1

    def run(self) -> None:
        """Executes the complete core simulation cycle."""
        print(f"Starting the game at position: {self.current_position}\n" + "-" * 65)

        for step in range(1, self.total_steps + 1):
            die1, die2, dice_total, is_double = self.dice.roll()
            
            log_msg = f"Step {step:03d}: Rolled {die1}+{die2}={dice_total:02d}"
            if is_double:
                log_msg += f" (Double #{self.dice.consecutive_doubles})"

            # Rule: 3 consecutive doubles triggers a Speeding Violation
            if self.dice.has_speeded:
                old_pos = self.current_position
                self.current_position = Board.JAIL
                self.dice.reset_doubles()
                self.visited_tracking[self.current_position] += 1
                
                print(f"{log_msg} | Speeding! 3 consecutive doubles. Sent to JAIL from {old_pos:02d} -> {self.current_position:02d}")
                continue

            # Compute standard physics movement execution
            new_position = Board.wrap_position(self.current_position + dice_total)
            jail_msg = ""

            # Check if lander space is the 'Go to Jail' interceptor pad
            if new_position == Board.GO_TO_JAIL:
                new_position = Board.JAIL
                jail_msg = " -> Caught! Sent to JAIL"

            log_msg += f" | Moved {self.current_position:02d} -> {new_position:02d}{jail_msg}"
            print(log_msg)

            self.current_position = new_position
            self.visited_tracking[self.current_position] += 1

        self._print_summary()

    def _print_summary(self) -> None:
        """Outputs statistical tracking analysis data."""
        print("\n" + "=" * 17 + " MOST VISITED PLACES " + "=" * 17)
        print("Space | Visits")
        print("-------|--------")
        
        # Sort values descending based on landed-on metric counts
        sorted_visits = sorted(self.visited_tracking.items(), key=lambda item: item[1], reverse=True)
        
        for space, visits in sorted_visits:
            special_label = Board.get_special_label(space)
            print(f"Space {space:02d}{special_label:<13} | {visits} times")