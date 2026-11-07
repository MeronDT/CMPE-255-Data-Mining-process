# CRISP-DM critique — round 3

**Reviewer:** a new independent Claude instance (Anthropic), started fresh. It received a plain-text export of the revised, re-executed notebook (markdown, code and text outputs), the figure PNGs, and the app and report files. For each phase it adopted the expert-persona prompt shown in that phase's critic section of the notebook. It formed its own judgement first, and only then read `round_2.md` to check whether the previous responses were adequate.
**Date:** 7 November 2026. **Below:** the review exactly as returned, followed by the response to each point.

---


**Scope.** I read the full packet, opened all 10 figures, and checked the claims against `artifacts/app/app.py`, `booking_features.py`, `model_metadata.json`, `requirements.txt`, `sample_bookings.csv` and `artifacts/reports/*.csv` (tuning log, success criteria, per-hotel and booking-date tables). I formed my judgement before reading `critiques/round_2.md`.

**Arithmetic.** Most numbers check out: 37.0 / 41.7 / 27.8 % cancellation rates, the lead-time bins, segment and country rates, 62 % vs 28 % PRT shares, €346 per booking, ~€7 M exposure, ~55k bookings a year, €1.09 M ≈ 9 % of room revenue, the confusion matrix (6,830 / 2,896 / 2,126 / 11,943), net values (€19,769, €9,620, €17,773, −€18,252), the +€10,149 and +€1,996 increments, and the cost-sensitivity rows. The figures are now all readable and the round-2 plotting bug is gone. A few statements are inaccurate (listed below). The remaining weaknesses are mostly about what the numbers mean, not about arithmetic.

---

## Phase 1 — Business Understanding · grade B

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The cost model is internally inconsistent.** 1.2 conditions the false-positive cost on demand (walk €200 × `P_FULL` 0.5 = €100). The true-positive value is not conditioned the same way: it assumes the freed room is always re-sold (+€100). But a re-sale needs the same thing as a walk, namely demand that exceeds capacity that night. On a night the hotel would not fill, the extra room in the allowance finds no buyer *and* causes no walk. Consistent pricing gives TP = 0.5 × €100 = €50 and FP = €100. The effective cost ratio is then 2:1, not 1:1. By the notebook's own sensitivity table that means threshold 0.66, and the value per 1,000 bookings is about half of €12,242 ≈ €6,100 (the rule gives ≈ €4,800), not €19,800. The headline € figure and the threshold both depend on this. | Define both outcomes on the same event, P(demand ≥ capacity): TP = P_full × re-sale value, FP = P_full × walk cost. Re-derive `COST_FP`/`VALUE_TP`, the threshold and every € figure, or argue explicitly why re-sale does not depend on demand. |
| 2 | High | **The benchmark is not what the hotel does today.** The Background says the hotels already overbook "by a fixed rule of thumb". The business criterion still compares against status quo = €0 (no overbooking) and the Non Refund rule. The real incumbent is an aggregate per-night allowance, for example historical cancellation rate × bookings on the books. The decision is also a per-night quantity, so per-booking flags have to beat a per-night forecast to add value. | Add the incumbent policy (historical rate per hotel × month × lead-time band) as the business benchmark, and state the criterion as improvement over it. |
| 3 | Medium | **"Calibrated probabilities" is a data mining goal with no success criterion.** 1.3 says the probabilities *must* be calibrated because staff read them and the overbooking count sums them, yet the criteria table only has AUC, precision and recall. Calibration is therefore never passed or failed formally, even though 5.1 shows residual errors of about 0.1. | Add a criterion such as "Brier ≤ 0.15 and per-date expected-vs-actual cancellations within ±X %". |
| 4 | Medium | **The business criteria are still loosely quantified.** "Clearly above the simplest rule" has no margin. The ~€7 M exposure is stated but there is no target share to recover. The actionability target (≥ 75 %) just copies the data mining precision criterion. | Set numeric targets, for example "≥ €X per 1,000 above the incumbent with the bootstrap lower bound > 0" and "recover ≥ Y % of the €7 M". |
| 5 | Medium | **The missing stakeholder is not treated as a risk.** Every business input (walk cost, P_full, re-sale value, when `country` is recorded, the Non Refund meaning) is an assumption that only the hotel can confirm. The inventory lists no domain expert and the risk table has no row for "no access to the business". | Add the risk "no stakeholder or finance access: all costs and recording practices assumed", with the contingency "validate in a pilot kick-off; cost sensitivity in 5.1". |
| 6 | Low | **The recall floor was set after the results were seen.** It was set at 0.50 when test recall was already about 0.68–0.70. This is disclosed, but a floor chosen with the answer known is weak evidence. | Justify 0.50 from the business side (e.g. the minimum share of cancellations that makes the overbooking count useful), or report the result against several floors. |

Done well: all generic tasks and named outputs are present. The single internal action and the GDPR constraint are clear and consistently carried through.

**Previous-round responses:** #1, #3, #6 and #7 are adequately fixed. #2 is only partly fixed: the "flag-all" straw man was replaced by the Non Refund rule, not by the realistic incumbent the reviewer named (the rule-of-thumb overbooking). #5 is partly fixed: the exposure is quantified but there is still no target. The new `P_FULL` term was applied to one side of the ledger only (#1 above).

**Verdict:** complete and much more coherent than round 2. The economics still contain a pricing asymmetry that roughly halves the headline value and moves the threshold.

---

## Phase 2 — Data Understanding · grade B+

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The `country` leakage hypothesis is still untested, although the data can partly test it.** Country is the #1 driver (permutation 0.091) and a go-live condition. The single-attribute AUC (0.64) cannot detect *partial* leakage, for example a PRT default on the bookings that never checked in, because a defaulted subset blends into a field that is otherwise genuine. A threshold of "> 0.80 alone" is the wrong test for this failure mode. | Run the within-stratum test the round-2 reviewer proposed: inside each market segment × agent stratum, excluding Non Refund, compare the PRT share among cancelled vs checked-out bookings. Also compare No-Show vs Canceled vs Check-Out PRT shares (`reservation_status` is legitimate for exploration). A large within-stratum gap supports defaulting. Report it as supported or refuted. |
| 2 | Medium | **The drift evidence (finding 7) is confounded by season.** The yearly figures (2015: 25 %, 2016: 26 %, 2017: 30 %) average different months (2015 covers Jul–Dec, 2017 covers Jan–Aug). They are also means of monthly rates rather than booking-weighted rates. The "test period cancels more (40.9 % vs 36.1 %)" check compares an Apr–Aug window with all seasons, and finding 6 shows that Apr–Aug is high season for the resort. The timeline figure does suggest real drift when like is compared with like (resort Jun–Aug about 0.31–0.34 in 2016 vs 0.37–0.39 in 2017), but the notebook never makes that comparison. | Compare the same months year on year (Apr–Aug 2016 vs Apr–Aug 2017, per hotel, booking-weighted) and restate finding 7 and the 3.5 sentence on that basis. |
| 3 | Medium | **The second leakage detector is limited by construction.** For numeric fields it uses the raw value as the score with `max(auc, 1−auc)`, so it only detects monotone relationships. A non-monotone leak (e.g. a sentinel value) would be missed. The 0.80 cut-off is arbitrary. The 2.4 text says it "covers every attribute", which overstates what it can find. | Bin numeric fields (deciles, target-encoded on the fit block) before scoring. Describe the detector as a screen for strong single-field leaks, not as proof of absence. |
| 4 | Low | **The test cut-off line in `eda_timeline.png` is in the wrong place.** It is drawn at 1 April 2017 (the quantile of month-start dates), but the real cut-off is 22/23 April. | Draw the line at `df.arrival_date.quantile(0.8)`. |
| 5 | Low | **The duplicate profile mixes in Non Refund rows.** Finding 8 ("duplicates cancel 58 %") includes the Non Refund rows (35.6 % of the duplicates cancel at 99 %), so it says little about the remaining duplicates. 28 % of duplicate rows are not Groups/offline TA/TO and could be true system duplicates. | Profile the duplicates that are not Non Refund separately (segment, cancel rate, set size). |
| 6 | Low | **Some exploration claims are not backed by printed output.** The "62 % vs 28 % Portuguese" shares (finding 4) appear in no output cell. They are arithmetically consistent, but the reader cannot verify them. | Print them. |

Done well: the format audit of both files, the quantified quality report with a remedy per problem, the Non Refund and duplicate profiles, and the integration of the published files.

**Previous-round responses:** #3–#6 are fixed. #1 is fixed only in the narrow sense that every attribute is now scored; the per-attribute "when recorded" table was declined. #2's reason for not running the within-segment PRT test ("the single-attribute AUC and 5.2 address the same question") is **weak**. Neither test can distinguish a genuine nationality effect from a defaulted value: the AUC check misses partial leaks, and the drop-column test measures dependence, not leakage.

**Verdict:** strong and well quantified. The highest-stakes hypothesis is still the one left untested, and the drift claim rests on a season-confounded comparison.

---

## Phase 3 — Data Preparation · grade B+

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | Medium | **The selection log contradicts the Phase 2 audit.** `rationale_for_inclusion_exclusion.csv` labels `country`, `total_of_special_requests` and `adr` "known at booking time, potentially predictive". 2.2 classifies the first two as *ambiguous* (they can be updated after booking), and round 2 noted that ADR can be revised at checkout. This CSV is the auditable record of the leakage decision, and it says the opposite of the analysis. | Give these attributes their own rationale: "ambiguous recording time; kept; sensitivity in 5.2; confirm with hotel". |
| 2 | Medium | **The 27 % exact duplicates are kept with no sensitivity check.** Keeping them is defensible. But they weight the multi-room blocks (98 % of the Non Refund rows) heavily in both training and the test metrics. The precision and € figures in 5.1 therefore partly measure how well the model recognises duplicated Non Refund blocks (see Phase 5 #1). | Add a sensitivity run with each duplicate set collapsed to one row with a count weight (`sample_weight`), and report test metrics on the de-duplicated test set next to the headline. |
| 3 | Medium | **One derived-attribute rationale is false, and one attribute is unmotivated.** 3.3 says the effect of `total_nights`, `total_guests` and `has_kids` "is checked in the 5.1 importance ranking". 5.1 computes permutation importance on the 25 *raw* fields, so derived attributes are never scored individually. `has_kids` is tied to no exploration finding (there is no children/family analysis in 2.3). | Either compute importance on the model inputs as well (or a drop-column CV test), or remove the claim. Tie `has_kids` to a finding or drop it. |
| 4 | Low | **The pooling of `agent_id` is untested.** `OneHotEncoder(min_frequency=0.005, max_categories=30)` pools the 334 agents into at most 30 levels, although agent is the #2 driver. The choice is reasonable, but it is never compared with alternatives (for example out-of-fold target encoding). | Try one alternative in CV and justify the setting. |
| 5 | Low | **The 0.877 → 0.878 claim cannot be reproduced.** "Removing [4 features] did not lower CV AUC" refers to a previous run that is not in the notebook. | Keep the comparison in a cell or in a report CSV. |

Done well: building the features as score code inside the pipeline, so notebook and app share them; the integration check against the published combined file (exemplary); imputation fitted on the training data only; a clean arrival-date split; a cleaning report with counts.

**Previous-round responses:** #2, #3, #5 and #6 are adequately addressed (the score code is a real improvement). #4 ("documented") is acceptable for the tree models. For #1, the reason for keeping the arrival-date primary split is sound: a booking-date split would leave only short-lead bookings in the test period. But see Phase 5 #4: the same truncation undermines how the booking-date robustness check is interpreted.

**Verdict:** technically clean, with no train/test contamination found. The documentation of leakage decisions is inconsistent, and the duplicate weighting is never stress-tested.

---

## Phase 4 — Modeling · grade B

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The test period has been seen in every revision round, not only in iteration 1.** The round-2 critique quotes the then-current test metrics (0.8676 / 0.7718 / 0.6827). The revision 2 changes were made with those numbers visible: features dropped, the RF tuning reverted to defaults, isotonic calibration added, a recall floor added. Each change is individually justified on training data, but "Since then it has not been used for any choice" (4.2) is not accurate at the level of the analyst's decisions. This is the garden-of-forking-paths problem, and the margins are thin (precision 0.763 vs 0.75). | Reword 4.2 and 5.2 QA: "test results were visible during two review rounds; changes were justified on CV, but the test period is no longer pristine." Make CV the primary evidence for the criteria (report OOF precision/recall/AUC against 1.3 alongside test), and freeze the test period from now on. |
| 2 | Medium | **"The same tuning budget" is not an equal effort.** 8 random candidates is a fair budget for logistic regression (1 parameter), but thin for HGB (5 parameters, three of them continuous) and RF (60 grid points). Tuned HGB lost to its defaults (−0.002), which suggests an under-sized search rather than a ceiling. The ranking RF > HGB (+0.010, 4/5 folds) may reflect the search budget rather than the model families. | Scale the budget to the size of the search space (e.g. 30–40 candidates for HGB/RF), or use successive halving. Also give HGB native categorical handling (`categorical_features`) rather than one-hot. |
| 3 | Medium | **The calibrator is fitted on scores from weaker models than the one it is applied to.** The out-of-fold scores come from fold models trained on 16k–79k rows (fold 1 is 4 months of data), but the deployed RF is trained on 95k rows. Its score distribution differs from theirs, and the residual miscalibration on test (≈0.1 at predicted ≈0.45 and ≈0.83) is consistent with that mismatch. | Fit the isotonic map only on the OOF scores of the later folds (e.g. folds 4–5, the models closest in size), or on a held-back final training block scored by a model trained on everything before it. Compare Brier/ECE on test for each option. |
| 4 | Low | **The logistic regression's assumptions are stated but not checked.** 2.3 shows a concave lead-time effect, yet `lead_time` enters linearly (standardised). An LR with `log1p(lead_time)` or splines might narrow the €2,000 gap, and the gap is the argument for the less interpretable model. | Check linearity (binned log-odds vs `lead_time`) and refit LR with a transform before ruling it out. |
| 5 | Low | **Two claims are unsupported.** Fold 3 is "the season with the most group business" (no output shows this). `min_samples_leaf ≥ 5` "limits memorising duplicate rows" (duplicate sets of dozens of identical rows easily fill a leaf of 5). | Print segment mix per fold or remove the claim; reword the duplicate rationale. |
| 6 | Low | **There is no per-model calibration in 4.4.** Round 2 asked for reliability and Brier per model; only the champion gets them, in 5.1. LR is a candidate whose raw probabilities may already be well calibrated, which is relevant to its €17,773. | Add the Brier score per candidate (OOF) to the 4.4 table. |

Done well: date-blocked expanding folds; three meaningful baselines including the Non Refund rule; per-fold scores and paired comparisons; a conservative 1-SE adoption rule; a transparent iteration history.

**Previous-round responses:** #1, #3, #5 and #6 are fixed (verified: `model_cv_comparison.png` is clean and the per-fold CSV exists). #4 is fixed (verified in `tuning_results.csv`: the best RF candidate is now in the interior of the grid, depth 15 / leaf 5). #2 ("disclosed") is adequate for iteration 1, but the disclosure stops short of the later revision rounds (#1 above).

**Verdict:** a sound test design and honest benchmarking. The remaining issues are test-set exposure across review rounds and an unequal effective tuning effort.

---

## Phase 5 — Evaluation · grade B−

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The precision criterion is met because of the anomalous Non Refund block.** On test the rule flags 9.63 % of bookings (≈ 2,291) at precision ≈ 1.0, so ≈ 2,290 of the model's 6,830 true positives are Non Refund bookings. With a 99.4 % Non Refund cancel rate, the calibrated forest almost certainly flags all of them. Its flags on all *other* bookings are then ≈ (6,830 − 2,290) / (8,956 − 2,291) ≈ **0.68 precision**, below the 0.75 actionability target. 2.3 calls Non Refund a likely data artefact (block allocations, 98 % duplicates) whose meaning only the hotel can confirm. If the hotel already knows these blocks will be released, the model's real actionability on individual bookings fails the criterion. | Report precision, recall and € for flags outside Non Refund (and de-duplicated, Phase 3 #2) next to the headline. State whether the actionability criterion holds there. Add this to the approval conditions. |
| 2 | High | **The money case is computed per booking, but the action is per night.** The flag's action is to add the booking to *that night's* allowance. Whether a false positive causes a walk depends on the net error that night: a missed cancellation on the same night (FN) offsets a false flag (FP). On test there are more misses (2,896) than false alarms (2,126), so many nights would see no walk at all, while on other nights FPs pile up. Pricing each FP independently at €100 (and, per Phase 1 #1, each TP at €100 regardless of demand) is not a model of the decision being made. The "sum of probabilities per arrival date" (6.1) is never evaluated either. | Simulate on the test period per hotel × arrival date: allowance = flagged count (or Σp), re-sold rooms = min(allowance, actual cancellations), walks = max(0, allowance − actual cancellations) × P_full. Compare with the incumbent (historical rate × bookings). Report € with a block-bootstrap CI. |
| 3 | Medium | **The decision says "all three criteria met", but they fail for important subgroups.** The resort's precision is **0.7498 < 0.75** (`performance_by_hotel.csv`); the prose rounds it to "0.75" and calls the two hotels "similar". Bookings made after the cut-off fail **all three** criteria (AUC 0.817, precision 0.65, recall 0.39). The precision CI's lower bound is 0.725. "All three data mining criteria … are met on unseen recent data" (5.3 Decision) is therefore too strong. The headline also says "not at the lower end of their confidence intervals", but recall *is* met at its lower end. | State explicitly that resort precision misses by a hair and short-lead bookings miss everything. Make the pilot scope consistent with that (e.g. city hotel only, or a separate threshold for lead < 30 days). Fix the headline wording. |
| 4 | Medium | **The booking-date check is mis-framed.** "Bookings made after the training cut-off are exactly the ones the deployed model would score in real use": no. Because the test window ends on 31 Aug, the after-cut-off group is truncated to lead ≤ ~130 days (median 19). New bookings in real use span all lead times. The before/after gap therefore mixes a "new booking" effect with a lead-time effect. | Compare the two groups within lead-time bands (0–7, 8–30, 31–90, 91–130). Only a gap that persists within bands is evidence of a real-use penalty. |
| 5 | Medium | **No uncertainty is attached to the money figures or the model comparison.** The bootstrap covers AUC, precision and recall, but not net value or the RF − LR (+€1,996) and RF − rule (+€10,149) differences. The €2,000 edge over LR is what justifies the less interpretable model. | Add paired block-bootstrap CIs for € per 1,000 and for the two differences (same resampled weeks for both strategies). |
| 6 | Medium | **The figures for the "without country" fallback are optimistic and unlike the deployed model.** In 5.2 each variant's threshold is chosen on the very block it is scored on, with no isotonic calibration and no CI. 5.3 then quotes "AUC 0.863, precision 0.83" as if it were a deployable estimate. That precision comes from an in-sample threshold of 0.51 on raw scores. | Evaluate the fallback exactly like the champion: OOF calibration, threshold from training OOF, scored once on test, with a CI. |
| 7 | Low | **The annualisation extrapolates from high season.** €19.8 per booking comes from an Apr–Aug test window with a 40.9 % cancel rate, and is scaled to a full year (€1.1 M). | Annualise using the per-month value on CV out-of-fold predictions, or label it "high-season rate". |
| 8 | Low | **The calibration prose misplaces the largest error.** It says the curve "misses by up to 0.1 around 0.4–0.5". The figure shows the largest miss at predicted ≈0.83 (observed ≈0.71) and ≈0.16 (observed ≈0.11), where the model over-states risk. | Describe the curve accurately; add bin counts. |

Done well: the threshold, the calibration and the cost-sensitivity thresholds all come from training out-of-fold scores; weekly block-bootstrap CIs; a per-hotel split; a review of process that lists every use of the test period; a decision that is conditional and pilot-scoped.

**Previous-round responses:** #1, #2, #4, #6 and #7 are fixed (all figures verified readable; the calibration curve and Brier score are present). #3 is fixed as asked (rule and LR added, sensitivity grid, annualised check). But the "fix" exposed Phase 1 #1 and Phase 5 #1–2, which round 2 did not raise. #5: per-variant thresholds were added, but "the no-country fallback now meets AUC and precision" relies on a threshold chosen on the scoring block itself (#6 above), so the claim is weaker than it reads.

**Verdict:** rigorous in mechanics and honest about thin margins. But the headline precision and € value rest on the Non Refund artefact and on a per-booking cost model that does not represent the per-night decision.

---

## Phase 6 — Deployment · grade B

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The rule that sets the allowance is ambiguous, and neither candidate quantity is validated.** 6.1 says a flag "counts the booking in that night's overbooking allowance" and also that "the sum of probabilities per arrival date gives the expected number of cancellations". These are different numbers. On test, flags (8,956) ≠ actual cancellations (9,726), and at threshold 0.49 the count of flags is a biased estimator of cancellations. Staff will not know which number to overbook by, and the batch tab shows both. | Pick one rule (Σp is the principled choice once calibrated). Validate it per arrival date (MAE vs the incumbent rule, Phase 5 #2). Show only that number as "recommended overbooking" in the app, per date. |
| 2 | Medium | **Monitoring alarms have fired with no recorded action, or with a circular one.** Agent-mix PSI is 0.43 against a 0.25 trigger ("investigate; retrain if persistent"), and no response is recorded. For the score-PSI alarm (0.118 > 0.1), the response "threshold re-checked on the bootstrap intervals, it holds" uses test outcomes. In production, outcomes are not available when the alarm fires, so this is not a procedure staff can repeat. | Record the agent-drift response (e.g. check whether new or unseen agents fall into the "infrequent" level, and their cancel rate). Define the score-PSI response using only data available at alarm time (re-fit the calibrator on the latest outcomes when they become available, with a lag). |
| 3 | Medium | **The performance trigger will fire on noise.** "Below the 1.3 criteria → retrain" is applied monthly per arrival cohort. A month has roughly 2,000–5,000 scored bookings, and the overall precision CI already reaches 0.725, so monthly precision will fall below 0.75 by chance regularly. | Trigger on a rolling 3-month window or on the CI's upper bound falling below the criterion. Compare against the same months of the previous year, as 6.2 already recommends for input drift. |
| 4 | Low | **The label-delay statement is muddled.** For an *arrival*-month cohort, outcomes are known by the end of the stay (month M or early M+1), so "long-lead bookings even later" is wrong for that cohort definition. It would apply only to booking-month cohorts. | Pick one cohort definition and state the delay for it. |
| 5 | Low | **The model card loses the hyperparameters.** `model_metadata.json` has `"parameters": {}` because `best_params == "defaults"`. The deployed model's settings (150 trees, depth 25, leaf 5, sqrt) are not recorded. | Write `best_model.named_steps["model"].get_params()` (the key ones) to the metadata. |
| 6 | Low | **Batch scoring checks column presence only.** Unknown hotel names, misspelled categories or text in numeric columns are silently coerced to "infrequent", all-zeros or NaN and then scored. With a PMS feed this produces wrong scores without warning. | Validate the categorical values against the training options and the numeric ranges, and list the offending rows before scoring. |
| 7 | Low | **The executive summary over-states one point and omits another.** "Inputs are restricted to the 25 fields known at booking time" contradicts the ambiguity of `country` and special requests. The caveats leave out the resort precision miss and the Non Refund dependence of precision (Phase 5 #1, #3). | Reword to "fields on the booking record (two with unconfirmed recording time)" and add the two caveats. |

Done well: the deployed model is exactly the evaluated one (assertion verified in code). The app takes raw PMS fields through shared score code and derives the dates from a date picker. The pilot is randomised by arrival date. Model ownership, versioning, rollback and a feedback column are named. The experience documentation is substantive.

**Previous-round responses:** #1, #2, #4 and #5 are genuinely fixed (verified in `app.py`, `booking_features.py`, `requirements.txt`, and the smoke test on rows not seen in training). #3 is only partly fixed: categorical PSI was added, but the agent alarm it raised has no response and the score-PSI response is circular (#2 above). #6 and #7 are partly fixed / planned, as stated, which is acceptable for this stage.

**Verdict:** a realistic, mostly operable deployment. The core operational number (how many rooms to overbook per night) is still undefined and unvalidated.

---

## Overall grade: B− (up from C+ in round 2)

The round-2 problems (corrupted figures, no rule baseline, uncalibrated probabilities, an app that could not take raw fields, the evaluated ≠ deployed model) are genuinely fixed and verified. What remains is substantive rather than cosmetic. The business case is priced inconsistently and per booking although the decision is per night. The headline precision depends on a suspected data artefact. And the most important leakage question can be partly answered from the data but has not been tested.

## Top 5 remaining fixes (ranked)

1. **Re-price the business case consistently and per night.** Condition both the TP value and the FP cost on P(demand ≥ capacity). That makes the effective ratio about 2:1, which moves the threshold to about 0.66 and roughly halves the €. Then simulate the per-arrival-date allowance (flags or Σp vs actual cancellations) on the test period against the incumbent rule-of-thumb overbooking, with block-bootstrap CIs.
2. **Report performance outside Non Refund (and de-duplicated).** Precision on bookings that are not Non Refund is ≈ 0.68 by the notebook's own counts, below the 0.75 actionability target. State it, and make it an approval condition.
3. **Test the `country` defaulting hypothesis in the data.** Compare the PRT share among cancelled vs checked-out bookings (and No-Show) within segment × agent strata, excluding Non Refund. Fix the selection log so `country`, special requests and `adr` are labelled ambiguous, not "known at booking time".
4. **Align the decision text with the subgroup evidence.** Resort precision 0.7498 < 0.75. Short-lead bookings fail all criteria, and the comparison must be re-run within lead-time bands. Evaluate the no-country fallback like the champion (calibrated, training-chosen threshold, CI). Disclose that test results were visible across the revision rounds and treat CV as the primary evidence.
5. **Make the deployed overbooking rule unambiguous and its monitoring workable.** Choose Σp or the flag count, show only that number per date in the app, and record responses to the agent-drift (0.43) and score-PSI (0.118) alarms that do not need test outcomes. Replace the monthly "below criteria → retrain" trigger with a rolling-window or CI-based rule.


---

# Responses to round 3 (what changed in the notebook)

The notebook was re-run end to end twice after these changes: once with the new cost model and tests, and once more after the `country` test led to excluding it. All numbers below come from the final run.

## Business Understanding
| # | Response |
|---|---|
| 1 | **Fixed.** Both outcomes are now weighted by `P_FULL`: a correct overbooking earns €100 × 0.5 = €50, a wrong one costs €200 × 0.5 = €100. The effective ratio is 2 : 1, the threshold moves to 0.67, and the per-booking value drops to about €5,700 per 1,000. The decision is also simulated **per night** (see Evaluation 2). |
| 2 | **Fixed.** The hotel's current rule of thumb (historical cancellation rate of that hotel and month × bookings on the books) is the business benchmark, and the criterion is "better than it, with the CI of the difference above zero". |
| 3 | **Partly.** Calibration is judged descriptively (Brier, reliability curve) and through a new forecast-accuracy criterion (nightly error vs the current rule), rather than a separate numeric pass mark. |
| 4 | **Fixed.** The revenue criterion requires the bootstrap lower bound above zero against the incumbent. A forecast-accuracy criterion was added. |
| 5 | **Fixed.** "No hotel stakeholder or finance access" was added as a High/High risk, with validation at a pilot kick-off and cost sensitivity as the contingency. |
| 6 | **Not changed.** The recall floor stays disclosed as set after first results; it is now **not met**, so its timing no longer flatters the result. |

## Data Understanding
| # | Response |
|---|---|
| 1 | **Fixed, and it changed the project.** The within-segment test was run (Non Refund excluded). In every segment, no-shows and cancellations are Portuguese far more often than check-outs (Groups 97 % / 97 % vs 29 %; Offline TA/TO 99 % / 95 % vs 24 %). The defaulting hypothesis is **supported**, so `country` is **excluded** (3.1). Adding it back is worth +0.034 AUC on the last training block (5.2), which shows how much the leak was inflating the results. |
| 2 | **Fixed.** Finding 7 now compares April–August 2016 with April–August 2017, booking-weighted (city 39.5 % → 43.9 %, resort 29.5 % → 35.1 %). |
| 3 | **Fixed (wording).** The detector is now described as a screen for strong single-field monotone leaks that cannot see partial leaks; the within-segment test covers that gap. Numeric binning was not added. |
| 4 | **Fixed.** The cut-off line is drawn at the real arrival-date quantile. |
| 5 | **Fixed.** Duplicates outside Non Refund are profiled separately: they cancel at 35.5 %, like all bookings, and are 58 % group bookings. |
| 6 | **Fixed.** The 62 % vs 28 % shares are printed. |

## Data Preparation
| # | Response |
|---|---|
| 1 | **Fixed.** The selection log marks `total_of_special_requests` and `adr` as ambiguous, and `country` as excluded because of the test. |
| 2 | **Partly.** No de-duplicated sensitivity run. Instead, results **without the Non Refund blocks** (98 % of which are duplicates) are reported next to the headline (AUC 0.774, precision 0.71, recall 0.31). |
| 3 | **Fixed.** The false claim was removed. `has_kids` is described honestly (no finding; kept as cheap and harmless). |
| 4 | **Not changed.** The agent pooling (`min_frequency` 0.005) is documented. Out-of-fold target encoding is listed as an iteration. |
| 5 | **Fixed.** The non-reproducible 0.877 → 0.878 claim was removed. |

## Modeling
| # | Response |
|---|---|
| 1 | **Fixed.** 4.2, 5.2 and the headline now say the test results were visible during review rounds 2 and 3. Cross-validation is reported as primary evidence next to every test criterion (CV AUC 0.841, precision 0.949, recall 0.405). |
| 2 | **Partly.** The thin budget for gradient boosting is acknowledged in 4.3 and 5.2 and listed as a next step. With nationality removed, RF leads HGB by only +0.004 (4/5 folds), and the text says the lead is small. |
| 3 | **Fixed.** The calibrator is fitted only on the out-of-fold scores of folds 3–5 (fold models trained on 48k–79k bookings). Test Brier is 0.168 → 0.163. |
| 4 | **Not changed.** The LR linearity check was not added. With nationality removed, LR trails RF by 0.033 AUC on 5/5 folds, a gap unlikely to close with a lead-time transform. |
| 5 | **Fixed.** The fold-3 "group business" claim was removed, and the `min_samples_leaf` rationale corrected (it cannot stop a block of identical rows filling a leaf). |
| 6 | **Not changed.** Calibration is assessed for the champion only. |

## Evaluation
| # | Response |
|---|---|
| 1 | **Fixed.** Results outside Non Refund are reported (precision 0.71, recall 0.31, AUC 0.774). Together with the model criteria now failing, the **per-booking flags are not approved for decisions**; they are an information-only watch list. |
| 2 | **Fixed.** A per-night simulation (262 hotel-nights, re-sale and walks both × `P_FULL`) compares no overbooking, the current rule, the Non Refund count, the count of flags, and the **sum of probabilities**, with a block bootstrap over weeks. The sum of probabilities beats the current rule by **€3,375 per 1,000 bookings (CI +€2,445 to +€4,324)**, with half the nightly error (4.6 vs 9.4 rooms). Counting flags does worse than the current rule. |
| 3 | **Fixed.** The criteria now read honestly: AUC and recall **not met**, precision met. Per-hotel recall is reported (resort 0.22). The decision is scoped to the nightly forecast only. |
| 4 | **Fixed.** The booking-date comparison is repeated within lead-time bands. The gap persists (31–90 days: AUC 0.687 vs 0.789), so new bookings really are harder. |
| 5 | **Partly.** Bootstrap CIs were added for the per-night value differences vs the incumbent, which is now the decisive comparison. The per-booking € figures have no CI. |
| 6 | **Changed.** With `country` excluded, the old "fallback" *is* the deployed model and is evaluated like the champion (calibrated, training-chosen threshold, test with CIs). The 5.2 table now shows what adding `country` back would do. |
| 7 | **Fixed.** Figures are labelled as high-season (April–August), and the annual extrapolation is stated as such. |
| 8 | **Fixed.** The calibration text was rewritten after recalibration. |

## Deployment
| # | Response |
|---|---|
| 1 | **Fixed.** There is one rule: **the rounded sum of probabilities per arrival date** is the recommended number of extra rooms. The batch tab shows it per hotel and date. It was validated per night in 5.1. Flags are an information-only watch list. |
| 2 | **Fixed.** The agent-drift response needs no outcomes: only 1.1 % of test bookings come from agents unseen in training, so the drift is a mix change among known agents. The score-drift response needs no outcomes either: compare the forecast with the current rule, and re-fit the calibrator once outcomes arrive. |
| 3 | **Fixed.** The performance trigger is now a rolling 3-month comparison of the forecast's nightly error against the current rule's. |
| 4 | **Fixed.** The cohort is defined by arrival month, with outcomes known by the end of the stay. |
| 5 | **Fixed.** The model card records the forest's hyperparameters. |
| 6 | **Partly.** The batch tab warns about category values never seen in training. Numeric range validation was not added. |
| 7 | **Fixed.** The executive summary now says 24 fields on the booking record, the exclusion of nationality, and the Non Refund and short-notice caveats. |
