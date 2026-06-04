# Monopoly

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
ID  | Space Name                          | Group        | Total Visits | Landed %  
-------------------------------------------------------------------------------------
10  | Just Visiting / Jail       | SPECIAL      | 6,311        | 5.43%
17  | Community Chest            | SPECIAL      | 5,673        | 4.88%
33  | Community Chest            | SPECIAL      | 5,226        | 4.49%
01  | GO                         | SPECIAL      | 4,077        | 3.51%
22  | Chance                     | SPECIAL      | 4,058        | 3.49%
02  | Community Chest            | SPECIAL      | 3,859        | 3.32%
07  | Chance                     | SPECIAL      | 3,561        | 3.06%
36  | Chance                     | SPECIAL      | 3,525        | 3.03%
24  | Illinois Avenue            | RED          | 3,178        | 2.73%
19  | New York Avenue                | ORANGE       | 3,130        | 2.69%
25  | B. & O. Railroad               | RAILROAD     | 3,083        | 2.65%
16  | St. James Place                | ORANGE       | 2,894        | 2.49%
28  | Water Works                    | UTILITY      | 2,879        | 2.48%
15  | Pennsylvania Railroad          | RAILROAD     | 2,864        | 2.46%
21  | Kentucky Avenue            | RED          | 2,852        | 2.45%
18  | Tennessee Avenue               | ORANGE       | 2,851        | 2.45%
20  | Free Parking               | SPECIAL      | 2,783        | 2.39%
26  | Atlantic Avenue            | YELLOW       | 2,717        | 2.34%
31  | Pacific Avenue             | GREEN        | 2,710        | 2.33%
11  | St. Charles Place          | PINK         | 2,703        | 2.32%
23  | Indiana Avenue             | RED          | 2,691        | 2.31%
12  | Electric Company               | UTILITY      | 2,624        | 2.26%
32  | North Carolina Avenue      | GREEN        | 2,597        | 2.23%
29  | Marvin Gardens             | YELLOW       | 2,582        | 2.22%
27  | Ventnor Avenue             | YELLOW       | 2,580        | 2.22%
05  | Reading Railroad               | RAILROAD     | 2,539        | 2.18%
34  | Pennsylvania Avenue        | GREEN        | 2,469        | 2.12%
13  | States Avenue              | PINK         | 2,410        | 2.07%
14  | Virginia Avenue            | PINK         | 2,405        | 2.07%
08  | Vermont Avenue             | LIGHT_BLUE   | 2,398        | 2.06%
35  | Short Line Railroad            | RAILROAD     | 2,331        | 2.00%
09  | Connecticut Avenue         | LIGHT_BLUE   | 2,323        | 2.00%
04  | Income Tax                 | SPECIAL      | 2,293        | 1.97%
06  | Oriental Avenue            | LIGHT_BLUE   | 2,245        | 1.93%
38  | Luxury Tax                 | SPECIAL      | 2,217        | 1.91%
37  | Park Place                 | DARK_BLUE    | 2,184        | 1.88%
39  | Boardwalk                  | DARK_BLUE    | 2,176        | 1.87%
03  | Mediterranean Avenue            | BROWN        | 2,174        | 1.87%
40  | Boardwalk                  | DARK_BLUE    | 2,129        | 1.83%
30  | Go To Jail                 | SPECIAL      | 0            | 0.00%
