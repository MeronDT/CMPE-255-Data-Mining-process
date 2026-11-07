# CRISP-DM critique — round 1

**Reviewer:** Claude (Anthropic), prompted with the expert persona below, reviewing the complete first draft of `CRISP_DM_Hotel_Cancellations.ipynb` (all six phases, code and outputs).
**Note on independence:** round 1 was run in the same Claude session that helped draft the notebook. Rounds 2 and 3 should be run in a **fresh** Claude chat (paste the revised phase + outputs) so the reviewer has not seen the drafting — record them in `round_2.md` / `round_3.md`.

**Prompt used (per phase):**
> You are a world-renowned authority on CRISP-DM, a sought-after keynote speaker, and the author of several award-winning books on the CRISP-DM methodology. Review the **[phase]** phase of my hotel-cancellation project below. Check it against every generic task and output CRISP-DM 1.0 defines for this phase. List (1) anything missing, (2) anything weak or unjustified, (3) methodological errors, and (4) concrete fixes, ranked by importance. Grade it as strictly as you would a professional engagement.

---

## Phase 1 — Business Understanding · grade B

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | The cost/benefit figures (+€100 / −€40) are asserted, not derived, and the false-positive cost looks far too low: walking a guest who does arrive costs a replacement room, transport and goodwill. Because these numbers set the decision threshold, they are the most consequential assumption in the project. | **Fixed.** Derived from the data: average booking ≈ €358 (ADR €101.8 × 3.43 nights). TP +€100 (≈ 28 % recovered); FP raised to −€100 (≈ one night's ADR). The threshold moved from 0.23 to 0.34 and precision rose from 0.64 to 0.77. |
| 2 | Medium | Why precision ≥ 0.75? A target needs a reason. | Justified as staff trust: if most flags are wrong, staff ignore them. |
| 3 | Low | Resource inventory and plan were placeholders. | Completed, including the AI critic as a resource and the expected iterations. |

## Phase 2 — Data Understanding · grade B+

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | "Non Refund deposits cancel 99 % of the time" is noted and then left alone. It is the opposite of what a non-refundable deposit should do, and a strong predictor — it must be investigated. | **Fixed.** Added a profile: these 14,587 bookings are 97 % Portuguese, 97 % group/tour-operator, have no special requests and a 183-day median lead time — most likely released block allocations. Reported as a data-quality question for the hotel. |
| 2 | **High** | `country` is highly predictive (62 % of cancelled bookings are Portuguese vs 28 % of arrived ones). If nationality is only confirmed at check-in, cancelled bookings keep a default value → leakage. | Can't be settled from the data; a **sensitivity test** was added in Phase 5 (see below). |
| 3 | Low | Format problems should be listed, not just fixed silently. | Listed in the data description report (padded text, `"NULL"` strings, type mismatch). |

## Phase 3 — Data Preparation · grade B

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | 27 % of rows are exact duplicates and are kept. With shuffled K-fold, identical bookings fall on both sides of a fold, so cross-validation rewards memorisation. | Kept (no booking ID to prove they are errors), but the test design was changed — see Phase 4. |
| 2 | Medium | `total_of_special_requests` can be added after booking. | Kept, included in the sensitivity test. |

## Phase 4 — Modeling · grade C+ → A− after fixes

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **Critical** | Shuffled CV gave ROC-AUC **0.956**, but the time-based test period gave **0.868** — the validation design is badly optimistic (duplicates + time drift). Model selection on such scores is unreliable. | **Fixed.** Switched to 5 expanding-window **time-series folds** on the training period. CV now 0.877 vs test 0.868 — validation predicts reality. |
| 2 | Medium | The "tuned" model was worse than the defaults on the same folds, yet it was adopted. | **Fixed.** Tuned settings are adopted only if they beat the defaults on identical folds (now 0.8789 vs 0.8770). |
| 3 | Medium | The first settings (unlimited depth, leaf size 1, wide search) took 15+ minutes and ran out of memory on a free-Colab-sized machine. | Depth capped, `min_samples_leaf` ≥ 5, smaller search, single-process permutation importance: 13.8 MB model, ≈ 8 min run time. |

## Phase 5 — Evaluation · grade B+

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | The leakage risk from ambiguous attributes is not quantified; an evaluator cannot judge how much the result depends on them. | **Fixed.** Sensitivity test on the last training-period block (test set untouched): without `country` ROC-AUC 0.897 → 0.862; without country, agent and special requests → 0.833. Adding back the excluded parking field gains only +0.009. Decision: **approve conditionally** — confirm with the hotel when country is recorded; the no-country variant is the fallback. |
| 2 | Medium | Resort recall (0.55) is much lower than city (0.73). | Recorded; hotel-specific thresholds listed as a next step. |
| 3 | Low | Probability calibration not checked, although the app shows probabilities to staff. | Recorded in the process review as a gap. |

## Phase 6 — Deployment · grade A−

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | The drift demo flags seasonal attributes (week PSI 7.7) as "drifted" — this would cause constant false alarms. | **Fixed.** Monitoring compares the same month year on year; the prediction-score PSI (0.118 here) is the main alarm. |
| 2 | Low | No owner, retraining procedure or retirement rule. | Added: the revenue manager owns it; retraining = re-run the notebook; retire if a retrained model misses the criteria. |

**Overall verdict after fixes:** a complete CRISP-DM engagement with every generic task and output present. The decisive improvements were the time-ordered validation and the honest treatment of leakage risk. The main open item is a business question, not a modeling one: when is `country` recorded?
