from simulation import MonopolySimulation

if __name__ == "__main__":
    # Runs the advanced batch routine simulation matrix
    sim = MonopolySimulation(total_games=1_000, steps_per_game=100)
    sim.run()