# SEMMA — NBA Expected Field-Goal Percentage

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MeronDT/CMPE-255-Data-Mining-process/blob/main/semma/SEMMA_NBA_Expected_FG.ipynb)

**Question:** how likely is any NBA shot to go in, given where and how it is taken? Comparing a player's actual FG% with the expected FG% (xFG%) of his shots separates shot *making* from shot *selection*.

**Data:** every regular-season field-goal attempt 2019-20 → 2024-25 from stats.nba.com via [shufinskiy/nba_data](https://github.com/shufinskiy/nba_data) (Apache-2.0). Five seasons (1,031,740 shots) form the population; 2024-25 (219,527 shots) is held out entirely.

## SEMMA steps → what was done

| Step | Enterprise Miner nodes | In this project |
|---|---|---|
| **Sample** | Input Data · Sample · Data Partition | 200k stratified sample, tested against the unsampled remainder on unstratified variables; size justified by a learning curve to 480k shots; 60/20/20 partition **grouped by game** |
| **Explore** | StatExplore · MultiPlot · Variable Selection · Cluster | shot charts, FG% by distance/type/clock, anomalies, bias-corrected variable worth, location clusters; caught `EVENT_TYPE` = target leakage |
| **Modify** | Drop · Transform · Replacement · Binning · Impute | engineered geometry (distance, angle, corner three, 3PT flag), shot families for rare shot types, fine distance bins at the rim, heave flag — written as reusable score code (`shot_features.py`) that keeps missing values for the Impute step |
| **Model** | Regression · Decision Tree · Neural Network · Gradient Boosting · Ensemble | five models, each tuned on the validation partition, vs three baselines; champion chosen with a game-level bootstrap |
| **Assess** | Model Comparison · Cutoff · Score · Segment Profile | test + unseen-season check; calibration by decile and by segment; player leaderboard with confidence intervals and shrinkage |

## Results

| | Log loss | ROC-AUC | Mean xFG / actual FG |
|---|---|---|---|
| Zone-average baseline (validation) | 0.6573 | 0.634 | — |
| Zone × shot-family baseline (validation) | 0.6454 | 0.647 | — |
| **Gradient boosting** (validation) | **0.6338** | **0.666** | 46.9 % / 46.8 % |
| Gradient boosting (test) | 0.6339 | 0.664 | 46.9 % / 46.4 % |
| Gradient boosting (**unseen 2024-25**) | 0.6370 | 0.659 | 46.5 % / 46.7 % |

- **Calibration on 2024-25.** Within **1.5 percentage points** in every decile, and within 2.1 points for every shot zone and shot family except backcourt heaves. Layups are slightly under-predicted.
- **Shot making over expected, 2024-25.** **Jokić +327 points** (95 % CI on FG over expected +8.5 to +13.6 points), Durant +226, Gilgeous-Alexander +196, Curry +139. 62 of 181 players are clearly different from zero.
- **Persistence.** The gap persists from season to season (**r = 0.70**, CI 0.60–0.78, 131 players), but less than raw FG% (0.86). It is best read as shot-making plus context the model cannot see.
- **The shot-type label.** Without the scorer's shot-type label the model loses most of its edge (log loss 0.6471, worse than the zone × shot-family baseline). Most of the gain depends on that label.

## Files

| Path | What |
|---|---|
| `SEMMA_NBA_Expected_FG.ipynb` | the full project, executed with outputs |
| `report/` | the notebook as an HTML and PDF report |
| `artifacts/figures/`, `artifacts/reports/` | every chart and table |
| `artifacts/app/` | Streamlit app: score any shot + leaderboard (`app.py`, `shot_features.py`, model) |
| `critiques/` | three rounds of expert-critic reviews and the changes they led to |
| `article/medium_article.md` | Medium article |
| `video/video_script.md` | walkthrough video script |

**App:** [cmpe-255-data-mining-process-nba-expected-fg.streamlit.app](https://cmpe-255-data-mining-process-nba-expected-fg.streamlit.app/) · **Article:** [Medium article](https://medium.com/@meron.tesfandrias/what-is-a-shot-actually-worth-building-an-nba-expected-fg-model-with-semma-c5a514833c04) · **Video:** `<YouTube link>`

**SAS Enterprise Miner:** the notebook's appendix exports the exact modeling sample as three files with the game-grouped train / validate / test split, and the target-leak column removed, plus a 2024-25 scoring file. It lists the node-by-node steps to rebuild the flow, available through SAS OnDemand for Academics when the instructor registers the class.
