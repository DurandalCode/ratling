#!/usr/bin/env python3
"""Build Bambu Studio .3mf projects from part manifests, by print group.

    python3 tools/make_plates.py [--pool] [MANIFEST ...]
    python3 tools/make_plates.py --list
    python3 tools/make_plates.py --dry-run stage3v4 pistol
    python3 tools/make_plates.py --check stage3v4

Manifests live in plates/*.json (see plates/README hints in docs/print.md).
Each part names a print group from tools/print_profiles.py. Same-group parts
share one project; Bambu's arrange packs them onto plates that fill as the
set grows. --pool merges matching groups across the selected manifests into
one project per (group, nozzle, filament, extras); without it each manifest
keeps its own projects (<id>_<group>).

Also accepts a pistol-style exports/*/parts.json (groups + parts list) by
path or by the shortcut name "pistol" (-> exports/pistol_build/parts.json).

Plain Python, no FreeCAD. Slicing needs Bambu Studio on macOS
(tools/print_plate.py). --dry-run / --list / plan output work anywhere.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import OrderedDict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import print_profiles
import orient_check

PLATES_DIR = os.path.join(REPO, "plates")
PRINT_PLATE = os.path.join(REPO, "tools", "print_plate.py")

# Shortcut names that are not plates/*.json files: alias -> (project id, path).
# The id is the <id>_<group> prefix (pistol_build_airtight, ...).
ALIASES = {
    "pistol": ("pistol_build", os.path.join(REPO, "exports", "pistol_build", "parts.json")),
}


def _load_json(path):
    with open(path) as f:
        return json.load(f)


def discover_manifests():
    """Sorted list of (id, path) for every plates/*.json."""
    if not os.path.isdir(PLATES_DIR):
        return []
    out = []
    for name in sorted(os.listdir(PLATES_DIR)):
        if name.endswith(".json"):
            out.append((name[:-5], os.path.join(PLATES_DIR, name)))
    return out


def resolve_targets(names):
    """Turn CLI names into (id, path) pairs. Empty names -> all plates/*.json."""
    if not names:
        found = discover_manifests()
        if not found:
            raise SystemExit("no manifests in plates/ and no names given")
        return found
    out = []
    known = dict(discover_manifests())
    for name in names:
        if name in ALIASES:
            mid, path = ALIASES[name]
            out.append((mid, path))
            continue
        if name in known:
            out.append((name, known[name]))
            continue
        path = name if os.path.isabs(name) else os.path.join(REPO, name)
        if os.path.isfile(path):
            stem = os.path.splitext(os.path.basename(path))[0]
            out.append((stem, path))
            continue
        raise SystemExit("unknown manifest %r (try --list)" % name)
    return out


def _as_part_rows(mid, data, path):
    """Normalise a plates/*.json or a pistol parts.json into part dicts."""
    # Pistol / export_parts style.
    if "parts" in data and "groups" in data and "id" not in data and "export" not in data:
        rows = []
        for p in data["parts"]:
            stl = p["stl"]
            if not os.path.isabs(stl):
                stl = os.path.join(REPO, stl)
            rows.append({
                "manifest": mid,
                "name": p.get("name") or os.path.splitext(os.path.basename(stl))[0],
                "stl": stl,
                "group": p["group"],
                "count": int(p.get("count") or 1),
                "nozzle": str(p.get("nozzle") or "0.4"),
                "filament": None,          # take the group's default
                "project": None,
                "extra": [],
                "allow_overhang": p.get("allow_overhang"),
                "source": path,
            })
            # Bridged pockets: pistol puts allow-overhang in BRIDGED; parts.json
            # may carry orientation only. Keep a hook if present.
            if p.get("allow_overhang") is not None:
                rows[-1]["extra"] = ["--allow-overhang", str(p["allow_overhang"])]
        return rows

    # plates/*.json style.
    mid = data.get("id") or mid
    export = data.get("export")
    if export and not os.path.isabs(export):
        export = os.path.join(REPO, export)
    rows = []
    for raw in data.get("parts") or []:
        if isinstance(raw, str):
            raise SystemExit("%s: part %r must be an object with file+group" % (path, raw))
        file_ = raw.get("file") or raw.get("stl")
        if not file_:
            raise SystemExit("%s: part missing file/stl: %r" % (path, raw))
        file_path, _, count_s = file_.partition(":")
        count = int(raw.get("count") or count_s or 1)
        if os.path.isabs(file_path):
            stl = file_path
        elif export and not file_path.startswith("exports" + os.sep) and not file_path.startswith("exports/"):
            stl = os.path.join(export, file_path)
        else:
            stl = os.path.join(REPO, file_path)
        stl = os.path.normpath(stl)
        group = raw.get("group")
        if not group:
            raise SystemExit("%s: part %s has no group" % (path, file_))
        if group not in print_profiles.PROFILES:
            raise SystemExit("%s: part %s: unknown group %r" % (path, file_, group))
        extra = list(raw.get("extra") or [])
        # Convenience keys -> print_plate flags. Skip values already in the
        # group's profile so pool_<group> names stay clean.
        prof_opts = print_profiles.PROFILES[group]["opts"]

        def _prof_val(flag):
            if flag in prof_opts:
                i = prof_opts.index(flag)
                if i + 1 < len(prof_opts) and not str(prof_opts[i + 1]).startswith("--"):
                    return str(prof_opts[i + 1])
            return None

        if raw.get("infill") and str(raw["infill"]) != _prof_val("--infill"):
            extra += ["--infill", str(raw["infill"])]
        if raw.get("pattern") and str(raw["pattern"]) != _prof_val("--pattern"):
            extra += ["--pattern", str(raw["pattern"])]
        if raw.get("walls") is not None and str(raw["walls"]) != _prof_val("--walls"):
            extra += ["--walls", str(raw["walls"])]
        if raw.get("support") and "--support" not in prof_opts:
            extra.append("--support")
        if raw.get("brim") is not None:
            extra += ["--brim", str(raw["brim"])]
        if raw.get("plate_each"):
            extra.append("--plate-each")
        if raw.get("allow_overhang") is not None:
            extra += ["--allow-overhang", str(raw["allow_overhang"])]
        if raw.get("process"):
            extra += ["--process", str(raw["process"])]
        rows.append({
            "manifest": mid,
            "name": raw.get("name") or os.path.splitext(os.path.basename(file_path))[0],
            "stl": stl,
            "group": group,
            "count": count,
            "nozzle": str(raw.get("nozzle") or "0.4"),
            "filament": raw.get("filament"),   # family name or None
            "project": raw.get("project"),     # force a project name (no pooling)
            "extra": extra,
            "source": path,
        })
    if not rows:
        raise SystemExit("%s: no parts" % path)
    return rows


def load_parts(targets):
    rows = []
    for mid, path in targets:
        if not os.path.isfile(path):
            raise SystemExit("no such manifest: %s" % path)
        rows.extend(_as_part_rows(mid, _load_json(path), path))
    return rows


def _bucket_key(part, pool):
    """Project identity: forced name, or pool/id + group + nozzle + filament + extras.

    --pool ignores a part's fixed project name so same-group parts from every
    selected manifest share one bed that fills as the set grows.
    """
    fam = part["filament"] or print_profiles.PROFILES[part["group"]]["filament"]
    extra = tuple(part["extra"])
    if part["project"] and not pool:
        return ("fixed", part["project"], part["group"], part["nozzle"], fam, extra)
    if pool:
        return ("pool", part["group"], part["nozzle"], fam, extra)
    return ("mod", part["manifest"], part["group"], part["nozzle"], fam, extra)


def _project_name(key):
    kind = key[0]
    if kind == "fixed":
        return key[1]
    if kind == "pool":
        _, group, nozzle, fam, extra = key
        name = "pool_%s" % group
    else:
        _, mid, group, nozzle, fam, extra = key
        name = "%s_%s" % (mid, group)
    default_fam = print_profiles.PROFILES[group]["filament"]
    if fam != default_fam:
        name += "_" + fam
    # When extras change the profile (e.g. 100 % infill), keep one project per
    # extras tuple; a short suffix stops silent merges of incompatible jobs.
    if extra:
        bits = []
        i = 0
        while i < len(extra):
            flag = extra[i]
            if flag.startswith("--") and i + 1 < len(extra) and not str(extra[i + 1]).startswith("--"):
                bits.append("%s_%s" % (flag.lstrip("-"), extra[i + 1]))
                i += 2
            else:
                bits.append(flag.lstrip("-"))
                i += 1
        tag = "_".join(bits).replace("%", "").replace(" ", "")[:32]
        if tag:
            name += "__" + tag
    if nozzle != "0.4":
        name += "_%s" % nozzle.replace(".", "")
    return name


def plan(parts, pool=False):
    """OrderedDict project_name -> {group, nozzle, filament, opts, parts:[...]}."""
    buckets = OrderedDict()
    for p in parts:
        key = _bucket_key(p, pool)
        name = _project_name(key)
        if name not in buckets:
            fam = p["filament"] or print_profiles.PROFILES[p["group"]]["filament"]
            buckets[name] = {
                "project": name,
                "group": p["group"],
                "nozzle": p["nozzle"],
                "filament": fam,
                "opts": print_profiles.profile_opts(p["group"], filament=fam,
                                                    nozzle=p["nozzle"], extra=p["extra"]),
                "parts": [],
                "key": key,
            }
        else:
            # Same project name from different keys would be a bug in naming.
            if buckets[name]["key"] != key:
                raise SystemExit("project name collision %r for %r vs %r"
                                 % (name, buckets[name]["key"], key))
        buckets[name]["parts"].append(p)
    return buckets


def check_stls(parts, check_orient=True):
    """Missing files and (optionally) orient_check FAIL -> list of error strings."""
    errors = []
    for p in parts:
        if not os.path.isfile(p["stl"]):
            errors.append("missing STL: %s (%s/%s)" % (
                os.path.relpath(p["stl"], REPO), p["manifest"], p["name"]))
            continue
        if not check_orient:
            continue
        support = "--support" in (p["extra"] or []) or "--support" in print_profiles.PROFILES[p["group"]]["opts"]
        allow = None
        if "--allow-overhang" in (p["extra"] or []):
            i = p["extra"].index("--allow-overhang")
            allow = float(p["extra"][i + 1])
        verdict, note = orient_check.verdict(orient_check.measure(p["stl"]), support, allow)
        tag = {"OK": "OK ", "WARN": "WARN", "FAIL": "FAIL"}[verdict]
        print("  [%s] %s: %s" % (tag, os.path.relpath(p["stl"], REPO), note), file=sys.stderr)
        if verdict == "FAIL":
            errors.append("orientation FAIL: %s (%s)" % (os.path.relpath(p["stl"], REPO), note))
    return errors


def run_project(job, dry_run=False):
    """Call print_plate.py for one project. Returns the JSON report or the planned cmd."""
    stl_args = []
    for p in job["parts"]:
        arg = p["stl"] if p["count"] == 1 else "%s:%d" % (p["stl"], p["count"])
        stl_args.append(arg)
    cmd = [sys.executable, PRINT_PLATE, job["project"]] + stl_args + job["opts"]
    if dry_run:
        return {"project": "exports/print/%s.3mf" % job["project"],
                "cmd": cmd, "parts": [{"stl": os.path.relpath(p["stl"], REPO),
                                       "count": p["count"], "name": p["name"],
                                       "manifest": p["manifest"]} for p in job["parts"]],
                "group": job["group"], "nozzle": job["nozzle"], "filament": job["filament"],
                "opts": job["opts"], "dry_run": True}
    print(">", " ".join(os.path.relpath(c, REPO) if isinstance(c, str) and c.startswith(REPO) else c
                        for c in cmd), flush=True)
    run = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if run.stderr:
        print(run.stderr.rstrip(), file=sys.stderr)
    if run.returncode:
        print(run.stdout[-2000:], file=sys.stderr)
        raise SystemExit("print_plate.py failed for %s (exit %d)" % (job["project"], run.returncode))
    report = json.loads(run.stdout)
    print("  %s: %d plate(s), %s" % (
        report["project"], report["plates"],
        ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in report["sliced"])),
          flush=True)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("manifests", nargs="*",
                    help="manifest id (plates/<id>.json), path, or 'pistol'; default: all in plates/")
    ap.add_argument("--pool", action="store_true",
                    help="merge matching groups across manifests into pool_<group> projects")
    ap.add_argument("--list", action="store_true", help="list known manifests and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the project plan as JSON; do not call Bambu Studio")
    ap.add_argument("--check", action="store_true",
                    help="only verify STLs exist and pass orient_check; do not slice")
    ap.add_argument("--no-orient", action="store_true",
                    help="with --check / before slice: skip orient_check (print_plate still runs it)")
    args = ap.parse_args(argv)

    if args.list:
        rows = discover_manifests()
        if not rows:
            print("no manifests in plates/")
        for mid, path in rows:
            data = _load_json(path)
            n = len(data.get("parts") or [])
            print("%-24s %3d parts  %s" % (mid, n, data.get("title") or os.path.relpath(path, REPO)))
        mid, path = ALIASES["pistol"]
        print("alias pistol -> %s (id %s)" % (os.path.relpath(path, REPO), mid))
        return 0

    targets = resolve_targets(args.manifests)
    parts = load_parts(targets)
    jobs = plan(parts, pool=args.pool)

    if args.check or not args.dry_run:
        # Always confirm STLs exist before slicing; orient is nice on --check.
        errs = check_stls(parts, check_orient=args.check and not args.no_orient)
        if errs and args.check:
            for e in errs:
                print(e, file=sys.stderr)
            return 1
        missing = [e for e in errs if e.startswith("missing")]
        if missing and not args.dry_run:
            for e in missing:
                print(e, file=sys.stderr)
            return 1

    if args.dry_run or args.check:
        out = {
            "pool": bool(args.pool),
            "manifests": [m for m, _ in targets],
            "projects": [run_project(job, dry_run=True) for job in jobs.values()],
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    reports = []
    for job in jobs.values():
        reports.append(run_project(job, dry_run=False))
    json.dump({"pool": bool(args.pool), "projects": reports}, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
