# -*- coding: utf-8 -*-
"""
Gatling fat-coaxial QEV sketch: thick short chamber + stub into the real barrel.

Intermediate decision (2026-11-12, docs/gatling.md): coaxial dump like v4.4 in a
50 x 1.5 chamber, not an external bottle. The Gatling module does not carry a
long barrel or a muzzle clamp: a short bought stub runs only through the
chamber, and the front cover (upper lid) takes the stub's stop and turns into a
printed fitting that plugs into the real projectile barrel (25 x 0.6).

Stack from v4.4 (seat ring, diaphragm, rear plug, chamber seals) via OVERRIDE +
library exec of module/stage3v4_coaxial_chamber.py. This file rebuilds the front:
short stub, rods ending on the front yoke, front cover with stub lip + a flat stop
for the real barrel and a plain Ø23.4 x 30 insert (0.2 radial clear, no O-ring —
the dump seals in the module; the real barrel only locates on the fitting).

    CH_OD x CH_WALL = 50 x 1.5 aluminium (nominal ID 47 until a tube is measured)
    CHAMBER_V       = 100 cm3
    TIE_R           = 29, PACK_PITCH = 68 (six around)
    Force path      : seat ring -> stub -> lip in front cover -> yoke -> rods

Run inside FreeCAD / freecadcmd:
    REPO = '/path/to/ratling'
    exec(open(REPO + '/gatling/fat_coax_qev.py').read())

Exports: exports/gatling_fat_coax_qev/
Library: set GATLING_FAT_COAX_LIBRARY = True before exec.
"""
import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    GATLING_FAT_COAX_LIBRARY
except NameError:
    GATLING_FAT_COAX_LIBRARY = False

# Nominal bought tube until a bore is measured (same habit as v4.4's CH_ID).
CH_OD, CH_WALL = 50.0, 1.5
CH_ID = CH_OD - 2 * CH_WALL          # 47.0

# Chamber O-ring: scale the v4.4 29 x 3 @ ID 34.6 up for ID 47 at ~18 % squeeze.
CH_ORING = (42.0, 3.0)

TIE_R = 29.0
PACK_PITCH = 68.0

# Real barrel the module plugs into (bought 25 x 0.6); shown ahead of the stop.
REAL_BARREL_SHOW = 200.0
# Plain printed nose into that bore (PLA: Ø23.4 prints to size; same clear as tube_plug).
# No O-ring: the real barrel only locates; chamber seals stay in the module.
FIT_RADIAL_CLEAR = 0.20
FIT_INSERT = 30.0
FIT_FLANGE_T = 4.0                   # axial thickness of the stop disc ahead of the sleeve
FIT_FLANGE_OVER_BARREL = 3.0         # stop face past the barrel OD (land for the tube end)
FIT_FLANGE_OVER_SLEEVE = 2.5         # and past the cover sleeve, so the butt reads as a rim
FIT_BORE = 18.0                      # dump path; still over seat Ø16 / spigot bore
STUB_LIP_T = 3.0                     # axial land where the stub bottoms in the cover
STUB_PAST_SLEEVE = 1.0               # stub tip this far short of the sleeve's front face

OVERRIDE = {
    "NAME": "gatling_fat_coax_qev",
    "CH_OD": CH_OD,
    "CH_WALL": CH_WALL,
    "CH_ID": CH_ID,
    "CH_ORING": CH_ORING,
    "TIE_R": TIE_R,
    "PACK_PITCH": PACK_PITCH,
    "CHAMBER_V": 100.0,
    "SEAT_D": 16.0,
    # Library still builds a long barrel + muzzle; this file throws them away.
    "MUZZLE_CLAMP": False,
    "BARREL_LEN": 300.0,
}

STAGE3V4_LIBRARY = True
exec(open(os.path.join(REPO, "module", "stage3v4_coaxial_chamber.py"), encoding="utf-8").read())

# stage3v4 left FreeCAD / Part / G / FV / V / Z / X and the valve solids in this namespace.
NAME = "gatling_fat_coax_qev"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- stub + front cover (upper lid)
fit_body_r = BARREL_ID / 2 - FIT_RADIAL_CLEAR          # Ø23.4, plain, no groove
# Stop disc must clear both the barrel OD and the cover sleeve, or it reads as flush.
fit_flange_r = max(BARREL_OD / 2 + FIT_FLANGE_OVER_BARREL, fp_out_r + FIT_FLANGE_OVER_SLEEVE)
lip_r = BARREL_ID / 2 + 0.2                            # stub end in a shallow counterbore

# Stub bottoms just inside the front plug's sleeve; cover continues into the fitting.
z_stub_end = z_fp_end - STUB_PAST_SLEEVE
z_lip1 = z_stub_end + STUB_LIP_T
BARREL_STUB_LEN = z_stub_end - z_sh
# Stop disc sits ahead of the sleeve; its FRONT face is the real-barrel butt.
z_flange0 = max(z_fp_end, z_lip1) + 0.5
z_stop = z_flange0 + FIT_FLANGE_T                      # barrel end butts here
z_fit1 = z_stop + FIT_INSERT                           # plain nose into the real barrel

# Front cover: v4.4 front-plug body through the sleeve, then stop disc + plain insert.
# Stub lip is a solid ring in the bore (seat push: stub -> lip -> cover -> yoke -> rods).
# At z_stop the OD steps fit_flange_r -> fit_body_r: that annulus is the barrel stop.
front_cover = revolve([
    (sock_r, z_fp_tip), (spigot_r - LEAD_CHAMFER, z_fp_tip), (spigot_r, z_fp_tip + LEAD_CHAMFER),
    (spigot_r, z_tf), (CH_OD / 2, z_tf), (CH_OD / 2, z_fs),
    (fp_out_r, z_fs + (CH_OD / 2 - fp_out_r)), (fp_out_r, z_fp_end),
    (fit_flange_r, z_fp_end), (fit_flange_r, z_stop),
    (fit_body_r, z_stop), (fit_body_r, z_fit1 - LEAD_CHAMFER),
    (fit_body_r - LEAD_CHAMFER, z_fit1), (0, z_fit1),
    (0, z_fp_tip), (sock_r, z_fp_tip),
]).removeSplitter()
# Through-bore: sock over the stub up to the lip, then FIT_BORE through lip + fitting.
front_cover = front_cover.cut(G.fuse_all([
    cyl(2 * sock_r, z_fp_tip - 1, z_stub_end + 0.01),
    cyl(2 * lip_r, z_stub_end - 0.01, z_lip1 + 0.01),
    cyl(FIT_BORE, z_lip1 - 0.01, z_fit1 + 1),
]))
# Same chamber / barrel O-ring grooves as the v4.4 front plug.
front_cover = front_cover.cut(G.fuse_all([fp_groove, fp_bgroove])).removeSplitter()

barrel_stub = tube(BARREL_OD, BARREL_ID, z_sh, z_stub_end)
real_barrel = tube(BARREL_OD, BARREL_ID, z_stop, z_stop + REAL_BARREL_SHOW)

# Rods end on the front yoke only — no muzzle ear.
z_front = z_fy1
_stick = WASHER_T + NUT_T + 2.0
z_rod0, z_rod1 = z_ry - _stick, z_front + _stick
tie_len = z_rod1 - z_rod0


def rods_yoke():
    """Both tie rods with a washer and a nut on the rear plug and the front yoke."""
    bits = []
    for a in TIE_ANGLES:
        x, y = at(TIE_R, a)[:2]
        bits.append(cyl(TIE_D, z_rod0, z_rod1, x, y))
        for z_face, toward in ((z_ry, -1), (z_fy1, +1)):
            z_w0 = z_face if toward > 0 else z_face - WASHER_T
            z_w1 = z_face + WASHER_T if toward > 0 else z_face
            bits.append(cyl(WASHER_D, z_w0, z_w1, x, y))
            z_n0 = z_w1 if toward > 0 else z_w0 - NUT_T
            z_n1 = z_w1 + NUT_T if toward > 0 else z_w0
            bits.append(cyl(NUT_AF / math.cos(math.pi / 6), z_n0, z_n1, x, y))
    return G.fuse_all(bits)


hardware = rods_yoke()

# Ball sits in the real barrel, just ahead of the fitting tip (projectile tube).
ball = Part.makeSphere(BARREL_ID / 2, V(0, 0, z_fit1 + BARREL_ID / 2 + 0.5))

# Chamber + stub + seat-spigot rings only; fitting into the real barrel is dry.
orings_g = G.fuse_all([
    torus(ch_root_r + CH_ORING[1] / 2, CH_ORING[1], rp_groove_z[0] + GROOVE_W * CH_ORING[1] / 2),
    torus(ch_root_r + CH_ORING[1] / 2, CH_ORING[1], fp_groove_z[1] - GROOVE_W * CH_ORING[1] / 2),
    torus(sp_root_r + SP_ORING[1] / 2, SP_ORING[1], z_spg2 - GROOVE_W * SP_ORING[1] / 2),
    torus(br_root_r - BR_ORING[1] / 2, BR_ORING[1], fp_bgroove_z[1] - GROOVE_W * BR_ORING[1] / 2),
])

# ---------------------------------------------------------------- checks (valve body from v4.4 + new front)
A_annulus = area(CH_ID) - area(BARREL_OD)
F_stub = F_ring                                          # seat push into the stub at 5 bar
# Lip as an annulus shear/bearing bound on STUB_LIP_T * pi * (sock_r^2 - lip_r^2) — use bearing on land.
lip_bearing = F_stub / max(math.pi * (sock_r ** 2 - lip_r ** 2), 1e-6)   # MPa if F in N, mm2
fit_wall = fit_body_r - FIT_BORE / 2
module_len = z_fit1 - z_ry

checks = [
    ("rear plug, seat ring, front cover valid single solids",
     all(G.single_solid(s) for s in (rp, sr, front_cover))),
    ("rear plug / diaphragm / seat ring clear (bead and the proud seat aside)",
     G.no_overlap(sr.cut(cyl(2 * seat_out_r + 0.2, -1, 0)), diaphragm) and G.no_overlap(sr, rp) and
     G.no_overlap(rp.cut(cyl(CH_ID + 2, z_f, 1)), diaphragm)),
    ("stop lip lands on the rear plug's face (squeeze %.0f %%)" % (DIA_SQUEEZE * 100),
     abs(sr.BoundBox.ZMin - z_f) < 1e-6 and G.no_overlap(sr, rp.cut(cyl(2 * BEAD_R + 2, z_f, 1)))),
    ("seat %.0f %% of the barrel bore" % (A_seat / A_bore * 100), A_seat >= 0.4 * A_bore),
    ("seat curtain >= 0.7 x seat (lift %.1f: %.0f mm2)" % (LIFT, A_curtain), A_curtain >= 0.7 * A_seat),
    ("chamber annulus round the socket >= 1.3 x the curtain (%.0f vs %.0f mm2)" % (A_sock_annulus, A_curtain),
     A_sock_annulus >= 1.3 * A_curtain),
    ("gallery entry over the clamp ring >= 1.5 x seat (%.0f mm2)" % A_entry, A_entry >= 1.5 * A_seat),
    ("opens after the pilot loses <= 55 %% (%.0f %%)" % (open_ratio * 100), open_ratio >= 0.45),
    ("diaphragm stretch at full lift <= 30 %% (%.0f %%)" % (dia_strain * 100), dia_strain <= 0.30),
    ("chamber %.0f cm3 within 3 %% of target" % chamber_v, abs(chamber_v - CHAMBER_V) <= 0.03 * CHAMBER_V),
    ("tie rods: M3 at %.0f MPa with rear plug and seat ring pushing at once (%.0f + %.0f N at %.0f bar)"
     % (TIE_SIGMA, F_rp, F_ring, P_MAX_BAR), TIE_SIGMA <= 150.0),
    ("rear plug's ears bend at <= 20 MPa at %.0f bar (%.0f)" % (P_MAX_BAR, YOKE_SIGMA), YOKE_SIGMA <= 20.0),
    ("front yoke on the front cover's flange, clear of the cover", abs(front_yoke.BoundBox.ZMin - z_fs) < 1e-6
     and z_fy1 <= z_fp_end and G.no_overlap(front_yoke, front_cover)),
    ("tie rods clear of the tube and the plugs",
     TIE_R - TIE_HOLE / 2 >= CH_OD / 2 + 0.3 and G.no_overlap(hardware, G.fuse_all([chamber, rp, front_cover]))),
    ("pack: footprint >= %.1f mm off the neighbours' (hex %.1f, square %.1f)"
     % (PACK_CLEAR, pack_gap["hex"], pack_gap["square"]), min(pack_gap.values()) >= PACK_CLEAR),
    ("chamber O-ring stretch 0..6 %% (%.1f %%)" % (ch_stretch * 100), 0 <= ch_stretch <= 0.06),
    ("barrel O-ring stretch 0..6 %% (%.1f %%)" % (br_stretch * 100), 0 <= br_stretch <= 0.06),
    ("spigot O-ring stretch 0..6 %% (%.1f %%)" % (sp_stretch * 100), 0 <= sp_stretch <= 0.06),
    ("stub bottoms on the cover lip, clear of the seat ring",
     abs(barrel_stub.BoundBox.ZMax - z_stub_end) < 1e-6 and G.no_overlap(sr, barrel_stub)),
    ("stub lip covers the tube wall (%.2f mm radial), bearing <= 25 MPa at %.0f bar (%.1f)"
     % (sock_r - lip_r, P_MAX_BAR, lip_bearing),
     sock_r - lip_r >= BARREL_WALL - 0.05 and lip_bearing <= 25.0),
    ("fitting: plain (no O-ring), wall >= 1.5 mm, insert %.0f mm, bore >= seat" % FIT_INSERT,
     fit_wall >= 1.5 and FIT_INSERT >= 20.0 and FIT_BORE >= SEAT_D),
    ("fitting clear of the stub; stop disc clear of the real barrel OD",
     z_stop >= z_stub_end and G.no_overlap(front_cover, barrel_stub)
     and G.no_overlap(front_cover.common(cyl(2 * fit_flange_r + 2, z_flange0 - 0.5, z_stop + 0.01)),
                      real_barrel)),
    ("real barrel butts on the stop face (land %.1f past tube, rim %.1f past sleeve), fitting inside"
     % (fit_flange_r - BARREL_OD / 2, fit_flange_r - fp_out_r),
     abs(real_barrel.BoundBox.ZMin - z_stop) < 1e-6
     and fit_flange_r >= BARREL_OD / 2 + FIT_FLANGE_OVER_BARREL - 1e-9
     and fit_flange_r >= fp_out_r + FIT_FLANGE_OVER_SLEEVE - 1e-9
     and front_cover.BoundBox.ZMax <= z_fit1 + 1e-6
     and abs((front_cover.BoundBox.ZMax - z_stop) - FIT_INSERT) < LEAD_CHAMFER + 1e-3),
    ("no muzzle part: rods end on the front yoke (z_front = z_fy1)", abs(z_front - z_fy1) < 1e-9),
    ("front cover no wider than the chamber tube on the spigot (O-ring cone)",
     front_cover.BoundBox.XMax <= max(CH_OD / 2, fit_flange_r) + 1e-6),
]

report = [
    NAME,
    "  flow path              : seat Ø%.0f (%.0f mm2 = %.0f %% of the Ø%.1f bore), curtain %.0f at lift %.1f,"
    " annulus round the socket %.0f, gallery entry %.0f"
    % (SEAT_D, A_seat, A_seat / A_bore * 100, BARREL_ID, A_curtain, LIFT, A_sock_annulus, A_entry),
    "  chamber                : %.0f cm3, tube %.0f x %.1f aluminium, %.0f mm long, %.0f g"
    % (chamber_v, CH_OD, CH_WALL, chamber_len, (area(CH_OD) - area(CH_ID)) * chamber_len * 2.70e-3),
    "  module                 : Ø%.0f (ears %.0f across), %.0f mm long rear plug to fitting tip; stub %.0f mm;"
    " no muzzle clamp" % (CH_OD, 2 * (TIE_R + EAR_R), module_len, BARREL_STUB_LEN),
    "  force path             : seat ring -> stub -> lip in front cover -> front yoke -> rods;"
    " seat push %.0f N at %.0f bar" % (F_stub, P_MAX_BAR),
    "  stub / real barrel     : stub 25 x 0.6 x %.0f through the chamber, bottoms in the cover;"
    " flat stop Ø%.1f (tube butts), plain fitting Ø%.1f x %.0f into the real barrel (bore Ø%.0f, no O-ring)"
    % (BARREL_STUB_LEN, 2 * fit_flange_r, 2 * fit_body_r, FIT_INSERT, FIT_BORE),
    "  tie rods               : 2 x M3 x %.0f at R%.1f, %.0f / %.0f deg; nuts on rear plug and front yoke only"
    % (tie_len, TIE_R, *TIE_ANGLES),
    "  pack                   : pitch %.0f; %.1f mm to neighbours (hex), %.1f (square)"
    % (PACK_PITCH, pack_gap["hex"], pack_gap["square"]),
    "  O-rings                : 2 x %g x %g (chamber), 1 x %g x %g (stub in cover), 1 x %g x %g (seat spigot);"
    " fitting dry" % (CH_ORING + BR_ORING + SP_ORING),
    "  rear plug / seat ring / front cover: %.1f / %.1f / %.1f cm3"
    % (rp.Volume / 1000, sr.Volume / 1000, front_cover.Volume / 1000),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]

if not GATLING_FAT_COAX_LIBRARY:
    print("\n".join(report))
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Rear_plug", rp, "stator"), ("Seat_ring", sr, "rotor"), ("Diaphragm", diaphragm, "shoe"),
                        ("Front_cover", front_cover, "stator"), ("Front_yoke", front_yoke, "stator")):
        sc.add("Printed", n, s, style)
    for n, s, style in (("Barrel_stub", barrel_stub, "ghost"), ("Real_barrel", real_barrel, "ghost"),
                        ("Chamber_tube", chamber, "ghost"), ("ORings", orings_g, "oring"),
                        ("Pilot_fitting", fitting, "steel"), ("Ball", ball, "flow"),
                        ("Tie_rods", hardware, "steel")):
        sc.add("Bought", n, s, style)
    half = Part.makeBox(120, 60, 1200, V(-60, -60, -600))
    for n in ("Rear_plug", "Seat_ring", "Diaphragm", "Front_cover", "Barrel_stub", "Real_barrel",
              "Chamber_tube", "ORings", "Ball", "Pilot_fitting", "Front_yoke", "Tie_rods"):
        style = dict(Rear_plug="stator", Seat_ring="rotor", Diaphragm="shoe", Front_cover="stator",
                     ORings="oring", Ball="flow", Pilot_fitting="steel", Front_yoke="stator",
                     Tie_rods="steel").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)
    for text, pos in [
        ("ОБРЕЗОК 25x0,6, %.0f мм" % BARREL_STUB_LEN, (-45, 0, z_sh + BARREL_STUB_LEN * 0.55)),
        ("КАМЕРА: труба %.0fx%.1f, %.0f мм, %.0f см3" % (CH_OD, CH_WALL, chamber_len, chamber_v),
         (45, 0, z_tf * 0.5)),
        ("КРЫШКА: упор обрезка + упор ствола", (45, 0, z_tf + 8)),
        ("УПОР СТВОЛА Ø%.1f" % (2 * fit_flange_r), (45, 0, z_stop - FIT_FLANGE_T / 2)),
        ("ФИТТИНГ Ø%.1f x %.0f без кольца" % (2 * fit_body_r, FIT_INSERT), (45, 0, z_stop + FIT_INSERT * 0.45)),
        ("СТВОЛ (снаряд) 25x0,6", (45, 0, z_stop + REAL_BARREL_SHOW * 0.55)),
        ("КОЛЬЦО СЕДЛА: седло Ø%.0f" % SEAT_D, (45, 0, 10)),
        ("МЕМБРАНА Ø%.1f" % (2 * DIA_R), (45, 0, 0)),
        ("ЗАДНЯЯ ПРОБКА с ушами: пилот G1/8 -> M3R110 A", (45, 0, z_rp)),
        ("2 шпильки M3 x %.0f (до ярма крышки)" % tie_len, (45, 0, z_ry - 5)),
    ]:
        sc.label("Labels", text, pos)
    sc.add("Jig", "Jig_guide", jig_guide, "stator", offset=V(-3 * CH_OD, 0, z_rp))
    sc.label("Labels", "ШАБЛОН для сверления мембраны", (-3 * CH_OD, 0, z_rp + 15))
    sc.finish(hidden_groups=("Section",), opaque_groups=("Section",))
    doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, flip=False):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for n, s, flip in (("rear_plug", rp, False), ("seat_ring", sr, False), ("front_cover", front_cover, True),
                       ("diaphragm", diaphragm_free, False), ("jig_guide", jig_guide, False),
                       ("front_yoke", front_yoke, True), ("oring_cone", oring_cone, True)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
