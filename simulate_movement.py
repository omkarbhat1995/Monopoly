import random

def simulate_monopoly_movement(total_turns=100):
    # Board setup: Start at GO (space 1)
    current_position = 1
    visited_places = [current_position]  # Track every visited position
    consecutive_doubles = 0  # Track consecutive doubles rolled
    
    print(f"Starting position: {current_position}\n")
    
    for turn in range(1, total_turns + 1):
        # Roll two 6-sided dice
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        roll_total = die1 + die2
        
        # Check for doubles
        if die1 == die2:
            consecutive_doubles += 1
            double_text = f" (Double #{consecutive_doubles}!)"
        else:
            consecutive_doubles = 0  # Reset if a non-double is rolled
            double_text = ""
            
        print(f"Turn {turn}: Rolled {die1} + {die2} = {roll_total}{double_text}")
        
        # Rule: 3 consecutive doubles sends you straight to jail
        if consecutive_doubles == 3:
            current_position = 10  # Teleport to Jail
            consecutive_doubles = 0  # Reset doubles tracker
            visited_places.append(current_position)  # Record jail visit
            print(f"  ❌ Rolled doubles 3 times! Sent straight to Jail (10).")
            print(f"  Current Position: {current_position}\n")
            continue  # End this turn immediately
            
        # Normal movement logic
        current_position += roll_total
        
        # Board wrapping: Keep within 1 to 40 range
        if current_position > 40:
            current_position -= 40
            
        # Check for landing on "Go to Jail" space (30)
        if current_position == 30:
            current_position = 10  # Teleport to Jail
            print(f"  👮 Landed on Go to Jail (30)! Teleported to Jail (10).")
            
        # Record the final position of this turn
        visited_places.append(current_position)
        print(f"  Current Position: {current_position}\n")
        
    return visited_places

# Run the simulation for 100 turns
history = simulate_monopoly_movement(100)

# Display summary results
print("--- SIMULATION COMPLETE ---")
print(f"Total positions recorded: {len(history)}")
print(f"Full history log: {history}")