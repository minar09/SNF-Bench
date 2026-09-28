#!/usr/bin/env python3
"""Non-scientific check: automatic masks fed through the external-mask path.

The mask is deliberately generated from the same video, so this is ONLY a
software parity check. It must never be reported as independent mask evidence.
"""

import argparse
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("fBD", "BFR", "FP", "MCFF_early", "MCFF_late",
          "DD_raw_late", "drift_frac_late", "DAR_signed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--out", type=Path,
                        default=ROOT / "manifest" / "mask_codepath_parity.json")
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    import snf_metrics_v11 as V11
    S = V11.S
    device = "cuda"
    model = S.load_raft(device)
    tensors, grays = S.read_frames(str(args.video), device)
    if tensors is None:
        raise ValueError("video has too few frames")
    win = max(S.MIN_WIN, int(len(tensors) * S.WIN_FRAC))
    early = np.mean([S.flow_mag(model, tensors[i], tensors[i + 1]).astype(np.float32)
                     for i in range(min(win, len(tensors) - 1))], 0)
    masks = S.build_masks(early)
    del tensors, grays
    original = V11.process_video(model, str(args.video), device)
    external = V11.process_video(model, str(args.video), device,
                                 external_masks=masks,
                                 mask_provenance={"mask_source": "automatic_codepath_check"})
    diffs = {name: None if original[name] is None or external[name] is None
             else float(external[name] - original[name]) for name in FIELDS}
    result = {"video": str(args.video), "purpose": "software parity only; masks are not independent",
              "fields": diffs, "max_abs_difference": max(abs(x) for x in diffs.values()
                                                if x is not None)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print("max absolute factor difference", result["max_abs_difference"])
    if result["max_abs_difference"] > 1e-5:
        raise SystemExit("external mask codepath differs from default when masks agree")


if __name__ == "__main__":
    main()
