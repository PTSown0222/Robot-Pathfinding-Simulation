<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=auto&height=200&section=header&text=Robot%20Pathfinding&fontSize=70" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Pygame-ed1c24?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Algorithms-A%20*%20%7C%20Dijkstra%20%7C%20BFS%20%7C%20DFS-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" />
</p>

<p align="center">
  <b>Robot Pathfinding Simulation</b>
</p>

## 🎬 Demo
<p align="center">
  <img src="assets/Demo.gif" width="85%" />
</p>

## ✨ Key Features

### 🗺️ Grid System
- **Dynamic Grid**: Sizes from 10x10 to 30x30 (default 20x20).
- **Two Movement Modes**:
  - **4 Directions**: Up, Down, Left, Right (cost = 1.0).
  - **8 Directions**: Includes the 4 cardinal directions + 4 diagonals (diagonal cost = √2 ≈ 1.414).

### 🎨 Cell Types
- **Normal Cell** (White): Cost = 1 Energy.
- **Wall** (Black): Impassable.
- **Trap/High Cost** (Brown): Cost = 5 Energy.
- **Road/Low Cost** (Light Blue): Cost = 0.5 Energy.
- **Start** (Green): Starting point.
- **End** (Red): Target destination.

### ⚡ Energy Mode vs Simple Mode
- **Energy Mode** (Default):
  - Full feature set including TRAP and ROAD cells.
  - Calculates energy consumption.
  - Automatically adds TRAP/ROAD when switching from Simple Mode.
  
- **Simple Mode**:
  - Binary logic: Only WALL and NORMAL cells (black & white).
  - Hides TRAP/ROAD buttons.
  - Automatically converts TRAP/ROAD to NORMAL when switching modes.

### 🔍 Pathfinding Algorithms
- **BFS** (Breadth-First Search): Finds the shortest path in terms of steps, ignoring weights.
- **DFS** (Depth-First Search): Does not guarantee the shortest path; ignores weights.
- **Dijkstra**: Finds the path with the lowest cost (respects weights).
- **A***: Uses heuristics + cost; optimized for both steps and energy efficiency.

**Automatic Heuristics**:
- 4 Directions: Manhattan Distance
- 8 Directions: Euclidean Distance



### 🎬 Visualization
- **Open Set** (Blue 'O'): Nodes currently being evaluated.
- **Closed Set** (Red 'X'): Nodes already evaluated.
- **Robot Animation**: Animates the robot moving step-by-step along the path.
- **Final Path** (Red Line): The resulting path after the robot completes the movement.

---

## 🚀 Usage & Interface

### Interface Layout
- **Left Side**: Grid map display.
- **Right Side**: Control Panel with settings and options.

### Basic Steps
1. **Configure Settings**: Select **Movement** (4/8 directions) and **Mode** (Energy/Simple).
2. **Create Map**: Click **"Random Map"** or draw manually.
3. **Choose Algorithm**: Select from BFS, DFS, Dijkstra, or A*.
4. **Find Path**: Click the button to start the simulation.
5. **View Statistics**: Real-time display of **Path Length**, **Total Energy**, and **Time Taken**.

---

## 🎮 Controls

### Mouse Interaction
- **Left Click + Drag**: Draw Walls (or selected cell type).
- **Right Click + Drag**: Draw Traps (Energy Mode only).
- **Middle Click + Drag**: Draw Roads (Energy Mode only).
- **Single Click**: Set Start/End positions.

### Keyboard Shortcuts
- **W**: Wall Mode | **T**: Trap Mode | **R**: Road Mode
- **S**: Start Mode | **E**: End Mode | **N**: Normal Mode

### UI Buttons
- **Find Path**: Execute search.
- **Clear Path**: Remove path/animation but keep the map.
- **Reset Grid**: Clear everything.
- **Random Map**: Generate a new solvable level.
- **Skip**: Show final result immediately.
- **Fast**: Speed up animation.

---

## 📊 Algorithm Comparison

### BFS vs Dijkstra
- **BFS**: Focuses on the minimum number of steps. It may be expensive if it traverses through traps.
- **Dijkstra**: Focuses on the lowest energy cost. It will actively avoid traps even if the path is longer.

### A*
- Combines the best of both worlds using heuristics.
- Much faster than Dijkstra because it is "guided" toward the destination.

### 4 Directions vs 8 Directions
- 8 Directions allow for more natural movement and often yield shorter paths due to diagonal shortcuts.

---

## 📁 Technical Structure

### File Overview
- `robot_astar.py`: Core logic (Nodes, Grid, Pathfinding Algorithms).
- `robot_astar_ui.py`: UI implementation using Pygame.

### Key Classes
- **Node**: Represents a cell's state and coordinates.
- **Grid**: Manages the collection of Nodes and neighbours.
- **PathfindingAlgorithms**: The engine for BFS, DFS, Dijkstra, and A*.

---

## 💡 Pro Tips & Troubleshooting

1. **Comparison Test**: Try running BFS on a map full of traps, then run Dijkstra. Notice how Dijkstra "snakes" around traps while BFS goes straight through.
2. **Animation**: BFS expands in a perfect circle/diamond, while A* creates a narrow "beam" toward the target.
3. **No Path Found?**: Ensure there is at least one gap between walls. If stuck, use "Random Map" to guarantee a solution.
4. **Efficiency**: Use "Simple Mode" if you only care about distance and not "Energy" costs.

---

## 📊 Summary Table

| Algorithm | Pros | Cons | Shortest Path? |
| :--- | :--- | :--- | :---: |
| **BFS** | Fewest steps | Slow on large maps | ✅ (Steps) |
| **DFS** | Low memory | Paths are often suboptimal | ❌ |
| **Dijkstra** | Lowest energy cost | Explores in all directions | ✅ (Cost) |
| **A\*** | Fast and efficient | Needs a heuristic function | ✅ (Cost) |

---

## 👨‍💻 Author
**Phuong The Son**

## 📄 License
Educational Project - Free for learning and academic use.




