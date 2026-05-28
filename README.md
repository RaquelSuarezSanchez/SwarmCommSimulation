# 🌕 Lunar Swarm Simulation

> **A robotic swarm simulation framework with dynamic BFS network routing and topographic coverage analysis.**
> 
> *Developed within the framework of the European Space Agency's (ESA) COSLE project.*

---

## Overview 🌙

This project provides a robust, lightweight 2D software simulation environment to evaluate the coordination and communication of a lunar robotic swarm. It utilizes real topographic elevation data (`.dt2`) to create a navigational grid and simulates telemetry exchange using multi-threaded, non-blocking UDP sockets. 

A dynamic routing algorithm allows rovers to act as signal relays based on proximity and battery levels, ensuring stable telemetry flow to the Supervisor (SV) node across irregular lunar terrain.

---

## Core Features 🌙

* **Peer-to-Peer Networking:** Simulates asynchronous communication using independent UDP socket threads for every rover.
* **Dynamic BFS Routing:** Calculates multi-hop relay trees in real-time, filtering out unhealthy nodes (battery < 20%) to maintain connectivity.
* **Real Topographical Mapping:** Parses GIS elevation data (`.dt2` formats via `rasterio`) and performs GPS-to-UTM coordinate transformations.
* **Swarm Exploration Strategies:** Implements the Strategy Design Pattern to easily switch between *Free Exploration* (dynamic boundary expansion) and *Fixed Exploration* (confined boundary).

---

## Repository Structure 🌙

The delivery is organized to separate the executable from the development source code:

```text
├── TFG_RaquelSuarez_UO295000.pdf     # Thesis document
├── 01_Executable/
│   └── SwarmCommSimulation.exe       # Standalone compiled application
└── 02_SourceCode/
    ├── main.py                       # Central simulation orchestrator
    ├── gui.py                        # Tkinter user interface entry point
    ├── environment.yml               # Conda environment dependencies
    ├── maps/                         # Topographical assets (.dt2)
    └── utils/                        # GIS parsing and BFS network logic
```
## Starting out 🌙
You can run the simulation using two different methods depending on your technical background.

### Option A: Standalone Executable (For End-Users)
No Python installation is required.
1. Navigate to the 01_Executable/ directory.
2. Double-click LunarSwarmSimulator.exe.
3. Configure your swarm parameters through the graphical interface or upload a .json file.
4. Click Start Simulation.

### Option B: Running from Source (For Developers)
Requires Conda to resolve C/C++ geospatial binary dependencies.
1. Clone this repository.
2. Open an Anaconda Prompt and navigate to the 02_SourceCode/ directory.
3. Create and activate the isolated environment:
```code
conda env create -f environment.yml
conda activate TFG
```
4. Launch the application:
```code
python gui.py
```

## Automated Configuration (.json) 🌙
To automate testing scenarios, you can bypass the manual UI by uploading a JSON configuration file. The file must strictly follow this schema:

| JSON Key | Data Type | Valid Range | Description |
| :--- | :--- | :--- | :--- |
| `"num_rovers"` | Integer | `3` to `7` | Total number of explorer nodes. |
| `"offset_sv_x"`| Float | Any | X-coordinate offset in meters for the SV. |
| `"offset_sv_y"`| Float | Any | Y-coordinate offset in meters for the SV. |
| `"area_size"`  | Float | `> 0` | Initial size of the exploration bounding box. |
| `"exploration_mode"` | Integer | `1` or `2` | `1`: Free Exploration. `2`: Fixed Exploration. |

Example `test_config.json`:
```json
{
  "num_rovers": 5,
  "offset_sv_x": 100.0,
  "offset_sv_y": -150.0,
  "area_size": 120.0,
  "exploration_mode": 2
}
```

## Author 🌙
**Raquel Suárez Sánchez** Bachelor's Degree in Software Engineering Universidad de Oviedo (2026)

Supervised by: Germán León Fernández & Olaya Pérez Mon.

