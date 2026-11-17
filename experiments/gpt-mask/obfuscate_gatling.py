# -*- coding: utf-8 -*-
"""
Gatling export: barrels become solid cylinders, the QEV becomes one closed body.

The station still execs the coax file. That copy, and the station's own valve
parts, are geometry: a solid cylinder in place of each barrel (same outside
diameter and length) and one housing with no chamber, bore, port, or groove.
Tie rods stay, so the carriage still finds them. Context only: `in` does not
take either file back. Rebuilt from the live module on each `out`, so the
slot, the stroke and the marble stay where the live station has them.
"""

from __future__ import print_function

import json
import os
import re
import shutil
import subprocess
import tempfile

_DUMP = r"""
import json, os, sys
REPO = os.environ["PACK_REPO"]
OUT = os.environ["PACK_OUT"]
sys.path.insert(0, REPO)

def _housing(ns):
    # Fill the live valve in place. The fillers stay inside the outer skin:
    # chamber wall, stub wall, nose tip, pilot fitting. The yoke shim only
    # bridges the 0.2 mm radial gap and does not pass the ear outline.
    rp, sr, diaphragm = ns["rp"], ns["sr"], ns["diaphragm"]
    front_cover, front_yoke = ns["front_cover"], ns["front_yoke"]
    chamber, barrel_stub, fitting = ns["chamber"], ns["barrel_stub"], ns["fitting"]
    G = ns["G"]
    parts = [rp, sr, diaphragm, front_cover, front_yoke, chamber, barrel_stub, fitting]
    fillers = [
        G.cyl(ns["CH_ID"] + 0.4, chamber.BoundBox.ZMin + 0.2, chamber.BoundBox.ZMax + 0.4),
        G.cyl(ns["BARREL_ID"] + 0.4, barrel_stub.BoundBox.ZMin + 0.2, ns["z_stop"] - 0.15),
        G.cyl(ns["FIT_BORE"] + 0.4, ns["z_stop"] - 2.0, front_cover.BoundBox.ZMax - 0.15),
        G.cyl(ns["G18_TAP_D"] + 0.6, fitting.BoundBox.ZMin + 0.15, rp.BoundBox.ZMax - 0.15),
        G.cyl(ns["CH_OD"] + 0.36, front_yoke.BoundBox.ZMin - 0.3, front_yoke.BoundBox.ZMax + 0.3),
    ]
    housing = parts[0].multiFuse(parts[1:] + fillers).removeSplitter()
    if (not housing.isValid()) or len(housing.Solids) != 1:
        raise SystemExit("housing is not one valid solid")
    return housing

def _span(shape):
    box = shape.BoundBox
    return [box.ZMin, box.ZMax]

def _fail(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    raise SystemExit(msg)

ns_long = {"REPO": REPO, "GATLING_LINEAR_BREECH_LIBRARY": True, "__name__": "station"}
exec(open(os.path.join(REPO, "gatling", "linear_breech.py"), encoding="utf-8").read(), ns_long)
ns_short = {"REPO": REPO, "GATLING_FAT_COAX_LIBRARY": True, "__name__": "pack"}
exec(open(os.path.join(REPO, "gatling", "fat_coax_qev.py"), encoding="utf-8").read(), ns_short)

long_h = _housing(ns_long)
short_h = _housing(ns_short)
V = ns_long["V"]
chamber = ns_long["chamber"]
z_mid = (chamber.BoundBox.ZMin + chamber.BoundBox.ZMax) / 2.0
z_nose = (ns_long["z_stop"] + ns_long["front_cover"].BoundBox.ZMax) / 2.0
for label, shape, pts in (
    ("long", long_h, (
        (0, 0, z_mid), (16, 0, z_mid), (22, 0, z_mid),
        (0, 0, z_nose), (7, 0, z_nose),
        (0, 0, (ns_long["fitting"].BoundBox.ZMin + ns_long["rp"].BoundBox.ZMax) / 2.0),
    )),
    ("short", short_h, (
        (0, 0, (ns_short["chamber"].BoundBox.ZMin + ns_short["chamber"].BoundBox.ZMax) / 2.0),
        (16, 0, (ns_short["chamber"].BoundBox.ZMin + ns_short["chamber"].BoundBox.ZMax) / 2.0),
        (0, 0, ns_short["front_cover"].BoundBox.ZMax - 1.0),
    )),
):
    for x, y, z in pts:
        if not shape.isInside(V(x, y, z), 1e-4, True):
            _fail("%s housing still open at (%.1f, %.1f, %.1f)" % (label, x, y, z))
if ns_long["nose"].distToShape(long_h)[0] < 0.2:
    _fail("housing grew into the nose clamp")
if ns_long["rails_s"].distToShape(long_h)[0] < 2.0:
    _fail("housing grew into the rails")

breech = open(os.path.join(REPO, "gatling", "linear_breech.py"), encoding="utf-8").read()
used = set(__import__("re").findall(r"[A-Za-z_][A-Za-z0-9_]*", breech))
nums = []
for name in sorted(ns_short):
    if not name[:1].isalpha() or name not in used:
        continue
    v = ns_short[name]
    if isinstance(v, bool):
        continue
    if isinstance(v, (int, float)):
        nums.append({"name": name, "repr": repr(v)})
    elif isinstance(v, tuple) and v and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
        nums.append({"name": name, "repr": repr(v)})

def _write(shape, name, solids):
    import Part
    path = os.path.join(OUT, name + ".brep")
    shape.exportBrep(path)
    raw = open(path, encoding="ascii").read()
    back = Part.Shape()
    back.importBrepFromString(raw)
    if abs(back.Volume - shape.Volume) > 1e-3 or not back.isValid() or len(back.Solids) != solids:
        _fail("roundtrip failed for %s (solids %d, valid %s)" % (name, len(back.Solids), back.isValid()))
    return {"name": name, "volume": shape.Volume}

blobs = {
    "hardware": _write(ns_short["hardware"], "hardware", 2),
    "short": _write(short_h, "short", 1),
    "long": _write(long_h, "long", 1),
}
meta = {
    "nums": nums,
    "stub": _span(ns_short["barrel_stub"]),
    "chamber": _span(ns_short["chamber"]),
    "blobs": blobs,
    "barrel_od": ns_short["BARREL_OD"],
    "barrel_show": ns_long["BARREL_SHOW"],
    "chamber_od": ns_short["CH_OD"],
    "chamber_id": ns_short["CH_ID"],
    "fit_bore": ns_short["FIT_BORE"],
    "pilot": ns_short["G18_TAP_D"],
}
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("PACK_OK")
"""


def _wrap(comp):
    """Comma-separated bytes, broken on commas so a later rename cannot join digits."""
    parts = [str(b) for b in comp]
    lines, line, width = [], [], 0
    for p in parts:
        line.append(p)
        width += len(p) + 1
        if width >= 100:
            lines.append(",".join(line))
            line, width = [], 0
    if line:
        lines.append(",".join(line))
    return ",\n".join(lines)


def _replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise ValueError("obfuscate_gatling: %s: expected 1 match, got %d" % (label, text.count(old)))
    return text.replace(old, new, 1)


def _load_blob(path):
    import zlib
    raw = open(path, "rb").read()
    return _wrap(zlib.compress(raw, 9))


def _build():
    freecad = shutil.which("freecadcmd")
    if not freecad:
        raise ValueError("freecadcmd is not on PATH; the housing form is taken from the live module")
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    tmp = tempfile.mkdtemp(prefix="gatling-pack-")
    try:
        script = os.path.join(tmp, "dump.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(_DUMP)
        env = dict(os.environ)
        env["LANG"] = "C.UTF-8"
        env["LC_ALL"] = "C.UTF-8"
        env["PACK_REPO"] = repo
        env["PACK_OUT"] = tmp
        proc = subprocess.run(
            [freecad, script], cwd=repo, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        meta_path = os.path.join(tmp, "meta.json")
        if proc.returncode != 0 or not os.path.exists(meta_path) or "PACK_OK" not in proc.stdout:
            tail = (proc.stdout or "")[-2000:]
            raise ValueError("could not read the housing form\n" + tail)
        meta = json.load(open(meta_path, encoding="utf-8"))
        blobs = {name: _load_blob(os.path.join(tmp, name + ".brep"))
                 for name in ("hardware", "short", "long")}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return meta, blobs


def _coax_source(meta, blobs):
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""One station housing: one solid body, and a solid cylinder for each barrel."""',
        "import math",
        "import zlib",
        "",
        "import FreeCAD as App",
        "import Part",
        "",
        "V = App.Vector",
        "",
    ]
    for item in meta["nums"]:
        if not re.match(r"[A-Za-z_][A-Za-z0-9_]*$", item["name"]):
            raise ValueError("unexpected name %r" % item["name"])
        if not re.match(r"-?[0-9.eE+,() ]+$", item["repr"]):
            raise ValueError("unexpected value for %s" % item["name"])
        lines.append("%s = %s" % (item["name"], item["repr"]))
    stub0, stub1 = meta["stub"]
    ch0, ch1 = meta["chamber"]
    lines += [
        "",
        "def at(r, a_deg, z=0.0):",
        "    a = math.radians(a_deg)",
        "    return V(r * math.cos(a), r * math.sin(a), z)",
        "",
        "def _s(blob):",
        '    raw = zlib.decompress(bytes(int(x) for x in blob.replace("\\n", "").split(",") if x))',
        "    sh = Part.Shape()",
        '    sh.importBrepFromString(raw.decode("ascii"))',
        "    return sh",
        "",
        'hardware = _s("""%s""")' % blobs["hardware"],
        'housing = _s("""%s""")' % blobs["short"],
        "rp = housing",
        "sr = housing.copy()",
        "diaphragm = housing.copy()",
        "front_cover = housing.copy()",
        "front_yoke = housing.copy()",
        "fitting = housing.copy()",
        "barrel_stub = Part.makeCylinder(BARREL_OD / 2.0, %.8f, V(0, 0, %.8f))" % (stub1 - stub0, stub0),
        "chamber = Part.makeCylinder(CH_OD / 2.0, %.8f, V(0, 0, %.8f))" % (ch1 - ch0, ch0),
        "",
    ]
    return "\n".join(lines)


def _station(text, long_blob):
    """Solid cylinders and one housing. The live file is not modified."""
    text = _replace_once(
        text,
        """Gatling linear breech: fat coax QEV on rails, fixed real barrel, top feed gap.

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
""",
        """One station: a carriage on two rails and one solid cylinder.

The housing on the carriage is one solid block. The cylinder ahead of the stop
is solid, the same outside diameter and length. Open, the carriage pulls back
by STROKE so one pellet can drop from +Y into the slot.
""",
        "station docstring",
    )
    text = _replace_once(
        text,
        "chamber = G.cyl(CH_OD, _chamber_z0, _chamber_z0 + CHAMBER_LENGTH).cut(\n"
        "    G.cyl(47.0, _chamber_z0 - 1, _chamber_z0 + CHAMBER_LENGTH + 1)).removeSplitter()",
        "chamber = G.cyl(CH_OD, _chamber_z0, _chamber_z0 + CHAMBER_LENGTH).removeSplitter()",
        "solid chamber",
    )
    text = _replace_once(
        text,
        "barrel_stub = G.cyl(BARREL_OD, barrel_stub.BoundBox.ZMin,\n"
        "                     barrel_stub.BoundBox.ZMax + chamber_extension).cut(\n"
        "    G.cyl(BARREL_ID, barrel_stub.BoundBox.ZMin - 1,\n"
        "          barrel_stub.BoundBox.ZMax + chamber_extension + 1)).removeSplitter()",
        "barrel_stub = G.cyl(BARREL_OD, barrel_stub.BoundBox.ZMin,\n"
        "                     barrel_stub.BoundBox.ZMax + chamber_extension).removeSplitter()",
        "solid stub",
    )
    text = _replace_once(
        text,
        "fixed_barrel = tube(BARREL_OD, BARREL_ID, z_stop, z_stop + BARREL_SHOW)",
        "fixed_barrel = G.cyl(BARREL_OD, z_stop, z_stop + BARREL_SHOW)",
        "solid barrel",
    )
    cradle_start = text.find("# ---------------------------------------------------------------- pellet cradle")
    cradle_end = text.find("# ---------------------------------------------------------------- QEV solids to slide")
    if cradle_start < 0 or cradle_end < 0 or cradle_end <= cradle_start:
        raise ValueError("obfuscate_gatling: pellet cradle block not found")
    housing = (
        "import zlib as _zlib\n"
        "\n"
        "def _load_housing(blob):\n"
        '    raw = _zlib.decompress(bytes(int(x) for x in blob.replace("\\n", "").split(",") if x))\n'
        "    sh = Part.Shape()\n"
        '    sh.importBrepFromString(raw.decode("ascii"))\n'
        "    return sh\n"
        "\n"
        '_housing = _load_housing("""%s""")\n'
        "rp = _housing\n"
        "sr = _housing.copy()\n"
        "diaphragm = _housing.copy()\n"
        "front_cover = _housing.copy()\n"
        "front_yoke = _housing.copy()\n"
        "fitting = _housing.copy()\n"
        "front_cover_feed = _housing.copy()\n"
        "z_tip = z_stop + FIT_INSERT\n"
        "\n"
    ) % long_blob
    text = text[:cradle_start] + housing + text[cradle_end:]
    text = _replace_once(
        text,
        "open_cradle_z1 = z_feed1 - STROKE\n",
        "",
        "drop cradle end",
    )
    text = _replace_once(
        text,
        "# Feed cradle on the cover: tip free, gutter under; OD slips into the barrel.\n"
        "open_tip_fit = z_tip - STROKE\n"
        "pellet_aft = pellet_z - PELLET_D / 2\n"
        "barrel_wall = tube(BARREL_OD + 2.0, BARREL_ID, z_stop, z_stop + BARREL_SHOW)\n"
        "feed_vs_barrel = feed.distToShape(barrel_wall)[0]\n"
        "feed_in_bore = feed.common(\n"
        "    G.cyl(BARREL_ID - 0.05, z_stop, z_tip + CRADLE_PAST_TIP + 1)).Volume\n"
        "drop_col = Part.makeCylinder(PELLET_D / 2 + 1.0, 40.0, V(0, 2.0, pellet_z), Y)\n"
        "open_feed = shifted(feed, -STROKE) if SHOW_OPEN else feed\n"
        "feed_hit_drop = open_feed.common(drop_col).Volume if SHOW_OPEN else 0.0\n"
        "feed_vs_clamp = feed.distToShape(barrel_clamp)[0]\n"
        "# Cover+feed is one solid; gutter stays below the pellet equator.\n"
        "feed_low = feed.BoundBox.YMax <= CRADLE_Y_TOP + 0.2\n",
        "open_tip_fit = z_tip - STROKE\n"
        "pellet_aft = pellet_z - PELLET_D / 2\n"
        "_barrel_axis = fixed_barrel.isInside(V(0, 0, z_stop + BARREL_SHOW / 2.0), 1e-6, True)\n"
        "_barrel_vol = math.pi * (BARREL_OD / 2.0) ** 2 * BARREL_SHOW\n"
        "_housing_axis = front_cover_feed.isInside(\n"
        "    V(0, 0, (chamber.BoundBox.ZMin + chamber.BoundBox.ZMax) / 2.0), 1e-6, True)\n",
        "solid checks",
    )
    text = _replace_once(
        text,
        '    ("+Y drop onto open cradle clear (vol %.0f)" % feed_hit_drop, feed_hit_drop < 1.0),\n'
        '    ("feed cradle stays below pellet equator (Ymax %.1f <= %.1f)"\n'
        '     % (feed.BoundBox.YMax, CRADLE_Y_TOP), feed_low),\n'
        '    ("open tip behind seated pellet (tip %.1f < pellet aft %.1f)"\n'
        '     % (open_tip_fit, pellet_aft),\n'
        '     SHOW_OPEN and open_tip_fit <= pellet_aft + 0.5),\n'
        '    ("feed cradle OD slips into barrel (OD %.1f < ID %.1f; wall clear %.1f)"\n'
        '     % (feed_od, BARREL_ID, feed_vs_barrel),\n'
        '     feed_od <= BARREL_ID - 0.2 and feed_vs_barrel >= 0.15),\n'
        '    ("closed cradle enters the bore (vol %.0f)" % feed_in_bore, feed_in_bore > 50),\n'
        '    ("closed cradle clear of breech clamp (%.1f mm)" % feed_vs_clamp, feed_vs_clamp >= 0.5),\n',
        '    ("fixed barrel is a solid cylinder",\n'
        '     _barrel_axis and abs(fixed_barrel.Volume - _barrel_vol) < 1.0),\n'
        '    ("housing is one solid and its axis is filled",\n'
        '     G.single_solid(front_cover_feed) and _housing_axis and len(front_cover_feed.Solids) == 1),\n'
        '    ("open tip behind seated pellet (tip %.1f < pellet aft %.1f)"\n'
        '     % (open_tip_fit, pellet_aft),\n'
        '     SHOW_OPEN and open_tip_fit <= pellet_aft + 0.5),\n',
        "cradle checks",
    )
    text = _replace_once(
        text,
        '    "  pellet cradle          : on front cover, low gutter OD %.1f past tip by %.0f mm; tip pushes"\n'
        '    % (feed_od, CRADLE_PAST_TIP),\n',
        '    "  barrel                 : solid cylinder OD %.2f x %.0f; housing is one solid"\n'
        '    % (BARREL_OD, BARREL_SHOW),\n',
        "report line",
    )
    return text


def apply(rel, text):
    """Return the masked text for a live-repo path, or text unchanged."""
    if rel not in ("gatling/fat_coax_qev.py", "gatling/linear_breech.py"):
        return text
    cached = getattr(apply, "pack", None)
    if cached is None:
        cached = _build()
        apply.pack = cached
    meta, blobs = cached
    if rel == "gatling/fat_coax_qev.py":
        return _coax_source(meta, blobs)
    return _station(text, blobs["long"])
