# What Is a Shot Actually Worth? Building an NBA Expected-FG% Model with SEMMA

*Five seasons, a million shots, and SAS's five-step data mining method — applied in Python.*

`<cover image: artifacts/figures/explore_shot_charts.png>`

Field-goal percentage is one of basketball's oldest stats, and one of its most misleading. A center who only dunks shoots 65 %; a guard who lives beyond the arc shoots 44 %. Who is the better shooter? Raw FG% can't say, because it mixes two different things: **which shots a player takes** and **how well he makes them**.

Expected field-goal percentage (xFG%) separates them. It asks: *given where and how a shot was taken, how often does the average NBA player make it?* Compare a player's real FG% with the xFG% of the same shots, and what's left is shot-making skill.

I built an xFG% model following **SEMMA** — Sample, Explore, Modify, Model, Assess — the data mining process SAS Institute designed around its Enterprise Miner software. Here's how each step shaped the project.

## The data

Every regular-season field-goal attempt from stats.nba.com, compiled in the open [shufinskiy/nba_data](https://github.com/shufinskiy/nba_data) repository: court coordinates, shot type ("Driving Layup Shot", "Step Back Jump shot"…), period and clock, and whether it went in. Five seasons (2019-20 to 2023-24) form the modeling population — **1,031,740 shots**. The 2024-25 season (**219,527 shots**) was locked away until the very end.

Unlike CRISP-DM, SEMMA has no "business understanding" phase; it assumes you already know the question. So the success criteria were set up front: beat a simple *zone-average* model, be well-calibrated, and hold up on a season the model has never seen.

## S — Sample: you don't need a million shots

SEMMA's first instinct is to *sample*: extract a portion big enough to contain the signal but small enough to work with quickly.

I drew 200,000 shots, stratified by season and outcome. Then I checked that the sample was representative instead of assuming it: FG% was 46.77 % in both sample and population, mean shot distance 13.58 vs 13.57 ft, and a Kolmogorov–Smirnov test found no difference in the distance distribution (p = 0.999).

Was 200k enough? A learning curve answered that. Validation error dropped fast up to about 25,000 training shots and then flattened — going from 50k to 120k barely moved it. Modeling all million shots would have cost time and added nothing.

The sample was then split 60/20/20 into training, validation and test sets — **by game**, so shots from the same game never ended up in two partitions.

## E — Explore: where shots go in

`<image: explore_distance_zone.png>`

The shot charts tell the story every coach knows, now quantified:

- **The rim dominates.** Shots at 0 ft go in 76 % of the time; by 4–5 ft it's already down to ~43 %.
- **Mid-range is flat.** From 5 to 20 ft, FG% hovers around 43 % — the reason analytics killed the long two.
- **Corner threes are better threes.** 38.1 % vs 35.6 % above the break, because the corner is 22 ft instead of 23.75.
- **How matters as much as where.** Cutting layups go in 70 % of the time, plain layups only 48 %, jump shots 37 %.
- **End-of-quarter heaves** with ≤ 2 seconds left: 29 %.

Exploration also caught a trap: a column called `EVENT_TYPE` ("Made Shot"/"Missed Shot") was the answer itself in disguise. Left in, it would have produced a perfect — and useless — model.

One more decision came from Explore: the shooter's identity is predictive, but I **excluded it on purpose**. The model is supposed to measure shot *quality*; who took the shot is analysed afterwards.

## M — Modify: one geometry for every shot

The raw data describes distance five overlapping ways (exact coordinates, rounded distance, three zone columns). Modify replaced them with one consistent set of engineered features: exact distance, shot angle, a corner-three flag, a 3-point flag computed from court geometry (it agrees with the official one on 99.95 % of shots), seconds left, overtime, "clutch" and "heave" flags, and distance bins for the linear model.

All of it lives in a small module, `shot_features.py`, that the deployed app imports too — the Python equivalent of the *score code* Enterprise Miner exports. Training and production can't drift apart.

## M — Model: five contenders

Following Enterprise Miner's playbook, several model families competed, tuned on the validation partition:

| Model | Validation log loss | ROC-AUC |
|---|---|---|
| **Gradient boosting** (tuned) | **0.6346** | **0.665** |
| Ensemble (avg of 3) | 0.6352 | 0.664 |
| Neural network | 0.6376 | 0.658 |
| Decision tree (depth 8) | 0.6399 | 0.658 |
| Logistic regression | 0.6400 | 0.659 |
| *Zone-average baseline* | *0.6572* | *0.634* |

I chose the champion by **log loss**, not accuracy, because xFG% is used as a *probability*: expected points = xFG% × shot value.

The gains look modest, and that's the honest answer: most of a shot's outcome is genuinely random once you know only where and what it was. The model can't see the defender's hand or the shooter's balance.

## A — Assess: does it hold up?

Three tests, all on data the model never trained on:

1. **Test partition:** log loss 0.6345, identical to validation — no over-fitting from model selection.
2. **The unseen 2024-25 season:** log loss 0.6377 vs 0.6577 for the baseline. Predicted league FG% 46.4 %, actual 46.7 %.
3. **Calibration by decile:** in every tenth of the probability range, predicted and actual FG% are within 0.9 points — from 30.5 % vs 31.0 % on the hardest shots to 83.7 % vs 84.6 % on the easiest.

`<image: assess_shot_making.png>`

### The payoff: who actually makes their shots?

Scoring every 2024-25 shot and adding up points over expected:

- **Nikola Jokić: +323 points.** He shot 57.6 % on shots worth 46.7 %. His shots aren't unusually easy — he simply converts them.
- **Kevin Durant (+228)** and **Shai Gilgeous-Alexander (+197)** take harder-than-average shots and still make them.
- **Stephen Curry's** raw 44.8 % looks ordinary until you see his shots are worth only 40.4 % — he's +143.

Is this skill or a lucky season? For 124 players with 500+ attempts in both 2023-24 and 2024-25, shot-making over expected correlated **r = 0.68** across seasons. It's mostly skill.

## Deployment (beyond SEMMA)

SEMMA stops at Assess, so I added a small Streamlit app: pick a spot on the court and a shot type, and it returns xFG% and expected points — a left-corner three is ~39 % for 1.18 expected points, a driving layup ~66 % for 1.31. A second tab shows the full shot-making leaderboard. `<app link>`

## What SEMMA got right — and what it leaves out

SEMMA is a disciplined *technical* core. It made me prove the sample was representative, justify its size, compare model families fairly on a validation partition, and check calibration rather than just accuracy. Its blind spots are the parts it never claimed to cover: the business question at the start and deployment at the end. In my CRISP-DM project those were the hardest parts.

**Limitations:** no defender distance, no tracking data, and `ACTION_TYPE` is coded by scorekeepers, so a few labels may be influenced by the outcome.

*Code, notebook, figures and app: [github.com/MeronDT/CMPE-255-Data-Mining-process](https://github.com/MeronDT/CMPE-255-Data-Mining-process). Video walkthrough: `<YouTube link>`.*

*AI disclosure: built with help from Claude (Anthropic) for code, drafting and expert critique; all results were produced by running the code.*
