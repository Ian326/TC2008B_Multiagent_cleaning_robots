# TC2008B_Multiagent_cleaning_robots
## Description 📋
This project implements a comprehensive multi-agent cleaning robot simulation system with three integrated components: a Python-based simulation engine, an HTTP server for data communication, and a Unity 3D visualization client. The system implements pathfinding using breadth-first search for robot navigation.

The system supports various test scenarios through input files, defining grid layouts with walls (X), litter quantities (numbers), paper bins (P), and robot starting positions (S).


## Core Components 💠
- Robot agents that explore the environment, collect litter, and coordinate with each other. Using sophisticated movement logic with collision detection and implement breadth-first search pathfinding for optimal route planning.
- GameBoard model that manages the simulation environment and agent scheduling


## Architecture 📝

### Structure 🧩
The `Python` folder contains the core multi-agent simulation logic using the Mesa framework, while the `Server` folder provides a web API layer for external integration. The system supports both standalone visualization (via matplotlib) and Unity-based 3D visualization through the HTTP server interface.

### HTTP Server Interface
The server file provides a REST API that bridges the Python simulation with external visualization clients.

### Data Processing Pipeline
- The server reads simulation output files in `tc2008B_server.py` processes the grid data, and serves structured JSON responses containing map data, robot positions, and grid dimensions.
- The server runs on port 8585 by default and can be configured for different ports.

### Unity 3D Visualization
The Unity client provides real-time 3D visualization of the simulation through two key components

### WebClient Communication
The `WebClient.cs` on the Unity Folder, establishes continuous communication with the Python server, sending POST requests every 0.25 seconds to retrieve updated simulation data.

### Dynamic Map Generation
The `MapGenerator.cs` on the Unity Folder, processes incoming JSON data and dynamically instantiates 3D prefabs for different game elements:

- Obstacle prefabs for walls (X)
- Robot prefabs for cleaning agents (S)
- Trash can prefabs for paper bins (P)
- Various garbage prefabs for different litter quantities (1-8)
- Floor tiles for the base environment

This architecture enables flexible visualization options - the Python simulation can run standalone with matplotlib visualization, or integrate with Unity for immersive 3D rendering. The modular design allows for easy extension with additional visualization clients or simulation parameters.


## Processing Flow 🔄
1. **Simulation Execution:** The Python simulation runs the multi-agent model, generating step-by-step grid states
2. **Data Export:** Simulation results are written to output files in a structured format
3. **Server Processing:** The HTTP server reads these files and converts them to JSON responses
4. **Unity Visualization:** The WebClient continuously polls the server and updates the 3D scene in real-time
5. **Dynamic Rendering:** MapGenerator clears and rebuilds the 3D environment for each simulation step


## Collaborators 👥
- Ian Joab Padrón Corona.
- Uri Jared Gopar Morales.
- María Fernanda Moreno Goméz.

<img src="https://hips.hearstapps.com/hmg-prod/images/pia23764-orig-1596114131.jpg" alt="imagen" align="center" width="800" height="200">
