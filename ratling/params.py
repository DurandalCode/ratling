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

# ---------------------------------------------------------------- drive (Stage 2 on)
SHAFT_D = 8.0               # steel rod, rotor and crank shaft
SHAFT_BORE_D = 8.15         # printed hole for the shaft
BEARING_OD = 22.0           # 608ZZ
BEARING_W = 7.0
BEARING_SEAT_D = 22.1       # printed seat; tune after a test print
BEARING_GAP = 8.0           # between the two bearings of the rotor shaft
CRANK_BEARING_GAP = 20.0    # crank shaft: longer, carries the hand load and
                            # keeps the crank clear of the frame arms
BEARING_BOSS_D = 32.0
SHIM = 1.0                  # washers between rotor hub and front bearing; set the gap

# Rotor (Stage 2: an arm, not a disc) and its hub. The hub is a separate part
# whose flange is the valve / detent cam; a steel dowel fixes its phase.
ROTOR_ARM_W = 30.0
ROTOR_CENTRE_D = 44.0
HUB_FLANGE_T = 6.0          # = cam thickness
HUB_BOSS_D = 22.0
HUB_BOSS_LEN = 12.0
HUB_SCREW_R = 14.0          # 3 x M3 into the rotor back
HUB_SCREW_PILOT = 2.5
HUB_SCREW_DEPTH = 8.0
SET_SCREW_PILOT = 2.5       # M3 set screw against a flat on the shaft
HUB_PIN_D = 3.0             # steel dowel (or Ø3 rod) through hub into rotor
HUB_PIN_HOLE = 3.05
HUB_PIN_R = 17.0
HUB_PIN_ANGLE = 120.0
HUB_PIN_DEPTH = 6.0         # into the rotor

# Frame: rear spider with the bearing boss, joined to the stator by 4 columns.
FRAME_COL_R = 90.0
FRAME_COL_D = 14.0
FRAME_BOLT_D = 5.5          # M5
FRAME_ARM_W = 16.0
FRAME_ARM_T = 10.0

# Stator (Stage 2: full disc, all 25 ports)
STATOR_PLATE_T = 10.0       # outside the port ring and the centre boss
PORT_RING_W = 24.0
CENTRE_BOSS_D = 40.0
STATOR_EDGE = 9.0           # stator rim beyond the column bolts

# Printed 1:1 straight bevel pair (ratling/gears.py). A bought set can replace
# it if BEVEL_MOUNT and the outside diameter are set to the vendor's values.
BEVEL_MODULE = 2.0
BEVEL_TEETH = 20
BEVEL_FACE = 9.0            # <= cone distance / 3
BEVEL_BACKLASH = 0.15       # at the pitch circle
BEVEL_HUB_D = 22.0
BEVEL_HUB_L = 10.0

CRANK_ARM = 50.0            # crank radius
CRANK_HUB_D = 20.0
CRANK_HUB_L = 10.0
CRANK_HANDLE_LEN = 30.0
CRANK_HANDLE_D = 12.0

# ---------------------------------------------------------------- pulse valve
# Airtac M3R110-06G: 3/2, roller lever, G1/8 (catalogue 2026, pp. 105-106).
# Body 27 x 18 x 46.5, 3 x Ø3.3 through holes; roller Ø15 x 8.5, its centre
# 18.5 above the body top when free; switches between 4.6 and 6.8 of roller
# travel (unit to unit). Force not catalogued: VALVE_FORCE is a guess.
VALVE_A = 27.0              # along the valve's own lever
VALVE_B = 18.0              # thickness; mounting holes and roller axle run this way
VALVE_D = 46.5
VALVE_HOLE_D = 3.3
VALVE_KA, VALVE_KB, VALVE_KC = 18.0, 15.5, 16.0
VALVE_ROLLER_D = 15.0
VALVE_ROLLER_W = 8.5
VALVE_ROLLER_H = 18.5       # free roller centre above the body top
VALVE_ROLLER_TO_BODY = 19.0 # roller centre to body centre along A (read off the drawing)
VALVE_PORTS_PR = (15.5, 31.5)   # two ports on one narrow face, from the body bottom
VALVE_PORT_A = 23.5         # single port on the other narrow face (taken as A, out)
VALVE_SWITCH = (4.6, 6.8)   # roller travel where it switches
VALVE_FORCE = 8.0           # N at the roller, provisional; measure
VALVE_ANGLE = 270.0         # where the valve follower sits (machine -Y: right in the view)

# Cam on the hub flange, 25 lobes, smooth (cosine) pitch curve; one track for
# the valve follower and the detent follower half a step apart.
CAM_PITCH_R = 60.0          # follower centre in a valley
FOLLOWER_D = 10.0           # 623ZZ: 10 x 3 x 4
FOLLOWER_W = 4.0
LEVER_L1 = 16.0             # pivot to follower; valve / spring at 2 x L1
LEVER_RATIO = 2.0
LEVER_W = 8.0
LEVER_T = 6.0
VALVE_TRAVEL = (3.3, 6.8)   # roller pressed in a valley / on a lobe; the screw
                            # in the lever end shifts both, which sets the pulse
DETENT_ANGLE = 3.6          # = VALVE_ANGLE + half a step + whole steps
DETENT_MARGIN = 1.5         # detent follower force / valve follower force
DETENT_SPRING_LEN = 10.0    # installed length between lever end and its pad
ADJUST_GAP = 1.0            # adjusting screw tip proud of the lever edge, nominal

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

# Bevel pair (shaft angle 90 deg, pitch cone 45 deg).
bevel_pitch_d = BEVEL_MODULE * BEVEL_TEETH
bevel_cone_distance = bevel_pitch_d / math.sqrt(2)
bevel_big_end = bevel_pitch_d / 2                        # apex to big end, axial
bevel_small_end = bevel_big_end * (bevel_cone_distance - BEVEL_FACE) / bevel_cone_distance
BEVEL_OD = bevel_pitch_d + 2 * BEVEL_MODULE * math.cos(math.radians(45))
BEVEL_MOUNT = bevel_big_end + BEVEL_HUB_L                # apex to the back of the hub
BEVEL_LEN = BEVEL_MOUNT - bevel_small_end                # hub back to small end

# Cam
cam_rise = (VALVE_TRAVEL[1] - VALVE_TRAVEL[0]) / LEVER_RATIO


def cam_pitch_r(theta_deg):
    """Follower-centre radius at rotor-frame angle theta (aligned position);
    lobes under the valve follower, valleys under the detent follower."""
    return CAM_PITCH_R + cam_rise / 2 * (1 + math.cos(math.radians(N_PORTS * (theta_deg - VALVE_ANGLE))))


def cam_profile(n=1200):
    """(radius, curvature radius of the pitch curve where concave, max pressure angle)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = cam_pitch_r(math.degrees(t))
        pts.append((r * math.cos(t), r * math.sin(t)))
    min_concave, max_pa = 1e9, 0.0
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[(i + 1) % n]
        a = math.hypot(x1 - x0, y1 - y0)
        b = math.hypot(x2 - x1, y2 - y1)
        c = math.hypot(x2 - x0, y2 - y0)
        cross = (x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)
        if cross < 0:                      # turning clockwise: concave
            min_concave = min(min_concave, a * b * c / (2 * abs(cross)))
        r1 = math.hypot(x1, y1)
        dr = (math.hypot(x2, y2) - math.hypot(x0, y0)) / (2 * 2 * math.pi / n)
        max_pa = max(max_pa, math.degrees(math.atan(abs(dr) / r1)))
    return pts, min_concave, max_pa


cam_od = 2 * (CAM_PITCH_R + cam_rise - FOLLOWER_D / 2)
follower_force_valve = VALVE_FORCE * LEVER_RATIO
follower_force_detent = DETENT_MARGIN * follower_force_valve
detent_spring_force = follower_force_detent / LEVER_RATIO


def pulse_window_deg(switch):
    """Rotor angle (+-, deg) around alignment while the roller is past `switch`."""
    lo, hi = VALVE_TRAVEL
    c = (switch - (lo + hi) / 2) / ((hi - lo) / 2)
    if c >= 1:
        return 0.0
    if c <= -1:
        return INDEX_DEG / 2
    return math.degrees(math.acos(c)) / N_PORTS


shoe_seal_window_deg = math.degrees((shoe_land_d / 2 - PORT_D / 2) / PORT_R)


def detent_holding_torque():
    """Peak torque (N*m) needed to move the rotor off a port; detent minus valve."""
    return N_PORTS * cam_rise / 2 * (follower_force_detent - follower_force_valve) / 1000

# Drive stack along the rotor axis (Stage 2 on).
rotor_sweep_r = PORT_R + ROTOR_ARM_W / 2
hub_back_z = rotor_back_z - HUB_FLANGE_T - HUB_BOSS_LEN
spider_front_z = hub_back_z - SHIM
bearing_boss_len = 2 * BEARING_W + BEARING_GAP
boss_back_z = spider_front_z - bearing_boss_len
bevel_apex_z = boss_back_z - 1.0 - BEVEL_MOUNT       # crank axis crosses the rotor axis here
crank_boss_y0 = BEVEL_MOUNT + 1.0
crank_boss_len = 2 * BEARING_W + CRANK_BEARING_GAP
crank_boss_y1 = crank_boss_y0 + crank_boss_len
crank_arm_y = crank_boss_y1 + SHIM
column_len = -spider_front_z
stator_d = 2 * (FRAME_COL_R + STATOR_EDGE)
rotor_shaft = (rotor_back_z, bevel_apex_z + BEVEL_MOUNT - BEVEL_LEN + 2)   # z top, z bottom
crank_shaft = (SHAFT_D / 2 + 4, crank_arm_y + CRANK_HUB_L)                # y start, y end
column_angles = (45.0, 135.0, 225.0, 315.0)

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

    # drive
    col_in = FRAME_COL_R - FRAME_COL_D / 2
    c("rotor arm clears the frame columns",
      rotor_sweep_r + 2.0 <= col_in, "sweep R %.1f, columns from R %.1f" % (rotor_sweep_r, col_in))
    d_col = min(math.hypot(FRAME_COL_R * math.cos(math.radians(a)) - PORT_R * math.cos(math.radians(b)),
                           FRAME_COL_R * math.sin(math.radians(a)) - PORT_R * math.sin(math.radians(b)))
                for a in column_angles for b in [i * INDEX_DEG for i in range(N_PORTS)])
    c("column bolt heads clear of the fittings",
      d_col >= fitting_corners / 2 + 5.0 + 1.0, "%.1f mm centre to centre" % d_col)
    c("hub flange screws clear of the channel",
      HUB_SCREW_R * math.sin(math.radians(60)) - HUB_SCREW_PILOT / 2 > CHANNEL_D / 2 + 1.0,
      "screws at 60/180/300 deg")
    c("bevel face width <= cone distance / 3",
      BEVEL_FACE <= bevel_cone_distance / 3 + 1e-9,
      "%.1f <= %.2f" % (BEVEL_FACE, bevel_cone_distance / 3))
    _, concave, pa = cam_profile()
    c("cam: follower rolls the valleys (concave R >= follower R + 1)",
      concave >= FOLLOWER_D / 2 + 1.0, "pitch curve concave R %.1f" % concave)
    c("cam: pressure angle <= 25 deg", pa <= 25.0, "%.1f deg" % pa)
    c("valve travel inside the catalogue range",
      VALVE_TRAVEL[0] < VALVE_SWITCH[0] and VALVE_TRAVEL[1] <= VALVE_SWITCH[1],
      "%.1f..%.1f vs switching %.1f..%.1f" % (VALVE_TRAVEL + VALVE_SWITCH))
    c("detent follower half a step from the valve follower",
      abs(((DETENT_ANGLE - VALVE_ANGLE - INDEX_DEG / 2) / INDEX_DEG) % 1) < 1e-9,
      "%.1f vs %.1f" % (DETENT_ANGLE, VALVE_ANGLE))
    c("detent stronger than the valve spring", DETENT_MARGIN > 1.0,
      "holding %.2f N*m" % detent_holding_torque())
    c("rotor shaft end clear of the crank shaft",
      rotor_shaft[1] - bevel_apex_z >= SHAFT_D / 2 + 1.0,
      "%.1f mm above the crank axis" % (rotor_shaft[1] - bevel_apex_z))
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
    lines += [
        "  stator Ø (Stage 2)     : %.0f, columns 4 x R %.0f, length %.1f" % (stator_d, FRAME_COL_R, column_len),
        "  drive z                : hub back %.1f, spider %.1f, boss back %.1f, bevel apex %.1f"
        % (hub_back_z, spider_front_z, boss_back_z, bevel_apex_z),
        "  shafts                 : Ø%g, rotor %.0f mm, crank %.0f mm"
        % (SHAFT_D, rotor_shaft[0] - rotor_shaft[1], crank_shaft[1] - crank_shaft[0]),
    ]
    lines += [
        "  cam                    : 25 lobes, pitch R %.1f..%.2f, rise %.2f, OD %.1f, follower Ø%g"
        % (CAM_PITCH_R, CAM_PITCH_R + cam_rise, cam_rise, cam_od, FOLLOWER_D),
        "  valve pulse            : +-%.1f deg if it switches at %.1f, +-%.1f deg at %.1f"
        % (pulse_window_deg(VALVE_SWITCH[0]), VALVE_SWITCH[0],
           pulse_window_deg(sum(VALVE_SWITCH) / 2), sum(VALVE_SWITCH) / 2),
        "  detent                 : spring %.0f N at the lever end (valve force %.0f N assumed)"
        % (detent_spring_force, VALVE_FORCE),
        "  port fully under shoe  : +-%.1f deg; set the pulse inside it with the lever screw"
        % shoe_seal_window_deg,
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
