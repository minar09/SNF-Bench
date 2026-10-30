# Contestant eligibility by publication protocol

Project-lead policy amendment, 2026-10-30 KST.

## Historical WACV v1 and existing collectors

The WACV audit uses externally released contestants. In `scripts/registry.py`,
`status="internal"` retains the historical meaning: excluded from its public
tables. Steady-Forcing, earlier internal ablations, postprocessed outputs and
scratch runs must not be silently inserted into those frozen comparisons.
The current `contestants(track)` API and release scanner retain that behavior.

## Future standalone journal protocol

The lead explicitly authorizes including **Steady-Forcing (T2V)** and
**SceneTether (I2V)** alongside contemporary released external methods.
Author affiliation is disclosed metadata, not a reason for permanent exclusion.
This approval supersedes older blanket statements for the future journal
study. It does not designate every internal variant as a contestant or claim
that an unpublished artifact is a public release.

Before ingesting journal results, implement an explicit protocol profile with
separate eligibility, provenance, native/port/control row types and affiliation.
Keep the historical default unchanged. Apply release checks to the selected
publication profile and approved release contents; do not disable them globally.
Keep credentials, participant records, machine paths and unrelated experiments
out of every public bundle regardless of profile.

Journal metric/threshold selection must not optimize either author method's
standing. Use independent sources and external-model confirmation, blind human
labels, equal run/reporting rules, and analyses with author methods included
and removed. Current runtime integration of this future profile is pending;
`configs/snf_journal_plan.json` records the planning decision only.
