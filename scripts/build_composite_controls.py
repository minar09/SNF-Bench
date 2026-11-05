"""Realism controls built from an entrant's own video: pass-through and support composites.

A source-pixel composite is the global optimum of every source-referenced
fidelity measure, so a support-realism candidate must be able to tell it from
the video it was made from (docs/SNF_PP_REALISM_DESIGN_2026_11_04.md §4). Every
mode, `passthrough` included, decodes the parent and re-encodes it the same
way. Each control therefore has a pass-through partner with the same encoding
history, and the comparison is control vs pass-through, not control vs the
once-encoded original (docs/SNF_PP_REALISM_REVIEW_2026_11_04.md §2). Modes are
defined in scripts/composite_ops.py.

Runs INSIDE the generation image, CPU only, with the renders' writer
(`torchvision.io.write_video(fps=16)`, libx264 defaults, yuv420p):

    docker run --rm -v <home>:/workspace -v <out>:/out -e CUDA_VISIBLE_DEVICES= \
        regfor:cuda12.1 python /workspace/snf-bench/scripts/build_composite_controls.py \
        <list.tsv> /workspace/snf-bench/prompts/v2/i2v/images <masks dir> /out \
        passthrough,paste,paste_residual

`list.tsv` rows are `<scene id>\t<video path inside the container>`.
Output: <out>/<mode>/<id>.mp4, plus <out>/<mode>/<id>.json with the SHA-256 of
the parent, source, mask and output, frame counts, fps and writer settings.
Nothing is ever overwritten: the run refuses to start if any target exists.
Each output is written under a temporary name, re-decoded with PyAV and
checked for frame count, frame rate, size, codec and pixel format; only then
are the video and its sidecar put in place. A shared encoding history removes
one confound; content-dependent compression can still differ between controls.
"""
import hashlib
import json
import os
import sys

import av
import torch
import torchvision
from torchvision.io import ImageReadMode, read_image, read_video, write_video

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import composite_ops as ops  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def decoded(path):
    """What the file actually contains, from the container rather than the writer's intent."""
    with av.open(path) as c:
        st = c.streams.video[0]
        n = sum(1 for _ in c.decode(st))
        return dict(frames=n, fps=float(st.average_rate), width=st.codec_context.width,
                    height=st.codec_context.height, codec=st.codec_context.name,
                    pix_fmt=st.codec_context.pix_fmt)


def main(listing, src_dir, mask_dir, out_dir, modes="passthrough,paste"):
    modes = modes.split(",")
    for m in modes:
        if m not in ops.MODES:
            raise SystemExit(f"unknown mode {m}; choose from {ops.MODES}")
    scenes = [line.rstrip("\n").split("\t") for line in open(listing)]
    taken = [p for m in modes for sid, _ in scenes
             for p in (f"{out_dir}/{m}/{sid}.mp4", f"{out_dir}/{m}/{sid}.json") if os.path.exists(p)]
    if taken:
        raise SystemExit(f"refusing to overwrite {len(taken)} existing outputs, e.g. {taken[0]}")
    for m in modes:
        os.makedirs(f"{out_dir}/{m}", exist_ok=True)
    for sid, video in scenes:
        frames, _, info = read_video(video, pts_unit="sec", output_format="THWC")
        assert round(info["video_fps"]) == 16, (sid, info)
        src_path, mask_path = f"{src_dir}/{sid}.jpg", f"{mask_dir}/{sid}/labels.png"
        src = read_image(src_path).permute(1, 2, 0).numpy()
        lab = read_image(mask_path, ImageReadMode.GRAY)[0].numpy()
        assert frames.shape[1:3] == src.shape[:2] == lab.shape == (480, 832), sid
        support = lab == 1
        parent = frames.numpy()
        for m in modes:
            out, tmp = f"{out_dir}/{m}/{sid}.mp4", f"{out_dir}/{m}/{sid}.partial.mp4"
            write_video(tmp, torch.from_numpy(ops.compose(m, parent, src, support)), fps=16)
            got = decoded(tmp)
            want = dict(frames=int(parent.shape[0]), fps=16.0, width=832, height=480,
                        codec="h264", pix_fmt="yuv420p")
            if got != want:
                os.remove(tmp)
                raise SystemExit(f"{sid}/{m}: decoded {got}, expected {want}")
            os.rename(tmp, out)
            json.dump(dict(scene=sid, mode=m, parent=video, parent_sha256=sha256(video),
                           source_sha256=sha256(src_path), mask_labels_sha256=sha256(mask_path),
                           output_sha256=sha256(out), parent_frames=int(parent.shape[0]),
                           parent_fps=float(info["video_fps"]), support_px=int(support.sum()),
                           writer="torchvision.io.write_video", writer_fps=16,
                           output_decoded=got, encoder="libx264 defaults via torchvision",
                           torchvision=torchvision.__version__, pyav=av.__version__,
                           feather_px=ops.FEATHER_PX, median_samples=ops.MEDIAN_SAMPLES),
                      open(f"{out_dir}/{m}/{sid}.json", "w"), indent=1)
        print(sid, "built", ",".join(modes), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:6])
