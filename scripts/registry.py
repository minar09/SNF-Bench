"""SNF-Bench model / asset registry — single source of truth for provenance.

Every evaluated system is declared here with:
  key        directory key in the source repo
  name       display name for papers/tables
  track      't2v' | 'i2v'
  status     'public'   -> external published model, eligible as a benchmark contestant
             'internal' -> our own model/ablation. NEVER a contestant (see docs/EXCLUSIONS.md)
             'postproc' -> a color-matched post-process variant of another entry
             'scratch'  -> smoke/debug run, not evaluation data
  setting    'native'   -> run under its authors' intended configuration  (Setting A)
             'matched'  -> run under our common long-horizon wrapper       (Setting B)
  ckpt       checkpoint path used, for the config table
  note       anything a reviewer would want stated
"""

# ---------------------------------------------------------------- T2V track
# Source repo: /home/minar/static-forcing  (videos in output/<key>/t2v_<dur>)
# SNF task metrics: SNF_Bench/task_results/r1_60s/<file>.json   (60s only)
# VBench:           SNF_Bench/results/<key>/<dur>/*eval_results.json
T2V = [
    dict(key="CausVid", name="CausVid", track="t2v", status="public", setting="native",
         ckpt="ckpt/CausVid/autoregressive_checkpoint/model.pt",
         r1="CausVid", note="autoregressive DMD distillation of Wan2.1-T2V-1.3B"),
    dict(key="self_forcing", name="Self-Forcing", track="t2v", status="public", setting="native",
         ckpt="ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt",
         r1="self_forcing", note=""),
    dict(key="infinite_forcing", name="Infinite-Forcing", track="t2v", status="public", setting="native",
         ckpt="(baseline repo)", r1="infinite_forcing",
         note="lowest NBF at 60s but lowest MCFF -> freeze-not-stability, the key confound case"),
    dict(key="rolling_forcing", name="Rolling-Forcing", track="t2v", status="public", setting="native",
         ckpt="ckpt/RollingForcing", r1="rolling_forcing", note=""),
    dict(key="reward_forcing", name="Reward-Forcing", track="t2v", status="public", setting="native",
         ckpt="ckpt/rewardforcing.pt", r1="reward_forcing", note=""),
    dict(key="longlive", name="LongLive", track="t2v", status="public", setting="native",
         ckpt="ckpt/longlive_models", r1="longlive", note=""),
    dict(key="causal_forcing", name="Causal-Forcing", track="t2v", status="public", setting="native",
         ckpt="ckpt/causal-forcing", r1="causal_forcing",
         note="high apparent motion + high drift attenuation; the headline interpretation-change case"),
    # --- excluded from all benchmark tables ---
    dict(key="steady_forcing", name="Steady-Forcing", track="t2v", status="internal", setting="native",
         ckpt="ckpt/Steady-Forcing", r1=None, note="OUR prior work - excluded from SNF-Bench"),
    dict(key="steady_forcing_bt", name="Steady-Forcing (BT)", track="t2v", status="internal", setting="native",
         ckpt="ckpt/Steady-Forcing", r1="steady_forcing_bt", note="OUR prior work - excluded from SNF-Bench"),
]

# ---------------------------------------------------------------- I2V track
# Source repo: /home/minar/region-forcing (videos in output/eval/<key>/<dur>)
# Metrics:     snf_eval/results/metrics/<key>/<dur>/{snf_task_metrics,snf_extra_metrics}.json
#              + vbench_std/*eval_results.json
_MATCHED = ("run in the common long-horizon I2V wrapper "
            "(configs/causal_forcing_dmd_f2s_steady_chunk6.yaml, nfpb=6, --i2v) -- "
            "NOT the model's native configuration. Setting B / stress test only.")
I2V = [
    dict(key="chunk6", name="Causal-Forcing++ (2-step)", track="i2v", status="public", setting="matched",
         ckpt="ckpt/causal-forcing++/framewise-2step.pt", note=_MATCHED),
    dict(key="cf++_1step", name="Causal-Forcing++ (1-step)", track="i2v", status="public", setting="matched",
         ckpt="ckpt/causal-forcing++/framewise-1step.pt", note=_MATCHED),
    dict(key="cf_framewise", name="Causal-Forcing (framewise)", track="i2v", status="public", setting="matched",
         ckpt="ckpt/causal-forcing/framewise/causal_forcing.pt", note=_MATCHED),
    dict(key="f2s_framewise", name="Causal-Forcing++ (2-step, native nfpb=1)", track="i2v",
         status="public", setting="native",
         ckpt="ckpt/causal-forcing++/framewise-2step.pt",
         note="run at its NATIVE pure-framewise config (causal_forcing_dmd_f2s_steady.yaml). "
              "The one public I2V entry with a genuine Setting-A run at 60s+."),
    dict(key="self_forcing", name="Self-Forcing", track="i2v", status="public", setting="matched",
         ckpt="ckpt/Self-Forcing/checkpoints/self_forcing_dmd.pt", note=_MATCHED),
    dict(key="causvid", name="CausVid", track="i2v", status="public", setting="matched",
         ckpt="ckpt/CausVid/autoregressive_checkpoint/model.pt", note=_MATCHED),
    dict(key="wan21_i2v", name="Wan2.1-I2V-14B-480P", track="i2v", status="public", setting="native",
         ckpt="ckpt/wan_models/Wan2.1-I2V-14B-480P",
         note="bidirectional 14B, native config, 5s only (fixed-length model)"),
    dict(key="wan22_i2v", name="Wan2.2-I2V-A14B", track="i2v", status="public", setting="native",
         ckpt="ckpt/wan_models/Wan2.2-I2V-A14B", note="bidirectional MoE, native config, 5s only"),
    dict(key="ltx_i2v", name="LTX-Video 13B-0.9.8-distilled", track="i2v", status="public", setting="native",
         ckpt="baseline_repos/LTX-Video", note="bidirectional, native config, 5s only"),
    # --- excluded from all benchmark tables ---
    dict(key="steady", name="Steady-Forcing", track="i2v", status="internal", setting="matched",
         ckpt="ckpt/Steady-Forcing/steady_forcing_t2v.pt", note="OUR prior work - excluded"),
    dict(key="rt500", name="RA-I2V (rt500)", track="i2v", status="internal", setting="matched",
         ckpt="runs/.../rt500", note="OUR method - excluded"),
    dict(key="phase7_500", name="RA-I2V-v1 (phase7_500)", track="i2v", status="internal", setting="matched",
         ckpt="runs/phase7_nfpb6/checkpoint_model_000500/model.pt", note="OUR method - excluded"),
    dict(key="nfpb1_control", name="nfpb=1 control", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR training control - excluded"),
    dict(key="nfpb1_control_at_nfpb1", name="nfpb=1 control @nfpb=1", track="i2v", status="internal",
         setting="native", ckpt="", note="OUR training control - excluded"),
    dict(key="phase7_at_nfpb1", name="phase7 @nfpb=1", track="i2v", status="internal", setting="native",
         ckpt="", note="OUR training control - excluded"),
    dict(key="abl_rs", name="ablation: region+static", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR ablation - excluded"),
    dict(key="abl_redmd", name="ablation: Re-DMD", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR ablation - excluded"),
    dict(key="abl_rsredmd", name="ablation: RS+Re-DMD", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR ablation - excluded"),
    dict(key="abl_v2", name="ablation: v2", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR ablation - excluded"),
    dict(key="phase7_000100", name="phase7 ckpt 100", track="i2v", status="internal", setting="matched",
         ckpt="", note="checkpoint ladder - excluded"),
    dict(key="phase7_000200", name="phase7 ckpt 200", track="i2v", status="internal", setting="matched",
         ckpt="", note="checkpoint ladder - excluded"),
    dict(key="phase7_000300", name="phase7 ckpt 300", track="i2v", status="internal", setting="matched",
         ckpt="", note="checkpoint ladder - excluded"),
    dict(key="phase7_000400", name="phase7 ckpt 400", track="i2v", status="internal", setting="matched",
         ckpt="", note="checkpoint ladder - excluded"),
    dict(key="f1s_framewise", name="Causal-Forcing++ (1-step, native)", track="i2v", status="public",
         setting="native", ckpt="ckpt/causal-forcing++/framewise-1step.pt",
         note="native pure-framewise config; partial coverage (50/65)"),
    # color-matched post-process variants
    dict(key="chunk6_cm", name="Causal-Forcing++ (2-step) +color-match", track="i2v", status="postproc",
         setting="matched", ckpt="", note="post-hoc color match of chunk6"),
    dict(key="rt500_cm", name="RA-I2V +color-match", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR method - excluded"),
    dict(key="phase7_500_cm", name="RA-I2V-v1 +color-match", track="i2v", status="internal", setting="matched",
         ckpt="", note="OUR method - excluded"),
    dict(key="nfpb1_control_cm", name="nfpb=1 control +color-match", track="i2v", status="internal",
         setting="matched", ckpt="", note="OUR control - excluded"),
    dict(key="_texture_test", name="(scratch)", track="i2v", status="scratch", setting="matched",
         ckpt="", note="debug run"),
]

ALL = T2V + I2V

# Durations, in canonical order
DURATIONS = ["5s", "60s", "120s", "240s"]

# Metric direction + display name.  '+' = higher better, '-' = lower better, '~' = context only
METRICS = {
    # --- SNF task metrics (RAFT + ORB) ---
    # NAMING (P0#3, 2026-08-13). Two renames, both because the old name asserted
    # something the mathematics does not:
    #   BFR "Background Flow Ratio" -> NBF "Normalized Background Flow".
    #       It was never a ratio -- there is no denominator that is itself a
    #       measured flow. It is a normalized magnitude, and it is now normalized
    #       in TIME as well as space (see FPS note below).
    #   DriftFrac -> SPLIT INTO TWO METRICS. The reviews assumed DriftFrac was
    #       1 - F_comp/F_raw and objected only to its name. Reading
    #       metric_code/snf_task_metrics.py:200 shows it is not that at all:
    #
    #           drift_frac_late = mean|u|_static(late) / mean|u|_dyn_raw(late)
    #
    #       -- a static-to-dynamic flow ratio that never touches the compensated
    #       flow dyn_res. It is unbounded above (it exceeds 1 on 20 of 161 T2V
    #       60s clips, impossible for a "fraction"), so no causal reading of it
    #       is defensible. It is, however, a good measure of the paper's third
    #       axis, drift LEAKAGE. So:
    #
    #   DLR "Drift Leakage Ratio"  = the shipped quantity, honestly named.
    #       Static-region flow relative to intended dynamic-region flow.
    #       Unbounded; DLR > 1 means the background moves more than the subject.
    #   DAR "Drift Attenuation Ratio" = 1 - MCFF_late / DD_raw_late, the
    #       quantity §4 actually describes. Derived from fields already stored
    #       per video, so it costs no recompute. Report it as "global
    #       compensation removes X% of measured dynamic-region flow under this
    #       estimator", never "X% of the motion is drift" -- where local flow
    #       opposes the global drift field, compensation can *increase*
    #       magnitude, and DAR is empirically negative on 22 of 161 clips.
    "fBD_mean":            ("-", "fBD",        "feature-aligned background drift, % of frame diagonal"),
    "NBF_mean":            ("-", "NBF",        "static-region flow magnitude, x1e3 frame-widths per SECOND"),
    "FP_mean":             ("+", "FP",         "drift-compensated flow persistence, late/early"),
    "MCFF_late_mean":      ("~", "MCFF",       "drift-removed late dynamic-region motion magnitude"),
    "DD_raw_late_mean":    ("~", "DD_raw",     "raw (uncompensated) late dynamic-region motion"),
    "DLR_mean":            ("-", "DLR",        "static-region flow / raw dynamic-region flow, late window; >1 = background outmoves subject"),
    "DAR_mean":            ("-", "DAR",        "1 - MCFF/DD_raw: relative reduction in measured dynamic-region flow after global drift compensation"),
    # --- cv2 extra metrics ---
    "sharp_ratio":  ("+", "sharp_ratio", "late/early Laplacian sharpness (<1 = blur grows)"),
    "sharp_mean":   ("~", "sharp_mean",  "absolute Laplacian sharpness"),
    "dE_static":    ("-", "dE_static",   "static-region Lab color drift"),
    "dL_static":    ("~", "dL_static",   "static-region lightness change (<0 = darkening)"),
    "idPSNR_late":  ("+", "idPSNR",      "static-region PSNR, frame0 vs late"),
    "FDP":          ("+", "FDP",         "frame-diff motion persistence"),
    "stag_onset":   ("+", "stag_onset",  "normalized time at which motion first collapses"),
    # --- VBench ---
    "background_consistency": ("+", "VB-bg",     "VBench background consistency"),
    "subject_consistency":    ("+", "VB-subj",   "VBench subject consistency"),
    "motion_smoothness":      ("+", "VB-smooth", "VBench motion smoothness (AMT)"),
    "temporal_flickering":    ("+", "VB-flick",  "VBench temporal flickering"),
    "imaging_quality":        ("+", "VB-imq",    "VBench imaging quality"),
    "aesthetic_quality":      ("+", "VB-aes",    "VBench aesthetic quality"),
    "dynamic_degree":         ("~", "VB-DD",     "VBench dynamic degree - THE metric SNF-Bench audits"),
}

SNF_TASK_KEYS = ["fBD_mean", "NBF_mean", "FP_mean", "MCFF_late_mean",
                 "DD_raw_late_mean", "DLR_mean", "DAR_mean"]

# --- Temporal normalization for NBF -----------------------------------------
# CORRECTED 2026-08-13 (second pass). The metric does NOT measure flow between
# native frames: snf_task_metrics.read_frames() subsamples with
#     interval = max(1, round(native_fps / SAMPLE_FPS)),  SAMPLE_FPS = 8
# so flow is computed between *sampled* frames. In this corpus native rates are
# 16 and 24 fps, giving intervals 2 and 3 and an effective rate of exactly
# 8.000 fps for every one of the 1881 videos.
#
# Consequence: there was never a frame-rate confound in the flow magnitudes --
# the subsampling already equalized the temporal rate by construction. An
# earlier fix here scaled by NATIVE fps, which multiplied LTX-Video by 24 and
# everything else by 16 and thereby INTRODUCED a 1.5x error, together with a
# spurious "LTX moves rank 6 -> 8" finding. That finding is retracted.
#
# The per-second unit is still correct and is kept, because it makes NBF
# physically meaningful and stays right for a future model whose native rate is
# not a clean multiple of SAMPLE_FPS (e.g. 30 fps -> interval 4 -> 7.5 fps).
# For the present corpus it is a uniform x8 rescale that changes no ranking.
SAMPLE_FPS = 8.0
FPS_DEFAULT = 16.0


def effective_fps(native_fps):
    """Temporal rate at which flow is actually measured, after subsampling."""
    if not native_fps or native_fps <= 0:
        native_fps = FPS_DEFAULT
    interval = max(1, round(native_fps / SAMPLE_FPS))
    return native_fps / interval
EXTRA_KEYS = ["sharp_ratio", "sharp_mean", "dE_static", "dL_static",
              "idPSNR_late", "FDP", "stag_onset"]
VBENCH_KEYS = ["background_consistency", "subject_consistency", "motion_smoothness",
               "temporal_flickering", "imaging_quality", "aesthetic_quality", "dynamic_degree"]


def by_key(track):
    return {m["key"]: m for m in ALL if m["track"] == track}


def contestants(track):
    """Models eligible to appear in a SNF-Bench leaderboard."""
    return [m for m in ALL if m["track"] == track and m["status"] == "public"]
