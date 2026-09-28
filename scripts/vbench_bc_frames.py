"""VBench background-consistency formula on validation-suite frame lists.

The embedding transform and score formula follow the local official VBench
implementation. The validation suite first subsamples frames to bound flow
cost, so these values must not be conflated with published full-video VBench
scores. They are paired corruption responses on identical sampled frames.
"""

import os
import sys

import cv2
import torch
import torch.nn.functional as F


def load_model(device):
    """Load the same CLIP ViT-B/32 image backbone used by VBench."""
    # This machine has a recent setuptools without pkg_resources, while the
    # pinned OpenAI CLIP package imports only pkg_resources.packaging. Supply
    # that single compatibility name without editing the external environment.
    try:
        import pkg_resources  # noqa: F401
    except ModuleNotFoundError:
        import packaging
        import packaging.version  # populate packaging.version for old CLIP
        import types
        shim = types.ModuleType("pkg_resources")
        shim.packaging = packaging
        sys.modules["pkg_resources"] = shim
    import clip
    model, _ = clip.load("ViT-B/32", device=device,
                         download_root=os.environ.get("SNF_CLIP_CACHE",
                                                      os.path.expanduser("~/.cache/clip")))
    model.eval()
    return model


def official_transform():
    """Import VBench's video-frame transform, not CLIP's PIL preprocessing."""
    root = os.environ.get("SNF_VBENCH_ROOT", "/home/minar/VBench")
    if root not in sys.path:
        sys.path.insert(0, root)
    from vbench.utils import clip_transform
    return clip_transform(224)


def score_features(features):
    """Official per-video mean of adjacent and first-frame clipped cosines."""
    if len(features) < 2:
        raise ValueError("at least two frames are required")
    features = F.normalize(features.float(), dim=-1, p=2)
    adjacent = (features[1:] * features[:-1]).sum(-1).clamp_min(0)
    first = (features[1:] * features[:1]).sum(-1).clamp_min(0)
    return float(((adjacent + first) / 2).mean().item())


@torch.no_grad()
def score_bgr_frames(model, frames, device, batch_size=32):
    """Score cv2 BGR frames in batches with VBench's RGB video transform."""
    transform = official_transform()
    features = []
    for start in range(0, len(frames), batch_size):
        batch = torch.stack([
            torch.from_numpy(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy())
                 .permute(2, 0, 1)
            for frame in frames[start:start + batch_size]
        ]).to(device)
        inputs = transform(batch)
        features.append(model.encode_image(inputs).float().cpu())
    return score_features(torch.cat(features))
