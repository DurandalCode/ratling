# -*- coding: utf-8 -*-
"""
Ratling shared parameters and design checks.

Plain Python, no FreeCAD. Part generators import it; running it on its own
prints the derived numbers and the checks:

    python3 -m ratling.params

Frame used by every selector part:

    Z ........ rotor axis, +Z = front (where the hoses leave).
    z = 0 .... stator sealing face. Stator body is z > 0, rotor is z < 0.
    X ........ the aligned port of the Stage 1 article lies on +X.

See docs/requirements.md for the decisions behind the numbers.
"""

import math

# ---------------------------------------------------------------- function
N_PORTS = 25
INDEX_DEG = 360.0 / N_PORTS

P_TEST_BAR = 0.5            # first tests
P_DESIGN_BAR = 2.0          # prototype design pressure (provisional)

# ---------------------------------------------------------------- fittings
# 6 mm straight push-in fitting, G1/8, tapped into the printed part.
G18_TAP_DRILL = 8.8
G18_TAP_DEPTH = 8.0
FITTING_HEX = 13.0          # across flats; check against the fittings bought
FITTING_SPACING = 1.0       # free gap between neighbouring hex corners

# ---------------------------------------------------------------- ports
PORT_R = 64.0               # port track radius
PORT_D = 4.0                # air passage everywhere in the selector
PORT_CHAMFER = 0.5          # on the stator face, so the shoe does not catch

# ---------------------------------------------------------------- rotor / stator
GAP = 1.5                   # rotor face to stator face; the shoe bridges it
MIN_WALL = 2.0              # printed wall around any pressurized passage

# One O-ring size for the whole rotor: spigot and shoe.
ORING_ID = 8.0
ORING_CS = 1.5
ORING_SQUEEZE = 0.20        # radial glands
ORING_STRETCH = 0.03        # target stretch on the groove root
GROOVE_W_FACTOR = 1.35      # groove width / cross-section
RADIAL_CLEAR = 0.2          # sliding diametral clearance, per side

# Centre inlet: rotor spigot in a stator bore, radial O-ring on the spigot.
SPIGOT_TIP_Z = 10.0         # spigot tip, measured from the stator face
SPIGOT_GROOVE_Z = 6.5       # groove centre
SPIGOT_BORE_EXTRA = 1.0     # bore deeper than the spigot tip
LEAD_CHAMFER = 1.0

# Floating shoe: piston in a rotor bore, radial O-ring, flat face on the stator.
SHOE_LEN = 8.0
SHOE_GROOVE_FROM_BACK = 3.0 # groove centre, from the shoe's back face
SHOE_FACE_CHAMFER = 0.4
SHOE_SPRING_SEAT_D = 6.4    # counterbore in the shoe back for a pen-type spring
SHOE_SPRING_SEAT_DEPTH = 1.0
SHOE_SPRING_SPACE = 4.0     # spring length when installed (shoe touching stator)
SHOE_SPRING_F = 3.0         # N, installed; keeps contact with no pressure
MIN_LAND = 1.5              # shoe face left around the port at worst misalignment

# Rotor internal channel, centre -> port radius. Slightly wider than the
# vertical passages it joins: equal radii meet tangentially and break the solid.
CHANNEL_D = PORT_D + 0.4
CHANNEL_FLOOR = 3.0         # material below the channel

# Plate variant: non-printed face plate on a printed stator body.
PLATE_T = 3.0
PLATE_ORING_ID = 6.0        # one small O-ring per port between plate and body
PLATE_ORING_CS = 1.5
PLATE_ORING_SQUEEZE = 0.25  # static face gland

# Friction estimate.
MU_SHOE = 0.3               # printed / POM on acrylic or printed, dry

# ---------------------------------------------------------------- helpers


def radial_gland(ring_id, cs, squeeze=ORING_SQUEEZE, stretch=ORING_STRETCH):
    """O-ring on a shaft/piston groove. Returns (groove root Ø, bore Ø)."""
    root_d = ring_id * (1 + stretch)
    bore_d = root_d + 2 * cs * (1 - squeeze)
    return root_d, bore_d


def disc_area(d):
    return math.pi * d * d / 4


# ---------------------------------------------------------------- derived
pitch = 2 * PORT_R * math.sin(math.pi / N_PORTS)     # chord between ports
fitting_corners = FITTING_HEX / math.cos(math.radians(30))
min_pitch = fitting_corners + FITTING_SPACING
min_port_r_for_fittings = min_pitch / (2 * math.sin(math.pi / N_PORTS))

oring_root_d, oring_bore_d = radial_gland(ORING_ID, ORING_CS)
groove_w = GROOVE_W_FACTOR * ORING_CS
groove_stretch = oring_root_d / ORING_ID - 1

# Spigot / centre bore
spigot_bore_d = oring_bore_d
spigot_d = spigot_bore_d - 2 * RADIAL_CLEAR
spigot_bore_depth = SPIGOT_TIP_Z + SPIGOT_BORE_EXTRA
spigot_cone_h = (spigot_bore_d - PORT_D) / 2         # 45 deg roof, printable
stator_t = math.ceil(spigot_bore_depth + spigot_cone_h + 1.0 + G18_TAP_DEPTH)

# Shoe
shoe_bore_d = oring_bore_d
shoe_d = shoe_bore_d - 2 * RADIAL_CLEAR
shoe_land_d = shoe_d - 2 * SHOE_FACE_CHAMFER
shoe_bore_depth = (SHOE_LEN - GAP) + SHOE_SPRING_SPACE   # from the rotor face
shoe_misalign_mm = (shoe_land_d - PORT_D) / 2 - MIN_LAND
shoe_misalign_deg = math.degrees(shoe_misalign_mm / PORT_R)

# Rotor
rotor_face_z = -GAP
shoe_floor_z = rotor_face_z - shoe_bore_depth
channel_z = shoe_floor_z - 1.0                      # axis, just below the floor
rotor_back_z = channel_z - CHANNEL_D / 2 - CHANNEL_FLOOR
rotor_t = rotor_face_z - rotor_back_z

# Plate variant face gland: ring rests on the outer wall (internal pressure).
plate_gland_od = PLATE_ORING_ID + 2 * PLATE_ORING_CS
plate_gland_depth = PLATE_ORING_CS * (1 - PLATE_ORING_SQUEEZE)

# Hydraulics of the shoe (linear pressure drop across the land).
A_shoe_back = disc_area(shoe_bore_d)
A_port = disc_area(PORT_D)
A_land = disc_area(shoe_land_d) - A_port
A_face_eff = math.pi / 4 * (PORT_D ** 2 + PORT_D * shoe_land_d + shoe_land_d ** 2) / 3
shoe_balance_k = (A_shoe_back - A_port) / A_land


def shoe_force(p_bar):
    """Net contact force of the shoe on the stator, N."""
    return p_bar * 0.1 * (A_shoe_back - A_face_eff) + SHOE_SPRING_F


def rotor_separating_force(p_bar):
    """Axial force pushing the rotor away from the stator, N.

    Pressure on the spigot cross-section plus the shoe's reaction.
    """
    return p_bar * 0.1 * disc_area(spigot_bore_d) + shoe_force(p_bar)


def shoe_torque(p_bar):
    """Friction torque of the shoe on the stator, N*m."""
    return MU_SHOE * shoe_force(p_bar) * PORT_R / 1000


# ---------------------------------------------------------------- checks


def checks():
    """List of (name, ok, detail)."""
    out = []

    def c(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    c("port pitch fits fitting hex",
      pitch >= min_pitch,
      "pitch %.2f >= %.2f (R >= %.1f)" % (pitch, min_pitch, min_port_r_for_fittings))
    c("O-ring stretch 0..6 %",
      0 <= groove_stretch <= 0.06, "%.1f %%" % (groove_stretch * 100))
    c("spigot/shoe wall at groove root >= MIN_WALL",
      (oring_root_d - PORT_D) / 2 >= MIN_WALL - 0.1,
      "%.2f" % ((oring_root_d - PORT_D) / 2))
    c("spigot groove inside the bore (plate variant too)",
      SPIGOT_GROOVE_Z - groove_w / 2 >= PLATE_T + LEAD_CHAMFER
      and SPIGOT_GROOVE_Z + groove_w / 2 <= SPIGOT_TIP_Z - LEAD_CHAMFER,
      "groove %.2f..%.2f" % (SPIGOT_GROOVE_Z - groove_w / 2, SPIGOT_GROOVE_Z + groove_w / 2))
    c("shoe groove stays in its bore",
      SHOE_GROOVE_FROM_BACK + groove_w / 2 <= SHOE_LEN - GAP - 0.5,
      "groove top %.2f from back, bore mouth at %.2f"
      % (SHOE_GROOVE_FROM_BACK + groove_w / 2, SHOE_LEN - GAP))
    c("shoe tolerates >= 0.5 deg misalignment",
      shoe_misalign_deg >= 0.5,
      "+-%.2f mm = +-%.2f deg at R %.0f" % (shoe_misalign_mm, shoe_misalign_deg, PORT_R))
    c("shoe face never reaches a neighbouring port",
      shoe_land_d / 2 + PORT_D / 2 + PORT_CHAMFER < pitch,
      "%.2f < %.2f" % (shoe_land_d / 2 + PORT_D / 2 + PORT_CHAMFER, pitch))
    c("shoe pressed at design pressure",
      shoe_force(P_DESIGN_BAR) > 0, "%.1f N" % shoe_force(P_DESIGN_BAR))
    c("wall between neighbouring tap holes >= 3 mm",
      pitch - G18_TAP_DRILL >= 3.0, "%.2f" % (pitch - G18_TAP_DRILL))
    c("plate gland ring clears the port",
      PLATE_ORING_ID > PORT_D, "ring ID %.1f > port %.1f" % (PLATE_ORING_ID, PORT_D))
    return out


def report():
    lines = [
        "ratling params",
        "  ports                  : %d x %.1f deg, R %.1f, pitch %.2f" % (N_PORTS, INDEX_DEG, PORT_R, pitch),
        "  stator Ø (track + 1 hex): ~%.0f" % (2 * PORT_R + fitting_corners + 6),
        "  O-ring (spigot, shoe)  : %g x %g, root Ø%.2f, bore Ø%.2f, groove w %.2f"
        % (ORING_ID, ORING_CS, oring_root_d, oring_bore_d, groove_w),
        "  spigot Ø / bore depth  : %.2f / %.1f" % (spigot_d, spigot_bore_depth),
        "  stator thickness       : %.1f" % stator_t,
        "  rotor face / back z    : %.1f / %.1f (t %.1f)" % (rotor_face_z, rotor_back_z, rotor_t),
        "  shoe Ø / land Ø / len  : %.2f / %.2f / %.1f" % (shoe_d, shoe_land_d, SHOE_LEN),
        "  shoe balance k         : %.2f (>1: contact pressure above line pressure)" % shoe_balance_k,
        "  plate O-ring           : %g x %g, gland Ø%.1f depth %.2f"
        % (PLATE_ORING_ID, PLATE_ORING_CS, plate_gland_od, plate_gland_depth),
    ]
    for p in (0.0, P_TEST_BAR, P_DESIGN_BAR):
        lines.append("  @%.1f bar: shoe %.1f N, rotor push-off %.1f N, shoe torque %.3f N*m"
                     % (p, shoe_force(p), rotor_separating_force(p), shoe_torque(p)))
    for name, ok, detail in checks():
        lines.append("  [%s] %s%s" % ("OK " if ok else "FAIL", name, ("  (" + detail + ")") if detail else ""))
    return "\n".join(lines)


def all_ok():
    return all(ok for _, ok, _ in checks())


if __name__ == "__main__":
    print(report())
