# InPicker Region Designer

InPicker Region Designer is a Python-based framework for defining, analyzing, and optimizing spatial picking regions within structured environments such as warehouses, grid systems, and coordinate-based layouts.

The system leverages principles from **computational geometry**, **spatial analysis**, and **optimization theory** to model regions, evaluate point inclusion, and support efficient picking workflows. Its design follows a **clean architecture approach**, ensuring a clear separation between domain logic, application use cases, and infrastructure concerns, which makes the system highly modular, testable, and extensible.

## Problem Statement

In logistics and warehouse environments, operational efficiency depends heavily on how physical space is structured and utilized. Key challenges include:

- **Spatial partitioning**: Dividing a continuous physical space into well-defined regions that are easy to manage and scale.
- **Efficient item assignment**: Mapping items, tasks, or agents to the appropriate regions based on location and operational constraints.
- **Travel cost minimization**: Reducing the total distance traveled during picking operations, which directly impacts time, energy consumption, and overall throughput.

These challenges can be formalized as a **spatial optimization problem**, where:

- The environment is modeled as a 2D coordinate space.
- Regions are defined as geometric subsets of that space.
- Picking operations aim to minimize a cost function, typically based on distance.

The goal of this project is to provide a structured and extensible framework to model these problems, evaluate spatial relationships, and enable more efficient decision-making in picking workflows.


## Mathematical Foundations

The system is grounded in basic principles of **Euclidean geometry** and **spatial optimization**, which enable the modeling and evaluation of picking regions.


### 1. Spatial Model

The environment is represented as a two-dimensional Cartesian space:

\[
(x, y) \in \mathbb{R}^2
\]

Each point corresponds to a physical location (e.g., a shelf, bin, or waypoint in a warehouse).


### 2. Region Definition

A region is defined as a subset of the plane:

\[
R \subseteq \mathbb{R}^2
\]

Regions partition the space into manageable areas and serve as the basis for assigning tasks and evaluating spatial relationships.


### 3. Axis-Aligned Bounding Box (AABB)

Rectangular regions are modeled using axis-aligned bounding boxes:

\[
R = \{(x, y) \mid x_{\min} \leq x \leq x_{\max}, \; y_{\min} \leq y \leq y_{\max} \}
\]

This representation allows for constant-time inclusion checks and is computationally efficient for grid-based layouts.


### 4. Point Inclusion Test

To determine whether a point belongs to a region:

\[
P = (x, y) \in R \iff 
\left( x_{\min} \leq x \leq x_{\max} \right) \land 
\left( y_{\min} \leq y \leq y_{\max} \right)
\]

This operation is fundamental for assigning items or agents to regions.


### 5. Distance Metric (Euclidean)

The primary cost metric used in the system is the Euclidean distance between two points:

:contentReference[oaicite:0]{index=0}

This metric is used to estimate travel cost, evaluate proximity, and support optimization strategies.


### 6. Optimization Objective

Picking workflows can be modeled as a path optimization problem:

\[
\min \sum_{i=1}^{n-1} d(P_i, P_{i+1})
\]

Where:
- \( P_i \) represents a sequence of picking locations
- The objective is to minimize total travel distance

This formulation is closely related to classical problems such as the **Traveling Salesman Problem (TSP)** and can be extended with additional constraints (e.g., region priorities, capacity limits).


## Architecture

inpicker/
├── domain/
├── application/
├── infrastructure

## Features

- Region definition
- Point evaluation
- Distance calculations
- Clean architecture


## ▶️ Usage

python app.py


