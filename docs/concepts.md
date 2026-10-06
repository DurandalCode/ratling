# Selector Concepts

This document captures candidate architectures for a low-pressure 1-to-25 pneumatic selector.

## A. Single-track rotary selector

### Layout

All 25 stator ports lie on one circular track.

A rotor contains a single passage from the common input to that same radius. Rotation selects one stator port at a time.

### Advantages

- very simple kinematics;
- one moving functional part;
- trivial mapping between shaft angle and output number;
- straightforward indexing;
- easy to inspect and reason about.

### Disadvantages

- poor use of disk area;
- required diameter grows with fitting/port pitch;
- routing 25 output connections can become bulky.

### Current status

Baseline architecture.

---

## B. Multi-track rotary selector

The stator ports are distributed over multiple concentric tracks.

The rotor contains multiple internal passages at different radii, arranged so that indexed angular positions still expose exactly one output at a time.

Possible packings include:

- 5 tracks x 5 positions;
- 4 tracks with uneven port counts;
- other layouts optimized around actual seal and channel dimensions.

### Advantages

- substantially better use of selector face area;
- potentially much smaller overall diameter.

### Disadvantages

- more complicated rotor geometry;
- more difficult sealing layout;
- more difficult validation of cross-port isolation;
- mapping angle to channel is less visually obvious.

### Current status

Second-generation optimization candidate, not preferred for the first prototype.

---

## C. Compact selector face + remote fitting panel

Keep only small flow ports on the selector face.

Route those passages through a thicker stator body to a separate rear or side connection panel, where standard fittings can be packed efficiently, for example in a 5 x 5 grid.

### Advantages

- selector diameter is determined by sealing geometry rather than fitting size;
- much cleaner hose management;
- service-friendly numbered connection panel;
- compatible with both single-track and multi-track selector faces.

### Disadvantages

- internal stator routing becomes more complex;
- thicker stator body;
- potentially more difficult to print or manufacture.

### Current status

Promising packaging technique that can be combined with A or B.

---

## D. Electronic valve manifold

Alternative architecture with no rotary pneumatic selector.

A common rated manifold feeds individually controlled normally-closed pneumatic valves. A shaft sensor or encoder observes crank movement and a controller activates outputs sequentially.

Typical building blocks:

- rotary encoder or Hall sensor;
- microcontroller;
- output drivers;
- 24 V valve manifold or valve terminal.

### Advantages

- almost no precision rotating pneumatic sealing;
- sequence can be changed in software;
- conventional industrial pneumatic components;
- diagnostics are easy to add.

### Disadvantages

- substantially higher component count and cost;
- wiring and power supply;
- electronics become part of the mechanism;
- less mechanically direct than a crank-driven selector.

### Current status

Fallback/reference architecture.

---

## Recommended development order

1. Build a 4-6 port single-track selector.
2. Test indexing, sealing, leakage, friction, and wear.
3. If successful, scale the geometry toward 25 ports.
4. Solve fitting packaging separately using a rear/side connection panel.
5. Consider multi-track packing only if the single-track selector becomes unacceptably large.
6. Keep the electronic manifold design as a comparison point for cost, complexity, and reliability.
