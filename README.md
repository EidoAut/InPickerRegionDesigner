# InPicker Region Designer

InPicker Region Designer is a Python-based framework for defining, analyzing, and optimizing spatial picking regions within structured environments such as warehouses, grid systems, and coordinate-based layouts.

The system leverages principles from **computational geometry**, **spatial analysis**, and **optimization theory** to model regions, evaluate point inclusion, and support efficient picking workflows. Its design follows a **clean architecture approach**, ensuring a clear separation between domain logic, application use cases, and infrastructure concerns, which makes the system highly modular, testable, and extensible.

---

## Problem Statement

In logistics and warehouse environments, operational efficiency depends heavily on how physical space is structured and utilized. Key challenges include:

- **Spatial partitioning**: Dividing a continuous physical space into well-defined regions that are easy to manage and scale.
- **Efficient item assignment**: Mapping items, tasks, or agents to the appropriate regions based on location and operational constraints.
- **Travel cost minimization**: Reducing the total distance traveled during picking operations, which directly impacts time, energy consumption, and overall throughput.

These challenges can be formalized as a **spatial optimization problem**, where:

- The environment is modeled as a 2D coordinate space
- Regions are defined as geometric subsets of that space
- Picking operations aim to minimize a cost function based on distance

The goal of this project is to provide a structured and extensible framework to model these problems, evaluate spatial relationships, and enable more efficient decision-making in picking workflows.

---

## Mathematical Foundations

The system is grounded in principles of **Euclidean geometry** and **spatial optimization**, enabling efficient modeling and evaluation of picking regions.

---

### 1. Spatial Model

The environment is represented as a two-dimensional Cartesian space:

```
(x, y) ∈ R^2
```

Each point corresponds to a physical location (e.g., a shelf, bin, or waypoint in a warehouse).

---

### 2. Region Definition

A region is defined as a subset of the plane:

```
R ⊆ R^2
```

Regions partition the space into manageable areas used for assigning tasks and evaluating spatial relationships.

---

### 3. Axis-Aligned Bounding Box (AABB)

Rectangular regions are defined as:

```
R = {(x, y) | x_min ≤ x ≤ x_max AND y_min ≤ y ≤ y_max}
```

This representation allows for fast inclusion checks and is efficient for grid-based layouts.

---

### 4. Point Inclusion Test

To determine whether a point belongs to a region:

```
A point P = (x, y) belongs to R if:

x_min ≤ x ≤ x_max
AND
y_min ≤ y ≤ y_max
```

This is one of the core operations of the system.

---

### 5. Distance Metric (Euclidean)

The Euclidean distance between two points is defined as:

```
d(P1, P2) = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

This metric is used to:

- Estimate travel cost
- Evaluate proximity between points
- Support optimization strategies

---

### 6. Optimization Objective

Picking workflows can be modeled as:

```
Minimize total distance:

Σ d(Pi, Pi+1)
```

Where:

- Pi represents a sequence of picking locations  
- The objective is to minimize total travel distance  

This problem is closely related to:

- Traveling Salesman Problem (TSP)
- Shortest path optimization

---

## Architecture

The project follows a clean and modular structure:

```
inpicker/
├── domain/         # Core logic and geometry
├── application/    # Use cases and orchestration
├── infrastructure/ # I/O and configuration
├── app.py          # Entry point
```

### Layer Responsibilities

- **Domain**
  - Geometry calculations
  - Region definitions
  - Core business rules

- **Application**
  - Use case orchestration
  - Region evaluation logic

- **Infrastructure**
  - Configuration handling (JSON)
  - Input/output operations

---

## Features

- Region definition using geometric models
- Point-in-region evaluation
- Distance-based reasoning
- Clean architecture design
- JSON-driven configuration

---

## Installation

```bash
git clone https://github.com/EidoAut/InPickerRegionDesigner.git
cd InPickerRegionDesigner
```

(Optional) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

---

## Usage

Run the application:

```bash
python app.py
```

---

## Example Workflow

1. Define regions in a configuration file
2. Load the configuration
3. Evaluate points against regions
4. Compute distances if needed
5. Analyze results

---

## Testing

```bash
pytest
```

---

## Future Improvements

- Polygonal region support
- Pathfinding algorithms (A*, Dijkstra)
- Visualization (matplotlib or UI)
- Spatial indexing for performance optimization

---

## License

MIT License
