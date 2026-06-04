# Monopoly AI Simulation Engine 🎩🎲

This project is a complete, Object-Oriented Programming (OOP) version of a Monopoly simulation. It is structured as a professional, maintainable software package that functions as a true Multi-Agent AI Simulator. It models advanced tournament rules, competitive economic pressure, and spatial probabilities to generate highly accurate gameplay analytics.

## ✨ Features

* **Multi-Agent AI Strategies:** Utilizes a Strategy Design Pattern to define different behavioral profiles, allowing you to pit Aggressive, Conservative, and Balanced AI profiles against each other.
* **Advanced Economic Engine:** Features property costs, multi-tiered rent structures based on houses and hotels, and exclusive ownership mechanisms. 
* **Dynamic Bankruptcies & Liquidation:** Simulates financial health where bankruptcies to a player transfer all physical assets instantly to the creditor, while bankruptcies to the Bank release properties back to the market.
* **Tournament-Accurate Mechanics:** Enforces the "Three Doubles" speeding penalty, precise board wrapping (spaces 1-40), and proper Jail interception vectors.
* **Card Decks:** Models standard 16-card stacks for Chance and Community Chest, processing teleportation paths, chain reactions, and financial penalties.
* **Statistical Heatmaps:** Runs massive nested loops to register spatial collisions to a frequency counter, generating probability heatmaps of standard game durations.

## 🗂️ File Architecture

The project enforces true separation of concerns, allowing you to update the UI or the economy independently without breaking the core game loop.

* `main.py` — Instantiates the execution loop with specified macro-parameters (such as AI strategies and total games) and acts as the simple terminal entry point.
* `simulation.py` — The programmatic core orchestrating independent matches, nested step execution loops, and tracking statistical aggregates.
* `bank.py` — The isolated economic engine, managing Vickrey auctions, liquidations, global housing supply shortages, and property deeds.
* `renderer.py` — Takes over all terminal outputs, live visual mapping, and statistical formatting.
* `player.py` — Encapsulates the financial health, location profile, and strategy bindings of an active entity.
* `strategy.py` — Defines the behavioral risk profiles and auction bidding limits for the players.
* `board.py` — Houses static immutable system constraints defining structural dimensions, ANSI color codes, and multi-tiered pricing matrices.
* `deck.py` — Models standard 16-card stacks and automatically recycles exhausted cards to the bottom of the deck (including Get Out of Jail Free tracking).
* `dice.py` — Manages pseudo-random number generation and maintains internal localized state variables to track consecutive double sequences.

## 🚀 How to Install & Run

1. Clone or download all script files into a clean directory on your workspace.
2. Ensure all files reside within the exact same folder structure level.
3. Open up a terminal CLI shell, navigate directly to that working path directory, and execute the initialization script utilizing your Python 3.x interpreter:

```bash
python main.py