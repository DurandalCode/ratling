# -*- coding: utf-8 -*-
"""
Reversible renaming of our Python sources for the external Mechanismus work tree. Pure Python.

A table of whole words (live -> neutral, names.json) is applied to every letter run in the text and
in file paths: identifiers, strings, comments. Case style survives (valve / Valve / VALVE), mixed-case
runs (makeCylinder, BoundBox) are never touched unless listed under "exact", so FreeCAD's API stays intact. Line count never
changes, which is what lets edits travel line by line and merge as plain 3-way text.
"""

from __future__ import print_function

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
NAMES_PATH = os.path.join(HERE, "names.json")

_RUN = re.compile(r"[A-Za-z]+")


class NamesError(Exception):
    pass


def load_names(path=NAMES_PATH):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    words = {k.lower(): v.lower() for k, v in data["words"].items()}
    for k, v in words.items():
        if not v.isalpha() or not v.isascii():
            raise NamesError("neutral word %r (for %r) must be plain letters" % (v, k))
    if len(set(words.values())) != len(words):
        raise NamesError("neutral words are not unique")
    both = set(words) & set(words.values())
    if both:
        raise NamesError("a word is both live and neutral: %s" % ", ".join(sorted(both)))
    data["words"] = words
    exact = data.setdefault("exact", {})
    if len(set(exact.values())) != len(exact):
        raise NamesError("exact neutral spellings are not unique")
    data.setdefault("forbidden_substrings", [])
    return data


def _swap(table, exact):
    def sub(m):
        w = m.group(0)
        if w in exact:
            return exact[w]
        n = table.get(w.lower())
        if n is None:
            return w
        if w == w.lower():
            return n
        if len(w) > 1 and w == w.upper():
            return n.upper()
        if w[1:] == w[1:].lower():
            return n[0].upper() + n[1:]
        return w
    return sub


def forward(text, names):
    return _RUN.sub(_swap(names["words"], names["exact"]), text)


def reverse(text, names):
    inv = {v: k for k, v in names["words"].items()}
    return _RUN.sub(_swap(inv, {v: k for k, v in names["exact"].items()}), text)


forward_path = forward
reverse_path = reverse


def vocabulary(texts):
    out = set()
    for t in texts:
        out.update(w.lower() for w in _RUN.findall(t))
    return out


def check_table(names, texts):
    """Problems that would make forward/reverse lossy; [] when the table is safe for these texts."""
    problems = []
    vocab = vocabulary(texts)
    for k, v in sorted(names["words"].items()):
        if v in vocab:
            problems.append("neutral word %r (for %r) already occurs in the sources" % (v, k))
    for k, v in sorted(names["exact"].items()):
        if v.lower() in vocab:
            problems.append("neutral spelling %r (for %r) already occurs in the sources" % (v, k))
    return problems


def leftovers(text, names):
    low = text.lower()
    return [s for s in names["forbidden_substrings"] if s.lower() in low]


_JOIN = re.compile(r"os\.path\.join\(\s*REPO\s*,([^)]*)\)")
_PLUS = re.compile(r"REPO\s*\+\s*['\"]([^'\"]+)['\"]")
_STR = re.compile(r"['\"]([^'\"]+)['\"]")
_IMPORT = re.compile(r"^\s*(?:import|from)\s+ratling(?:\.(\w+))?", re.M)


def _refs(text):
    for m in _JOIN.finditer(text):
        parts = _STR.findall(m.group(1))
        if parts:
            yield "/".join(parts)
    for m in _PLUS.finditer(text):
        yield m.group(1).lstrip("/")
    for m in _IMPORT.finditer(text):
        yield "ratling/__init__.py"
        if m.group(1):
            yield "ratling/%s.py" % m.group(1)


def closure(roots, repo=REPO_ROOT):
    """Repo-relative files reachable from roots through REPO-joined paths and `import ratling.*`."""
    seen, todo = [], list(roots)
    while todo:
        rel = todo.pop(0)
        if rel in seen:
            continue
        path = os.path.join(repo, rel)
        if not os.path.isfile(path):
            continue
        seen.append(rel)
        if not rel.endswith(".py"):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for ref in _refs(f.read()):
                if ref.endswith((".py", ".json")):
                    todo.append(ref)
    return sorted(seen)
