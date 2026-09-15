# Fly-in

A turn-based drone routing simulator in Python that moves drones across a network of zones and connections while respecting capacity limits.

---

## Description

**Fly-in** simulates the movement of `N` drones through a map of landing zones and flight paths from a `start_hub` to an `end_hub`.

The simulation runs in discrete turns, moving drones toward the goal while following a few basic rules:
- **Zone Capacities:** Each zone limits how many drones can stay there at the same time (`max_drones`, default: 1). Start and end hubs have unlimited capacity.
- **Connection Capacities:** Paths limit how many drones can fly through them during the same turn (`max_link_capacity`, default: 1).
- **Zone Types & Movement:**
  - `normal`: Takes 1 turn to cross.
  - `priority`: Takes 1 turn to cross, but preferred by pathfinding.
  - `restricted`: Takes 2 turns to cross (Turn 1: flying on the path, Turn 2: landing).
  - `blocked`: Impassable (drones cannot enter).

---

## Instructions

### Setup & Installation
Install the required development and linting dependencies:
```bash
make install
```

### Running the Simulation
Run using `make run` by specifying the target map file via `file=<filepath>`:
```bash
make run file=maps/easy/01_linear_path.txt
```

Or execute directly with Python:
```bash
python3 __main__.py maps/easy/01_linear_path.txt
```

### Debugging
Run the simulation in Python's interactive debugger (`pdb`):
```bash
make debug file=maps/easy/01_linear_path.txt
```

### Code Quality & Validation
Run static analysis and strict type checking:
```bash
make lint
```

### Cleaning Cache
Remove Python bytecode cache files:
```bash
make clean
```

---

## Algorithm Explanation

### 1. Object-Oriented Design & Graph Models
The simulation uses simple Object-Oriented Programming (OOP) classes that keep the code organized and easy to read:

- **`Zone`**:
  - Represents each zone or landing hub with its coordinates, capacity (`max_drones`), color, and type (`normal`, `priority`, `restricted`, `blocked`).
  - Implements `__repr__` (`Zone(<name>, <type>)`) so printing a zone gives clear, readable information when debugging.

- **`Connection`**:
  - Represents a flight corridor connecting two zones (`zone_a` and `zone_b`) along with its maximum capacity (`max_link_capacity`).
  - Implements `Connection.other(zone)`: given one end of a connection, it automatically returns the zone on the other side (`return self.zone_b if zone == self.zone_a else self.zone_a`). This makes finding neighbors simple and avoids repetitive `if/else` checks throughout the code.
  - Implements `__repr__` (`Connection(<zoneA>-<zoneB>, cap=<cap>)`) for quick inspection in print statements or the `pdb` debugger.

- **`Graph`**:
  - Stores the full map layout and keeps a list of connections linked to each zone.
  - In `Graph.get_neighbors(zone)`, it finds connected zones by asking each connection for its other side using `conn.other(zone)`:
    ```python
    return [(conn.other(zone), conn) for conn in self.adj.get(zone.name, [])]
    ```
    This lets each connection object handle its own endpoints, keeping the graph logic short and straightforward.

- **`Drone`**:
  - Tracks a drone's ID, route, progress (`steps_taken`), and in-flight status (`travelling`).
  - Uses Python `@property` methods to calculate helpful values on demand without storing extra variables:
    - `@property current_zone`: Returns the zone the drone is currently on (`path[steps_taken]`).
    - `@property next_zone`: Peeks ahead at the next zone on the path without crashing if the drone is already at the end.
    - `@property has_arrived`: Checks if the drone has completed its journey (`steps_taken >= len(path) - 1`).
  - Implements `__repr__` (`Drone(<id>, at <zone>)`) to make it easy to follow drone positions during a run.

### 2. Dual-Mode Pathfinding (`pathfinder(weighted: bool)`)
The graph has a flexible pathfinder that chooses the right algorithm depending on what is needed:

- **Unweighted BFS (`weighted=False`, default):**
  - Runs standard Breadth-First Search (BFS) to find the path with the fewest steps.
  - Used when parsing maps to quickly check if a path exists between `start_hub` and `end_hub` without calculating extra weights.

- **Weighted Dijkstra (`weighted=True`):**
  - Uses Dijkstra's algorithm with a priority queue (`heapq`) to find the fastest route based on zone turn costs:
    - `normal`: Cost = `1.0` (1 turn)
    - `restricted`: Cost = `2.0` (2 turns)
    - `priority`: Cost = `0.9` (favored over normal paths with a `-0.1` bonus)
    - `blocked`: Ignored completely
  - Used during the simulation so drones take the fastest possible route.

### 3. Simulation & Conflict Resolution
Each turn of the simulation runs in a few simple steps:
1. **Reset Connections:** Connection counts are cleared at the start of each turn so links can be used again.
2. **Move Front Drones First:** Active drones are sorted by `steps_taken` in reverse order. Drones furthest ahead move first, freeing up room for the drones behind them and preventing traffic jams.
3. **Check Capacity:** A drone only moves if both the destination zone has room (`len(zone.current_drones) < zone.max_drones`) and the connection isn't full (`len(conn.current_drones) < conn.max_link_capacity`).
4. **Restricted Zones (2 Turns):** When a drone enters a `restricted` zone, it takes two turns using the `travelling` state:
   - Turn 1: Enters the link and prints `D<ID>-<zoneA>-<zoneB>`.
   - Turn 2: Lands at the destination and prints `D<ID>-<zoneB>`.

---

## Visual Representation Features

The simulator features ANSI terminal colorization via the `Visualizer` class:
- **Map-Driven Palette:** Maps configure zone colors (e.g. `[color=red]`, `[color=green]`, `[color=blue]`, `[color=yellow]`). Move outputs dynamically display zones in their defined color codes.
- **Readable Turn Logs:** Output format matches the 42 subject specification (`D<ID>-<zone>` or `D<ID>-<conn>`). Stationary drones that cannot move during a turn are omitted to keep output clean and concise.

---

## Example Input and Expected Output

### Input Map File (`maps/easy/01_linear_path.txt`)
```text
# Easy Level 1: Linear path with capacity constraints
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue max_drones=3]
hub: waypoint2 2 0 [color=yellow max_drones=1]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Execution
```bash
python3 __main__.py maps/easy/01_linear_path.txt
```

### Output
```text
Graph loaded successfully: 4 zones, 3 connections, 2 drones
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```
