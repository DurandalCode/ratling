# Mechanismus pipe (multi-product)

GPT works in an **external** folder with neutral names. Live repo keeps the truth.

Products: `pistol`, `mitrailleuse`, `gatling` (profiles in `products/*.json`).
`gatling` currently **extends** `mitrailleuse` (same printed frame; concept B has no generators yet).

## Usage

```sh
# Pistol
experiments/gpt-mask/mask out -p pistol --rebuild
experiments/gpt-mask/mask hot -p pistol

# Mitrailleuse / gatling
experiments/gpt-mask/mask out -p mitrailleuse --rebuild
experiments/gpt-mask/mask out -p gatling --rebuild   # same solids, own work dir

experiments/gpt-mask/mask in -p mitrailleuse
experiments/gpt-mask/mask status -p mitrailleuse
MASK_PRODUCT=mitrailleuse freecadcmd -c "REPO='$PWD'; exec(open('mitrailleuse/pack_frame.py').read())"
```

Default work tree: `$MECHANISMUS/<product>` or `../mechanismus/<product>/`.

Overlays:
- pistol → `pistol/mask_overlays/`
- mitrailleuse / gatling → `mitrailleuse/mask_overlays/`

Cache of pulled parts: `experiments/gpt-mask/cache/<product>/` (gitignored).

## Both directions

Python edits are the main way back; BREP/STEP stay as the way out and as a fallback in.

- `out` writes every part as `parts/<stem>.brep` + `.step` twin (the **unedited** base: pull runs with
  `MASK_EDITS=0`), `manifest.json` with per-part `sees` (which parts an edit's `ctx` can hold, taken from
  what exists at the live overlay hook), and the current `edits/<stem>.py` from `<product>/mask_edits/`.
  All names are the neutral stems from `products/*.json`.
- The GPT side writes `edits/<stem>.py` with `def edit(part, ctx) -> Part.Shape`
  (`mechanismus_template/edit_runner.py` runs them; checks: valid shape, same solid count, volume
  50%..150%). `build.py` in the work folder applies them to the base.
- `in` takes edited `edits/*.py`, dry-runs them against the cached base (`check_edits.py`), and only
  then copies them to `<product>/mask_edits/` (tracked in git). A bad edit takes nothing.
  `--edits-only` skips solids. Solids as `.brep`/`.step` still work (newest file wins, STEP is converted)
  and land as overlays; edits are applied on top of overlays.
- Live generators call `tools/mask_overlays.py`: overlays first, then edits, loud failure on a bad edit.
  `MASK_EDITS=0` turns edits off.
- `cache/<product>/ledger.json` keeps hashes of files that already crossed; `status` shows per shell part
  whether the work solid and the work edit are `in sync` or `EDITED, run in`.
- `out` refuses to wipe a work folder holding edits not taken by `in` (`--force` overrides).
- `hot` syncs edits both ways (and solids, including STEP).
