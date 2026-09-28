# Git sync diagnosis (2026-09-28)

## Observed state

- Local `main`: `0b6d5f0` before the current rescore work, 1,480 tracked paths.
- `origin/main`: `e0cd2d2`, a 16-path release repository.
- `git merge-base main origin/main` exits 1. Their root commits differ (`e329f05` locally, `0f370e3` remotely), so the reported `ahead 34, behind 8` counts two **unrelated histories**, not a routine divergence from a common base.
- The working tree was clean when diagnosed; no merge, rebase, or unmerged index entries were present.
- `git push --dry-run origin main:refs/heads/research-main` fails before sending objects: `fatal: could not read Username for 'https://github.com': No such device or address`. No credential helper is configured; `gh` is unavailable.
- The largest tracked file in local `main` is about 5.4 MB. The observed failure is authentication, not a GitHub single-file size rejection. We have not tested the actual upload.

## Safe recovery order

1. **Keep both histories.** Do not force-push `main`, run `git pull --allow-unrelated-histories` blindly, or use `git reset --hard origin/main`. A default unrelated-history merge would combine the full research tree with the 16-file release tree; it would not preserve the release as a small, curated branch.
2. Finish and commit the rescore artifacts on local research `main`. Confirm `git status --short` is clean and record the commit ID. The remote release currently remains unchanged.
3. Configure GitHub authentication outside this repository (credential manager or SSH key with repository write access). Then re-run `git ls-remote origin refs/heads/main` and `git push --dry-run origin main:refs/heads/research-main`. Do not put a token in the remote URL, shell history, scripts, or docs.
4. Publish the research history as a **separate branch** once credentials work: `git push -u origin main:research-main`. This preserves `origin/main` exactly. If branch creation is denied by repository policy, use an authorized fork or request branch permission.
5. For the curated release, start from `origin/main` in a separate worktree and deliberately copy only reviewed, licensed release files from the research branch. Merge that release branch by PR after release checks. Treat the research and release lines as separate products until a deliberate migration is designed.
6. After a successful research-branch push, set local `main` to track `origin/research-main` if this checkout is intended to continue research development: `git branch --set-upstream-to=origin/research-main main`. Keep the remote release branch name explicit in release commands.

This file records a diagnosis and procedure. No remote refs or branch history were changed during the diagnosis.
