# Requirements — working baseline

Decisions agreed for the first prototype. Values marked *provisional* are
placeholders until measured or tested.

## Function

- 1 common input → exactly one of 25 outputs at a time.
- Sequential selection only. One full rotor revolution = one full cycle of
  25 positions (14.4° per position).
- Non-selected outputs vent to atmosphere.
- Air is delivered as a pulse. The pulse is produced by a separate
  off-the-shelf 3/2 valve, mechanically triggered by the mechanism only while
  a port is aligned. Transitions between ports therefore carry no flow, and
  break-before-make geometry is not required.

## Layout and orientation

- Stator is stationary and stands vertically, face to the front.
- All 25 outputs and the common input leave the unit **towards the front**.
  The input enters on the rotor axis at the stator centre.
- Rotor sits behind the stator. It carries one internal passage from the
  centre to the port radius; no rotary union, no moving hoses.
- Rotor shaft runs backwards from the rotor.
- The crank is **on the side**: crank axis is horizontal, left–right,
  perpendicular to the rotor axis, coupled through a 1:1 bevel pair.
  The ratio may change later (reduction) without changing the layout.
- The 25-position detent and the valve cam sit on the **rotor shaft**, not on
  the crank shaft, so gear backlash affects neither port alignment nor pulse
  timing.

## Sealing concept ("shoe")

- Two seals on the rotor face: one around the centre inlet (rotates in place),
  one around the outlet ("shoe") that travels over the stator ports.
- Stator face carries no seals. It is a flat plate; a non-printed face plate
  (acrylic / POM / aluminium) is the preferred candidate and is compared
  against a printed face in Stage 1.
- Leakage past the shoe goes to atmosphere, not into neighbouring channels.

## Pulse valve

- Off-the-shelf 3/2 valve with roller/plunger actuator, stationary, on the
  input line.
- Actuated by a 25-lobe cam on the rotor shaft, phased with the detent so the
  valve opens only in the aligned position.
- Lobe width is a tuning parameter (pulse duration vs. crank speed).

## Pressure

- Tubing: 6 mm OD, standard push-in fittings.
- Prototype design pressure: 2 bar working, testing from 0.5 bar.
  *Provisional*; the final value is a separate discussion.
- Printed pressurized parts: thick walls, 100 % infill around channels, small
  pressurized volumes. Thin-epoxy impregnation is an option; lacquer is not
  relied upon.

## Output connector: 6 mm hose → 25 × 1 mm metal tube

The tube is installed once (permanent).

- Tube: 25 mm OD, 1 mm wall, metal. ID **23 mm (*provisional*, to be
  measured)**.
- Printed plug inserted into the tube; the tube is supported from inside.
- Seal: O-ring on the plug.
  - O-ring cross-section 2.5 mm, ~20 % squeeze → groove depth 2.0 mm,
    groove root Ø19.0 mm, groove width ~3.3 mm.
  - O-ring 18 × 2.5 (preferred, ~5 % stretch) or 19 × 2.5.
  - Plug body Ø22.6 mm (0.2 mm radial clearance).
- Retention: 2–3 radial self-tapping screws through the tube wall into the
  plug, placed **between the O-ring and the tube end** (on the unpressurized
  side), optionally plus epoxy.
  - Axial blow-off force: ~83 N at 2 bar (415 mm² × 0.2 MPa), ~415 N at
    10 bar.
- Hose side: 6 mm straight push-in fitting, G1/8 thread tapped into the plug
  end, or a bulkhead push-in fitting through the plug end wall.

## Open items

- Measure tube ID; adjust groove/plug diameters.
- Final working pressure.
- Port radius and pitch: depends on whether outputs are on the stator face
  directly or routed to a front panel (concept C).
- Cam lobe width / pulse duration.
- Optional reduction in the crank drive.
