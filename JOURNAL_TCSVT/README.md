# SNF-Bench++ journal draft: IEEE TCSVT

Venue fixed 2026-11-04: IEEE Transactions on Circuits and Systems for Video
Technology. TCSVT asks for the IEEE Transactions LaTeX template from the IEEE
Author Center. That template is `IEEEtran.cls` v1.8b (2015/08/26), still the
current release, used with `IEEEtran.bst`. Both are vendored here unmodified
from CTAN, and their hashes are in `TEMPLATE_SHA256`.

**Template rule.** Never edit `IEEEtran.cls`, `IEEEtran.bst` or the formatting
of `main.tex`. Content goes in `sec/`:

| file | holds |
|---|---|
| `sec/packages.tex` | packages and macros |
| `sec/front.tex` | title, authors, running heads |
| `sec/abstract.tex`, `sec/keywords.tex` | abstract, index terms |
| `sec/sections.tex` | section order; `main.tex` inputs only this |
| `sec/NN_*.tex`, `sec/appendix.tex` | sections and appendices |

Check the template is intact with `sha256sum -c TEMPLATE_SHA256`.
Unfinished content is marked `\pending{...}` and prints in red;
`grep -n '\\pending{' sec/*.tex` must return only the macro definition before
submission. `working_draft.pdf` is rebuilt from the current sources.

Structure follows benchmark papers in top venues, which typically have
construction, measurement suite, metric validation, results, findings and
datasheet sections. See `../docs/SNF_PP_JOURNAL_BEST_PRACTICES_2026_11_04.md`.

**Figures.** All diagrams are TikZ in `sec/fig_*.tex` (vector, editable, no
extra packages beyond `tikz` and `pifont`); symbols and colours are defined once
in `sec/packages.tex` (Okabe--Ito colours, each paired with a shape; status
symbols: filled circle frozen, half circle candidate, outlined square
diagnostic, open circle planned).

| figure | file | data |
|---|---|---|
| overview (Fig. 1) | `sec/fig_overview.tex` | snapshots below; Physics-IQ scene 0140 (CC BY 4.0, credited), roles from its official motion masks |
| scene composition | `sec/fig_scenes.tex` | `figures/generated/scene_donut.tex` from `../scripts/build_journal_visuals.py` |
| region-to-measure routing | `sec/fig_routing.tex` | `../docs/METRIC_SPEC_v1.1.md` |
| 240 s qualitative panel | `sec/fig_qualitative.tex` | lossless native 832x480 PNG frames, `figures/snapshots/t2v240/p0/` |
| all four 240 s prompts (appendix) | `sec/fig_qualitative_all.tex` | JPEG q95 4:4:4, 416x240, `figures/snapshots/t2v240_hq/` |

The historical 240 s T2V snapshot panel and viewer overlap a simultaneous
Steady-Forcing journal submission and are excluded from the active manuscript
and supplement. Their source files remain as historical working material; do
not distribute them in the new supplementary package. New T2V samples with no
submission overlap are needed. The I2V comparison uses existing 5 s output
from four pipelines on two documented public sources, and is built with
`../scripts/build_journal_i2v_comparison.py`; its hash record is in the
figure's `PROVENANCE.json`. It is short-horizon illustration only.

**Interactive companions** (offline, no network; open in a browser, intended
as supplementary material):

* `interactive/index.html`: landing page for the current companions;
* `interactive/i2v_comparison.html`: two image-conditioned sources, four
  pipelines, and frames at 2.5 and 5 seconds;
* `interactive/measurement_map.html`: clickable role, axis, realism and
  comparator graph with status filters;
* `interactive/scene_explorer.html`: sunburst of families and regimes that
  filters a searchable table of all 144 specifications.

They describe specifications and constructs, not validated results. The old
`interactive/qualitative_viewer.html`, its snapshots and sprites are excluded
from the current supplement; any previously hosted copy must be reviewed before
sharing. `figures/wacv_t2v_qualitative.pdf` is the unmodified historical WACV
figure and is no longer used in the draft.

**Panel rule.** Only published methods appear, each as its single released
configuration. Steady-Forcing (arXiv 2606.14732) and SceneTether (arXiv ID
pending, placeholder `scenetether2026` in `references.bib`) are cited as
independent preprints (SceneTether only once its preprint is actually public) and judged under the same rules as external
methods. No internal ablation or variant of either appears in any table.

Not submission-ready. Still open:

- the fresh source set;
- independent annotations;
- native comparisons;
- human construct validation;
- the real-footage reference bands (`../docs/SNF_PP_REALISM_DESIGN_2026_11_04.md`);
- overlap disclosures.

Do not submit placeholders. The bibliography was copied from the WACV
manuscript; verify every entry before submission. The WACV manuscript itself is
kept separately in `WACV_2027_latex/`.

Build from this directory:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The protocol and completion gates are in
`../docs/TCSVT_JOURNAL_EXECUTION_PROTOCOL_2026_11_01.md`.
