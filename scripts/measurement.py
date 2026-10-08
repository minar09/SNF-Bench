"""What makes two SNF records the same measurement, and refusal to pool them if not.

A number in a table is defined by more than the metric's name. Output-derived
masks and shared-source masks partition different pixels; v1.0 and v1.1
compensate with different motion models; a prompt set fixes what was asked for.
Two values that differ in any of these are different measurements, and the
method project's own matched comparison found interpretations change materially
after shared-mask scoring. Pooling them into one table row, mean or ranking is
therefore an error, not an approximation.

Records already carry most of the labels; this makes them a single key and
gives every table builder one function to call:

    signature(summary, per_video) -> tuple
    assert_poolable(records)      -> raises if more than one signature

Unlabelled records (the v1.0 sweep wrote none of these fields) get an explicit
`unlabelled` value rather than being assumed compatible with anything.
"""

FIELDS = ("prompt_set", "metric_spec_version", "mask_version",
          "flow_backbone", "feature_backbone")
UNLABELLED = "unlabelled"


def signature(summary, per_video):
    """The measurement key of one per-video record inside one entry record."""
    def get(k):
        if k == "prompt_set":
            return summary.get("prompt_set", "v1")      # pre-label records are v1
        v = per_video.get(k)
        return UNLABELLED if v in (None, "") else str(v)
    return tuple(get(k) for k in FIELDS)


def describe(sig):
    return ", ".join(f"{k}={v}" for k, v in zip(FIELDS, sig))


def signatures(records):
    """records: iterable of (label, summary_dict). -> {signature: [labels]}"""
    out = {}
    for label, summary in records:
        for v in summary.get("per_video", []):
            out.setdefault(signature(summary, v), []).append(label)
    return out


def assert_poolable(records):
    """Raise if the records are not all one measurement."""
    sigs = signatures(records)
    if len(sigs) > 1:
        parts = [f"  {describe(s)}  <- {len(ls)} clip(s), e.g. {ls[0]}"
                 for s, ls in sorted(sigs.items(), key=lambda kv: -len(kv[1]))]
        raise ValueError("refusing to pool different measurements:\n" + "\n".join(parts))
    return next(iter(sigs)) if sigs else None
