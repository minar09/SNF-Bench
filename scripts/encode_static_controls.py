"""Encode each v2 source as a static clip with the generators' own writer.

Runs INSIDE the generation image (it needs PyAV, which the scoring env lacks),
CPU only, so the encoder path is byte-for-byte the renders':

    docker run --rm -v <home>:/workspace -v <out>:/out -e CUDA_VISIBLE_DEVICES= \
        regfor:cuda12.1 python /workspace/snf-bench/scripts/encode_static_controls.py \
        /workspace/snf-bench/prompts/v2/i2v/images /out 10

Output: <out>/<id>.mp4, `torchvision.io.write_video(fps=16)` (libx264 defaults,
yuv420p). Consumed by scripts/candidate_floors.py --clips <out>.
"""
import glob
import os
import sys

from torchvision.io import read_image, write_video


def main(src_dir, out_dir, secs):
    os.makedirs(out_dir, exist_ok=True)
    for p in sorted(glob.glob(f"{src_dir}/*.jpg")):
        sid = os.path.splitext(os.path.basename(p))[0]
        img = read_image(p).permute(1, 2, 0)                 # HWC uint8, RGB
        assert img.shape[:2] == (480, 832), (sid, img.shape)
        write_video(f"{out_dir}/{sid}.mp4",
                    img.unsqueeze(0).repeat(16 * int(secs), 1, 1, 1), fps=16)
    print("encoded", len(glob.glob(f"{out_dir}/*.mp4")))


if __name__ == "__main__":
    main(*sys.argv[1:4])
