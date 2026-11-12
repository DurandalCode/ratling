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

- `out` writes every part as `parts/<stem>.brep` plus a `.step` twin: the GPT side can read either.
- `in` takes a part back as `.brep` or `.step`/`.stp` (STEP is converted through `freecadcmd`).
  For each part the newest file in the work folder wins (`exports/<Label>`, `<Label>`, `parts/<stem>`).
  Only parts edited since the last crossing are taken; `--all` takes every shell part, `--only VAR…` picks some.
- `cache/<product>/ledger.json` keeps the hashes of files that already crossed the pipe. `status` shows
  per shell part whether the work copy is `in sync` or `EDITED, run in`, and whether the live build
  uses an `overlay` or the `parametric` solid.
- `out` refuses to wipe a work folder holding edits that `in` has not taken (`--force` overrides), so
  a live rebuild never eats unsent work. After `in` + live build, `out --rebuild` brings the edited
  solids back into the work folder.
- `hot` does the same continuously, including STEP.

Do not copy this README / `mask_*.py` / `pull_*.py` into the GPT workspace.
