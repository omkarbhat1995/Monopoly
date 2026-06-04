from simulation import MonopolySimulation

if __name__ == "__main__":
    # TOGGLE MODE HERE:
    # Set debug_mode=True to look at a single game play out live.
    # Set debug_mode=False to high-speed simulate 1,000 statistical batch games.
    sim = MonopolySimulation(total_games=1_000, steps_per_game=40, debug_mode=True)
    sim.run()