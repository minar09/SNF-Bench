#!/usr/bin/env python3
"""Check whether I2V source images align to generated first frames.

This is a mask-readiness audit. ORB matching is a diagnostic only: transparent
water, smoke, and low-light scenes may have few matches even when the crop is
correct. Human review and an explicit image-to-video transform remain required
before transferring a shared source mask to model outputs.
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def alignment(source, frame):
    sh, sw = source.shape[:2]
    fh, fw = frame.shape[:2]
    aspect_gap = abs(sw / sh - fw / fh) / (fw / fh)
    src = cv2.resize(source, (fw, fh), interpolation=cv2.INTER_AREA)
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=2000)
    kp_src, des_src = orb.detectAndCompute(src_gray, None)
    kp_frame, des_frame = orb.detectAndCompute(frame_gray, None)
    out = {"source_wh": [sw, sh], "frame_wh": [fw, fh],
           "relative_aspect_gap": float(aspect_gap),
           "source_keypoints": len(kp_src), "frame_keypoints": len(kp_frame),
           "ratio_matches": 0, "ransac_inliers": 0, "ransac_inlier_fraction": None,
           "median_inlier_reprojection_px": None, "corner_shift_fraction": None}
    if des_src is None or des_frame is None or len(des_frame) < 2:
        return out
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(des_src, des_frame, k=2)
    good = [a for a, b in pairs if a.distance < 0.75 * b.distance]
    out["ratio_matches"] = len(good)
    if len(good) < 4:
        return out
    p0 = np.float32([kp_src[m.queryIdx].pt for m in good])
    p1 = np.float32([kp_frame[m.trainIdx].pt for m in good])
    H, inliers = cv2.findHomography(p0, p1, cv2.RANSAC, 3.0)
    if H is not None and inliers is not None:
        keep = inliers.ravel().astype(bool)
        out["ransac_inliers"] = int(keep.sum())
        out["ransac_inlier_fraction"] = float(keep.mean())
        pred = cv2.perspectiveTransform(p0[keep, None, :], H)[:, 0, :]
        out["median_inlier_reprojection_px"] = float(
            np.median(np.linalg.norm(pred - p1[keep], axis=1)))
        corners = np.float32([[[0, 0]], [[fw - 1, 0]],
                              [[fw - 1, fh - 1]], [[0, fh - 1]]])
        moved = cv2.perspectiveTransform(corners, H)
        out["corner_shift_fraction"] = float(
            np.mean(np.linalg.norm(moved - corners, axis=2)) / np.hypot(fw, fh))
    return out


def audit(duration, model):
    base = ROOT / "prompts" / "i2v" / duration
    prompts = json.loads((base / "target_crop_info_16-9.json").read_text())
    videos = ROOT / "videos" / "i2v" / model / duration
    rows = []
    for item in prompts:
        prompt_id = item["caption"][:100]
        source_path = base / "images" / item["file_name"]
        video_path = videos / f"{prompt_id}.mp4"
        record = {"prompt_id": prompt_id, "source": str(source_path.relative_to(ROOT)),
                  "video": str(video_path.relative_to(ROOT)),
                  "source_exists": source_path.is_file(),
                  "video_exists": video_path.is_file()}
        if record["source_exists"] and record["video_exists"]:
            source = cv2.imread(str(source_path))
            cap = cv2.VideoCapture(str(video_path))
            ok, frame = cap.read()
            cap.release()
            if source is not None and ok:
                record.update(alignment(source, frame))
            else:
                record["decode_error"] = True
        rows.append(record)
    return {"track": "i2v", "duration": duration, "model": model,
            "method": "direct resize followed by ORB ratio matching and RANSAC; diagnostic only",
            "n_prompts": len(rows), "n_pairs": sum(r["source_exists"] and r["video_exists"] for r in rows),
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", default="60s")
    parser.add_argument("--model", default="self_forcing")
    parser.add_argument("--out", type=Path, default=ROOT / "manifest" / "i2v_alignment_pilot.json")
    args = parser.parse_args()
    result = audit(args.duration, args.model)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{result['n_pairs']}/{result['n_prompts']} image/video pairs -> {args.out}")
    for r in result["rows"]:
        if r.get("relative_aspect_gap", 0) > 0.05:
            print("aspect mismatch:", r["source"], r["source_wh"], r["frame_wh"])


if __name__ == "__main__":
    main()
