# Ratling

Ratling is an experimental low-pressure pneumatic routing project.

The core idea is a mechanically indexed rotary selector that connects one common pneumatic input to exactly one of 25 stationary output channels at a time.

## Scope

This repository is intentionally focused only on the routing mechanism itself.

It does **not** define or document an end application for the selector.

The project explores:

- a stationary stator with 25 output channels;
- a mechanically driven rotor;
- one common pneumatic input;
- indexed selection of exactly one output at a time;
- low-pressure operation;
- 3D-printable structural parts;
- replaceable seals and standard pneumatic fittings;
- mechanical crank-driven indexing;
- compact channel packing;
- comparison against an electronic valve-manifold architecture.

## Design principles

1. Any pressure reservoir, regulator, safety device, hose, fitting, or other pressure-rated supply component should be an off-the-shelf rated part.
2. Printed parts are used for geometry, support, indexing, and flow routing rather than stored-energy pressure vessels.
3. The first prototype should be small and simple before scaling to 25 outputs.
4. The mechanism should remain inspectable and serviceable.
5. Seals, shafts, bearings, and fittings should be replaceable commodity parts where practical.

## Current baseline concept

The simplest candidate is a single-track rotary selector:

- 25 stator ports arranged around one circular track;
- one rotor passage aligned with one stator port at a time;
- a rotor shaft driven by a side crank through a 1:1 bevel pair;
- a detent/indexer providing 25 discrete angular positions;
- a pulse valve opened by a cam on the rotor only while a port is aligned;
- all hoses and output fittings remain stationary.

This design is intentionally geometry-inefficient but mechanically simple.

Agreed decisions and numbers: [docs/requirements.md](docs/requirements.md).

## Repository layout

- `ratling/params.py` — all dimensions and the design checks; plain Python:
  `python3 -m ratling.params`.
- `ratling/geom.py`, `ratling/gears.py`, `ratling/fcview.py` — shared FreeCAD
  geometry, bevel gears, and the way parts are shown.
- `selector/stage1_interface.py`, `selector/stage2_rotary.py` — one generator
  per test article; `connectors/` — hose and tube connectors.
- `exports/` — generated STEP / STL / FCStd and reports; not in git.

Generators run inside FreeCAD:

```python
REPO = '/path/to/ratling'
exec(open(REPO + '/selector/stage2_rotary.py').read())
```

Each prints its report with the checks, opens the model (parts, bought
parts, references, section, labels as groups) and writes `exports/<name>/`.
Printed parts are exported in their print orientation.

## Alternatives

See [docs/concepts.md](docs/concepts.md) for the concepts currently under consideration.

## Prototype plan

Initial prototype target:

- 4-6 outputs;
- manual crank;
- replaceable sealing interface;
- standard fittings;
- no downstream load required for initial routing/leak testing.

The prototype should validate:

- indexing repeatability;
- sealing behavior;
- friction and required crank torque;
- leakage between adjacent channels;
- wear over repeated cycles;
- ease of assembly and maintenance.

Once the basic mechanism is validated, the selector can be scaled and packing efficiency can be revisited.
