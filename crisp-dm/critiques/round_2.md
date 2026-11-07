# CRISP-DM critique — round 2

**Reviewer:** an independent Claude instance (Anthropic), started fresh. It had no access to the drafting conversation or to round 1. It received a plain-text export of the executed notebook (markdown, code and text outputs), the figure PNGs, and the app and report files. For each phase it adopted the expert-persona prompt shown in that phase's critic section of the notebook, and answered it.
**Date:** 6 November 2026. **Below:** the review exactly as returned, followed by the response to each point.

---


Scope: the review packet (executed notebook export), every referenced figure (opened and inspected; the notebook's own embedded PNGs were also extracted and checked), plus `app.py`, `model_metadata.json`, `requirements.txt`, `sample_bookings.csv`, `README.md` and `artifacts/reports/*.csv`. The `critiques/` folder was not read.

Numbers checked and found correct: the 37.0 % cancellation rate, 41.7 / 27.8 % by hotel, lead-time bins (9.6 % → 68 %), segment rates, the 62 % / 28 % Portuguese shares, the CV table, the tuning log, test metrics (0.8676 / 0.7718 / 0.6827), the confusion matrix (6,640 / 3,086 / 1,963 / 12,106), net value (€19,655, €17,029, −€18,252 per 1,000), the "~15 % more than 0.5" figure (19,655 / 17,029 = 1.154), the per-hotel table, the sensitivity table and the PSI values. The prose is numerically honest. The problems are in method, evidence and deployment, not in arithmetic.

---

## Phase 1 — Business Understanding · grade B−

*Persona: CRISP-DM authority reviewing against BU tasks 1.1–1.4.* Every generic task and named output is present (background, objectives, business success criteria, inventory, requirements/assumptions/constraints, risks, terminology, costs/benefits, DM goals, DM success criteria, project plan, initial tools assessment), and that is better than most engagements. The weak points are the economics and how the criteria fit together.

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The flag triggers an undefined action, so the cost model has nothing concrete to price.** 1.1 lists three different interventions (deposit request, reminder, count in overbooking). 1.2 prices a FP as "room oversold, guest walked" (−€100) and a TP as "room re-sold or deposit secured" (+€100). A reminder costs about €0 when wrong. A deposit request to a genuine guest risks *losing the booking*, which is not priced. A walk only happens if the hotel is actually full on that date, so it is not one walk per FP. The one number used for all three actions is not defensible, and it drives the threshold. | Pick the primary action (e.g. "add flagged bookings to the overbooking count") and price it. Alternatively, build a small cost matrix per action and derive one threshold per action. State the walk probability per FP explicitly (P(full) × walk cost). |
| 2 | High | **The precision criterion can be met trivially because there is no recall or coverage floor.** "Precision ≥ 0.75 at the chosen threshold": any threshold high enough meets it (the PR curve shows precision ≈ 1.0 up to recall 0.24). Separately, the business criterion "clearly above flag everything" is satisfied by construction: with symmetric ±€100 and a base rate < 50 %, "flag all" is *always* negative, so it is a straw man. | Restate as "precision ≥ 0.75 **and** recall ≥ X" (or "≥ Y % of cancellations flagged ≥ 7 days before arrival"). Replace the "flag everything" benchmark with the realistic incumbent: the current rule-of-thumb overbooking policy, or a simple deposit/lead-time rule. |
| 3 | High | **No legal or ethical requirement is recorded, although nationality is used to drive a customer-facing action.** Requirements list explainability and reproducibility but not GDPR, data protection or non-discrimination. `country` later becomes the #1 driver, and a flag triggers deposit requests, which would effectively mean asking for deposits by nationality. CRISP-DM 1.0's "Requirements, assumptions and constraints" explicitly covers legal and security requirements. | Add a legal/ethical requirement ("no differential customer treatment on nationality without legal review") and a matching risk row. Decide up front whether `country` may drive guest-facing actions or only internal overbooking. |
| 4 | Medium | **The cost figures are asserted, and no sensitivity analysis is planned.** €100 = "≈ 28 % of an average booking recovered" has no basis for the 28 %, and "≈ one night's ADR" for a walk is low by industry convention (a comparable room plus transport plus compensation and loyalty damage often costs 1–2 nights or more). With VALUE_TP = COST_FP and COST_FN = 0, the optimal threshold for a calibrated model is exactly 0.5. Every downstream € figure depends on this ratio. | Plan (and later run) a sensitivity grid over COST_FP/VALUE_TP ∈ {0.5, 1, 2, 3}, and report the threshold and value for each. Cite a source for walk costs or label the figures "placeholder pending hotel finance". |
| 5 | Medium | **The business objective has no baseline or target.** "Reduce the revenue lost to cancellations" is never quantified: no € lost per year today (≈ 37 % × €358 × ~55k bookings/yr) and no target reduction. The €358 "average booking" is mean(ADR) × mean(nights), which is not mean(ADR × nights), and it includes €0-ADR complimentary stays. | Quantify the current loss and set a target (e.g. "recover ≥ 5 % of lost revenue in the pilot"). Compute the booking value as mean(adr × total_nights) over arrived bookings. |
| 6 | Medium | **The representativeness assumption is unrealistic and appears in no risk row.** "2015–2017 behaviour is representative of future bookings" is the most fragile assumption for a model deployed in 2026: the data predates the pandemic and the shifts in OTA and free-cancellation norms. | Add this as a High-likelihood risk, with the contingency "retrain on the hotel's recent PMS data before go-live; treat the 2015–17 model as a proof of concept". |
| 7 | Low | **The project plan's iteration claim is mislabelled.** It says the "Evaluation → Business Understanding" loop "happened", but what changed was the *test design* (a Modeling task), not the BU outputs. The "Usability: working web app" criterion has no measure (no task-completion or staff test). | Correct the iteration description. Make usability measurable (e.g. "3 reservations staff score a day's file unaided in < 5 min"). |

**Verdict:** structurally complete and well organised, but the economic core (which action is taken, what it costs, a non-trivial benchmark) and the criteria design (no recall floor, legal constraint missing) are not yet at professional standard.

---

## Phase 2 — Data Understanding · grade B

*Persona: CRISP-DM authority reviewing against DU tasks 2.1–2.4.* All four tasks and their reports are present. The format audit of both files and the Non Refund profile are genuinely good, and every number in the exploration report matches the figures.

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The leakage audit does not cover every attribute; it skips the attribute that matters most.** `leakage_suspects()` drops any column with > 30 levels and any group < 1 % of rows. That silently excludes `country` (177 levels), `agent`, `company`, `lead_time` and `adr`, and `country` turns out to be the #1 driver and the main leakage worry. The "known at booking time?" audit in 2.2 is a three-bucket prose paragraph, not a per-attribute table with evidence. `adr` (computed from lodging transactions, which can be revised at checkout for arrived guests), `customer_type`, `deposit_type` and `agent` are classified as "clearly known" without justification. | Produce a 31-row table: attribute · when recorded · can be updated? · evidence · decision. Extend the detector to high-cardinality and numeric columns, e.g. a single-feature time-split AUC per attribute, flagging any > 0.80. |
| 2 | Medium | **The hypotheses are implications, not tests, and the testable ones go untested.** The "block allocation" explanation for Non Refund could be checked in the data: what share of NR rows are exact duplicates, how concentrated they are in a few agents, and whether they cluster on arrival dates. The country-leakage hypothesis could be partly tested: within Online TA, compare the PRT share among cancelled vs arrived bookings, and among cancellations made long before arrival (via `reservation_status_date`). A default-to-PRT effect would show there. | Add a "test" column to the exploration report and run the three checks above. Report the result as supported or refuted. |
| 3 | Medium | **Drift over calendar time is never explored, even though it is a top-two risk.** All seasonality plots pool years by month-of-year. The train/test base-rate gap (36.1 % vs 40.9 %) is only discovered in 3.5. | Plot the monthly cancellation rate on the real timeline (Jul 2015 – Aug 2017) per hotel, plus lead-time and segment mix over time. |
| 4 | Medium | **The 31,994 duplicates (27 %) are explained by assertion.** "Plausibly separate rooms of a group booking" is a testable claim (share of duplicates in Groups / Offline TA/TO / NR, group size per duplicate set), but nothing is tested. This decision later shapes validation and the 0.956 → 0.868 story. | Profile duplicate sets by segment, deposit type and size. If most are NR/Groups, say so: it also supports the block-allocation hypothesis. |
| 5 | Low | **Implausible values are not listed in the quality report.** `adults` up to 55, `babies`/`children` up to 10, stays up to 69 nights and `lead_time` 737 are visible in the histogram and later in `model_metadata.json` min/max, but none appear in the quality report. Non-complimentary bookings with `adr = 0` are also unexamined. | Add rows for these with counts and a remedy (cap, flag or verify). |
| 6 | Low | **Code and figure blemishes.** `padded_text` is checked only on the resort file (`a[c]`), not both files. The `adr` histogram is stretched to 5,400 by one outlier, so it is unreadable. The month plot labels only every other month. Pearson correlation on heavily skewed counts is a weak screening tool. | Check both files. Clip the `adr` axis at the 99th percentile. Label all months. Use Spearman, or bin-wise rates. |

**Verdict:** solid, honest and well documented; it loses marks because "every attribute was audited for leakage" is not literally true, and the most consequential hypotheses were left untested.

---

## Phase 3 — Data Preparation · grade B−

*Persona: CRISP-DM authority reviewing against DP tasks 3.1–3.5.* All five tasks and both phase outputs are present. Fitting all preprocessing inside the pipeline is correct, and validating the integration against the published combined file is exemplary.

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The booking date is not "unavailable": it can be derived exactly as `arrival_date − lead_time`.** 1.2 and 2.1 list "no booking date" as a constraint and as "data wanted but unavailable", but by the dataset's own definition it can be reconstructed. That matters for the split: deployment scores *new bookings each morning* (6.1), yet the split is by **arrival** date. Some test-period bookings were made in 2016, before many training bookings, and their outcomes would not have been known when they were scored. A booking-date split with an outcome-known cut-off is the design that actually mirrors use. | Construct `booking_date`. Re-split on booking date, keeping in training only bookings whose arrival is before the cut-off (outcome known), and report test metrics under that design. Remove "booking date unavailable" from the constraints. |
| 2 | Medium | **The derived attributes are not justified by exploration findings, and the results show they add almost nothing.** `arrival_weekday`, `adr_per_guest`, `has_company` and `room_type_x_hotel` have no supporting finding in 2.3 (there was no weekday or price analysis). Their permutation importances are ≈ 0: 0.0021, 0.0002, 0.0004, 0.0004, and `has_agent` is −0.0001. | Tie each derived attribute to a numbered 2.3 finding, or drop it. Consider ones that *are* motivated by the findings, e.g. `lead_time` × `hotel` and a `previous_cancellations` ratio. |
| 3 | Medium | **Some Phase 2 quality issues are carried into the model unresolved.** `adults` = 55, `children` = 10, `babies` = 10 and 69-night stays remain (they now set the app's input ranges). The `children` NA handling is inconsistent: `total_guests` and `has_kids` are built with `fillna(0)` *before* the pipeline, while `children` itself is median-imputed inside it. | Resolve or explicitly accept each outlier class in the cleaning report. Use one consistent imputation rule. |
| 4 | Medium | **Exact linear redundancies are built in.** `total_nights` = week + weekend nights and `total_guests` = adults + children + babies are exact linear combinations, and `has_agent` is implied by `agent_id`. That is harmless for RF but contradicts the Phase 4 claim that logistic-regression multicollinearity was "checked". | Drop the components or the totals for the LR pipeline, or state the redundancy explicitly. |
| 5 | Low | **Same-date duplicates can straddle CV fold edges.** `TimeSeriesSplit` cuts by row position, so fold boundaries fall inside a date (fold 1 train ends 2015-10-25 and validation starts 2015-10-25). Identical same-day duplicate rows can therefore land on both sides. The train/test split uses `>` on dates, so it is clean. | Build the folds on date boundaries (e.g. a custom splitter on `arrival_date` quantiles, or `GroupKFold`-style blocking by date). |
| 6 | Low | **`StandardScaler` runs for the tree models, and `X[CAT] = X[CAT].astype(object)` is applied after `X_train`/`X_test` were already sliced (they are then re-sliced).** Both are harmless but untidy. | Scale only in the LR pipeline. Slice once. |

**Verdict:** leakage hygiene inside the pipeline is good and the integration check is a highlight, but the time split is aligned to the wrong event (arrival rather than booking), and the derived features are decoration rather than findings-driven construction.

---

## Phase 4 — Modeling · grade C+

*Persona: CRISP-DM authority reviewing against Modeling tasks 4.1–4.4.* All tasks and outputs are named. Moving from shuffled CV to time-series CV was the right call, and it is honestly documented.

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The "Assess model" figure is corrupted.** `model_cv_comparison.png` (and the same image embedded in the notebook) draws the ROC-AUC bars *on top of the stale correlation-matrix axes*: the heat-map cells, correlation values and colour bar sit under the bars, with an "adr" tick label. Cause: `cv_table[...].plot.barh()` without a new figure, in an environment where `plt.show()` did not close the previous figure. The one graphical output of 4.4 is unreadable, and the HTML/PDF report inherits it. | Use `fig, ax = plt.subplots()` for every plot, pass `ax=`, and `plt.close(fig)` after saving. Re-run and re-export the report. |
| 2 | High | **The test set was seen before the final test design was chosen.** 4.4 "Revised parameter settings" states that iteration 1 compared shuffled-CV 0.956 against **0.868 on the later test period**, and the design was changed *because of* that gap. So the test period informed a modeling decision. The claims "used once" and "never used for training or tuning" (headline, 4.2, 5.2, README) are therefore not strictly true. | Disclose it plainly. Better, carve out a fresh final hold-out (e.g. arrivals Jul–Aug 2017) that has never been scored, and report it as the confirmatory result. |
| 3 | Medium | **The baseline comparison is not meaningful, and the benchmarking is unequal.** The majority class (AUC 0.5) is a floor, not a benchmark. The ROC curve's vertical jump to TPR ≈ 0.24 at FPR ≈ 0 shows that one rule ("deposit = Non Refund") captures about a quarter of cancellations at about 100 % precision. A rule baseline (NR, or NR + lead time) is the comparison a hotel would care about. RF was given hand-picked parameters and then tuned, while HGB ran on defaults and was never tuned. The 0.007 AUC gap is a quarter of the fold SD (0.028), and no paired per-fold comparison is shown. | Add a rule-based baseline and a single-feature `lead_time` baseline. Tune RF, HGB and LR with an equal budget. Report per-fold scores and a paired comparison, and only declare a winner on a consistent per-fold margin. |
| 4 | Medium | **The search space is weak and the selection is optimistically biased.** The search covers 6 of 36 grid points (just grid-search all 36). The winner sits on the grid edge (`min_samples_leaf` = 20, the maximum offered), so the optimum may lie beyond it. "Adopt if best-of-6 > default" compares a maximum against a single draw: the +0.0019 gain is about 1/13 of the fold SD, i.e. noise. | Search the full grid and extend `min_samples_leaf` to {20, 50, 100} and `max_depth` to {None}. Adopt tuning only if it wins by more than about 1 SE of the per-fold differences. |
| 5 | Medium | **The model assumptions were not actually checked.** "Limited multicollinearity — correlations checked in 2.3" is false for the modeled matrix: there are exact linear dependencies (`total_nights`, `total_guests`) and one-hot redundancies (see Phase 3 #4), and 2.3 covered only 10 raw numerics. The RF "realistic probabilities" claim in 4.1 is an untested assumption. Phase 5 later shows a 0.34 optimum under symmetric costs, which points to miscalibration. | Compute VIF on the LR design matrix (or drop redundant columns). Add a reliability curve and Brier score per model to 4.4. |
| 6 | Low | **The narrative over-claims.** "The later folds (higher cancellation seasons) are harder" is not backed by any per-fold output. The model description says the output is "the share of trees voting cancel", but sklearn RF averages per-tree leaf class *probabilities*; it does not count hard votes. "Revised parameter settings" actually documents a revised *test design*. | Print per-fold AUC with fold dates. Correct the RF description. Put the parameter revision (default → tuned) under that heading and the CV change under 4.2. |

**Verdict:** the core validation idea is right, but a corrupted assessment figure, test-set information leaking into the design, and a benchmark set that cannot show whether the RF beats what a hotel already knows keep this below professional standard.

---

## Phase 5 — Evaluation · grade C+

*Persona: CRISP-DM authority reviewing against Evaluation tasks 5.1–5.3.* All outputs are present (assessment against business criteria, approved models, review of process, list of actions, decision). Choosing the threshold on out-of-fold training predictions is correct, and the per-hotel breakdown and leakage sensitivity test are the right instincts. Every reported number reconciles.

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **Two of the three evaluation figures are broken.** `eval_threshold_selection.png` has the correct title and axis labels ("Net value per 1,000 bookings vs. threshold", "decision threshold", "EUR") but shows the stale CV bar chart over the correlation heat-map, and **the threshold curve is not visible at all**. This is the single piece of visual evidence for the 0.34 choice. `eval_feature_importance.png` was drawn into the third panel of the test-performance figure: the importance bars are microscopic on a 0–1 axis, overlaid on the PR curve with an "AP = 0.83" legend. The notebook's embedded images and the HTML/PDF report are equally broken. | Same fix as Phase 4 #1. Then inspect every figure before submission. |
| 2 | High | **Probability calibration was not checked, although three decisions depend on it.** (a) Under the stated costs (+€100 TP / −€100 FP / €0 FN), a calibrated model's optimal threshold is exactly 0.5; finding 0.34 means the scores are under-confident or have shifted. (b) The app shows "Probability of cancellation 37.6 %" to staff. (c) 6.1 says "the sum of risks per arrival date informs the overbooking level", and that is only valid with calibrated probabilities. The OOF scores come from fold models trained on as little as 4 months, and the threshold is then transferred unchanged to a model refit on all data (6.1). | Add a reliability diagram and Brier score on OOF and on test. Calibrate with isotonic or sigmoid on time-ordered folds. Re-derive the threshold on calibrated scores, and re-derive it again for the refit model. |
| 3 | High | **The money comparison is against a straw man, and the dominant assumptions get no sensitivity check.** €19,700 per 1,000 is compared only with "do nothing" and "flag all". From the PR/ROC curves, a one-line rule "flag Non Refund" captures roughly 24 % of test cancellations at ≈ 100 % precision. That alone would be worth roughly €9–10k per 1,000 under the same cost model, so the model's *incremental* value over a trivial rule is about half the headline. There is no annualised sanity check either: ≈ 55k bookings per year × €19.7 ≈ €1.1 M per year for two mid-size hotels (about 5–6 % of the implied room revenue) should be stated and challenged. There is no sensitivity to COST_FP/VALUE_TP. | Add the NR rule and logistic regression to the `business` table. Add a cost-ratio sensitivity table (threshold, precision, € per 1,000 at FP/TP ratios 0.5–3). Annualise and sanity-check. |
| 4 | Medium | **The success criteria are met on thin margins with no uncertainty reported.** AUC 0.868 vs 0.85 (margin 0.018) while the fold SD is 0.028; precision 0.772 vs 0.75 overall and **0.754 for the resort**. Precision depends on prevalence, and the test period has a higher base rate (40.9 % vs 36.1 %), which flatters it. Precision at 0.34 on the training OOF is never reported. | Report block-bootstrap 95 % CIs (by arrival week) for AUC and precision, plus OOF precision at 0.34, and state whether the criteria are met at the CI lower bound. |
| 5 | Medium | **The fallback variant fails a success criterion, and nobody says so.** 5.3 action 2 says "deploy the 'without country' variant" if country turns out to be recorded at check-in, but its precision on the validation block is **0.743 < 0.75**. The variants are all scored at the *fixed* 0.34 threshold rather than a per-variant optimum, so the precision comparisons are not like-for-like. `deposit_type` (#2 driver, flagged as anomalous) and `adr` were not included in the sensitivity test. | Re-derive the threshold per variant on its own OOF scores. Add "without deposit_type" and "without adr" variants. State plainly whether the fallback meets both criteria, and if not, what the go-live decision becomes. |
| 6 | Medium | **"Test period used once" is contradicted three times.** By the iteration-1 comparison (Phase 4 #2), by permutation importance computed on test, and by the drift demo using test. The last two are interpretive and acceptable, but the QA statement in 5.2 is inaccurate. | Reword the QA statement to list every use of the test period and its purpose. |
| 7 | Low | **The review of process misses its own biggest misses.** It lists "probability calibration not checked" but not the broken figures, the arrival-vs-booking split, or the missing rule baseline. The decision is justified conditionally, which is good, but "Usability — see the deployed app" is marked met while the URL is still `<deployed URL>`. | Mark usability as "not yet verified" until the app is live and tried by a user. Add the omissions above to the review table. |

**Verdict:** honest and numerically correct, and the threshold was selected without touching test. But the key threshold figure is blank, the probabilities feeding both the app and overbooking were never calibrated, and the € value is never compared with what a trivial rule already delivers.

---

## Phase 6 — Deployment · grade C+

*Persona: CRISP-DM authority reviewing against Deployment tasks 6.1–6.4.* All four outputs exist (deployment plan, monitoring and maintenance plan, final report with executive summary, experience documentation). The PSI demo with a correct seasonal caveat and the named owner are good.

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The planned PMS integration cannot work as built, and the single-booking form is unrealistic for staff.** `construct()` runs *outside* the saved pipeline, so the model expects 32 columns including derived ones: `arrival_weekday`, `total_nights`, `total_guests`, `has_kids`, `adr_per_guest`, `has_agent`, `agent_id`, `has_company`, `room_type_x_hotel`, `arrival_date_week_number`. A raw "nightly export from the PMS" will hit the batch tab's "Missing columns" error. In the single-booking tab, staff must hand-enter 32 fields and can enter contradictions (April with week 40 and a non-matching weekday; `total_nights` ≠ week + weekend; `adr_per_guest` ≠ adr / guests) that the model silently scores. | Wrap `harmonize`/`construct` in a `FunctionTransformer` as the first pipeline step. Make the app ask only for raw booking fields (hotel, arrival date picker, nights, guests, ADR, segment, channel, deposit, agent, country, requests…) and derive the rest. Validate ranges and consistency. |
| 2 | High | **The deployed model is not the evaluated model.** It is refit on train + test (reasonable), but the threshold 0.34 and the `test_metrics` shown in the app caption ("test ROC-AUC 0.868") belong to the earlier model. The refit model's score distribution is unverified, and the app's smoke test scores `sample_bookings.csv` rows taken from `X_test`, which the deployed model was trained on. | Either deploy the evaluated model, or re-derive the threshold for the refit model via OOF on all data and label the metrics "estimated from the hold-out evaluation of the train-only model". Smoke-test on rows the deployed model has not seen, or on synthetic rows. |
| 3 | Medium | **Monitoring ignores the main drivers, and its own trigger already fires.** PSI is computed only for `NUM`, so `country`, `deposit_type`, `agent_id`, `customer_type` and `market_segment` (5 of the top 7 drivers) are not monitored. The plan sets "score PSI > 0.1 → review threshold", and the demo shows **0.118** at hand-off: the trigger has fired before go-live and the plan records no response. Label delay (outcomes arrive up to `lead_time` days later) is not addressed in the performance monitor. | Add categorical PSI or chi-square drift for the top categorical drivers. Record the decision taken on the 0.118 alarm. Define performance monitoring on arrival cohorts with the delay stated (e.g. evaluate month M at M + 1). |
| 4 | Medium | **The pilot cannot measure the € impact it promises.** "Compare with the same month last year" is confounded by trend, seasonality and the 2017 base-rate shift seen in the data. | Randomise: score every booking, but apply the action to a random 50 % of flagged bookings (or alternate days), and compare cancellation loss, walks and complaints between arms. |
| 5 | Medium | **There is no guardrail on nationality-driven actions.** Deposit requests driven by a model whose top driver is `country` would put nationality-based differential treatment of EU customers into production with no review. Neither the deployment plan nor the go-live condition covers this (the go-live condition concerns only *timing* of `country`). | Add a go-live condition: legal/DPO review. Restrict `country`-driven flags to internal overbooking only, or deploy the no-country variant for guest-facing actions. Log decisions for audit. |
| 6 | Medium | **The deliverables are incomplete.** The app URL is still `<deployed URL>` in the notebook and README, the article and video links are placeholders, and `video/` contains only a script. The final report (HTML/PDF) embeds the three broken figures. For a stakeholder, the "final report" currently has a blank threshold chart and an unreadable driver chart. | Deploy and insert the URL, fix and re-export the report, and record the video before submission. |
| 7 | Low | **Maintenance and operations details are thin.** There is no rollback or model-versioning scheme beyond a timestamp, no human-override or feedback capture (staff marking "flag was wrong"), and `pandas` is unpinned in `requirements.txt` although the pickled pipeline was built with pandas 3.0.5. The `number_input` ranges are hard-capped at the training max (e.g. `lead_time` ≤ 737), so valid new bookings can be rejected. | Version models (`model_v{date}.joblib` plus a hash), keep the previous model for rollback, add an override/feedback column in the batch output, pin pandas, and widen the input bounds. |

**Verdict:** the paperwork is complete and the monitoring plan has real triggers and owners, but the delivered app cannot take the data feed its own plan specifies, and the stakeholder-facing report and app are not in a deliverable state (broken figures, placeholder URL).

---

## Overall grade: C+ (borderline B−)

The project is unusually complete as a CRISP-DM document, every task and output is present, and the arithmetic is honest throughout. Judged as a professional engagement, though, it falls short in four places:

- **The evidence chain is broken.** Three of nine figures, including the threshold-selection and importance charts, are corrupted in the notebook, the PNGs and the report.
- **The money case is thin.** It rests on undifferentiated actions, untested cost assumptions, uncalibrated probabilities and a straw-man benchmark.
- **The validation story overstates its purity.** The test set was seen in iteration 1, and the split is by arrival rather than booking date.
- **The app cannot consume the PMS feed its own deployment plan describes.**

## Top 5 fixes (ranked by importance)

1. **Repair the three corrupted figures** (`model_cv_comparison`, `eval_threshold_selection`, `eval_feature_importance`). Create a fresh `fig, ax` per chart and `plt.close(fig)` after saving, then re-run and re-export the HTML/PDF report. These are the core visual evidence for model choice, threshold and drivers, and they are currently unreadable or blank.
2. **Rebuild the business case on defensible economics.** Define the single action a flag triggers and price it (including a walk probability rather than one walk per FP). Add a rule baseline ("flag Non Refund", worth roughly half the headline €19.7k per 1,000) and logistic regression to the € table. Run a COST_FP/VALUE_TP sensitivity grid. Add a recall floor to the precision criterion and replace the "beat flag-all" criterion.
3. **Check and fix probability calibration.** The 0.34 optimum under symmetric costs implies miscalibration. Add reliability curves and Brier scores, calibrate on time-ordered folds, and re-derive the threshold for both the calibrated model and the refit deployed model. The app's displayed probabilities and the "sum of risks" overbooking rule depend on this.
4. **Make deployment real.** Move `construct()` into the pipeline so the model accepts raw PMS fields. Cut the app form to raw booking inputs with consistency checks. Add categorical drift monitoring for country, deposit type and agent, and respond to the already-tripped score-PSI alarm (0.118). Design the pilot as a randomised holdout, deploy the app, and insert the real URL.
5. **Tighten validation honesty and leakage coverage.** Disclose that the test period informed the iteration-1 redesign, or reserve a fresh untouched hold-out. Construct `booking_date = arrival_date − lead_time` and validate on a booking-date split. Extend the leakage audit and sensitivity test to `country`, `deposit_type` and `adr`, re-deriving thresholds per variant. State that the no-country fallback misses the precision criterion (0.743), and add a legal/fairness review of nationality-driven actions as a go-live condition.


---

# Responses to round 2 (what changed in the notebook)

The full notebook was re-run end to end after these changes. All numbers below come from the re-run.

## Business Understanding
| # | Response |
|---|---|
| 1 | **Fixed.** A flag now has one action: the booking is counted in that night's overbooking allowance. It is internal, so guests are not contacted. The false-positive cost is priced as walk cost €200 × 50 % chance the hotel is full = €100 (`WALK_COST`, `P_FULL` in the config). |
| 2 | **Fixed.** Added a recall floor (≥ 0.50), disclosed as added after the first results. The business benchmark is now the "flag every Non Refund booking" rule instead of "flag everything". |
| 3 | **Fixed.** Added a legal/ethical requirement and a risk row: nationality may drive only the internal overbooking count, never a guest-facing action, without a legal / data-protection review. That review is a go-live condition (5.1, 6.1). |
| 4 | **Fixed.** A cost-ratio sensitivity grid (0.5–3) in 5.1 re-derives the threshold on training data for each ratio. At 3:1 the simple rule beats the model, and this is stated. |
| 5 | **Fixed.** Booking value is now mean(ADR × nights) over arrived bookings (€346, median €259), computed in 2.3. The yearly exposure (~€7 M of cancelled booked revenue) is stated in 1.1. |
| 6 | **Fixed.** Added "2015–17 behaviour no longer representative" as a High/High risk, with "retrain on recent data before go-live" as the contingency. |
| 7 | **Fixed.** The iteration description is corrected, and usability is now measurable (3 staff score a day's file unaided in < 5 min). |

## Data Understanding
| # | Response |
|---|---|
| 1 | **Fixed.** A second leakage detector scores **every** attribute alone on later arrivals (target-encoded, test period untouched). Only `reservation_status` stands out (AUC 1.00); country 0.64, deposit type 0.63, lead time 0.70. A full 31-row "when recorded" table was not added: the selection log (3.1) and quality report already give a decision per attribute. |
| 2 | **Partly.** The Non Refund hypothesis was tested: 98 % of NR rows are exact duplicates, which strongly supports block allocations. Their concentration across arrival dates is low (403 dates). The exploration report now has a "Tested?" column. The within-segment PRT share test was not run, because the single-attribute AUC and the 5.2 sensitivity test address the same question. |
| 3 | **Fixed.** Added a monthly cancellation-rate plot on the real timeline (finding 7): the resort rose from 25–26 % to 30 % in 2017. |
| 4 | **Fixed.** Duplicate sets are profiled (finding 8): 58 % cancel and 72 % are Groups / offline TA-TO, so they are mostly multi-room group bookings. |
| 5 | **Fixed.** Rows for ADR = 0 outside Complementary (1,279), stays > 30 nights, > 10 adults and ≥ 9 children/babies were added, each with a decision. |
| 6 | **Fixed.** The padded-text check now covers both files, the histograms are clipped at the 99.5th percentile, all months are labelled, and the correlation matrix uses Spearman. |

## Data Preparation
| # | Response |
|---|---|
| 1 | **Partly.** "Booking date unavailable" was removed from the constraints. A booking-date split was added as a robustness check in 5.1: bookings made after the cut-off score AUC 0.817, precision 0.65 and recall 0.39. That is a real finding, now in the headline caveats. The primary split stays by arrival date, because a booking-date split leaves only short-lead bookings in the test period (outcomes are not yet known for long-lead ones). |
| 2 | **Fixed.** `arrival_weekday`, `adr_per_guest`, `has_agent` and `room_type_x_hotel` were removed. They had no finding and an importance of ≈ 0, and CV AUC is unchanged (0.877 → 0.878). |
| 3 | **Fixed.** Outliers are explicitly accepted in the quality report. `children` NA is set to 0 consistently inside the score code. |
| 4 | **Documented.** The exact sums are harmless for trees, and the L2 penalty identifies the LR coefficients. LR coefficients are not interpreted one by one (3.5, 4.1). |
| 5 | **Fixed.** Fold edges are moved to date boundaries (`date_blocked_folds`), so same-day duplicates never straddle a fold. |
| 6 | **Not changed.** Scaling for trees is harmless. The double slicing was removed. |

## Modeling
| # | Response |
|---|---|
| 1 | **Fixed.** The root cause was a plotting bug in the original execution environment: `plt.show()` did not close figures, so the next chart drew on top of the previous one. `savefig` now closes every figure and every chart creates its own axes. All 9 figures were re-checked, and the report was re-exported. |
| 2 | **Disclosed.** The test period informed the iteration-1 design change. This is now stated in the headline, 4.2 and the 5.2 QA statement (which lists every use of the test period). No fresh hold-out exists in this data (it ends August 2017). |
| 3 | **Fixed.** Added the Non Refund rule and lead-time-only baselines (CV AUC 0.664 / 0.688). All three families get the same 8-candidate search budget. Per-fold scores and a paired comparison are reported: RF beats LR 5/5 and HGB 4/5 folds. |
| 4 | **Fixed.** The RF grid is extended (leaf up to 100, depth up to 40). Tuning is adopted only if the gain exceeds 1 SE of the paired fold differences. Result: RF defaults kept (+0.003 ± 0.005), LR tuned (C = 0.075). |
| 5 | **Fixed.** Calibration is checked with a reliability curve and Brier score (0.153 → 0.146 after isotonic). The multicollinearity claim is corrected (see DP 4). |
| 6 | **Fixed.** Per-fold AUC with dates is printed. "Later folds are harder" is replaced by the actual pattern (summer 2016 hardest). The RF description now says "averages leaf class shares". The revision history is listed under "Revised parameter settings". |

## Evaluation
| # | Response |
|---|---|
| 1 | **Fixed.** See Modeling 1. The threshold curve and importance chart are now readable. |
| 2 | **Fixed.** Isotonic calibration on the training OOF scores moved the optimal threshold to **0.49** under symmetric costs, as theory predicts. The deployed model is the evaluated model plus its calibrator, so the threshold applies to it unchanged. |
| 3 | **Fixed.** The business table now includes the Non Refund rule (€9,620 per 1,000) and tuned LR (€17,773). The model's increment over the rule is about €10,100. The cost sensitivity grid and the annualised sanity check (~€1.1 M, ~9 % of room revenue, flagged as high) were added. |
| 4 | **Fixed.** Block-bootstrap 95 % CIs by arrival week were added. AUC 0.867 (0.850–0.885), precision 0.763 (0.725–0.798), recall 0.702 (0.670–0.735). The criteria are met at the point estimate, not at the CI's lower end, and this is said plainly. OOF precision at the threshold is 0.794. |
| 5 | **Fixed.** Each variant now gets its own value-optimal threshold. Without-deposit-type and without-ADR variants were added. The no-country fallback now meets AUC and precision (0.863 / 0.83), with recall 0.57. |
| 6 | **Fixed.** The QA statement lists every use of the test period and its purpose. |
| 7 | **Fixed.** Usability is marked "not yet verified". The review table includes the omissions. |

## Deployment
| # | Response |
|---|---|
| 1 | **Fixed.** Construction is now score code (`booking_features.prepare`) and the first pipeline step. The model and the app take the **25 raw booking-system fields**. The single-booking form uses a date picker and derives month, ISO week and day, so contradictions are impossible. |
| 2 | **Fixed.** The deployed model **is** the evaluated model (training-period RF + isotonic calibration). An assertion checks that it reproduces the evaluated test scores. `sample_bookings.csv` holds raw test-period rows it has never seen. |
| 3 | **Fixed.** Categorical PSI for country, agent, deposit type, segment and others was added; agent mix drifts (PSI 0.43). The response to the 0.118 score-PSI alarm is recorded. Performance monitoring runs on arrival-month cohorts, with the label delay stated. |
| 4 | **Fixed.** The pilot is randomised by arrival date (act on flags for half the dates), and short-notice vs early bookings are reported separately. |
| 5 | **Fixed.** Flags drive only the internal overbooking count. A legal / DPO review is a go-live condition, and the app states that guests are not contacted on the basis of the score. |
| 6 | **Partly.** The broken figures are fixed and the report is re-exported. The app URL, article and video depend on the author's deployment and recording, which follow this revision. |
| 7 | **Fixed / planned.** Model versioning with rollback and a "flag was wrong" feedback column were added to the maintenance plan (not built yet). Implemented now: pinned pandas (and `streamlit>=1.40`), and input bounds widened to twice the training maximum. |
