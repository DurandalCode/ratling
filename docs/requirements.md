# Requirements — working baseline

Decisions agreed for the first prototype. Values marked *provisional* are
placeholders until measured or tested.

The numbers below are the agreed starting point. The working values, and the
checks that tie them together, live in `ratling/params.py`
(`python3 -m ratling.params` prints them); when the two disagree, the code
is current and this page needs updating.

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
  The input enters on the rotor axis at the stator centre. An inlet from the
  stator rim through an internal channel was considered and rejected: the
  channel would pass ~4 mm from the ports through printed walls, the leak
  path this design most needs to avoid.
- Port track: single track, fittings straight in the stator face (no remote
  panel). Pitch is set by the G1/8 fitting hex: R 64 mm, pitch 16.04 mm,
  stator Ø198 (Stage 2).
- Rotor sits behind the stator. It carries one internal passage from the
  centre to the port radius; no rotary union, no moving hoses.
- Rotor shaft runs backwards from the rotor.
- The crank is **on the side**: crank axis is horizontal, left–right,
  perpendicular to the rotor axis, coupled through a 1:1 bevel pair.
  The ratio may change later (reduction) without changing the layout.
- Drive: Ø8 steel shafts, two 608ZZ bearings per shaft. Both bearing pairs
  sit in one printed rear frame, so the bevel mesh depends on one part. The
  frame is joined to the stator by four columns (M5 through); the column
  bolts are tightened with the rotor in place so the spigot centres the
  frame.
- Bevel pair: printed straight bevel gears, module 2, 20 teeth, 0.15 mm
  backlash, mesh checked for interference in the model. A bought pair can
  replace it by changing the gear numbers in `params.py`.
- The 25-position detent and the valve cam sit on the **rotor shaft**, not on
  the crank shaft, so gear backlash affects neither port alignment nor pulse
  timing.

## Sealing concept

- Centre inlet: a spigot on the rotor runs in a bore in the stator centre,
  sealed by a radial O-ring on the spigot. It also centres the rotor.
- Outlet: a **floating shoe**, a small piston in a bore in the rotor with a
  radial O-ring, pressed on the stator face by a pen-type spring and by line
  pressure (balance ratio > 1). Its flat face is the only sliding seal and
  the only part that wears; it is printed for the first tests and can be
  turned from POM.
- One O-ring size for both: 8 × 1.5.
- Shoe face and port: the port stays fully under the shoe face within
  ±2.4° of alignment; alignment within ±1.1° keeps a 1.5 mm land around it.
- Stator face carries no seals. It is a flat plate; a non-printed face plate
  (acrylic / POM / aluminium) is the preferred candidate and is compared
  against a printed face in Stage 1 (variants A and B of the test strips).
- Leakage past the shoe goes to atmosphere, not into neighbouring channels.
- The rotor turns with no pressure in it (the valve has vented the line), so
  only the spring presses the shoe while moving: friction torque is small.

## Pulse valve, cam and detent

- Valve: Airtac M3R110-06G (3/2, roller lever, G1/8), stationary on the rear
  frame, on the input line: P from the supply, A to the stator centre, R
  vents the selector after each pulse.
- Cam: the rotor hub flange, 25 smooth lobes, phased to the rotor by a steel
  dowel. Being on the rotor side of the gears, it is not affected by gear
  backlash.
- The valve roller (Ø15, needs ~5–7 mm of travel) cannot follow 25 lobes on
  a cam of any size that fits, so a printed lever with a 623 bearing follows
  the cam and presses the roller through an M3 screw at 2:1. The screw sets
  the preload and with it the pulse width; it is set on the bench so the
  pulse stays inside the ±2.4° window above.
- Detent: an identical lever on the same cam, half a step from the valve
  lever, loaded by a spring. The valve spring alone would pull the rotor
  between ports, so the detent spring must be stronger (~1.5 × the valve
  force through the lever).
- Inlet hose A → centre: ~220 mm of 6/4, ~3 cm³; with the passages in stator
  and rotor ~5 cm³ is filled and vented per pulse. If the downstream volume
  per pulse turns out small, a 4 mm hose on this run cuts it to ~1 cm³.

## Pressure

- Tubing: 6 mm OD, standard push-in fittings.
- Prototype design pressure: 2 bar working, testing from 0.5 bar.
  *Provisional*; the final value is a separate discussion.
- Printed pressurized parts: thick walls, 100 % infill around channels, small
  pressurized volumes. Thin-epoxy impregnation is an option; lacquer is not
  relied upon.

## Output connector: 6 mm hose → ~25 mm metal tube

The tube is installed once (permanent).

- Tube: metal, ID **23.8 mm**, wall **0.59 mm** (OD ~25.0), measured.
- Printed plug inserted into the tube; the tube is supported from inside.
- Seal: O-ring on the plug.
  - O-ring in hand: 11/16″ × 1/8″, i.e. 17.46 × 3.18 mm (fits, third PLA
    print). Beware an AS568-212 with the same label: it is 15.5 × 3.5 and
    would be stretched ~14 % — wrong ring for this tube.
  - 12 % squeeze → groove depth 2.8 mm, groove root Ø18.2 mm, ring
    stretch ~4 %. 20 % would not go into the tube by hand; a static seal
    at 0.5–2 bar needs no more than 10–15 %.
  - Groove is a trapezoid: square wall on the flange side (pressure pushes
    the ring there), 45° wall on the tip side so it prints without an
    overhang; a square groove sagged in the first test print. Flat bottom
    1.1 × the ring section (3.5 mm), ring fills ~58 % of it.
  - Plug body Ø23.4 mm (0.2 mm radial clearance), flange Ø29.0. PLA prints
    came out at the drawn diameter, so no shrink allowance; Ø23.3 went in
    loose.
- Retention: 2–3 radial self-tapping screws through the tube wall into the
  plug, placed **between the O-ring and the tube end** (on the unpressurized
  side), optionally plus epoxy.
  - Axial blow-off force: ~89 N at 2 bar (445 mm² × 0.2 MPa), ~445 N at
    10 bar.
- Hose side: 6 mm straight push-in fitting, G1/8 thread tapped into the plug
  end, or a bulkhead push-in fitting through the plug end wall.

## Open items

- Plug: fit confirmed in PLA (body Ø23.4, 11/16″ × 1/8″ ring in the
  trapezoid groove); next a PETG print with a tapped G1/8 hole and a
  pressure test.
- Fitting PS06-01: thread type (G or R 1/8) and a matching tap; the plug
  hole is Ø8.8 for a G1/8 tap.
- Final working pressure.
- Measure the fitting hex: the port pitch has only 0.03 mm margin for a
  13 mm hex; a 14 mm hex needs R ≈ 69.
- Valve: actuating force (8 N assumed; sets the detent spring), which port
  is A, roller-to-body offset (read off the drawing).
- Test-print a 608 bearing seat (Ø22.1) and a shaft bore (Ø8.15).
- Pulse width: set with the lever screw, then decide whether the cam needs
  sharper lobes.
- Stand / feet for the unit.
- Optional reduction in the crank drive.
