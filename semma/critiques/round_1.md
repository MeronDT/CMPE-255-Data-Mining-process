# SEMMA critique — round 1

**Reviewer:** Claude (Anthropic), prompted with the expert persona below, reviewing the complete first draft of `SEMMA_NBA_Expected_FG.ipynb` (all five steps, code and outputs).
**Note on independence:** round 1 was run in the same Claude session that helped draft the notebook. Rounds 2 and 3 should be run in a **fresh** Claude chat (paste the revised step + outputs) so the reviewer has not seen the drafting — record them in `round_2.md` / `round_3.md`.

**Prompt used (per step):**
> You are a world-renowned authority on the SEMMA data mining methodology and SAS Enterprise Miner, a sought-after keynote speaker, and the author of several award-winning books on SEMMA and predictive modeling. Review the **[step]** of my NBA expected-field-goal-percentage project below. Check it against everything SEMMA's [step] step should accomplish (and the Enterprise Miner nodes that implement it). List (1) anything missing, (2) anything weak or unjustified, (3) methodological errors, and (4) concrete fixes, ranked by importance. Grade it as strictly as you would a professional engagement.

---

## Sample — grade B+

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | The learning curve that justifies `SAMPLE_SIZE` uses a reduced feature set (location, clock, coded action), not the final model, so it is indicative only. | Kept (cheap, runs before Modify exists) but stated as indicative in the text. The curve is flat after ~25k training shots (validation log loss 0.6382 → 0.6355 at 120k), so a 200k sample has a wide safety margin. |
| 2 | Low | Stratifying on the *target* is unusual for a probability model — it could distort the base rate if done disproportionately. | It is proportional; FG% is 0.4677 in both population and sample. Justified in the text. |
| 3 | Low | Two seasons are atypical (2019-20 bubble, 2020-21 72 games). | Checked: season FG% ranges only 46.0–47.5 %, so pooling is reasonable. Stated in the text. |

## Explore — grade A−

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | Variable worth ranks `PLAYER_NAME` (MI 0.022) above several shot inputs, yet it is dropped. The exclusion must be argued, not just listed. | Text now explains the design choice: xFG% measures *shot quality*; shooter identity is deliberately left out so it can be measured afterwards as shot *making* (A.4). |
| 2 | Low | The location clusters are descriptive only. | Linked to Modify: the three outer clusters at ~25 ft vs the corner clusters motivated the angle and corner-three variables. |

## Modify — grade A−

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | `ACTION_TYPE` is coded by scorers during/after the play; some labels could be influenced by the outcome. | Cannot be verified from the data; recorded as a limitation. It describes the attempt (a dunk *attempt* is a dunk), which is standard in public xFG models. |
| 2 | Low | Geometry-based 3PT flag replaces the official one — show it is right. | Already shown: 99.95 % agreement with `SHOT_TYPE`. |

## Model — grade B

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | Unfair comparison: the decision tree was tuned on the validation partition, but gradient boosting ran with a single setting. | **Fixed.** Gradient boosting now tuned over 4 settings on validation (best: learning rate 0.05, 31 leaves, log loss 0.6346). It remains the champion. |
| 2 | Low | The neural network is untuned. | Noted; it was 3rd and the ensemble (which includes it) did not beat boosting, so tuning it is unlikely to change the decision. |

## Assess — grade B+

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | Calibration only checked on average (mean xFG vs actual). A probability model must be calibrated across its range. | **Fixed.** Added a calibration-by-decile table on the unseen 2024-25 season: every decile within 0.9 percentage points of the actual FG%. |
| 2 | **High** | The player leaderboard could be noise — a single season of ~1,000 shots has large variance. | **Fixed.** Added a persistence check: for 124 players with 500+ attempts in both 2023-24 and 2024-25, FG over expected correlates r = 0.68 across seasons, so it is largely a repeatable skill. |
| 3 | Medium | The improvement over the baseline looks small in AUC (0.665 vs 0.634); explain why that is still meaningful. | Text explains that most shot outcomes are irreducibly random given only location/type; log loss improves 3.4 % (0.6572 → 0.6346) and calibration is tight, which is what matters for an expected-value metric. |

**Overall verdict after fixes:** the SEMMA flow is complete and defensible. Main remaining limitation: no defender, shooter or play-context data (tracking data is not public).
