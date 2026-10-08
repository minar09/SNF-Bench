"""Candidate measurements for SNF-Bench v2 -- CPU kernels, none admitted yet.

These implement step 2 of docs/I2V_METRIC_REVIEW_2026_10_08.md. Every function
here is a *candidate*: it has a measurement identity of its own, it is never
pooled with `sourcefixed-1.0` or v1.1 values, and it reaches a headline only by
passing the single-cause admission study (step 3) on independent controls.

  support colour   pixelwise CIEDE2000 between source and output over the
                   (eroded) rigid support: mean and 90th percentile per frame.
                   The `sourcefixed-1.0` `dE_static` compares region *means*,
                   so an equal-mean texture swap scores ~0 there and high here.
  material detail  high-frequency energy on tiles fully inside the dynamic
                   region, relative to the source and to the early window.
                   Over-smoothing ("glassy water") removes it; a frozen sharp
                   frame keeps it -- so it is only read beside activity.
  material activity mean absolute change between consecutive sampled frames on
                   the same interior tiles. Flicker and noise raise it too;
                   neither kernel is a naturalness score.
  recurrence       the strongest multi-frame match between the dynamic region
                   now and itself at least `min_lag_s` earlier. Exact loops
                   score ~1; natural surf can score high on single frames,
                   which is why it requires a run of consecutive matches.

Colour is computed from 8-bit sRGB with an explicit D65 conversion, not
OpenCV's uint8 Lab, and CIEDE2000 is checked against the formula authors' test
pairs (tests/data/ciede2000_sharma.txt).
"""

import cv2
import numpy as np

IDENTITY = {
    "support_de00": "cand-support-de00-0",
    "material_detail": "cand-material-detail-0",
    "material_activity": "cand-material-activity-0",
    "recurrence": "cand-recurrence-0",
}

SAMPLE_FPS = 8            # matches snf_task_metrics.SAMPLE_FPS
TILE = 32                 # px at 832x480
ERODE_PX = 6              # keeps mask-edge pixels out of support statistics

# --------------------------------------------------------------------- colour

_M_RGB2XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                       [0.2126729, 0.7151522, 0.0721750],
                       [0.0193339, 0.1191920, 0.9503041]])
_WHITE_D65 = np.array([0.95047, 1.0, 1.08883])


def srgb_to_lab(bgr_u8):
    """8-bit BGR -> CIELAB (D65, 2 degree), float64, L in [0, 100]."""
    rgb = bgr_u8[..., ::-1].astype(np.float64) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _M_RGB2XYZ.T / _WHITE_D65
    eps, kappa = 216 / 24389, 24389 / 27
    f = np.where(xyz > eps, np.cbrt(xyz), (kappa * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1)


def ciede2000(lab1, lab2):
    """CIEDE2000 (kL = kC = kH = 1), vectorised over the last axis = (L, a, b)."""
    L1, a1, b1 = np.moveaxis(np.asarray(lab1, np.float64), -1, 0)
    L2, a2, b2 = np.moveaxis(np.asarray(lab2, np.float64), -1, 0)
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb7 = ((C1 + C2) / 2) ** 7
    G = 0.5 * (1 - np.sqrt(Cb7 / (Cb7 + 25.0 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    h1p = np.where((a1p == 0) & (b1 == 0), 0.0, h1p)
    h2p = np.where((a2p == 0) & (b2 == 0), 0.0, h2p)
    dLp, dCp = L2 - L1, C2p - C1p
    zero = (C1p * C2p) == 0
    dh = h2p - h1p
    dhp = np.where(zero, 0.0, np.where(np.abs(dh) <= 180, dh,
                                       np.where(dh > 180, dh - 360, dh + 360)))
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hs = h1p + h2p
    hbp = np.where(zero, hs, np.where(np.abs(h1p - h2p) <= 180, hs / 2,
                                      np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)))
    T = (1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp))
         + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dtheta = 30 * np.exp(-((hbp - 275) / 25) ** 2)
    Cbp7 = Cbp ** 7
    RC = 2 * np.sqrt(Cbp7 / (Cbp7 + 25.0 ** 7))
    SL = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2)
    SC = 1 + 0.045 * Cbp
    SH = 1 + 0.015 * Cbp * T
    RT = -np.sin(np.radians(2 * dtheta)) * RC
    return np.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2
                   + RT * (dCp / SC) * (dHp / SH))


def erode(mask, px=ERODE_PX):
    if px <= 0:
        return mask.astype(bool)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
    return cv2.erode(mask.astype(np.uint8), k) > 0


def support_de00(frames_bgr, source_bgr, support, erode_px=ERODE_PX):
    """Per frame: mean and p90 of pixelwise CIEDE2000 vs source over eroded support."""
    m = erode(support, erode_px)
    if m.sum() < 50:
        return None
    ref = srgb_to_lab(source_bgr)[m]
    mean, p90 = [], []
    for f in frames_bgr:
        d = ciede2000(ref, srgb_to_lab(f)[m])
        mean.append(float(d.mean()))
        p90.append(float(np.percentile(d, 90)))
    return dict(identity=IDENTITY["support_de00"], n_px=int(m.sum()), erode_px=erode_px,
                mean=mean, p90=p90)

# ------------------------------------------------------------- material tiles


def interior_tiles(mask, tile=TILE):
    """(y, x) origins of tiles lying entirely inside `mask`."""
    H, W = mask.shape
    out = []
    for y in range(0, H - tile + 1, tile):
        for x in range(0, W - tile + 1, tile):
            if mask[y:y + tile, x:x + tile].all():
                out.append((y, x))
    return out


def _hp_energy(gray_f32, tiles, tile=TILE):
    """Mean squared Laplacian-of-Gaussian response over the tiles (fine detail)."""
    hp = cv2.Laplacian(cv2.GaussianBlur(gray_f32, (0, 0), 0.8), cv2.CV_32F)
    return float(np.mean([np.mean(hp[y:y + tile, x:x + tile] ** 2) for y, x in tiles]))


def material_detail_activity(frames_bgr, source_bgr, dynamic, fps_sampled=SAMPLE_FPS,
                             tile=TILE, early_s=5.0):
    """Detail retention and activity on fully interior dynamic tiles, per sampled frame.

    detail_ratio_src[t]   = HF energy(t) / HF energy(source)
    detail_ratio_early[t] = HF energy(t) / mean HF energy over the first `early_s`
    activity[t]           = mean |gray(t) - gray(t-1)| on the tiles (8-bit units)
    """
    tiles = interior_tiles(dynamic, tile)
    if not tiles:
        return None
    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames_bgr]
    src_e = _hp_energy(cv2.cvtColor(source_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32), tiles, tile)
    e = np.array([_hp_energy(g, tiles, tile) for g in grays])
    n_early = max(1, int(round(early_s * fps_sampled)))
    early = e[:n_early].mean()
    act = [0.0] + [float(np.mean([np.abs(grays[i][y:y + tile, x:x + tile]
                                         - grays[i - 1][y:y + tile, x:x + tile]).mean()
                                  for y, x in tiles])) for i in range(1, len(grays))]
    return dict(identity=(IDENTITY["material_detail"], IDENTITY["material_activity"]),
                n_tiles=len(tiles), tile=tile,
                detail_ratio_src=(e / max(src_e, 1e-9)).tolist(),
                detail_ratio_early=(e / max(early, 1e-9)).tolist(),
                activity=act)

# ----------------------------------------------------------------- recurrence


def _descriptor(gray_f32, dynamic, size=(48, 27)):
    """Zero-mean, unit-norm thumbnail of the dynamic region's bounding box."""
    ys, xs = np.nonzero(dynamic)
    crop = gray_f32[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    m = dynamic[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32)
    t = cv2.resize(crop * m, size, interpolation=cv2.INTER_AREA).ravel()
    t = t - t.mean()
    n = np.linalg.norm(t)
    return t / n if n > 0 else t


def recurrence(frames_bgr, dynamic, fps_sampled=SAMPLE_FPS, min_lag_s=2.0, run_s=1.0):
    """Strongest sustained self-match of the dynamic region at lag >= min_lag_s.

    For every lag L and start t, the score is the mean correlation over a run of
    `run_s` consecutive sampled frames between frames t..t+k and t-L..t-L+k.
    Returns the maximum score, its lag (s) and time (s). A single matching frame
    cannot score high, because the run must match frame after frame.
    """
    if dynamic.sum() < 50:
        return None
    D = np.stack([_descriptor(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32), dynamic)
                  for f in frames_bgr])
    n = len(D)
    k = max(2, int(round(run_s * fps_sampled)))
    Lmin = int(round(min_lag_s * fps_sampled))
    if n < Lmin + k:
        return dict(identity=IDENTITY["recurrence"], score=None, reason="clip shorter than lag + run")
    C = D @ D.T                                   # frame-to-frame correlation
    best = (-1.0, None, None)
    for L in range(Lmin, n - k + 1):
        diag = np.diagonal(C, offset=-L)          # C[t, t-L] for t = L..n-1
        if len(diag) < k:
            continue
        runs = np.convolve(diag, np.ones(k) / k, mode="valid")
        i = int(np.argmax(runs))
        if runs[i] > best[0]:
            best = (float(runs[i]), L / fps_sampled, (i + L) / fps_sampled)
    return dict(identity=IDENTITY["recurrence"], score=best[0], lag_s=best[1], at_s=best[2],
                run_frames=k, min_lag_s=min_lag_s)

# ------------------------------------------------------------------- decoding


def read_sampled(path, fps_sampled=SAMPLE_FPS):
    """Full-resolution BGR frames at the analysis rate (same interval rule as SNF)."""
    cap = cv2.VideoCapture(path)
    native = cap.get(cv2.CAP_PROP_FPS) or 16.0
    step = max(1, int(round(native / fps_sampled)))
    out, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % step == 0:
            out.append(f)
        i += 1
    cap.release()
    return out, native / step
