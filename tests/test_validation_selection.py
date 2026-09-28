"""Selection should span media before repeating alphabetical river prompts."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_suite import select_reference_clips  # noqa: E402


def test_category_round_robin(tmp_path):
    table = tmp_path / "categories.csv"
    with table.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=["track", "duration", "prompt_id", "category"])
        writer.writeheader()
        for prompt, category in (("a_river", "river"), ("b_river", "river"),
                                 ("z_fire", "fire")):
            writer.writerow({"track": "t2v", "duration": "60s",
                             "prompt_id": prompt, "category": category})
    clips = [f"{name}-0-123.456.mp4" for name in ("a_river", "b_river", "z_fire")]
    picked = select_reference_clips(clips, 2, stratified=True, category_csv=table)
    assert {p.split("-0-")[0] for p in picked} == {"a_river", "z_fire"}
    assert select_reference_clips(clips, 2) == clips[:2]
