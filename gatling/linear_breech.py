# -*- coding: utf-8 -*-
"""
Gatling linear breech: fat coax QEV on rails, fixed real barrel, top feed gap.

One station of the rotating pack. The QEV slides on two rails parallel to the
barrel; closed, its stop flange butts the real barrel and the dry fitting sits
inside the bore; open, it pulls back by STROKE so a pellet can drop from +Y
into the breech mouth. Later the same linear unit repeats around the rotor,
fed by a multi-passage rotary union on the pilot lines.

Builds on gatling/fat_coax_qev.py (library). Sketch: rails, carriage, barrel
clamps, front-cover pellet cradle, AirTAC M3R110 pilot valve, closed + open
ghost. The AirTAC tip is pressed by hand / by the mechanism (the carriage's
L-thumb auto-press is gone since 2026-11-15). Hopper /
rotary union / pack ring not drawn.

Run inside FreeCAD / freecadcmd:
    REPO = '/path/to/ratling'
    exec(open(REPO + '/gatling/linear_breech.py').read())

Exports: exports/gatling_linear_breech/
Library: set GATLING_LINEAR_BREECH_LIBRARY = True before exec.
"""
import importlib
import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
try:
    GATLING_LINEAR_BREECH_LIBRARY
except NameError:
    GATLING_LINEAR_BREECH_LIBRARY = False
# Pack variant of the station (breech_pack / breech_mechanism set it before exec):
# the carriage and the nose guide stand on round feet around each rail, like the
# barrel clamps, instead of one plate spanning both rails (two neighbours' plates
# meet at the pack axis below R ~73; feet clear from R ~66.3), and the rails end
# at the muzzle. Library only: a standalone run writes the STLs the bench plates
# use, so it always builds the bench variant, even if a console still holds True.
try:
    PACK_STATION
except NameError:
    PACK_STATION = False
if not GATLING_LINEAR_BREECH_LIBRARY:
    PACK_STATION = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech")
NAME = "gatling_linear_breech"

# ---------------------------------------------------------------- load QEV as library
GATLING_FAT_COAX_LIBRARY = True
exec(open(os.path.join(REPO, "gatling", "fat_coax_qev.py")).read(), globals())
# fat_coax overwrites OUT_DIR / NAME; put them back for this sketch.
OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech")
NAME = "gatling_linear_breech"

# Length adaptation keeps the rear seat fixed and shifts the complete front end.
CHAMBER_LENGTH = 200.0
_chamber_z0, _chamber_old_z1 = chamber.BoundBox.ZMin, chamber.BoundBox.ZMax
chamber_extension = CHAMBER_LENGTH - chamber.BoundBox.ZLength
chamber = G.cyl(CH_OD, _chamber_z0, _chamber_z0 + CHAMBER_LENGTH).cut(
    G.cyl(47.0, _chamber_z0 - 1, _chamber_z0 + CHAMBER_LENGTH + 1)).removeSplitter()
for _front_part in (front_cover, front_yoke):
    _front_part.translate(V(0, 0, chamber_extension))
barrel_stub = G.cyl(BARREL_OD, barrel_stub.BoundBox.ZMin,
                     barrel_stub.BoundBox.ZMax + chamber_extension).cut(
    G.cyl(BARREL_ID, barrel_stub.BoundBox.ZMin - 1,
          barrel_stub.BoundBox.ZMax + chamber_extension + 1)).removeSplitter()
# Retain the original end hardware; extend only the straight M3 tie-rod spans.
_tie_cut_z = 40.0
_tie_rear = hardware.common(Part.makeBox(100, 100, _tie_cut_z + 100, V(-50, -50, -100)))
_tie_front = hardware.common(Part.makeBox(100, 100, 300, V(-50, -50, _tie_cut_z)))
_tie_front.translate(V(0, 0, chamber_extension))
_tie_links = [G.cyl(3.0, _tie_cut_z - 0.1, _tie_cut_z + chamber_extension + 0.1,
                   at(TIE_R, a).x, at(TIE_R, a).y) for a in TIE_ANGLES]
hardware = G.fuse_all([_tie_rear, _tie_front] + _tie_links).removeSplitter()
z_fs += chamber_extension
z_stop += chamber_extension

# ---------------------------------------------------------------- breech parameters
# Stroke: fitting fully out + gap for a ØBARREL_ID pellet to drop past the stop face.
PELLET_D = BARREL_ID
STROKE_MARGIN = 12.0
STROKE = FIT_INSERT + PELLET_D + STROKE_MARGIN

# Two aluminium tubes under the module (+Y is the feed side, kept clear).
# Keep them tight under the Ø50 tube so a hex pack at PACK_PITCH still clears.
RAIL_OD, RAIL_WALL = 8.0, 1.0
RAIL_HOLE = 8.3                  # printed bushing
RAIL_CLEAR = 0.5                 # rail OD to QEV solids
RAIL_X = 12.0                    # half-spacing under the chamber
RAIL_Y = -(CH_OD / 2 + RAIL_OD / 2 + 1.0)
RAIL_PAST_REAR = 20.0            # rail behind open rear plug
RAIL_PAST_FRONT = 40.0           # rail ahead of barrel clamp

# Carriage: plain rail bores in its plate + bridge bolted to the rear plug ears (M3 holes).
BUSH_L = 28.0
BUSH_OD = RAIL_OD + 7.0
CARR_T = 8.0                     # bridge thickness behind the rear plug
CARR_EAR_R = EAR_R + 2.0
CARR_BOLT = TIE_HOLE
CARR_WEB = 6.0
NOSE_GAP = 1.0                   # nose clamp split at Y=0 (as the barrel clamps)
PILOT_PASS_D = 17.0              # bridge hole round the pilot fitting (hex AF 13 = 15.0 over the corners)

# The bridge sits on the studs between the plug ears and the rear washers. Until
# 2026-11-21 the washers and nuts were drawn on the ears, inside the bridge (112 mm3),
# and the studs were CARR_T short: move them aft by the bridge, lengthen the studs.
_hw_aft = hardware.common(Part.makeBox(100, 100, 100, V(-50, -50, z_ry - 100)))
_hw_fwd = hardware.common(Part.makeBox(100, 100, 400, V(-50, -50, z_ry)))
_hw_aft.translate(V(0, 0, -CARR_T))
hardware = G.fuse_all([_hw_aft, _hw_fwd] + [G.cyl(TIE_D, z_ry - CARR_T - 0.1, z_ry + 0.1, at(TIE_R, a).x, at(TIE_R, a).y)
                                            for a in TIE_ANGLES]).removeSplitter()
STUD_L = tie_len + chamber_extension + CARR_T

# Barrel clamps: two split rings on the real barrel (breech + forward) for coax.
# Both sit on the rails; two points beat one for barrel/QEV alignment.
# Flush M3 through the ring wall (no external bolt lugs) — hex pack neighbour
# gap is then set by clamp OD / yoke ears, not by tangential lug ears.
CLAMP_L = 28.0
CLAMP_OD = BARREL_OD + 14.0
CLAMP_BOLT = 3.4                 # M3 through the halves
CLAMP_BOLT_X = 0.25 * (BARREL_OD + 0.3 + CLAMP_OD)  # mid-wall, ±X
CLAMP_GAP = 1.0                  # split at Y=0 (top/bottom); feed on +Y
CLAMP_SPAN = 70.0                # minimum; adjusted below for the fixed barrel length
# Fixed barrel drawn ahead of the breech clamp. Override before exec (breech_pack 2×).
try:
    BARREL_SHOW
except NameError:
    BARREL_SHOW = 400.0
CLAMP_SPAN = max(CLAMP_SPAN, BARREL_SHOW - 2 * CLAMP_L - 34.0)
# Nose guide: second rail station under the chamber front (the rear one stays on the
# rear-plug bridge). Its own part now - a clamp on the Al chamber tube, 2 x M3.
NOSE_BUSH_L = BUSH_L

# Pellet cradle fused into the front cover (one print with the QEV lid). Fitting
# fills the bore, so the gutter lives ahead of the tip only — a low half-pipe
# bonded onto the tip nose. Open well below the pellet equator so the tip can
# shove the pellet without the walls pinching it (the old separate tip-cup did).
CRADLE_RADIAL = 0.35             # gutter OD under BARREL_ID
CRADLE_WALL = 2.2                # half-pipe wall; ID cradles the pellet
CRADLE_PAST_TIP = PELLET_D + 2.0
CRADLE_BOND = 4.0                # overlap onto the tip nose
CRADLE_Y_TOP = -2.0              # keep walls below the pellet equator (no pinch)

# AirTAC M3R110-06 (roller off): same body numbers as pistol/hammer_layout.py.
# Ports swapped like the pistol: supply→R, silencer→P, A→pilot → normally open
# on the pilot (charged at rest, dumps when the plunger is pressed).
AIRTAC = dict(L=46.5, W=18.0, T=27.0, plunger=(6.0, 3.0),
              straight={"A": (10.0, 20.0), "R": (12.0, 22.0)},
              silencer=(8.0, 14.0),
              ports={"A": 23.0, "R": 15.0, "P": 31.0})
VENT_PUSH = 2.5                  # AirTAC tip sits this far aft of the closed plate's rear face

# Open/closed: closed at fat_coax pose; open = QEV translated -Z by STROKE.
SHOW_OPEN = True

X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector


def at_xy(x, y, z=0.0):
    return V(x, y, z)


def tube(od, idd, z0, z1, x=0.0, y=0.0):
    return G.cyl(od, z0, z1, x, y).cut(G.cyl(idd, z0 - 1, z1 + 1, x, y))


def rail_centers():
    return ((-RAIL_X, RAIL_Y), (RAIL_X, RAIL_Y))


# Closed pose: barrel breech face at z_stop (from fat_coax).
z_clamp0 = z_stop
z_clamp1 = z_clamp0 + CLAMP_L
# Forward collar further along the real barrel (same print as the breech clamp).
z_clamp2_0 = z_clamp1 + CLAMP_SPAN
z_clamp2_1 = z_clamp2_0 + CLAMP_L
z_rail0 = (z_ry - STROKE) - RAIL_PAST_REAR
z_rail1 = z_clamp2_1 + RAIL_PAST_FRONT
if PACK_STATION:
    # In the pack the rails end in the front barrel-plate, not 6 mm past the muzzle.
    z_rail1 = min(z_rail1, z_stop + BARREL_SHOW)

# ---------------------------------------------------------------- rails (bought Al tube)
rails = [
    tube(RAIL_OD, RAIL_OD - 2 * RAIL_WALL, z_rail0, z_rail1, x, y)
    for x, y in rail_centers()
]
rails_s = G.fuse_all(rails)

# ---------------------------------------------------------------- carriage (printed, rear pusher)
# The Al rails are the tubes: the carriage rides them through plain bores in its
# plate - no printed sleeve barrels, they only duplicated the rails. The bridge
# sandwiches on the QEV tie studs between the rear washers and the plug ears.
bridge = G.cyl(CH_OD + 2.0, z_ry - CARR_T, z_ry)
for a in TIE_ANGLES:
    p = at(TIE_R, a)
    bridge = bridge.fuse(G.cyl(2 * CARR_EAR_R, z_ry - CARR_T, z_ry, p.x, p.y))
if PACK_STATION:
    # Pack: a round foot around each rail bore (subset of the bench plate).
    plate = G.fuse_all([G.cyl(BUSH_OD, z_ry - CARR_T, z_ry, x, y) for x, y in rail_centers()])
else:
    # Flat plate under the rear plug spanning both rails; the rail bores run through it.
    plate = Part.makeBox(2 * RAIL_X + BUSH_OD, BUSH_OD + 2.0, CARR_T,
                         V(-RAIL_X - BUSH_OD / 2, RAIL_Y - BUSH_OD / 2 - 1.0, z_ry - CARR_T))
# Vertical webs from the bridge disc down to the plate (overlap both). They stop on the
# bridge's front face: until 2026-11-21 they ran 1 mm on into the rear plug (262 mm3).
# In the pack they stop on its aft face too, where the valve bracket seats (2026-11-21).
webs = []
_web_aft = 0.0 if PACK_STATION else 1.0
for x, y in rail_centers():
    webs.append(Part.makeBox(CARR_WEB, abs(RAIL_Y) + BUSH_OD / 2, CARR_T + _web_aft,
                             V(x - CARR_WEB / 2, RAIL_Y - BUSH_OD / 2, z_ry - CARR_T - _web_aft)))
carriage = G.fuse_all([bridge, plate] + webs).removeSplitter()
# Through the bridge: the studs, the rails and (since 2026-11-21) the pilot fitting in the
# middle of the plug, which went through the solid bridge (1071 mm3).
carriage = carriage.cut(G.fuse_all(
    [G.cyl(CARR_BOLT, z_ry - CARR_T - 1, z_ry + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]
    + [G.cyl(RAIL_HOLE, z_ry - CARR_T - 1, z_ry + 1, x, y) for x, y in rail_centers()]
    + [G.cyl(PILOT_PASS_D, z_ry - CARR_T - 2, z_ry + 1)]
)).removeSplitter()

# ---------------------------------------------------------------- nose guide (printed, clamps the chamber)
# Second rail guide under the chamber front, now its own part: the long link bars
# that used to tie it to the rear carriage are gone (they only duplicated the rails
# and actually clashed with them). Like the barrel clamps, it grips the Al chamber
# tube - split at Y=0, 2 x M3 through the side walls - and rides the rails through
# plain bores in its skirt plate.
z_nose1 = z_fs - 2.0
z_nose0 = z_nose1 - NOSE_BUSH_L
y_ch_clear = -CH_OD / 2 - 0.5          # stay below the chamber tube
y_link0 = RAIL_Y - BUSH_OD / 2 - 1.0
z_mid = (z_nose0 + z_nose1) / 2
nose_parts = []
# Skirt plate under the chamber spanning both rails (below the tube OD).
nose_h = y_ch_clear - y_link0
assert nose_h >= 4.0, "no room for nose skirt under chamber"
nose_plate = Part.makeBox(2 * RAIL_X + BUSH_OD, nose_h, 10.0,
                          V(-RAIL_X - BUSH_OD / 2, y_link0, z_mid - 5.0))
# Lower clamp half: band under the chamber OD (cut above -NOSE_GAP / 2).
nose_band = tube(CH_OD + 6.0, CH_OD + 0.5, z_nose0 + 6.0, z_nose1 - 6.0)
nose_band = nose_band.cut(Part.makeBox(CH_OD + 20.0, CH_OD + 20.0, NOSE_BUSH_L,
                                       V(-(CH_OD + 20.0) / 2, -NOSE_GAP / 2, z_nose0 - 1.0)))
if PACK_STATION:
    # Pack: a round foot around each bore instead of the skirt plate; it runs into
    # the band, so the chamber bore is cut through it below.
    nose_parts += [G.cyl(BUSH_OD, z_mid - 5.0, z_mid + 5.0, x, y) for x, y in rail_centers()]
else:
    nose_parts.append(nose_plate)
nose_parts.append(nose_band)
for x, y in rail_centers():
    # Web at each rail: thickens the skirt around the bore (stops below the band).
    nose_parts.append(Part.makeBox(CARR_WEB, nose_h, 12.0,
                                   V(x - CARR_WEB / 2, y_link0, z_mid - 6.0)))
nose_lower = G.fuse_all(nose_parts).removeSplitter()
if PACK_STATION:
    # A foot keeps ~3 mm above its bore, so no lip slot; clear the chamber tube.
    _nose_cuts = ([G.cyl(RAIL_HOLE, z_nose0 - 2, z_nose1 + 2, x, y) for x, y in rail_centers()]
                  + [G.cyl(CH_OD + 0.5, z_nose0 - 2, z_nose1 + 2)])
else:
    _nose_cuts = (
        [G.cyl(RAIL_HOLE, z_nose0 - 2, z_nose1 + 2, x, y) for x, y in rail_centers()]
        # Open each bore's top through the skirt edge: the chamber sits 1 mm above the
        # rail, too close for a printable 0.35 mm lip; the rail stays captured ~300 deg.
        + [Part.makeBox(RAIL_HOLE + 1.0, 0.7, NOSE_BUSH_L + 4.0,
                        V(x - (RAIL_HOLE + 1.0) / 2, RAIL_Y + RAIL_HOLE / 2 - 0.5, z_nose0 - 2.0))
           for x, y in rail_centers()])
nose_lower = nose_lower.cut(G.fuse_all(_nose_cuts)).removeSplitter()
# Upper clamp half: the closing ring over the tube (+Y side).
nose_upper = tube(CH_OD + 6.0, CH_OD + 0.5, z_nose0 + 6.0, z_nose1 - 6.0)
nose_upper = nose_upper.cut(Part.makeBox(CH_OD + 20.0, CH_OD + 20.0, NOSE_BUSH_L,
                                         V(-(CH_OD + 20.0) / 2, NOSE_GAP / 2 - (CH_OD + 20.0), z_nose0 - 1.0)))
# 2 x M3 through the ring side walls at +-X (mid-wall), closing the halves on the tube.
_nose_bolt_r = (CH_OD + 0.5 + CH_OD + 6.0) / 4.0
for _s in (-1.0, 1.0):
    _bolt = Part.makeCylinder(TIE_HOLE / 2, CH_OD + 8.0,
                              V(_s * _nose_bolt_r, -(CH_OD + 8.0) / 2, z_mid), V(0, 1, 0))
    nose_lower = nose_lower.cut(_bolt)
    nose_upper = nose_upper.cut(_bolt)
# The QEV tie studs (r TIE_R) run past the band (outer r 28): a channel each, since
# 2026-11-21 (the band took 0.5 mm of each stud, 24 mm3). Cut again after anything is
# fused onto the halves (the bench's link journal sits on the 30 deg stud).
nose_rod_cut = G.fuse_all([G.cyl(TIE_HOLE, z_nose0 - 1, z_nose1 + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES])
nose_lower = nose_lower.cut(nose_rod_cut)
nose_upper = nose_upper.cut(nose_rod_cut)
nose_lower = nose_lower.removeSplitter()
nose_upper = nose_upper.removeSplitter()
nose = Part.makeCompound([nose_lower, nose_upper])

# ---------------------------------------------------------------- AirTAC M3R110 (bought)
# Plunger points -Z (tip aft). Body toward the barrel. The carriage used to carry an
# L-thumb that pushed the tip +Z over the last VENT_PUSH of closing (dump only when
# seated); removed 2026-11-15 - the pilot is now dumped by hand / by the mechanism.
a = AIRTAC
# Tip reference: the valve stays put, its tip VENT_PUSH aft of the closed plate's rear face.
z_push_closed = z_ry - CARR_T - 4.0          # closed-carriage reference face (was the L-pad's)
z_plunger_free = z_push_closed - VENT_PUSH + 16.5  # manual valve, ahead of carriage sweep
z_stem = z_plunger_free + a["plunger"][1]     # stem face (plunger roots here, points -Z)
z_vent1 = z_stem + a["L"]                     # forward end of the body (toward barrel)
# Body under the rails, clear of +Y feed.
vent_x, vent_y = 0.0, RAIL_Y - RAIL_OD / 2 - a["T"] - 3.0
vent_body = Part.makeBox(a["W"], a["T"], a["L"],
                         V(vent_x - a["W"] / 2, vent_y, z_stem))
# Plunger sticking -Z from the stem face.
vent_plunger = Part.makeCylinder(a["plunger"][0] / 2, a["plunger"][1] + 0.01,
                                 V(vent_x, vent_y + a["T"] / 2, z_stem), V(0, 0, -1))


def _port_z(name):
    # Port heights measured from the plunger/stem face toward the body (same catalog numbers).
    return z_stem + a["ports"][name]


fit = []
od, stick = a["straight"]["A"]
fit.append(Part.makeCylinder(od / 2, stick,
                             V(vent_x, vent_y, _port_z("A")), V(0, -1, 0)))
od, stick = a["straight"]["R"]
fit.append(Part.makeCylinder(od / 2, stick,
                             V(vent_x, vent_y + a["T"], _port_z("R")), V(0, 1, 0)))
fit.append(Part.makeCylinder(a["silencer"][0] / 2, a["silencer"][1],
                             V(vent_x, vent_y + a["T"], _port_z("P")), V(0, 1, 0)))
vent_fittings = Part.makeCompound(fit)
vent_valve = Part.makeCompound([vent_body, vent_fittings, vent_plunger])

# Printed cradle: socket under the rails only (no tall webs into the QEV).
cradle_wall = 3.0
cradle = Part.makeBox(a["W"] + 2 * cradle_wall, a["T"] + cradle_wall, a["L"] + 4.0,
                      V(vent_x - a["W"] / 2 - cradle_wall, vent_y - cradle_wall,
                        z_stem - 2.0))
pocket = Part.makeBox(a["W"] + 0.6, a["T"] + 0.6, a["L"] + 2.0,
                      V(vent_x - a["W"] / 2 - 0.3, vent_y - 0.3, z_stem - 1.0))
cradle = cradle.cut(pocket)
# Open the -Z face for the plunger; open -Y for the A fitting.
cradle = cradle.cut(Part.makeBox(a["W"] + 4, a["T"] + 10, 24,
                                 V(vent_x - a["W"] / 2 - 2, vent_y - 8, z_stem - 18)))
cradle = cradle.cut(Part.makeBox(a["W"] + 4, 30, 16,
                                 V(vent_x - a["W"] / 2 - 2, vent_y - 25, _port_z("A") - 8)))
# Clips onto the rails from below only (top of clip = rail axis → clear of the Ø50 tube).
rail_bottom = RAIL_Y - RAIL_OD / 2
for x, y in rail_centers():
    # Half-cradle under the tube: up to the rail centreline, bored for the tube.
    clip_h = (y - rail_bottom) + RAIL_OD / 2 + 0.5   # stops at ~rail axis
    clip = Part.makeBox(BUSH_OD, clip_h, 16.0,
                        V(x - BUSH_OD / 2, rail_bottom - 1.0, z_stem + 4.0))
    clip = clip.cut(G.cyl(RAIL_HOLE, z_stem + 3, z_stem + 21, x, y))
    strap = Part.makeBox(6.0, max(1.0, y - vent_y - 2.0), 10.0,
                         V(x - 3.0, vent_y + 1.0, z_stem + 6.0))
    cradle = cradle.fuse(clip).fuse(strap)
cradle = cradle.removeSplitter()

# Rails must cover the cradle and the open carriage's plate.
z_rail0 = min(z_rail0, z_ry - CARR_T - 1 - STROKE - RAIL_PAST_REAR, z_stem - RAIL_PAST_REAR)
rails = [
    tube(RAIL_OD, RAIL_OD - 2 * RAIL_WALL, z_rail0, z_rail1, x, y)
    for x, y in rail_centers()
]
rails_s = G.fuse_all(rails)

# ---------------------------------------------------------------- barrel clamps (printed, two halves each)
def make_barrel_clamp(z0, z1, feed_notch=False):
    """Top/bottom split ring on the barrel with feet on the rails."""
    ring = tube(CLAMP_OD, BARREL_OD + 0.3, z0, z1)
    for x, y in rail_centers():
        foot = G.cyl(BUSH_OD, z0, z1, x, y).cut(
            G.cyl(RAIL_HOLE, z0 - 1, z1 + 1, x, y))
        web = Part.makeBox(6.0, -RAIL_Y - 10.0, z1 - z0,
                           V(x - 3.0, RAIL_Y, z0))
        ring = ring.fuse(foot).fuse(web)
    ring = ring.cut(G.cyl(BARREL_OD + 0.3, z0 - 1, z1 + 1))
    for x, y in rail_centers():
        ring = ring.cut(G.cyl(RAIL_HOLE, z0 - 1, z1 + 1, x, y))
    # Cross bolts behind the feed notch pull the upper/lower halves together.
    for sx in (-1, 1):
        ring = ring.cut(Part.makeCylinder(CLAMP_BOLT / 2, CLAMP_OD + 2,
                        V(sx * CLAMP_BOLT_X, -CLAMP_OD / 2 - 1, z1 - 5.0), Y))
    kerf = Part.makeBox(CLAMP_OD * 2, CLAMP_GAP, (z1 - z0) + 4,
                        V(-CLAMP_OD, -CLAMP_GAP / 2, z0 - 2))
    ring = ring.cut(kerf)
    if feed_notch:
        # Top notch at the breech so +Y feed stays visible.
        ring = ring.cut(Part.makeBox(BARREL_OD + 8, CLAMP_OD, 20,
                                     V(-(BARREL_OD + 8) / 2, 0, z0 - 2)))
    return ring.removeSplitter()


barrel_clamp = make_barrel_clamp(z_clamp0, z_clamp1, feed_notch=True)
barrel_collar = make_barrel_clamp(z_clamp2_0, z_clamp2_1, feed_notch=False)

# Fixed real barrel (bought), breech face at z_stop, held by both clamps.
fixed_barrel = tube(BARREL_OD, BARREL_ID, z_stop, z_stop + BARREL_SHOW)

# ---------------------------------------------------------------- pellet cradle (part of front cover)
# Half-pipe ahead of the tip + a solid lower bond onto the tip nose, fused into
# the cover. Named feed_* so it does not clash with the AirTAC cradle above.
# Walls stay below CRADLE_Y_TOP so the tip (not the gutter) drives the pellet.
feed_od = BARREL_ID - 2 * CRADLE_RADIAL
feed_id = max(6.0, feed_od - 2 * CRADLE_WALL)
z_tip = z_stop + FIT_INSERT
z_feed0 = z_tip - CRADLE_BOND
z_feed1 = z_tip + CRADLE_PAST_TIP


def _low_half(shape, z0, z1):
    """Cut everything above CRADLE_Y_TOP between z0 and z1."""
    return shape.cut(Part.makeBox(
        feed_od + 4.0, feed_od + 4.0, (z1 - z0) + 4.0,
        V(-(feed_od + 4.0) / 2, CRADLE_Y_TOP, z0 - 2.0)))


# Past-tip gutter: half-pipe the pellet sits on.
feed = _low_half(tube(feed_od, feed_id, z_tip, z_feed1), z_tip, z_feed1)
# Bond pad: solid lower crescent overlapping the tip nose wall (keep FIT_BORE open).
bond = _low_half(G.cyl(feed_od, z_feed0, z_tip), z_feed0, z_tip)
bond = bond.cut(G.cyl(FIT_BORE, z_feed0 - 1.0, z_tip + 1.0))
feed = feed.fuse(bond).removeSplitter()
# Cover with feed cradle (breech-station lid; standalone fat_coax cover unchanged).
front_cover_feed = front_cover.fuse(feed).removeSplitter()

# ---------------------------------------------------------------- QEV solids to slide
qev_closed = {
    "Rear_plug": rp,
    "Seat_ring": sr,
    "Diaphragm": diaphragm,
    "Front_cover": front_cover_feed,
    "Front_yoke": front_yoke,
    "Barrel_stub": barrel_stub,
    "Chamber_tube": chamber,
    "Tie_rods": hardware,
    "Pilot_fitting": fitting,
    "Carriage": carriage,
    "Nose_clamp": nose,
}
# Drop the library's free-floating real_barrel; this sketch owns the fixed one.


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


qev_open = {n: shifted(s, -STROKE) for n, s in qev_closed.items()} if SHOW_OPEN else {}

# Pellet on the open cradle, ahead of the open fitting tip.
pellet_z = (z_tip + PELLET_D / 2) - STROKE
# Pellet geometry omitted; its nominal size only defines the future feed envelope.

# ---------------------------------------------------------------- checks
qev_body = G.fuse_all([rp, front_cover_feed, chamber, front_yoke, hardware, barrel_stub])
rail_to_qev = rails_s.distToShape(qev_body)[0]
# Guides: the rails pass clean through both plates (plain bores, no printed
# sleeves) and keep a wall of material below each bore. The probe rod is a touch
# under the bore: a same-size cylinder leaves boolean slivers on coincident faces.
_probe = RAIL_HOLE - 0.2
_pass_rear = [G.cyl(_probe, z_ry - CARR_T + 1, z_ry - 1, x, y) for x, y in rail_centers()]
_pass_nose = [G.cyl(_probe, z_nose0 + 9.0, z_nose1 - 9.0, x, y) for x, y in rail_centers()]
bush_ok = (all(p.common(carriage).Volume < 1e-4 for p in _pass_rear)
           and all(p.common(nose_lower).Volume < 1e-4 for p in _pass_nose)
           and all(carriage.isInside(V(x, RAIL_Y - RAIL_HOLE / 2 - 1.5, z_ry - CARR_T / 2), 1e-3, True)
                   for x, y in rail_centers())
           and all(nose_lower.isInside(V(x, RAIL_Y - RAIL_HOLE / 2 - 1.5, (z_nose0 + z_nose1) / 2), 1e-3, True)
                   for x, y in rail_centers()))
# The rails must not touch either guide anywhere else (the old link bars
# overlapped the rail tubes by ~1050 mm3 along their whole length).
rail_clash = rails_s.common(carriage).Volume + rails_s.common(nose).Volume
nose_vs_chamber = nose.distToShape(chamber)[0]
# The carriage on the plug: round the pilot fitting, short of the plug, ahead of the
# stud washers; the nose clamp round the studs (all overlaps until 2026-11-21).
carr_on_plug = (carriage.common(fitting).Volume, carriage.common(rp).Volume, carriage.common(hardware).Volume)
carr_pilot_gap = carriage.distToShape(fitting)[0]
nose_on_studs = nose.common(hardware).Volume
nose_vs_clamp = nose.distToShape(barrel_clamp)[0]
collar_vs_clamp = barrel_collar.distToShape(barrel_clamp)[0]
# Open: fitting tip behind the barrel breech face (not cover bbox — cradle leads the tip).
open_tip_z = z_tip - STROKE
open_gap = z_stop - open_tip_z  # ~ STROKE - FIT_INSERT = PELLET_D + margin
open_cradle_z1 = z_feed1 - STROKE
# Top feed clear: no rail / carriage above y = 0 in the breech window.
feed_box = Part.makeBox(CH_OD, 80, STROKE + 10,
                        V(-CH_OD / 2, 2.0, z_stop - STROKE - 5))
feed_hit_rail = rails_s.common(feed_box).Volume
feed_hit_carr_open = (qev_open["Carriage"].common(feed_box).Volume
                      + qev_open["Nose_clamp"].common(feed_box).Volume) if SHOW_OPEN else 0.0
# Pack: rails must clear a neighbour module at PACK_PITCH (hex / square).
nbr = qev_body.translated(V(PACK_PITCH, 0, 0))
rail_to_nbr = rails_s.distToShape(nbr)[0]
rail_r_max = max(math.hypot(x, y) + RAIL_OD / 2 for x, y in rail_centers())
airtac_cradle_vs_qev = cradle.distToShape(qev_body)[0]
vent_vs_rails = vent_body.distToShape(rails_s)[0]
# Feed cradle on the cover: tip free, gutter under; OD slips into the barrel.
open_tip_fit = z_tip - STROKE
pellet_aft = pellet_z - PELLET_D / 2
barrel_wall = tube(BARREL_OD + 2.0, BARREL_ID, z_stop, z_stop + BARREL_SHOW)
feed_vs_barrel = feed.distToShape(barrel_wall)[0]
feed_in_bore = feed.common(
    G.cyl(BARREL_ID - 0.05, z_stop, z_tip + CRADLE_PAST_TIP + 1)).Volume
drop_col = Part.makeCylinder(PELLET_D / 2 + 1.0, 40.0, V(0, 2.0, pellet_z), Y)
open_feed = shifted(feed, -STROKE) if SHOW_OPEN else feed
feed_hit_drop = open_feed.common(drop_col).Volume if SHOW_OPEN else 0.0
feed_vs_clamp = feed.distToShape(barrel_clamp)[0]
# Cover+feed is one solid; gutter stays below the pellet equator.
feed_low = feed.BoundBox.YMax <= CRADLE_Y_TOP + 0.2

checks = [
    ("chamber tube is valid and 200 mm long", G.single_solid(chamber) and abs(chamber.BoundBox.ZLength - CHAMBER_LENGTH) < 1e-6),
    ("extended barrel stub valid single solid", G.single_solid(barrel_stub)),
    ("extended tie rods valid two solids", hardware.isValid() and len(hardware.Solids) == 2),
    ("fixed barrel matches requested length", G.single_solid(fixed_barrel) and abs(fixed_barrel.BoundBox.ZLength - BARREL_SHOW) < 1e-6),
    ("carriage (rear pusher) valid single solid", G.single_solid(carriage)),
    ("nose clamp: lower half single solid", G.single_solid(nose_lower)),
    ("nose clamp: upper half single solid", G.single_solid(nose_upper)),
    ("barrel clamp valid two connected halves", barrel_clamp.isValid() and len(barrel_clamp.Solids) == 2),
    ("forward barrel collar valid two connected halves", barrel_collar.isValid() and len(barrel_collar.Solids) == 2),
    ("front cover+feed cradle valid single solid", G.single_solid(front_cover_feed)),
    ("AirTAC cradle valid single solid", G.single_solid(cradle)),
    ("rails clear of closed QEV body (%.1f mm >= %.1f)" % (rail_to_qev, RAIL_CLEAR),
     rail_to_qev >= RAIL_CLEAR),
    ("carriage + nose clamp have plain rail bores at both stations", bush_ok),
    ("rails pass clean through both guides (clash %.2f mm3)" % rail_clash, rail_clash < 0.01),
    ("carriage on the plug: pilot fitting through its bridge (%.2f mm, %.2f mm3), plug %.2f mm3,"
     " stud washers and nuts behind it %.2f mm3 (studs 2 x M3 x %.0f)"
     % (carr_pilot_gap, carr_on_plug[0], carr_on_plug[1], carr_on_plug[2], STUD_L),
     max(carr_on_plug) < 0.01 and carr_pilot_gap >= 0.5),
    ("nose clamp clear of the tie studs (%.2f mm3)" % nose_on_studs, nose_on_studs < 0.01),
    ("nose saddle clear of chamber (%.1f mm)" % nose_vs_chamber, nose_vs_chamber >= 0.2),
    ("nose bushings clear of breech clamp (%.1f mm)" % nose_vs_clamp, nose_vs_clamp >= 0.5),
    ("forward collar clear of breech clamp (%.1f mm span)" % collar_vs_clamp,
     collar_vs_clamp >= CLAMP_SPAN - 1.0),
    ("stroke extracts the fitting: open tip z %.1f <= breech %.1f (gap %.1f >= pellet+margin %.1f)"
     % (open_tip_z, z_stop, open_gap, PELLET_D + STROKE_MARGIN - 0.5),
     SHOW_OPEN and open_tip_z <= z_stop + 1e-3
     and open_gap >= PELLET_D + STROKE_MARGIN - 0.5),
    ("stroke = fitting + pellet + margin (%.1f = %.1f + %.1f + %.1f)"
     % (STROKE, FIT_INSERT, PELLET_D, STROKE_MARGIN),
     abs(STROKE - (FIT_INSERT + PELLET_D + STROKE_MARGIN)) < 1e-6),
    ("+Y feed window clear of rails (vol %.0f)" % feed_hit_rail, feed_hit_rail < 1.0),
    ("+Y feed window clear of open carriage (vol %.0f)" % feed_hit_carr_open,
     feed_hit_carr_open < 1.0),
    ("+Y drop onto open cradle clear (vol %.0f)" % feed_hit_drop, feed_hit_drop < 1.0),
    ("feed cradle stays below pellet equator (Ymax %.1f <= %.1f)"
     % (feed.BoundBox.YMax, CRADLE_Y_TOP), feed_low),
    ("open tip behind seated pellet (tip %.1f < pellet aft %.1f)"
     % (open_tip_fit, pellet_aft),
     SHOW_OPEN and open_tip_fit <= pellet_aft + 0.5),
    ("feed cradle OD slips into barrel (OD %.1f < ID %.1f; wall clear %.1f)"
     % (feed_od, BARREL_ID, feed_vs_barrel),
     feed_od <= BARREL_ID - 0.2 and feed_vs_barrel >= 0.15),
    ("closed cradle enters the bore (vol %.0f)" % feed_in_bore, feed_in_bore > 50),
    ("closed cradle clear of breech clamp (%.1f mm)" % feed_vs_clamp, feed_vs_clamp >= 0.5),
    ("rails clear of neighbour at pack pitch (%.1f mm >= %.1f; envelope R %.1f)"
     % (rail_to_nbr, RAIL_CLEAR, rail_r_max),
     rail_to_nbr >= RAIL_CLEAR),
    ("closed stop face at barrel breech (z_stop %.1f)" % z_stop,
     abs(fixed_barrel.BoundBox.ZMin - z_stop) < 1e-6),
    ("breech clamp holds the barrel OD (hole ~Ø%.1f)" % (BARREL_OD + 0.3),
     barrel_clamp.BoundBox.ZMin <= z_clamp0 + 1e-3 and barrel_clamp.BoundBox.ZMax >= z_clamp1 - 1e-3),
    ("forward collar on barrel (z %.0f .. %.0f)" % (z_clamp2_0, z_clamp2_1),
     barrel_collar.BoundBox.ZMin <= z_clamp2_0 + 1e-3
     and barrel_collar.BoundBox.ZMax >= z_clamp2_1 - 1e-3
     and z_clamp2_1 <= z_stop + BARREL_SHOW + 1e-3),
    ("AirTAC cradle clear of closed QEV (%.1f mm)" % airtac_cradle_vs_qev,
     airtac_cradle_vs_qev >= 0.5),
    ("AirTAC body clear of rails (%.1f mm)" % vent_vs_rails, vent_vs_rails >= 0.5),
    ("open nose clears manual valve cradle", shifted(nose, -STROKE).distToShape(cradle)[0] >= 0.5),
    ("manual valve and cradle ahead of rear carriage sweep",
     min(s.BoundBox.ZMin for s in (cradle, vent_body, vent_fittings, vent_plunger))
     >= carriage.BoundBox.ZMax + 0.5),
]

report = [
    NAME,
    "  station                : fat coax QEV on 2 rails, fixed real barrel, top (+Y) feed",
    "  stroke                 : %.1f mm (fitting %.0f + pellet Ø%.1f + margin %.0f); open tip gap %.1f mm"
    % (STROKE, FIT_INSERT, PELLET_D, STROKE_MARGIN, open_gap if SHOW_OPEN else -1),
    "  rails                  : Al tube Ø%.0f x %.0f, axes (±%.0f, %.1f), z %.0f .. %.0f (%.0f mm)"
    % (RAIL_OD, RAIL_WALL, RAIL_X, RAIL_Y, z_rail0, z_rail1, z_rail1 - z_rail0),
    "  carriage               : rear pusher (plain rail bores in the %s, bridge on the tie studs)"
    " + nose clamp 2xM3 on the chamber (bores in its %s); no sleeves, no link bars"
    % (("feet", "feet") if PACK_STATION else ("plate", "skirt")),
    "  tie studs              : 2 x M3 x %.0f: plug ears | carriage bridge %.0f | washer | nut; Ø%.0f hole"
    " in the bridge round the pilot fitting" % (STUD_L, CARR_T, PILOT_PASS_D),
    "  barrel clamps          : breech + forward (span %.0f), split L/R on Ø%.1f, feet on rails"
    % (CLAMP_SPAN, BARREL_OD),
    "  pellet cradle          : on front cover, low gutter OD %.1f past tip by %.0f mm; tip pushes"
    % (feed_od, CRADLE_PAST_TIP),
    "  pilot valve            : AirTAC M3R110 under rails, plunger -Z; A→pilot;"
    " no auto-press on the carriage (L-thumb removed 2026-11-15) - dump by hand / mechanism",
    "  pack                   : pitch %.0f, rail envelope R %.1f, clear to neighbour %.1f mm"
    % (PACK_PITCH, rail_r_max, rail_to_nbr),
    "  not drawn              : hopper, rotary union / supply hose to R, crank for the stroke",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
if not GATLING_LINEAR_BREECH_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- scene + export
if not GATLING_LINEAR_BREECH_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc

    styles_qev = {
        "Rear_plug": "stator", "Seat_ring": "rotor", "Diaphragm": "shoe",
        "Front_cover": "stator", "Front_yoke": "stator", "Barrel_stub": "ghost",
        "Chamber_tube": "ghost", "Tie_rods": "steel", "Pilot_fitting": "steel",
        "Carriage": "stator", "Nose_clamp": "rotor",
    }
    for n, s in qev_closed.items():
        sc.add("Closed", n, s, styles_qev.get(n, "stator"))
    sc.add("Fixed", "Rails", rails_s, "steel")
    sc.add("Fixed", "Barrel_clamp", barrel_clamp, "stator")
    sc.add("Fixed", "Barrel_collar", barrel_collar, "stator")
    sc.add("Fixed", "Fixed_barrel", fixed_barrel, "ghost")
    sc.add("Fixed", "AirTAC_cradle", cradle, "stator")
    sc.add("Bought", "AirTAC_body", vent_body, "steel")
    sc.add("Bought", "AirTAC_fittings", vent_fittings, "ghost")
    sc.add("Bought", "AirTAC_plunger", vent_plunger, "shoe")
    if SHOW_OPEN:
        for n, s in qev_open.items():
            sc.add("Open", "Open_" + n, s, "ghost")

    for text, pos in [
        ("ЗАКРЫТО: упор в ствол, жёлоб крышки в канале", (55, 0, z_stop - 5)),
        ("ОТКРЫТО: пулька на жёлобе крышки, ход %.0f мм" % STROKE, (55, 40, pellet_z)),
        ("РЕЛЬСЫ Ø%.0f x %.0f под модулем (+Y свободен)" % (RAIL_OD, RAIL_WALL),
         (55, RAIL_Y - 15, (z_rail0 + z_rail1) / 2)),
        ("САЛАЗКИ: задний толкатель + носовой хомут (2×M3)", (55, 0, (z_ry - CARR_T + z_nose1) / 2)),
        ("AirTAC M3R110: сброс пилота — нажим руками / механизмом", (55, vent_y - 20, (z_stem + z_vent1) / 2)),
        ("ХОМУТ У КАЗЁННИКА", (55, 0, z_clamp0 + CLAMP_L / 2)),
        ("НАСАДКА НА СТВОЛЕ (2-я опора)", (55, 0, (z_clamp2_0 + z_clamp2_1) / 2)),
        ("ЖЁЛОБ НА КРЫШКЕ QEV: сброс +Y → фиттинг толкает", (0, 45, pellet_z)),
    ]:
        sc.label("Labels", text, pos)

    sc.finish(hidden_groups=("Labels",), opaque_groups=())
    doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, flip=False):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.15).write(
            os.path.join(OUT_DIR, name + ".stl"))

    # Cover: flange/chamber face on the bed (no flip — tip-down overhangs more).
    # Clamps and AirTAC cradle: +Z on the bed.
    for n, s, flip in (("carriage", carriage, False),
                       ("nose_clamp", nose, False),
                       ("barrel_clamp", barrel_clamp, True),
                       ("barrel_collar", barrel_collar, True),
                       ("front_cover_feed", front_cover_feed, False),
                       # 2026-11-22: the bench prints the cover without the gutter (the pellet tray leaves the
                       # QEV's nose; where it goes is open). The pack's model still carries the gutter.
                       ("front_cover_plain", front_cover, False),
                       ("airtac_cradle", cradle, True)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")

    if not all(ok for _, ok in checks):
        raise SystemExit("gatling linear breech has [FAIL] checks")
