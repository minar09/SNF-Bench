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
