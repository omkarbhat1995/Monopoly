from simulation import MonopolySimulation

if __name__ == "__main__":
    # Runs 1,000,000 independent games. Each game lasts exactly 100 turns.
    sim = MonopolySimulation(total_games=1_000, steps_per_game=100)
    sim.run()