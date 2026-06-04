from simulation import MonopolySimulation

if __name__ == "__main__":
    # Configure total simulation cycle turn length here
    sim = MonopolySimulation(total_steps=100)
    sim.run()