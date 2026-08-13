"""Post-hoc COLOR/identity match — fix i2v color drift WITHOUT touching the model.

Recolors each generated frame to the input image's color statistics (Reinhard
per-channel mean/std). Pure pixel post-process on the decoded video, so it has
ZERO effect on motion / artifacts structure — it only removes the color cast that
drifts away from the conditioning image over the clip.

Usage:
  python scripts/color_match.py --video out/i2v/clip.mp4 --ref prompts/i2v/sk_flood_etc/img.png \
      --out out/i2v/clip_cm.mp4 --strength 0.9

  --strength 1.0 = force input color exactly; 0.7-0.9 keeps a little of the model's
                   own color dynamics. --space lab is perceptually gentler than rgb.
  --ref_frame0   = match to the FIRST generated frame instead of the input image
                   (use if frame0 already matches the input but later frames drift).
"""
import argparse
import numpy as np

try:
    import imageio.v2 as imageio
except Exception:
    import imageio
from PIL import Image


def _to_lab(x):  # x: [...,3] float [0,255] -> rough LAB via opencv if available, else identity
    try:
        import cv2
        return cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    except Exception:
        return x


def _from_lab(x):
    try:
        import cv2
        return cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
    except Exception:
        return x


def _stats(img):  # [H,W,3] -> per-channel mean,std
    f = img.reshape(-1, img.shape[-1])
    return f.mean(0), f.std(0) + 1e-6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--ref", required=True, help="reference image (the i2v input)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--strength", type=float, default=0.9)
    ap.add_argument("--space", choices=["rgb", "lab"], default="rgb")
    ap.add_argument("--ref_frame0", action="store_true",
                    help="match to generated frame 0 instead of the input image")
    ap.add_argument("--fps", type=int, default=0, help="0 = keep source fps")
    args = ap.parse_args()

    reader = imageio.get_reader(args.video)
    try:
        src_fps = reader.get_meta_data().get("fps", 8)
    except Exception:
        src_fps = 8
    frames = [np.asarray(f)[..., :3].astype(np.float32) for f in reader]
    if not frames:
        raise SystemExit("no frames read from --video")

    if args.ref_frame0:
        ref_img = frames[0].copy()
    else:
        ref_img = np.asarray(Image.open(args.ref).convert("RGB")).astype(np.float32)

    ref_c = _to_lab(ref_img) if args.space == "lab" else ref_img
    r_mean, r_std = _stats(ref_c)

    out = []
    s = float(args.strength)
    for f in frames:
        fc = _to_lab(f) if args.space == "lab" else f
        s_mean, s_std = _stats(fc)
        matched = (fc - s_mean) / s_std * r_std + r_mean      # per-frame -> ref color stats
        blended = fc * (1 - s) + matched * s
        rgb = _from_lab(blended) if args.space == "lab" else blended
        out.append(np.clip(rgb, 0, 255).astype(np.uint8))

    imageio.mimsave(args.out, out, fps=(args.fps or src_fps))
    print(f"[color_match] wrote {len(out)} frames -> {args.out} "
          f"(space={args.space}, strength={s}, ref={'frame0' if args.ref_frame0 else args.ref})")


if __name__ == "__main__":
    main()
