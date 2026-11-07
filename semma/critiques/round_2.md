# SEMMA critique — round 2

**Reviewer:** an independent Claude instance (Anthropic), started fresh. It had no access to the drafting conversation or to round 1. It received a plain-text export of the executed notebook (markdown, code and text outputs), the figure PNGs, and the app and report files. For each phase it adopted the expert-persona prompt shown in that phase's critic section of the notebook, and answered it.
**Date:** 6 November 2026. **Below:** the review exactly as returned, followed by the response to each point.

---


Reviewer stance: SEMMA / SAS Enterprise Miner authority, professional-engagement strictness. I checked the prose against the printed outputs, every figure PNG, the app files (`artifacts/app/*.py`, `model_metadata.json`, `requirements.txt`), the README, and the `artifacts/reports/*.csv` files. I did not open `critiques/`.

---

## Sample · grade B+

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | Medium | **The learning curve is weaker evidence for sample size than the prose says (S.3).** The quick HGB uses a fixed `max_iter=150` with no early stopping, so the 2k and 5k points are mostly *over-fitting*, not data scarcity. Also, the curve is still falling between 50k and 120k (0.6378 → 0.6355, Δ 0.0023). That gap is about 4× the Gradient Boosting vs Ensemble gap (0.0006) used to pick the champion in A.1. "Doubling buys almost nothing" contradicts how fine-grained the later model selection is. And at most it justifies a 120k *training* set, not the 200k sample, and not leaving out 80 % of the population. | Rerun the curve with early stopping and the real Modify pipeline. Extend it to 240k and 480k training shots (the population loads in 5 s, so cost is no argument). Compare the slope with the model-selection margins. If it is still falling, raise `SAMPLE_SIZE` or refit the champion on more data (see Assess #3). |
| 2 | Medium | **Circular representativeness evidence (S.2).** The sample is stratified on `SHOT_MADE_FLAG`, so "FG% 46.77 % in both" holds by construction and proves nothing. The KS test compares a sample with the population it was drawn from: the two are not independent, so p = 0.999 is expected and has no evidential weight. Only 4 marginals are checked. `ACTION_TYPE` (the strongest input), court zone and location are not. | Present FG% match as a *design property*, not evidence. Add chi-square or PSI checks on `ACTION_TYPE`, `SHOT_ZONE_BASIC` and `SHOT_ZONE_AREA`, and a 2-D check on (LOC_X, LOC_Y). Compare the sample with the *unsampled remainder*, not the full population, so the test is valid. |
| 3 | Medium | **The leakage rationale names the wrong dependency (S.3).** "Game-level effects (pace, arena, opponent) cannot leak": none of these are features, so the risk is optimistic evaluation from correlated residuals. The dominant correlated unit is the **player-season** (and team-season), and that is spread across all three partitions. Grouping by game is fine, but the stated reason oversells what it protects against. | Say plainly that grouping by game guards against within-game correlation only. Justify why player-level correlation is acceptable (identity is excluded by design, and the out-of-time season is the real guard). Optionally add a sensitivity check: a partition grouped by `PLAYER_ID` and its validation log loss. |
| 4 | Low | **The partition does not keep the stratification.** The sample is stratified by season × outcome, but `GroupShuffleSplit` ignores it: test FG% is 46.39 % vs train 46.90 % (0.5 pp). Season shares per partition are not reported. | Use `StratifiedGroupKFold` (stratify on season, group on game) to make the 60/20/20 split, and report season shares per partition. |
| 5 | Low | The sample has 199,999 rows, not the 200,000 configured (per-stratum `frac` rounding). The `assert` checks train∩valid and train∩test but not valid∩test. | Use `n=` per stratum, or note the rounding. Add the third disjointness assert. |
| 6 | — | Done well: proportional stratification preserves the base rate, which matters for probability output. A true out-of-time season is held out. The configuration is centralised. | — |

**Verdict:** Sound and above typical student work. The representativeness and sample-size evidence is presented as stronger than it is.

---

## Explore · grade B−

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The Variable Selection figure is broken.** `artifacts/figures/explore_variable_worth.png` is a corrupted composite. `worth.plot.barh(...)` was called without a new figure or axes, so it drew into the *previous* figure (`explore_action_clock`). The PNG shows the "FG% by shot type" panel on the left. On the right, the MI bars are drawn on top of the clock histogram, on a categorical x-axis where values of about 0.04 are invisible slivers. The Variable Selection node has no readable output, and the report and article will carry this image. | `fig, ax = plt.subplots(figsize=(7,5)); worth.plot.barh(ax=ax, ...)`. Rerun, then visually check every saved PNG. |
| 2 | Medium | **The MI estimates are not comparable, and "shooter identity carries information (0.022)" is mostly estimator bias.** `PLAYER_NAME` (896 levels) is scored with the discrete plug-in MI, whose upward bias is about (K−1)/(2N) = 895/60,000 ≈ **0.015 nats**. That is roughly 70 % of the reported 0.022. The *same information* as `PLAYER_ID` (continuous kNN estimator) scores 0.0048 (`variable_worth.csv`). Zones (plug-in) are also ranked against LOC_X/LOC_Y (kNN) as if on one scale. | Use one estimator family: bin continuous variables and use plug-in MI with a bias correction (Miller–Madow), or a permutation-null MI per variable. Or use EM-style chi-square / R² worth. Rewrite the PLAYER_NAME sentence. Shooter effects are better shown with a partial-pooling estimate than with raw MI. |
| 3 | Medium | **Factual error in Finding 1.** "FG% … 23 % at 30 ft": the plotted value at 30 ft is about 31 %. The curve only reaches about 23 % at 33 ft (and 17 % at 35 ft). "43 % by 4–5 ft" is about 41 % at 5 ft. Finding 2's 35.6 % above-the-break figure comes from the *Modify* geometry flag, while the Explore zone chart shows 35.8 %. | Pull the numbers programmatically from `by_ft` and the zone table. Cite the source cell for each number in the findings table. |
| 4 | Medium | **Anomalies are not explored.** `describe()` shows LOC_Y up to 797 (79.7 ft), SHOT_DISTANCE up to 81, LOC_Y down to −50 (behind the backboard), and a Backcourt zone with n = 229 at 2.6 %. The hexbin quietly truncates at LOC_Y < 400. None of this appears in the findings or gets a treatment decision (filter, cap or flag). Finding anomalies is an explicit SEMMA Explore goal. "No missing values in any column" is asserted, but no missing-value count is printed for the categoricals. | Add an anomalies row to the findings table, with counts and a decision. Print `train.isna().sum()`. Add a Filter-node equivalent (or justify keeping these shots, with the `heave` flag as the treatment). |
| 5 | Medium | **No redundancy analysis.** The prose says "distance is represented several overlapping ways" but shows no correlation or Variable Clustering result. Modify then *adds* more overlapping inputs (dist_ft, distance_bin, is_three, heave, angle, abs_angle). | Add a correlation / Cramér's V matrix among the candidate and engineered inputs (EM Variable Clustering equivalent). Use it to decide which overlapping inputs the regression gets. |
| 6 | Medium | **Possible label leakage in `ACTION_TYPE` is never checked.** It is scorer-annotated *after* the play. Labels such as "Cutting Dunk Shot" (93 % FG) may partly reflect the outcome, for example missed dunk attempts logged as layups. Its taxonomy may also drift by season (inconsistent casing like "Pullup Jump shot" vs "Jump Shot" hints at label hygiene issues). This is the top input, and it matters for the out-of-time season. | Add an action-type × season frequency table, with new or retired labels flagged. Discuss the post-hoc annotation risk explicitly as a known limitation. |
| 7 | Low | **Finding 5 over-claims.** "Clusters confirm that angle, not only distance, separates shot quality": the corner clusters (21.5–22.2 ft) and above-the-break clusters (25.2–25.8 ft) also differ in distance, so angle is confounded. The Modify angle chart later shows a weak, non-monotone angle effect. k = 8 is not justified (no elbow or silhouette), and clusters are not used downstream. | Compare FG% for corner vs above-break *at matched distance*. Justify k, or state that the clusters are descriptive only. |
| 8 | Low | `describe()` reports means and quantiles of ID columns (GAME_ID, PLAYER_ID, TEAM_ID), which is noise. | Exclude identifiers from the numeric summary. |
| 9 | — | Done well: Explore is strictly training-only, and the `EVENT_TYPE` target-duplicate was caught with a crosstab. | — |

**Verdict:** Good instincts and the right nodes. But one key figure is broken, the MI analysis is statistically flawed, and anomalies and redundancy are skipped.

---

## Modify · grade B−

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The rare-level Replacement pools incompatible shot types (M.3).** `min_frequency=0.005` collapses "Putback Dunk", "Reverse Dunk", "Running Alley Oop Dunk", "Driving Reverse Dunk" and "Alley Oop Layup" (all near-certain makes) into one level with "Jump Bank Shot", "Fadeaway Bank shot" and "Hook Bank Shot" (about 40–50 %). The pooled level's estimate means nothing for any of its members. The app still offers all 48 actions in its dropdown (`meta["actions"]`), so a user choosing "Running Alley Oop Dunk Shot" gets a dunk scored like a blend that includes bank jumpers. This also handicaps the Regression and NN nodes. | Pool by *shot family* (dunk / layup / hook / floater / jumper / bank / tip), or by similar training FG% (EM Replacement / Interactive Grouping by target rate). Keep `infrequent` only as a fallback for unseen labels, and restrict the app dropdown to the modelled levels. |
| 2 | Medium | **Several engineered variables have no Explore justification.** `clutch` (period ≥ 4, ≤ 120 s) has no supporting finding. `heave` uses ≤ 3 s and ≥ 30 ft, but Explore only showed a ≤ 2 s bin that was *not* split by distance (so the 29 % is confounded with distance). `is_overtime` covers 0.6 % of shots with no finding. The prompt's own standard is that every transform is tied to an Explore finding. | Add a two-way FG% table (secs left × distance bin) and a period-4 last-2-min check. Derive the thresholds from it, or drop the unsupported flags. |
| 3 | Medium | **The binning puts its resolution in the wrong place.** The steepest part of the curve (76 % at 0 ft → about 48 % at 3 ft) gets one bin (0–4 ft), while the flat mid-range gets three. With linear `dist_ft` plus these bins, the logistic node cannot fit the rim drop-off. That is part of why Regression ties the single tree (0.6400 vs 0.6399). It is also not "Interactive Binning" in the EM sense (supervised Gini or χ² splits): the edges are hand-picked. | Use supervised or finer bins near the rim (0–1, 1–2, 2–3, 3–5 ft), or a spline or log transform of `dist_ft` (the SAS appendix even suggests log `dist_ft`, but the notebook never does it). |
| 4 | Medium | **The Impute node is largely nominal.** `engineer()` runs `.astype(int)` on `MINUTES_REMAINING`, `SECONDS_REMAINING` and `PERIOD` *before* the imputer, so a NaN raises an error instead of being imputed. A NaN location becomes the string `'nan'` through `pd.cut(...).astype(str)`, and a NaN action becomes `'nan'` through `astype(str)`. The categorical imputer therefore never sees a missing value, and `is_three` silently becomes 0. The claim "possible in new data → imputed" is not true end to end. | Keep NaNs as NaN inside `engineer` (nullable `Int64` / float, and `.astype("string")` that preserves `<NA>`). Add a unit test that scores a row with missing fields. |
| 5 | Low | The Modify diagnostic chart (`modify_new_variables.png`) shows angle is weak and non-monotone (44–49 %, with a 55 % "90–180°" bin that is really just behind-the-basket shots). The text does not comment on its own diagnostic, and `angle_deg` and `abs_angle` both enter the model. | Interpret the chart, and keep one angle representation unless validation shows both help. |
| 6 | Low | Dropping `HTM`/`VTM` as "home team code" gives no reason. A derived `is_home` flag is shot *context*, not shooter identity, and is a legitimate candidate. | State why home/away is excluded, or test `is_home`. |
| 7 | — | Done well: the drop log is explicit and correctly reasoned (leakage, constants, IDs, identity by design). The geometry-derived 3PT flag is validated at 99.95 % agreement. All learned transforms sit inside the pipeline fitted on train only. Shipping `engineer()` as shared score code (`shot_features.py`, verified identical in the app folder) is exactly the right deployment pattern. | — |

**Verdict:** Excellent structure (score code, pipeline-contained fitting). But the rare-level pooling is substantively wrong, and several features and the imputation path are not backed by evidence or code.

---

## Model · grade B−

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **Unequal tuning budgets make the comparison unfair.** The tree gets 6 depths and Gradient Boosting gets 4 settings, while Regression runs at default `C=1.0` and the NN gets a single architecture with default learning rate and no search. "GB wins" is partly "GB was tuned". | Give every family a comparable validation search (e.g. C ∈ {0.01…10} for Regression; 2–3 widths, alpha and learning rate for the NN). Report the search size per node in the settings table. |
| 2 | High | **Winners are picked at noise level, with no uncertainty.** GB 0.6346 vs Ensemble 0.6352 (Δ 0.0006). The four GB settings span 0.6346–0.6352, and "best" is chosen by the 4th decimal. No interval is reported, so the champion choice is not statistically supported. | Run a paired bootstrap over *games* on the validation partition and report the 95 % CI of each model's log-loss difference vs GB. If they overlap, choose by parsimony or speed and say so. |
| 3 | Medium | **The baseline is a low bar.** The zone average uses location only, but every learned model also sees `ACTION_TYPE`, the strongest variable. "Beats baseline" therefore mostly shows that action type helps. No no-information baseline is shown either: the league-mean log loss is about 0.691. | Add (a) the constant base rate and (b) a zone × shot-family average. Report the gain over (b) as the honest headline. |
| 4 | Medium | **"Fully interpretable" Regression is not interpretable as presented.** `OneHotEncoder` keeps all levels (no reference category), so coefficients are identified only by the L2 penalty. Linear `dist_ft`, `distance_bin`, `is_three` and `heave` are collinear: `distance_bin_30+ ft` comes out **+0.495**, i.e. long shots "help". Reading "dunks +1.0 to +1.7 log-odds" as effects is invalid. There are also no action × distance interactions, so a "Jump Shot" at 2 ft and at 25 ft share one action effect. | Use `drop="first"` (or effect coding), remove redundant distance encodings, add an action-family × distance-bin interaction, and interpret only after that. |
| 5 | Medium | **No champion interpretation.** EM's Gradient Boosting node reports variable importance, but the notebook never shows what the champion relies on. | Add permutation importance on validation and partial dependence for distance, action family and seconds left. |
| 6 | Low | **Ensemble design and timing are not explained.** The Decision Tree is excluded from the Ensemble without a stated reason. HGB's `early_stopping=True` holds back 10 % of *train* internally, so GB fits on 90 % while the others fit on 100 %. Fit time is `NaN` for the tree and the ensemble in the comparison table. | Explain member choice (or try weights fitted by a validation-CV stack). Note the internal split. Record fit times for all nodes. |
| 7 | — | Done well: all tuning used only the validation partition, the test set was never touched in Model, five EM-equivalent families plus a baseline are included, and settings are tabulated. | — |

**Verdict:** The right set of competing nodes and clean partition discipline. But the contest is unevenly configured and decided on differences no larger than noise.

---

## Assess (incl. Deployment and SAS appendix) · grade B

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The "repeatable skill" conclusion (r = 0.68) is not supported as stated.** FG − xFG is a *player-level residual*. It persists both for genuine shot-making and for any shot-quality the model cannot see but which is stable for a player's role (defender distance, self-created vs assisted, post-ups). The notebook lists exactly these omissions, then still calls the residual "skill". There is also no benchmark: if raw FG% persists at a similar r, xFG adds nothing to the claim. The sample is 124 players (95 % CI roughly 0.57–0.77), with survivor selection (500+ FGA in both seasons). | Rename it a "persistent residual (skill plus unmodelled context)". Report the persistence of raw FG% and of xFG% alongside it, give a CI, and note the selection. |
| 2 | High | **Calibration is checked by decile only, not by segment.** The leaderboard depends on calibration *within shot types*. If threes or post shots are systematically mis-predicted, high-volume shooters of that type are inflated or deflated. Decile calibration on OOT (max gap 0.9 pp, verified) cannot detect this. On validation, the NN's low end (0.28 → 0.32) and Regression around 0.5 are visibly off, so "all models are well calibrated" overstates the picture. | Add OOT calibration by zone, 2PT/3PT, action family and season. Report the gap per segment, and feed any large gaps back as a leaderboard caveat. |
| 3 | Medium | **The deployed champion is not refit.** The app model is trained on 120k shots (about 12 % of the population), even though the learning curve is still falling and test/OOT confirmed the configuration. Standard practice after selection is to refit the chosen configuration on train + validate, or a larger sample, and then deploy. | Refit the selected configuration on train + validate (or the full 2019-24 population). Re-run the OOT check once, and deploy that model. |
| 4 | Medium | **The single-use status of the test and OOT sets is weakened by iteration.** Cells labelled "Critique fix: tune the boosting model…" and "Critique fix: calibration by decile on the unseen 2024-25 season" show the pipeline was revised after earlier runs had already shown test and OOT results. The effect is probably small here, but "untouched" is no longer strictly true, and the "Critique fix" comments are process leftovers in a final deliverable. | Disclose the revision history in one sentence ("test/OOT were viewed in earlier iterations"). Remove the "Critique fix" labels. For a clean result, add a later season or a fresh untouched hold-out. |
| 5 | Medium | **Player rankings have no uncertainty, and the narrative over-reads.** With about 1,000 FGA, the SE of FG% is about 1.6 pp, so many top-15 and bottom-5 ranks are not distinguishable. "SGA takes *harder* shots than Jokić" rests on a 0.6 pp xFG difference (46.1 vs 46.7 %), which is noise. "Mostly young players … development curves" is speculation (Scottie Barnes is in his 4th season and is listed). | Add binomial or bootstrap CIs for FG_over_expected, and shrink toward 0 (empirical Bayes). Soften or quantify the narrative claims. |
| 6 | Low | **Points use the geometry `is_three` (99.95 % agreement), not the official `SHOT_TYPE`.** Actual points should come from the official record. Saying "no over-fitting" because test ≈ validation tests only selection bias; it is not a train-vs-validation check. | Compute actual points from `SHOT_TYPE`. Report train log loss to support the over-fitting claim. |
| 7 | Medium | **Deployment is not finished.** App URL, article and video are still `<deployed URL>` / `<…link>` placeholders in both the packet and the README. `requirements.txt` pins scikit-learn and numpy but leaves **pandas** and **streamlit** unpinned. `engineer()` relies on pandas casting behaviour, and the pickled pipeline embeds it. | Deploy and insert the URL. Pin pandas and streamlit to the training versions. Add an automated smoke test in CI (the demo-row cell already exists). |
| 8 | Low | **The app accepts out-of-domain input without warning.** Any action can be paired with any location (e.g. "Cutting Dunk Shot" at 35 ft). The clock input allows 12:59 in a 12-minute quarter. Monitoring covers only calibration-in-the-large, not `ACTION_TYPE` label drift. | Add a warning when the action/distance combination has fewer than N training shots, and clamp the clock to 12:00 (5:00 in OT). Add label-drift and per-segment calibration checks to monitoring. |
| 9 | Low | **The SAS appendix is instructions only, with gaps.** No EM run is shown, so the node mapping in the intro table is asserted, not demonstrated. The export keeps `EVENT_TYPE` (the target leak) and relies on the user to reject it. EM is told to partition randomly by row, losing the game grouping. Step 7 says "Score on 2024-25", but no 2024-25 file is exported. The suggested selection statistic (misclassification/ASE) differs from the notebook's log loss without comment. | Drop `EVENT_TYPE` from the export. Export three files (train/validate/test) and assign Input Data roles so EM uses the same game-grouped partition. Export a 2024-25 scoring file. Pick ASE and explain that it equals Brier. Include EM screenshots if access is obtained. |
| 10 | — | Done well: log loss is the right selection criterion for a probability product. Test and OOT are scored in a single cell. OOT decile calibration was verified (max |gap| 0.885 pp). The lift (≈ 1.8× in the top decile), cutoff table and all quoted numbers match the outputs. The score code is shared with the app. | — |

**Verdict:** Assessment mechanics are strong and the numbers check out. The headline player-level conclusion ("repeatable shot-making skill") claims more than the evidence supports, and segment calibration is missing.

---

## Overall grade: B

A well-organised, honest SEMMA project with good partition discipline and a reusable score code. It is held back by a broken Variable Selection figure, a flawed rare-level grouping, an uneven model contest decided at noise level, and a player-level "skill" claim that runs ahead of its evidence.

### Top 5 fixes (ranked)
1. **Back up or soften the "repeatable shot-making skill" claim.** Add OOT calibration by segment (zone, 2PT/3PT, action family). Add CIs and shrinkage to player FG-over-expected. Benchmark r = 0.68 against the persistence of raw FG% and xFG%. Call it a persistent residual unless the benchmark supports more.
2. **Redo the `ACTION_TYPE` Replacement.** Pool by shot family or target rate instead of a 0.5 % frequency cutoff that merges dunks with bank jumpers, and restrict the app dropdown to modelled levels.
3. **Make the model contest fair and statistically grounded.** Give Regression and the NN real validation searches, add a zone × action-family baseline and the base-rate log loss, and choose the champion with paired, game-level bootstrap CIs rather than 4th-decimal differences.
4. **Fix the Explore variable-worth analysis.** Regenerate `explore_variable_worth.png` on its own axes (the current PNG is a corrupted overlay on the previous figure). Use one bias-corrected MI estimator so PLAYER_NAME's 0.022 (about 0.015 of which is plug-in bias) is not misreported. Correct the Finding 1 numbers (30 ft ≈ 31 %, not 23 %).
5. **Finish deployment honestly.** Refit the chosen configuration on train + validate (or more data) before deploying. Pin pandas and streamlit. Make `engineer()` keep NaNs so the Impute node actually works. Replace the `<deployed URL>` placeholders, and drop `EVENT_TYPE` from the SAS export.


---

# Responses to round 2 (what changed in the notebook)

The full notebook was re-run end to end after these changes. All numbers below come from the re-run.

## Sample
| # | Response |
|---|---|
| 1 | **Fixed.** The learning curve uses early stopping and extends to 240k and 480k training shots, drawn from population games outside validation and test: 0.6351 at 120k → 0.6338 at 480k. The text says honestly that the last 360k shots buy about as much as the gap between the top models. 200k is kept for comparing model families, and the **deployed** model is refit on train + validate (160k). |
| 2 | **Fixed.** FG% and season shares are now described as matching *by design*. Representativeness is tested against the **unsampled remainder** on unstratified variables: distance, LOC_X, 3PT share, ACTION_TYPE mix, both zone mixes and overtime share, with all p ≥ 0.37. |
| 3 | **Fixed.** The text now says game grouping guards against within-game correlation only, and explains why player-level correlation is acceptable (identity is not an input; the out-of-time season is the real test). The player-grouped sensitivity partition was not added. |
| 4 | **Partly.** Season shares per partition are reported (all within 3 points). The split itself was not changed to `StratifiedGroupKFold`: the differences are small and the partitions are documented. |
| 5 | **Fixed.** The 199,999 rounding is stated, and the validate ∩ test disjointness assert was added. |

## Explore
| # | Response |
|---|---|
| 1 | **Fixed.** The root cause was a plotting bug in the original execution environment (figures were not closed, so the next chart drew on top). `savefig` now closes every figure, and the variable-worth chart has its own axes. All figures were re-checked. |
| 2 | **Fixed.** Discrete MI is Miller–Madow corrected. PLAYER_NAME drops from 0.022 to **0.008** (bias 0.013), and the prose is rewritten. ID columns are excluded from the candidates. |
| 3 | **Fixed.** Finding 1 now uses printed values (76 / 71 / 59 / 48 / 41 % at 0–5 ft; 31 % at 30 ft; 23 % at 33 ft). Finding 2 uses a matched-distance comparison. |
| 4 | **Fixed.** An anomaly table was added (beyond half court, behind the hoop line, > 40 ft, backcourt), with a keep decision and the heave flag as the treatment. The missing-value count is printed. |
| 5 | **Partly.** No Variable Clustering matrix. Overlap was handled in Modify instead: one angle representation, and the clutch / overtime flags dropped. |
| 6 | **Fixed.** A label-stability check by season was added (2 of 48 labels missing in some season, 0.12 % of shots). The post-hoc scorer annotation is stated as a limitation. |
| 7 | **Fixed.** Corner vs above-the-break at **matched distance** (22–24 ft): 38.3 % vs 35.3 %, so angle matters beyond distance. The clusters are labelled "descriptive only". |
| 8 | **Fixed.** Identifiers are excluded from the numeric summary. |

## Modify
| # | Response |
|---|---|
| 1 | **Fixed.** Added `action_family` (dunk, layup, alley-oop, tip/putback, hook, floater, bank, fadeaway, pull-up, jump). The 19 pooled rare labels keep their family (6 dunks, 5 bank shots, …). The app dropdown is limited to the 44 labels with ≥ 50 training shots. |
| 2 | **Fixed.** A two-way FG% table (time left × distance) justifies `heave` (8 % for ≤ 3 s at 30+ ft, vs 33 %). `clutch` and `is_overtime` had no supporting finding and were removed. |
| 3 | **Fixed.** Finer rim bins (0–1, 1–2, 2–3, 3–5 ft) and `log_dist` were added. The regression gained about 0.004 log loss (0.6400 → 0.6358). |
| 4 | **Fixed.** `engineer()` keeps NaNs (numeric coercion, object columns with NaN), so the imputer actually runs. A unit test scores a shot with missing location, clock and action. |
| 5 | **Fixed.** Only `abs_angle` is kept. The angle chart is restricted to shots 5+ ft out, so behind-the-basket shots no longer dominate it. |
| 6 | **Fixed (documented).** HTM/VTM: the app scores a shot without a game context, so home/away is left out, and the drop log says so. |

## Model
| # | Response |
|---|---|
| 1 | **Fixed.** Regression is tuned over 4 values of C and the neural network over 4 configurations. The settings table reports the search size per node. |
| 2 | **Fixed.** A paired bootstrap over validation games was added. GB and the ensemble are tied (Δ +0.0001, CI −0.0003 to +0.0005), and GB is kept as the simpler single model. NN, regression and tree are clearly worse. |
| 3 | **Fixed.** Added a base-rate baseline (0.691) and a zone × shot-family baseline (0.6454). The honest gain over the strong baseline is 0.0116 log loss (1.8 %). |
| 4 | **Partly.** The coefficients are now described as directional only (L2-identified, overlapping encodings). `drop="first"` and interaction terms were not added, because the regression is a benchmark, not the champion. |
| 5 | **Fixed.** Permutation importance of the champion on validation: LOC_Y 0.043, ACTION_TYPE 0.039, LOC_X 0.037, clock ≈ 0.001. |
| 6 | **Fixed.** The ensemble member choice is explained, early stopping's internal 10 % is noted, and fit times are recorded for every node. |

## Assess (incl. Deployment and SAS appendix)
| # | Response |
|---|---|
| 1 | **Fixed.** Persistence is benchmarked: FGOE r = 0.68 (CI 0.57–0.77), raw FG% 0.86, xFG% 0.94. The claim is renamed a **persistent residual** (skill plus unmodelled stable context), and survivor selection is noted. |
| 2 | **Fixed.** Calibration on 2024-25 by zone, 2PT/3PT and shot family was added. Everything is within 2.1 points except backcourt heaves. Layups are under-predicted by 2.1 points, which is fed back as a leaderboard caveat (rim attackers slightly flattered). |
| 3 | **Fixed.** The deployed model is refit on train + validate (160k shots) and checked once on 2024-25 (log loss 0.6370, the same as the assessed model). |
| 4 | **Fixed.** Disclosed that test / out-of-time were scored in revision 1 before tuning. The "Critique fix" labels were removed. |
| 5 | **Fixed.** Every player gets a binomial 95 % interval and an empirical-Bayes shrunk estimate. 62 of 181 players are clearly different from 0. "SGA takes harder shots" and the speculation about young players were softened. |
| 6 | **Fixed.** Points use the official `SHOT_TYPE`. Training log loss (0.6320) is reported to support the over-fitting claim. |
| 7 | **Partly.** pandas is pinned (`streamlit>=1.40`), and the deployment cell runs a smoke test. The app URL depends on the author's Streamlit deployment, which follows this revision. |
| 8 | **Fixed.** The app warns when a shot family / distance combination had < 30 training shots, and the clock is clamped (12:00, OT 5:00). Monitoring adds segment calibration and label drift. |
| 9 | **Fixed.** `EVENT_TYPE` was dropped from the export. A `_PARTITION` column carries the game-grouped split, a 2024-25 scoring file is exported, and ASE (= Brier) is chosen and explained. EM screenshots depend on the class being registered for SAS OnDemand. |
