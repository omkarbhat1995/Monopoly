import random

def simulate_monopoly_movement(steps=100):
    # Board setup
    current_position = 1  # Starting at GO (1)
    JAIL = 10
    GO_TO_JAIL = 30
    BOARD_SIZE = 40
    
    print(f"Starting simulation at position {current_position}\n")
    
    for step in range(1, steps + 1):
        # Roll two 6-sided dice
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total_roll = die1 + die2
        
        # Move the piece
        current_position += total_roll
        
        # Handle board wrapping (modulo logic for 1-40 indexing)
        if current_position > BOARD_SIZE:
            current_position = current_position - BOARD_SIZE
            
        print(f"Step {step:03d}: Rolled {die1} + {die2} = {total_roll}. Moved to {current_position}")
        
        # Check for "Go to Jail" space
        if current_position == GO_TO_JAIL:
            current_position = JAIL
            print(f"🚨 Landed on GO TO JAIL ({GO_TO_JAIL})! Teleported to JAIL ({JAIL}).")
            
    print(f"\nSimulation complete. Final position: {current_position}")

# Run the simulation
simulate_monopoly_movement(100)