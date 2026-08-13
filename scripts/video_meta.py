"""Extract per-video FPS / frame-count / resolution for the whole asset set.

Needed because the NBF (formerly BFR) definition is moving to a *per-second*
normalization,

    NBF = mean |u| / (W * dt),        dt = 1 / fps

so that methods running at different native frame rates are not silently
compared on a per-frame basis. The audit deliberately preserves each method's
native FPS, which makes frame-rate a hidden confound in any per-frame flow
statistic. None of the metric JSONs recorded FPS, so it is recovered here from
the video containers themselves.

Also emits width, which NBF's spatial normalization already uses, so the
recomputation has both terms from one source of truth.

Run with the snfeval env (needs cv2):
    ~/miniconda3/envs/snfeval/bin/python scripts/video_meta.py
"""

import csv
import glob
import os
import sys

import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = f"{ROOT}/manifest"


def probe(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    finally:
        cap.release()
    if not fps or fps <= 0:
        return None
    return dict(fps=round(float(fps), 4), n_frames=int(n or 0),
                width=int(w or 0), height=int(h or 0),
                seconds=round(float(n) / float(fps), 3) if n else 0.0)


def main():
    rows, bad = [], []
    vids = sorted(glob.glob(f"{ROOT}/videos/*/*/*/*.mp4"))
    for i, p in enumerate(vids):
        # videos/<track>/<model>/<duration>/<file>.mp4
        parts = p.split(os.sep)
        track, model, dur, name = parts[-4], parts[-3], parts[-2], parts[-1]
        m = probe(p)
        if m is None:
            bad.append(p)
            continue
        rows.append(dict(track=track, model=model, duration=dur, video=name, **m))
        if (i + 1) % 250 == 0:
            print(f"  {i + 1}/{len(vids)}", file=sys.stderr)

    os.makedirs(MAN, exist_ok=True)
    with open(f"{MAN}/video_meta.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["track", "model", "duration", "video",
                                          "fps", "n_frames", "width", "height", "seconds"])
        w.writeheader()
        w.writerows(rows)

    fps_set = sorted({r["fps"] for r in rows})
    print(f"{len(rows)} videos probed -> manifest/video_meta.csv")
    print(f"distinct fps values: {fps_set}")
    if len(fps_set) > 1:
        print("!! multiple native frame rates present -- per-second NBF normalization "
              "is REQUIRED, not optional")
    by = {}
    for r in rows:
        by.setdefault((r["track"], r["model"]), set()).add(r["fps"])
    for k, v in sorted(by.items()):
        if len(v) > 1:
            print(f"   !! {k} has mixed fps {sorted(v)}")
    if bad:
        print(f"!! {len(bad)} unreadable videos")


if __name__ == "__main__":
    main()
