# Video walkthrough script — SEMMA: NBA expected FG% (≈ 11 min)

**Setup before recording:** the notebook open in Colab after *Run all* (outputs visible), the GitHub repo in a second tab, the deployed app in a third. Screen-record at 1080p; zoom the browser to ~125 %.

| Time | On screen | What to say (talking points, not a script to read word for word) |
|---|---|---|
| 0:00–0:45 | Title cell | Who you are; the question: *how likely is any NBA shot to go in, given where and how it's taken?* Why it matters — separates shot **selection** from shot **making** (link to your earlier MVP project). |
| 0:45–1:30 | SEMMA table in the title cell | SEMMA = Sample, Explore, Modify, Model, Assess, from SAS. Unlike CRISP-DM it starts from the data, not the business — so the project context is one short cell. Each step maps to an Enterprise Miner node. |
| 1:30–3:00 | **Sample**: population table, representativeness table, learning curve | 1.03 M shots across five seasons. Why sample: the learning curve flattens after ~25k shots, so 200k is plenty. Show sample = population on every statistic (KS p = 0.999). Partition 60/20/20 **by game** — explain why (no game in two partitions). 2024-25 held back entirely. |
| 3:00–4:45 | **Explore**: FG% by distance, the two shot charts, shot types, game clock, variable worth, clusters | Point at the rim hot zone (76 % at 0 ft) and the flat mid-range. Corner threes beat above-the-break threes (38 % vs 36 %). Heaves with ≤ 2 s left: 29 %. Leakage catch: `EVENT_TYPE` *is* the target. Player identity is informative but excluded on purpose. |
| 4:45–6:00 | **Modify**: drop log, score-code cell, new-variable charts | Every dropped column has a reason. Feature engineering written once as `shot_features.py` and reused by the app — the Python equivalent of Enterprise Miner score code. Geometry-based 3PT flag agrees 99.95 % with the official one. |
| 6:00–7:30 | **Model**: each node cell, then the comparison table | Five models + baseline. Tree depth and boosting settings tuned on the validation partition (mention this came from the AI critic). Why log loss (we need probabilities, not yes/no). Gradient boosting wins. |
| 7:30–9:30 | **Assess**: ROC/calibration/lift, final table, decile calibration, leaderboard, persistence plot | Test = validation → no over-fit. Unseen 2024-25: predicted 46.4 % vs actual 46.7 %, every decile within 0.9 points. Leaderboard: Jokić +323 points over expected; Curry's raw FG% undersells him. Skill or luck? r = 0.68 season to season — mostly skill. |
| 9:30–10:30 | The deployed app | Drag a shot to the left corner → 3 pts, ≈ 39 % → 1.18 expected points; a driving layup at the rim ≈ 66 % → 1.31. Leaderboard tab. |
| 10:30–11:00 | GitHub repo + critiques folder | Where everything lives; the critic reviews and what they changed; limitations (no defender data); thanks. |

**SAS segment (optional, +3 min, if your class has Enterprise Miner):** show the diagram built from `nba_shots_sample_for_sas.csv` (appendix steps) and compare its Model Comparison result with section A.1.
