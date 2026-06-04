# Monopoly

import os

readme_content = """# Monopoly Game Board Simulation (OOP Batch Engine)

An optimized, high-performance Python simulation engine designed to approximate the statistical landing frequencies across a standard 40-space Monopoly board layout. 

Unlike standard infinite-loop Markov chain algorithms, this engine utilizes an object-oriented paradigm to run batch architectures (**1,000,000 independent games consisting of exactly 100 steps each**). By resetting state metrics at the beginning of each game initialization, the simulation accurately maps the true short-duration probability heatmap of normal casual play rather than infinite-horizon asymptotic equilibrium.

---

## Technical Specifications & Features

- **Object-Oriented Architecture (OOP):** Modular file-based architecture adhering strictly to the Single Responsibility Principle (SRP) and strong encapsulation constraints.
- **Batch Simulation Environment:** Implements an outer simulation loop ($N = 1,000,000$) running nested micro-loops ($T = 100$ steps) to observe short-range game trajectories initialized from the default `GO` state.
- **Consecutive Doubles Constraint (Speeding Rule):** Monitored autonomously inside encapsulated dice states. A sequence of 3 consecutive doubles flags a speeding event, truncating active trajectory execution and instantly teleporting the position state to `Jail`.
- **Spatial Coordinate Mapping:** Coordinates are modeled within a modular ring $\mathbb{Z}_{40}$ mapped to $[1, 40]$. Overflows are normalized automatically via modulo-arithmetic operations.
- **Special Landings Interception:** Real-time spatial boundaries continuously poll for specific positions. Landing directly on space `30` (`Go to Jail`) triggers instant positional shifting to space `10` (`Jail`).

---

## File Architecture

The software is modularized into four clear interface boundaries:
├── main.py        # Project entry-point configuring and execution loop trigger.
├── simulation.py  # Central engine orchestrating independent matches and metric tables.
├── board.py       # Spatial physics layer containing ring transformations and naming indices.
└── dice.py        # Independent mechanics controller tracking rolling and consecutive double states.

### 1. `dice.py`
Manages standard pseudo-random number generation for a pair of six-sided dice. It maintains an internal localized state variable tracking consecutive double sequences and provides explicit mutation interfaces to flush streaks during violation triggers or game resets.

### 2. `board.py`
Houses static immutable system constraints defining structural dimensions ($SIZE = 40$), penalty nodes ($GO\_TO\_JAIL = 30$), and landing traps ($JAIL = 10$). Provides class-level algorithmic logic to gracefully handle coordinate mapping wrapping across the circular board boundaries.

### 3. `simulation.py`
The programmatic core containing statistical aggregate tracking. It manages nested step execution loops, registers every space collision to a frequency counter (`collections.Counter`), shifts state pointers during penalty interceptions, and formats percentages against total processed records upon loop termination.

### 4. `main.py`
Instantiates the execution loop with specified macro-parameters (1,000,000 games, 100 turns per game) and acts as the simple terminal entry point.

---

## Algorithmic Execution Workflow
[Main Entry Point] ➔ Triggers Simulation Engine (1,000,000 Runs)
│
├──► For each separate Game (1 to 1,000,000):
│       │
│       ├───► Reset Player Position = 1 (GO)
│       ├───► Reset Consecutive Doubles Streak = 0
│       │
│       └───► Loop Step (1 to 100):
│               │
│               ├──► Roll Dice Pair
│               │     ├── Double?  ➔ Streak += 1
│               │     └── Regular? ➔ Streak = 0
│               │
│               ├──► IF Streak == 3 (Speeding):
│               │     ├── Teleport to Space 10 (Jail)
│               │     ├── Reset Streak = 0
│               │     └── Log Visit ➔ Terminate Step Early
│               │
│               ├──► Else: Move Forward by Dice Sum
│               ├──► Apply Board Wrap Modulo (Keep within 1-40)
│               │
│               ├──► IF Position == Space 30 (Go To Jail):
│               │     └── Teleport to Space 10 (Jail)
│               │
│               └──► Increment Hit Counter for Current Position
│
└─► Generate Frequency Distribution Report & Display Landed % Tables


---

## How to Install & Run

1. Clone or download all four script files (`dice.py`, `board.py`, `simulation.py`, `main.py`) into a clean directory on your workspace. Ensure all files reside within the exact same folder structure level:
   ```bash
   mkdir monopoly-sim && cd monopoly-sim
   # (Populate files inside this directory)
Open a standard CLI shell terminal, navigate directly to that working path directory, and execute the initialization script utilizing Python 3.x interpreter:

Bash
python main.py

Because the engine processes exactly 100 turns across 1,000 independent trials, it registers precisely $101,000$ unique coordinate states (1,000 initial spawn records at space 1, plus 100,000 standard physical steps).Upon completion, a summary statistical tracking breakdown is formatted cleanly within standard text outputs:

--- SIMULATION COMPLETE (1,000 GAMES x 100 STEPS) ---
Space              | Total Visits    | Landed %  
--------------------------------------------------
Space 10 (Jail)    | 5,470           | 5.42%
Space 01 (GO)      | 3,209           | 3.18%
Space 17           | 2,866           | 2.84%
Space 18           | 2,808           | 2.78%
Space 19           | 2,798           | 2.77%
Space 28           | 2,787           | 2.76%
Space 20           | 2,743           | 2.72%
Space 24           | 2,735           | 2.71%
Space 26           | 2,718           | 2.69%
Space 16           | 2,693           | 2.67%
Space 22           | 2,688           | 2.66%
Space 25           | 2,687           | 2.66%
Space 27           | 2,655           | 2.63%
Space 15           | 2,652           | 2.63%
Space 21           | 2,632           | 2.61%
Space 32           | 2,632           | 2.61%
Space 29           | 2,631           | 2.60%
Space 23           | 2,615           | 2.59%
Space 31           | 2,576           | 2.55%
Space 13           | 2,527           | 2.50%
Space 14           | 2,508           | 2.48%
Space 12           | 2,506           | 2.48%
Space 33           | 2,440           | 2.42%
Space 09           | 2,394           | 2.37%
Space 06           | 2,389           | 2.37%
Space 34           | 2,376           | 2.35%
Space 04           | 2,347           | 2.32%
Space 08           | 2,345           | 2.32%
Space 07           | 2,337           | 2.31%
Space 36           | 2,283           | 2.26%
Space 35           | 2,281           | 2.26%
Space 02           | 2,252           | 2.23%
Space 03           | 2,247           | 2.22%
Space 11           | 2,234           | 2.21%
Space 05           | 2,224           | 2.20%
Space 40           | 2,219           | 2.20%
Space 39           | 2,181           | 2.16%
Space 38           | 2,175           | 2.15%
Space 37           | 2,140           | 2.12%
Space 30 (Go To Jail) | 0               | 0.00%