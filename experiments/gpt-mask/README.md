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
MASK_PRODUCT=mitrailleuse freecadcmd -c "REPO='$PWD'; exec(open('mitrailleuse/pack_frame.py').read())"
```

Default work tree: `$MECHANISMUS/<product>` or `../mechanismus/<product>/`.

Overlays:
- pistol → `pistol/mask_overlays/`
- mitrailleuse / gatling → `mitrailleuse/mask_overlays/`

Cache of pulled `.brep`: `experiments/gpt-mask/cache/<product>/` (gitignored).

Do not copy this README / `mask_*.py` / `pull_*.py` into the GPT workspace.
