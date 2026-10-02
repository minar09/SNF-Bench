#!/bin/bash
# Chained finalisation: wait for the metric sweep and the validation suite to
# drain, then rebuild every derived artifact in dependency order and compile the
# paper. Safe to run more than once -- every step regenerates from scratch.
#
#   setsid nohup scripts/finalize.sh > finalize.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$(readlink -f "$0")")/.."   # repo root, wherever it is
PY=~/miniconda3/envs/snfeval/bin/python
TEX=~/miniconda3/envs/tex/bin/tectonic

echo "[$(date +%H:%M:%S)] waiting for metric workers and validation to finish..."
while ps -eo args | grep -q '[m]etric_worker.py'; do sleep 60; done
echo "[$(date +%H:%M:%S)] metric sweep drained"
while ps -eo args | grep -q '[v]alidation_suite.py'; do sleep 60; done
echo "[$(date +%H:%M:%S)] validation drained"

echo "[$(date +%H:%M:%S)] rebuilding derived artifacts"
$PY scripts/schema_scan.py;      echo "  schema_scan   -> $?"
$PY scripts/categories.py        > /dev/null && echo "  categories    -> ok"
$PY scripts/build_tables.py      > /dev/null && echo "  build_tables  -> ok"
$PY scripts/figures.py           && echo "  figures       -> ok"
$PY scripts/paper_assets.py      | tail -12
$PY scripts/gate_status.py;      echo "  gate_status   -> $?"

echo "[$(date +%H:%M:%S)] compiling paper"
mkdir -p .texbuild
(cd latex && $TEX -X compile main.tex --outdir ../.texbuild --keep-logs) \
  && echo "  compile OK" || echo "  compile FAILED"
grep -oE "Output written on.*\(([0-9]+) pages" .texbuild/main.log | head -1
cp -f .texbuild/main.pdf latex/main.pdf 2>/dev/null && echo "  latex/main.pdf updated"
echo "[$(date +%H:%M:%S)] done"
