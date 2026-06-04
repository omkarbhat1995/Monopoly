# Monopoly Simulation Engine 🎩🎲

A professional-grade, strictly objective, mathematical simulation engine for Monopoly. This project runs lightning-fast batch simulations of Monopoly matches to gather telemetry on landing probabilities, and it provides a real-time, terminal-based visual dashboard for single games.

It natively enforces **advanced tournament rules** that are often overlooked in casual play, modeling the exact economic chokeholds that win real-world championships.

## Features & Tournament Rules Implemented

* **Vickrey Property Auctions:** When a player lands on unowned land but cannot afford it (or refuses to buy to save cash), it instantly triggers a background AI auction where players calculate their max valuations and snipe the property.
* **Global Housing Supply Shortages:** Accurately restricts the game economy to the physical 32 Houses and 12 Hotels included in a real box. Players can (and will) hoard low-level housing to strategically choke their opponents from building.
* **Even Building Rules:** Structurally restricts real estate development; houses must be built symmetrically across color blocks.
* **Financial Distress & Asset Liquidation:** If a player goes broke, they aren't instantly dead. They systematically sell off houses at 50% value and mortgage their empty land to pay the landlord. 
* **Bankruptcy Seizures:** Bankruptcies to a player transfer all physical assets (and debt!) instantly to the creditor, creating massive late-game mega-landlords. Bankruptcies to the Bank release the properties back to the wild.
* **True Rent Physics:** Rent scales dynamically based on unimproved monopolies (2x), house/hotel tiers, railroad counts, and active dice multiplier dependencies for Utilities.
* **Live ASCII Output:** Watch games play out natively in the terminal with a real-time tracking map, property portfolio summaries, and color-coded event feeds.

---

## File Structure & Architecture

The architecture is aggressively decoupled using Object-Oriented Programming (OOP) paradigms to ensure logic remains localized and highly readable.

* `main.py`: The application entry point. Used to toggle between live Visual Debug Mode and mass Background Batch Mode.
* `board.py`: Houses the core Spatial Data. Maps out the 40 tiles, assigns ANSI color codes, and stores the multi-tiered rent and pricing arrays.
* `deck.py`: Manages the physical layout and shuffling of Chance and Community Chest cards. Simulates the single exact inventory of the real game (including extracting "Get Out of Jail Free" cards from circulation).
* `dice.py`: Simulates dual 6-sided dice logic, including 3-consecutive double arrests.
* `player.py`: Tracks an agent's individual state (cash, physical location, property inventories, jail states, and held asset cards).
* `simulation.py`: The heart of the program. Divided into three subsystems:
    1.  **`GameRenderer`**: Handles all visual console feedback and heatmap metrics.
    2.  **`CentralBank`**: Enforces strict economic boundaries, processes auctions, and processes liquidations.
    3.  **`MonopolySimulation`**: Orchestrates the round loops and coordinates game state handoffs.

---

## How to Run

1. Ensure you have Python 3.9+ installed. (No external pip libraries are required!)
2. Open your terminal in the project directory.
3. Run the script:
   ```bash
   python main.py


## Toggle Run Modes
Inside main.py, you can alter the simulation behavior via the constructor:

To watch a live single game unfold: Set debug_mode=True.

To run a 1,000-game statistical batch processor:
Set debug_mode=False. It will disable printing, run the loop natively, and dump the aggregated financial averages and Board Heatmaps at the end.