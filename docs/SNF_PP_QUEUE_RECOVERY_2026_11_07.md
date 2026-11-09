# GPU queue recovery: 2026-11-07

At 13:49 UTC, the original chain had progressed beyond the earlier waiting status. Wan2.2's one-scene smoke report exists, and a 12-scene render process is running on GPU 2. Two geometry reports, `geometry_v2_fp.json` and `geometry_v2_unt.json`, exist. Do not start a duplicate Wan job or assume the full Wan run has finished.

The conveyor and patch steps both exited 1 before writing final reports. The chain continued because its `run()` helper prints the command status but then returns the status of `echo`; it did not stop on either failure. In each case, `icb04` had no generated spatial controls or sidecars because its source role map had too few material pixels. The first 9 scenes' conveyor flows and first 14 scenes' patch flows were already cached before the failure. Those cached flows are not complete experiment reports.

`manifest/realism_dev_2026_11_05/lists/list_t100_spatial_eligible_2026_11_07.tsv` contains the other 41 of 42 scenes; only `icb04` is excluded. A preflight checked all seven spatial-control families and found `icb04` was the only expected scene without required control sidecars. Exclusion is due to inapplicability, not a failed or successful measurement, and must be reported in the denominator.

Recovery was started on GPU 3, in order: conveyor modes, then patch modes, using the existing hash-checked flow cache and writing the originally intended reports under new non-overwriting output paths. The second command runs only if the first succeeds. `realism_geometry_run.py` refuses a busy GPU and checks >=110 GB available on both `/` and the cache filesystem; cached video hashes are verified before reuse. The active worker was launched through the Codex command session, not through the old wait script. Check the report files and process status before treating recovery as complete; this note records a start, not a result.

At the check, `/` had about 152 GiB free and the cache filesystem about 396 GiB. GPU status is time-varying. The queue should be revised to fail closed on command errors and should check process-query failures rather than interpret them as an idle GPU before it is reused.
