# -*- coding: utf-8 -*-
"""
Gatling linear breech: fat coax QEV on rails, fixed real barrel, top feed gap.

One station of the rotating pack. The QEV slides on two rails parallel to the
barrel; closed, its stop flange butts the real barrel and the dry fitting sits
inside the bore; open, it pulls back by STROKE so a pellet can drop from +Y
into the breech mouth. Later the same linear unit repeats around the rotor,
fed by a multi-passage rotary union on the pilot lines.

Builds on gatling/fat_coax_qev.py (library). Sketch: rails, carriage, barrel
clamp, AirTAC M3R110 pilot valve, closed assembly + open ghost. The carriage
thumb (a truncated pistol-style pad) presses the AirTAC plunger in the last
millimetres of closing — QEV itself dumps the pilot when the breech seats.
Hopper / rotary union / pack ring not drawn.

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

# Carriage: bushings on the rails + bridge bolted to the rear plug ears (M3 holes).
BUSH_L = 28.0
BUSH_OD = RAIL_OD + 7.0
CARR_T = 8.0                     # bridge thickness behind the rear plug
CARR_EAR_R = EAR_R + 2.0
CARR_BOLT = TIE_HOLE
CARR_WEB = 6.0

# Barrel clamps: two split rings on the real barrel (breech + forward) for coax.
# Both sit on the rails; two points beat one for barrel/QEV alignment.
CLAMP_L = 28.0
CLAMP_OD = BARREL_OD + 14.0
CLAMP_BOLT_R = CLAMP_OD / 2 + 4.0
CLAMP_BOLT = 3.4                 # M3 through the halves
CLAMP_GAP = 1.0                  # split at ±Y so top feed is not blocked by a bridge
CLAMP_SPAN = 70.0                # clear gap between breech clamp and forward collar
BARREL_SHOW = 160.0              # fixed barrel drawn ahead of the breech clamp
# Forward QEV bushings: second rail guide under the chamber front (rear bushings
# stay on the rear-plug bridge). Span along Z ≈ chamber length for coax to the bore.
NOSE_BUSH_L = BUSH_L

# AirTAC M3R110-06 (roller off): same body numbers as pistol/hammer_layout.py.
# Ports swapped like the pistol: supply→R, silencer→P, A→pilot → normally open
# on the pilot (charged at rest, dumps when the plunger is pressed).
AIRTAC = dict(L=46.5, W=18.0, T=27.0, plunger=(6.0, 3.0),
              straight={"A": (10.0, 20.0), "R": (12.0, 22.0)},
              silencer=(8.0, 14.0),
              ports={"A": 23.0, "R": 15.0, "P": 31.0})
VENT_SWITCH = 2.0                # measured click travel on the bench M3R110
VENT_PUSH = 2.5                  # closed thumb over-travel past first contact
VENT_GAP = 0.3                   # free tip clear of the open-approach thumb face
# Thumb: L-shaped pad behind the AirTAC tip. Plunger points -Z; the pad's forward
# face pushes the tip +Z (into the body) as the breech closes — fire only when seated.
THUMB_W, THUMB_H, THUMB_ARM = 16.0, 14.0, 18.0

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

# ---------------------------------------------------------------- rails (bought Al tube)
rails = [
    tube(RAIL_OD, RAIL_OD - 2 * RAIL_WALL, z_rail0, z_rail1, x, y)
    for x, y in rail_centers()
]
rails_s = G.fuse_all(rails)

# ---------------------------------------------------------------- carriage (printed)
# One solid: rear bridge on the plug + vertical webs down to bushings under the tube.
z_bush0 = z_ry - CARR_T - 4.0
z_bush1 = z_bush0 + BUSH_L
bridge = G.cyl(CH_OD + 2.0, z_ry - CARR_T, z_ry)
for a in TIE_ANGLES:
    p = at(TIE_R, a)
    bridge = bridge.fuse(G.cyl(2 * CARR_EAR_R, z_ry - CARR_T, z_ry, p.x, p.y))
# Flat plate under the rear plug spanning both rails, then bushing barrels.
plate = Part.makeBox(2 * RAIL_X + BUSH_OD, BUSH_OD + 2.0, CARR_T,
                     V(-RAIL_X - BUSH_OD / 2, RAIL_Y - BUSH_OD / 2 - 1.0, z_ry - CARR_T))
# Vertical webs from the bridge disc down to the plate (overlap both).
webs = []
for x, y in rail_centers():
    webs.append(Part.makeBox(CARR_WEB, abs(RAIL_Y) + BUSH_OD / 2, CARR_T + 2.0,
                             V(x - CARR_WEB / 2, RAIL_Y - BUSH_OD / 2, z_ry - CARR_T - 1.0)))
    webs.append(G.cyl(BUSH_OD, z_bush0, z_bush1, x, y))
carriage = G.fuse_all([bridge, plate] + webs).removeSplitter()
carriage = carriage.cut(G.fuse_all(
    [G.cyl(CARR_BOLT, z_ry - CARR_T - 1, z_ry + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]
    + [G.cyl(RAIL_HOLE, z_bush0 - 2, z_bush1 + 2, x, y) for x, y in rail_centers()]
)).removeSplitter()

# Forward (nose) bushings under the chamber front — second guide so the fitting
# stays coaxial with the barrel while the breech closes. Bottom saddle only (+Y open).
z_nose1 = z_fs - 2.0
z_nose0 = z_nose1 - NOSE_BUSH_L
y_ch_clear = -CH_OD / 2 - 0.5          # stay below the chamber tube
y_link0 = RAIL_Y - BUSH_OD / 2 - 1.0
nose_parts = []
# Flat plate under the chamber spanning both rails (below the tube OD).
nose_h = y_ch_clear - y_link0
assert nose_h >= 4.0, "no room for nose plate under chamber"
nose_plate = Part.makeBox(2 * RAIL_X + BUSH_OD, nose_h, 10.0,
                          V(-RAIL_X - BUSH_OD / 2, y_link0,
                            (z_nose0 + z_nose1) / 2 - 5.0))
# Half-band under the chamber OD (cut the upper half away).
nose_band = tube(CH_OD + 6.0, CH_OD + 0.5, z_nose0 + 6.0, z_nose1 - 6.0)
nose_band = nose_band.cut(Part.makeBox(CH_OD + 20.0, CH_OD + 20.0, NOSE_BUSH_L,
                                       V(-(CH_OD + 20.0) / 2, 0.0, z_nose0 - 1.0)))
nose_parts.append(nose_plate)
nose_parts.append(nose_band)
for x, y in rail_centers():
    # Web from plate up to rail bushing (stops below chamber).
    web_h = min(abs(RAIL_Y) + BUSH_OD / 2, y_ch_clear - y_link0)
    nose_parts.append(Part.makeBox(CARR_WEB, web_h, 12.0,
                                   V(x - CARR_WEB / 2, y_link0,
                                     (z_nose0 + z_nose1) / 2 - 6.0)))
    # Full bushing barrel, then trim anything that enters the chamber envelope
    # (rail axes sit close under Ø50 — a full Ø15 barrel would nick the tube).
    nb = G.cyl(BUSH_OD, z_nose0, z_nose1, x, y)
    nb = nb.cut(G.cyl(CH_OD + 1.0, z_nose0 - 1, z_nose1 + 1))
    nose_parts.append(nb)
    # Link bar under the rail: ties rear bushings to nose into one printable carriage.
    nose_parts.append(Part.makeBox(CARR_WEB + 2.0, 6.0, z_nose0 - z_bush1 + 2.0,
                                   V(x - (CARR_WEB + 2.0) / 2, y_link0,
                                     z_bush1 - 1.0)))
nose = G.fuse_all(nose_parts).removeSplitter()
nose = nose.cut(G.fuse_all(
    [G.cyl(RAIL_HOLE, z_nose0 - 2, z_nose1 + 2, x, y) for x, y in rail_centers()]
)).removeSplitter()
carriage = carriage.fuse(nose).removeSplitter()

# ---------------------------------------------------------------- AirTAC M3R110 (bought) + L-thumb on carriage
# Plunger points -Z (tip aft). Body toward the barrel. Closing (+Z) drives an L-pad
# whose forward face is behind the tip and pushes it +Z into the body → dump only when seated.
a = AIRTAC
# Closed: pusher face has driven the tip by VENT_PUSH. Free tip sits VENT_PUSH aft of that face.
z_push_closed = z_ry - CARR_T - 4.0          # forward face of the L-pad at closed
z_plunger_free = z_push_closed - VENT_PUSH    # tip at rest (first contact on close)
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

# L-thumb on the carriage: web from the bridge plate down to a forward-facing pad behind the tip.
# Pad's +Z face is at z_push_closed when breech is closed.
thumb_yc = vent_y + a["T"] / 2
# Vertical web: from near the rail plate (y ≈ RAIL_Y) down to the valve centreline.
web_y0, web_y1 = thumb_yc - THUMB_H / 2, RAIL_Y + BUSH_OD / 2 + 1.0
web_z0, web_z1 = z_push_closed - THUMB_ARM, z_ry - CARR_T + 1.0
drop = Part.makeBox(THUMB_W, web_y1 - web_y0, web_z1 - web_z0,
                    V(-THUMB_W / 2, web_y0, web_z0))
# Pad block behind the tip; forward (+Z) face at z_push_closed hits the tip on close.
pad = Part.makeBox(THUMB_W, THUMB_H, THUMB_ARM,
                   V(-THUMB_W / 2, thumb_yc - THUMB_H / 2, z_push_closed - THUMB_ARM))
# Mild lead on the upper edge of the forward face.
lead = Part.makeBox(THUMB_W + 2, THUMB_H / 2 + 1, 8.0,
                    V(-THUMB_W / 2 - 1, thumb_yc - 1, z_push_closed - 0.01))
lead.rotate(V(0, thumb_yc + THUMB_H / 2, z_push_closed), X, -35)
pad = pad.cut(lead)
thumb = drop.fuse(pad).removeSplitter()
carriage = carriage.fuse(thumb).removeSplitter()

# Printed cradle: socket under the rails only (no tall webs into the QEV).
cradle_wall = 3.0
cradle = Part.makeBox(a["W"] + 2 * cradle_wall, a["T"] + cradle_wall, a["L"] + 4.0,
                      V(vent_x - a["W"] / 2 - cradle_wall, vent_y - cradle_wall,
                        z_stem - 2.0))
pocket = Part.makeBox(a["W"] + 0.6, a["T"] + 0.6, a["L"] + 2.0,
                      V(vent_x - a["W"] / 2 - 0.3, vent_y - 0.3, z_stem - 1.0))
cradle = cradle.cut(pocket)
# Open the -Z face for the plunger/thumb; open -Y for the A fitting.
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

# Rails must cover the cradle and the open-pose L-thumb.
z_rail0 = min(z_rail0, z_push_closed - STROKE - THUMB_ARM - RAIL_PAST_REAR, z_stem - RAIL_PAST_REAR)
rails = [
    tube(RAIL_OD, RAIL_OD - 2 * RAIL_WALL, z_rail0, z_rail1, x, y)
    for x, y in rail_centers()
]
rails_s = G.fuse_all(rails)

# ---------------------------------------------------------------- barrel clamps (printed, two halves each)
def make_barrel_clamp(z0, z1, feed_notch=False):
    """Split L/R ring on the barrel with feet on the rails."""
    ring = tube(CLAMP_OD, BARREL_OD + 0.3, z0, z1)
    for sx in (-1, 1):
        lug = G.cyl(8.0, z0, z1, sx * CLAMP_BOLT_R, 0.0).cut(
            G.cyl(CLAMP_BOLT, z0 - 1, z1 + 1, sx * CLAMP_BOLT_R, 0.0))
        ring = ring.fuse(lug)
    for x, y in rail_centers():
        foot = G.cyl(BUSH_OD, z0, z1, x, y).cut(
            G.cyl(RAIL_HOLE, z0 - 1, z1 + 1, x, y))
        web = Part.makeBox(abs(x) - BARREL_OD / 2 + 2, 6.0, z1 - z0,
                           V(min(0.0, x) + (BARREL_OD / 2 - 2 if x < 0 else 0),
                             -3.0, z0))
        ring = ring.fuse(foot).fuse(web)
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

# ---------------------------------------------------------------- QEV solids to slide
qev_closed = {
    "Rear_plug": rp,
    "Seat_ring": sr,
    "Diaphragm": diaphragm,
    "Front_cover": front_cover,
    "Front_yoke": front_yoke,
    "Barrel_stub": barrel_stub,
    "Chamber_tube": chamber,
    "Tie_rods": hardware,
    "Pilot_fitting": fitting,
    "Carriage": carriage,
}
# Drop the library's free-floating real_barrel; this sketch owns the fixed one.


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


qev_open = {n: shifted(s, -STROKE) for n, s in qev_closed.items()} if SHOW_OPEN else {}

# Pellet at the breech mouth when open (drops from +Y into the gap).
pellet_z = z_stop - STROKE / 2.0
pellet = Part.makeSphere(PELLET_D / 2, V(0, 0, pellet_z))

# ---------------------------------------------------------------- checks
qev_body = G.fuse_all([rp, front_cover, chamber, front_yoke, hardware, barrel_stub])
rail_to_qev = rails_s.distToShape(qev_body)[0]
# Bushing: rail axis inside the uncut bushing barrel (the hole voids fail isInside).
bush_ok = all(
    G.cyl(BUSH_OD, z0, z1, x, y).isInside(
        V(x, y, (z0 + z1) / 2), 1e-3, True)
    for x, y in rail_centers()
    for z0, z1 in ((z_bush0, z_bush1), (z_nose0, z_nose1))
)
nose_vs_chamber = nose.distToShape(chamber)[0]
nose_vs_clamp = nose.distToShape(barrel_clamp)[0]
collar_vs_clamp = barrel_collar.distToShape(barrel_clamp)[0]
# Open: fitting tip behind the barrel breech face.
open_cover = qev_open["Front_cover"]
open_tip_z = open_cover.BoundBox.ZMax
open_gap = z_stop - open_tip_z  # ~ STROKE - FIT_INSERT = PELLET_D + margin
# Top feed clear: no rail / carriage above y = 0 in the breech window.
feed_box = Part.makeBox(CH_OD, 80, STROKE + 10,
                        V(-CH_OD / 2, 2.0, z_stop - STROKE - 5))
feed_hit_rail = rails_s.common(feed_box).Volume
feed_hit_carr_open = qev_open["Carriage"].common(feed_box).Volume if SHOW_OPEN else 0.0
# Pack: rails must clear a neighbour module at PACK_PITCH (hex / square).
nbr = qev_body.translated(V(PACK_PITCH, 0, 0))
rail_to_nbr = rails_s.distToShape(nbr)[0]
rail_r_max = max(math.hypot(x, y) + RAIL_OD / 2 for x, y in rail_centers())
# Thumb vs AirTAC: closed presses >= VENT_SWITCH; open clears the free tip.
# Closing (+Z): forward pad face drives the aft-pointing tip into the body.
closed_press = z_push_closed - z_plunger_free      # = VENT_PUSH by construction
open_push_face = z_push_closed - STROKE
open_clear = z_plunger_free - open_push_face       # tip still ahead of the open pad
cradle_vs_closed = cradle.distToShape(qev_body)[0]
vent_vs_rails = vent_body.distToShape(rails_s)[0]
# Sanity: open must NOT press (pad behind tip); closed must press.
press_on_close = closed_press >= VENT_SWITCH and open_clear >= 5.0

checks = [
    ("carriage valid single solid (with thumb + nose)", G.single_solid(carriage)),
    ("barrel clamp valid (may be multi-solid halves)", barrel_clamp.Volume > 1000),
    ("forward barrel collar valid (may be multi-solid halves)", barrel_collar.Volume > 1000),
    ("AirTAC cradle valid single solid", G.single_solid(cradle)),
    ("rails clear of closed QEV body (%.1f mm >= %.1f)" % (rail_to_qev, RAIL_CLEAR),
     rail_to_qev >= RAIL_CLEAR),
    ("carriage has rear+nose bushings on both rail axes", bush_ok),
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
    ("closed: L-pad presses AirTAC >= switch (press %.2f >= %.2f); open clears %.1f mm"
     % (closed_press, VENT_SWITCH, open_clear),
     abs(closed_press - VENT_PUSH) < 1e-6 and press_on_close and SHOW_OPEN),
    ("cradle clear of closed QEV (%.1f mm)" % cradle_vs_closed, cradle_vs_closed >= 0.5),
    ("AirTAC body clear of rails (%.1f mm)" % vent_vs_rails, vent_vs_rails >= 0.5),
]

report = [
    NAME,
    "  station                : fat coax QEV on 2 rails, fixed real barrel, top (+Y) feed",
    "  stroke                 : %.1f mm (fitting %.0f + pellet Ø%.1f + margin %.0f); open tip gap %.1f mm"
    % (STROKE, FIT_INSERT, PELLET_D, STROKE_MARGIN, open_gap if SHOW_OPEN else -1),
    "  rails                  : Al tube Ø%.0f x %.0f, axes (±%.0f, %.1f), z %.0f .. %.0f (%.0f mm)"
    % (RAIL_OD, RAIL_WALL, RAIL_X, RAIL_Y, z_rail0, z_rail1, z_rail1 - z_rail0),
    "  carriage               : rear bushings Ø%.0f x %.0f + nose Ø%.0f x %.0f under chamber; bridge on rear M3"
    % (BUSH_OD, BUSH_L, BUSH_OD, NOSE_BUSH_L),
    "  barrel clamps          : breech + forward (span %.0f), split L/R on Ø%.1f, feet on rails"
    % (CLAMP_SPAN, BARREL_OD),
    "  pilot valve            : AirTAC M3R110 under rails, plunger -Z; L-pad presses %.1f mm on CLOSE"
    " only (switch %.1f); A→pilot" % (VENT_PUSH, VENT_SWITCH),
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
        "Carriage": "stator",
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
        sc.add("Open", "Pellet", pellet, "flow")

    for text, pos in [
        ("ЗАКРЫТО: упор в ствол, фиттинг внутри", (55, 0, z_stop - 5)),
        ("ОТКРЫТО: ход %.0f мм, щель под пульку сверху" % STROKE, (55, 40, z_stop - STROKE / 2)),
        ("РЕЛЬСЫ Ø%.0f x %.0f под модулем (+Y свободен)" % (RAIL_OD, RAIL_WALL),
         (55, RAIL_Y - 15, (z_rail0 + z_rail1) / 2)),
        ("САЛАЗКИ: задние + носовые втулки", (55, 0, (z_bush0 + z_nose1) / 2)),
        ("AirTAC M3R110: сброс только на ЗАКРЫТИИ", (55, vent_y - 20, (z_stem + z_vent1) / 2)),
        ("ХОМУТ У КАЗЁННИКА", (55, 0, z_clamp0 + CLAMP_L / 2)),
        ("НАСАДКА НА СТВОЛЕ (2-я опора)", (55, 0, (z_clamp2_0 + z_clamp2_1) / 2)),
        ("ПОДАЧА ПУЛЬКИ +Y", (0, 50, z_stop - STROKE / 2)),
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

    for n, s, flip in (("carriage", carriage, False),
                       ("barrel_clamp", barrel_clamp, False),
                       ("barrel_collar", barrel_collar, False),
                       ("airtac_cradle", cradle, False)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")

    if not all(ok for _, ok in checks):
        raise SystemExit("gatling linear breech has [FAIL] checks")
