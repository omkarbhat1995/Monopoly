from simulation import MonopolySimulation
from strategy import AGGRESSIVE_STRATEGY, BALANCED_STRATEGY, CONSERVATIVE_STRATEGY

if __name__ == "__main__":
    # Define the matchup! Let's pit 2 Aggressive players against 1 Conservative and 1 Balanced.
    matchup_strategies = [
        AGGRESSIVE_STRATEGY,  # Player 1
        AGGRESSIVE_STRATEGY,  # Player 2
        CONSERVATIVE_STRATEGY, # Player 3
        BALANCED_STRATEGY      # Player 4
    ]

    # Set debug_mode=False and total_games=1000 to see who survives statistically on average
    sim = MonopolySimulation(
        total_games=1_000, 
        steps_per_game=100, 
        debug_mode=False, 
        strategies=matchup_strategies
    )
    sim.run()