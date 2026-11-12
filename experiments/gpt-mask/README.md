# Mechanismus pipe (multi-product)

GPT works on **our own Python generators**, copied into an external folder with every project word
replaced by a neutral one. Edits come back line by line and are merged into the live files.

Products: `pistol`, `mitrailleuse`, `gatling` (`products/*.json`: `roots` = generators to expose,
`build_pre` = globals set before running). `gatling` extends `mitrailleuse` (same files).

## Usage

```sh
experiments/gpt-mask/mask out -p pistol          # live -> ../mechanismus/pistol/ (or $MECHANISMUS/pistol)
# ... GPT edits files in that folder and runs them with freecadcmd (see its README.md) ...
experiments/gpt-mask/mask in -p pistol           # work folder -> live files
experiments/gpt-mask/mask status -p pistol       # per file: edited in work / changed in live
```

After `in`, rebuild the live model (the command is printed). Nothing needs FreeCAD except running
the generators themselves.

## How it works

- `rename.py`: `names.json` maps whole words live -> neutral (identifiers, strings, comments and
  file paths: `pistol/hammer_assembly.py` becomes `handheld/striker_assembly.py`). Case style survives,
  mixed-case runs (`makeCylinder`, `BoundBox`) are untouched unless listed under `exact`. Line count
  never changes.
- The file set is not listed by hand: `closure(roots)` follows `os.path.join(REPO, ...)` paths and
  `import ratling.*` from the roots.
- `out` refuses to write if `names.json` is unsafe for these sources: a neutral word that already
  occurs in the code (reverse renaming would corrupt it), a word from `forbidden_substrings` left in
  the output or in a path, or a file where `reverse(forward(x)) != x`.
- `cache/<product>/neutral_base` (gitignored) keeps what crossed last time. Both
  directions are 3-way line merges (`git merge-file`) against it:
  - `in`: your edit moves into the live file even if live changed elsewhere since `out`;
  - `out`: live changes flow into the work file even if it holds unsent edits;
  - the same line changed on both sides is a conflict: nothing is written for that file, the other
    files still go through. A syntax error in an edited file rejects the whole `in`.
  - `out --force` overwrites the work files and drops pending edits.
- Files GPT adds that are not part of the product are ignored with a notice.

## Extending the vocabulary

A new domain word that must not leave the repo: add `live -> neutral` to `names.json`. The neutral
word must be plain lowercase letters, unique, and absent from the exposed sources (`out` checks).
Russian words are dropped from the exposed copies automatically (`strip_russian`) and stay in the live
files: `in` merges against the stripped base, so your edits never delete them. Editing a line that
holds Russian text on the GPT side gives a conflict for that file.

After `in`, `new words` lists words GPT introduced and `WARNING` flags live-vocabulary words it wrote;
extend `names.json` for those (see AGENTS.md).

Do not copy this README, `mask_sync.py` or `rename.py` into the GPT workspace.
