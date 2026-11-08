# Video script: SEMMA, NBA expected field-goal percentage (about 15 minutes)

Each segment has **SHOW** (what is on screen and what to click) and **SAY** (narration you can read as written; about 140 words a minute). Section names match the notebook headings, so the Colab *Table of contents* panel (left sidebar, ☰ icon) is the fastest way to jump.

## Before you record

- The repo is **public** (the Colab badge and the article images need it).
- The app is awake: open https://cmpe-255-data-mining-process-nba-expected-fg.streamlit.app/ a few minutes before you start (free apps sleep when nobody has used them for a while).
- Open three browser tabs:
  1. the notebook in Colab (README → *Open in Colab*);
  2. the GitHub repo at `semma/`;
  3. the app.
- The saved outputs are already in the notebook. *Run all* downloads about 1.2 M shots, so if you want to show it running, start it well before recording.
- If you re-run in Colab, the last digit of some numbers can differ slightly because Colab's library versions differ. Narrate from the saved outputs, which match this script, the report and the article.
- Record at 1080p with the browser zoomed to about 125 %. Collapse the code cells you don't talk about.

---

### 1. Introduction (0:00–0:55)

**SHOW:** Colab, title cell.

**SAY:**
> Hi, I'm Meron Tesfandrias, and this is my SEMMA project for CMPE 255. Field-goal percentage is one of basketball's oldest stats, and one of its most misleading. A center who only dunks shoots 65 percent, and a guard who lives beyond the arc shoots 44. Who's the better shooter? Raw FG% can't tell you, because it mixes two things: which shots a player takes, and how well he makes them. Expected FG% separates them. Given where and how a shot was taken, how often does the average NBA player make it? Compare a player's real FG% with the expected FG% of the same shots, and what's left is shot making.

### 2. SEMMA and the project context (0:55–1:50)

**SHOW:** The SEMMA table in the title cell, then **Project context (pre-SEMMA)**. Open the *Table of contents* to show S / E / M / M / A and the "🔍 Critic review" headings.

**SAY:**
> SEMMA stands for Sample, Explore, Modify, Model, Assess. It's the process SAS designed around Enterprise Miner, and each section here maps to an Enterprise Miner node: Input Data, Sample, StatExplore, Variable Selection and so on. Unlike CRISP-DM, SEMMA has no business understanding phase. It assumes you already know the question. So the context is one short cell, with the success criteria set up front: beat simple zone-average baselines, be well calibrated, and hold up on a season the model has never seen. Every step ends with a critic review. An expert-persona reviewer critiqued each step three times, the last two rounds in fresh, independent sessions, and each table shows what was found and what changed.

### 3. Sample (1:50–3:30)

**SHOW:**
1. **S.1 Input Data**: the population table (five seasons, 1,031,740 shots; 2024-25 held out).
2. **S.2 Sample**: the representativeness table (sample vs remainder, KS / χ² p-values).
3. **S.3 Data Partition**: **code:** expand the partition cell and point at `GroupShuffleSplit` (grouped by `GAME_ID`). Then show the partition table, and the learning-curve table and chart in the cell below.

**SAY:**
> The data is every regular-season shot from stats.nba.com: court coordinates, shot type, period and clock, and whether it went in. Five seasons, 2019-20 through 2023-24, make up the modeling population: just over a million shots. The 2024-25 season, 219,527 shots, is kept out of all fitting until the very end.
>
> SEMMA's first instinct is to sample. I drew 200,000 shots, stratified by season and outcome. My first proof that the sample was representative was circular: FG% matched because I had stratified on it. The honest test compares the sample with the 832,000 shots I *didn't* draw, on variables I didn't stratify on. Distance, location, three-point share, shot types and zones all match, and every p-value is above 0.37.
>
> Was 200,000 enough? This learning curve goes up to 480,000 training shots. Error falls fast up to about 25,000 and then barely moves. The last 360,000 shots buy a thousandth of a point of log loss. Finally, the sample is split 60/20/20 by game. In the code that's scikit-learn's `GroupShuffleSplit` with the game ID as the group, so shots from the same game never land in two partitions.

### 4. Explore (3:30–5:05)

**SHOW:**
1. **E.1 StatExplore**: the anomalies output and point at `EVENT_TYPE`.
2. **E.2 MultiPlot / Graph Explore**: FG% by distance, the shot charts, FG% by shot type.
3. **E.3 Variable Selection**: the variable-worth table (`PLAYER_NAME` 0.022 → 0.008 after bias correction).
4. **E.4 Cluster** briefly, then the **Exploration findings** table.

**SAY:**
> Explore is where the shot charts tell the story every coach knows, now with numbers. The rim is a cliff: 76 percent at zero feet, 59 at two feet, 41 at five. Mid-range is flat, about 43 percent from 10 to 15 feet, which is why analytics killed the long two. Corner threes are a bit better, but mostly because they're shorter. At the same 24 feet, corners go in 37 percent against 35 above the break. How the shot is taken matters as much as where: dunks 89 percent, layups 56, pull-ups 40. And heaves are their own thing: from 30-plus feet with three seconds or less on the clock, 8 percent.
>
> Exploration also caught a trap. A column called `EVENT_TYPE`, "Made Shot" or "Missed Shot", is the target in disguise. And the shooter's name looked informative until I corrected mutual information for its 800 levels: it dropped from 0.022 to 0.008. It's excluded by design anyway. This model measures shot quality, and who took the shot is analysed afterwards.

### 5. Modify (5:05–7:15)

**SHOW:**
1. **M.1 Drop**: the drop log.
2. **Code: M.2 Transform Variables…**: expand the cell and scroll through `def engineer(raw)`, pausing on the `dist_ft`, `abs_angle`, `corner` / `is_three` and `heave` lines.
3. **Code: M.3 Replacement & Impute**: expand `def make_prep` (median impute + scale; rare `action` labels pooled with `min_frequency=0.005`; families and bins with `handle_unknown="ignore"`). Then show the probe output (missing location → 0.551; unseen dunk label → 0.924).

**SAY:**
> The raw data describes distance five overlapping ways. Modify replaces them with one consistent geometry: the exact distance, finer bins at the rim, the angle, a corner-three flag and a three-point flag computed from the court lines, which agree with the official flag on 99.95 percent of shots, plus seconds left and a heave flag. Shot types are grouped into families like dunk, layup, floater and pull-up, so a rare label like "Running Alley Oop Dunk Shot" is still treated as a dunk.
>
> Here's the code, the `engineer` function. Coordinates come in tenths of a foot with the hoop at zero. Distance is the hypotenuse, and the angle is measured from straight on. A corner three is at least 22 feet to the side and below the break, and anything else beyond 23 feet 9 inches is a three. A heave is 30 feet or more with three seconds or less left. Missing inputs stay missing on purpose, so the pipeline's impute step handles them.
>
> All of this lives in a small module, `shot_features.py`, that the deployed app imports too. That's the Python equivalent of the score code Enterprise Miner exports. `make_prep` is the Replacement and Impute node: medians for numbers, rare shot labels pooled, and unseen values ignored. These probes show it copes with missing values and with labels it has never seen.

### 6. Model (7:15–9:10)

**SHOW:**
1. **Baseline — zone average**: the three-baseline output (0.691 / 0.6573 / 0.6454).
2. Scroll past the **Regression / Decision Tree / Neural Network** headings. **Code:** at **Gradient Boosting node**, expand the cell and point at the tuning loop: `HistGradientBoostingClassifier(learning_rate=lr, … max_leaf_nodes=leaves …)` wrapped in `pipe(...)`. Then show its tuning table.
3. Under **Ensemble node**: the ablation lines (no shot type 0.6471; no angle 0.6340).
4. **Model families in the competition** table.

**SAY:**
> Following Enterprise Miner's playbook, five model families compete: logistic regression, a decision tree, a neural network, gradient boosting and an ensemble. Each is tuned on the validation partition. In this cell, for example, boosting tries combinations of learning rate and tree size, and every candidate is the same pipeline: engineer, prepare, model. The selection metric is log loss, not accuracy, because expected FG% is used as a probability: expected points are xFG% times the shot value.
>
> The baselines matter more than the ranking. Giving every shot the league average scores 0.691. League FG% by court zone gets 0.657. And by zone *and* shot family, 0.645. That last one is a strong baseline. Gradient boosting beats it by 0.0116, about 1.8 percent. That's modest, and it's the honest answer: once you know only where and what the shot was, most of the outcome is genuinely random.
>
> One reviewer asked how much the model depends on the shot-type label, because scorekeepers assign it after the play. Without it, the model scores 0.647, worse than the zone-by-family baseline. So most of the edge comes from that label, and I say so in the limitations.

### 7. Assess (9:10–11:50)

**SHOW:**
1. **A.1 Model Comparison**: the comparison table (Gradient Boosting 0.6338, Ensemble 0.6340). **Code:** scroll to the comment "Paired bootstrap over GAMES of the validation partition" and its output.
2. **A.3 Final check on untouched data**: the train / validate / test / out-of-time table (0.6320 / 0.6338 / 0.6339 / 0.6370), then the decile calibration.
3. **A.4 Score & Segment Profile**: the leaderboard (Jokić at the top), then the actual vs expected scatter, then the persistence table (r = 0.70, raw FG% 0.86).

**SAY:**
> Gradient boosting wins with a validation log loss of 0.6338, tied with the ensemble. To check whether that gap is real, the code resamples whole games of the validation partition, because shots within a game aren't independent, and recomputes the difference each time. The gap is noise, so I kept the simpler model.
>
> Does it hold up? Training, validation and test scores are 0.632, 0.634 and 0.634, so there's no over-fitting. On the 2024-25 season, which the model never saw, it scores 0.637 and still beats both baselines. It predicts a league FG% of 46.5 percent, and the actual was 46.7. In every decile, predicted and actual are within one and a half points. Layups go in about two points more often than predicted, which slightly flatters players who live at the rim.
>
> Now the payoff. Scoring every 2024-25 shot and adding up points over expected, Nikola Jokić leads at plus 327 points. He shot 57.6 percent on shots worth 46.6. Kevin Durant takes harder shots and still makes them, plus 226. Stephen Curry's raw 44.8 percent looks ordinary until you see his shots are worth only 40.4. With about a thousand attempts, shot making is only known to about plus or minus three points, and just 62 of 181 regulars are clearly different from average. That's why the leaderboard shows intervals.
>
> Is it skill? For 131 players in both seasons, shot making over expected correlates at 0.70 year to year. But raw FG% persists even more, at 0.86, so part of it is context the model can't see. "Persistent residual" is the honest name. One more critic story: that 131 used to be 124. I had matched seasons by name, and the data spells Jokić with the accent in one season and without it in the other, so the league's best shot maker had silently dropped out. Matching on player ID fixed it.

### 8. Deployment, in the app (11:50–12:55)

**SHOW:**
1. App tab **Evaluate a shot**.
2. Keep *Shot type* = "Jump Shot". Set *Feet left/right* = 22 and *Feet out from the hoop* = 0 for a corner three (about 39 %). Show **Expected FG%**, **Shot value** "3 pts (corner)" and **Expected points** (about 1.19).
3. Set both sliders to 0 with *Shot type* = "Driving Layup Shot".
4. Set *Shot type* = "Dunk Shot" and *Feet out* = 25 → the **Unusual shot** warning.
5. Tab **2024-25 shot-making leaderboard**.

**SAY:**
> SEMMA stops at Assess, so deployment is my addition. In this Streamlit app you pick a spot on the court, a shot type and the clock, and it returns the expected FG% and expected points. Here's a corner three, and here's a driving layup at the rim. If I ask for a dunk from 25 feet, it warns me that the model has barely seen that shot, so I should treat the number with caution. The second tab is the full leaderboard with confidence intervals.

### 9. Wrap-up (12:55–14:35)

**SHOW:**
1. GitHub repo tab, folder by folder:
   - `artifacts/figures/`;
   - `artifacts/reports/` (a CSV per table, e.g. `model_comparison_validation.csv`, `shot_making_leaderboard_2024_25.csv`);
   - `artifacts/app/` (`app.py`, `shot_features.py`, `model.joblib`, `model_metadata.json`, `leaderboard.csv`, `requirements.txt`);
   - then `critiques/`, `report/`, `article/`.
2. Optionally the **Appendix — SAS Enterprise Miner demo** heading.

**SAY:**
> All the artifacts are in the repo: every chart under figures, every table as a CSV under reports, and the app folder with the model, the score-code module, the leaderboard and pinned requirements.
>
> SEMMA is a disciplined technical core. It made me justify the sample, compare model families fairly on a validation partition, and check calibration, not just accuracy. Its blind spots are the parts it never claimed to cover: the question at the start and deployment at the end. The critiques caught what accuracy numbers never show: a corrupted chart, a shot grouping that lumped dunks with bank shots, an overclaimed "skill" result, and the name-matching bug. The limitations are no defender data, and shot-type labels assigned after the play. The appendix has the files and steps to rebuild this in SAS Enterprise Miner. Everything, including the reports and the Medium article, is in this repo. Thanks for watching.

**Optional SAS segment (+3 min, only if you have Enterprise Miner):** follow the notebook appendix with the exported role files and compare its Model Comparison result with section A.1.
