# SEMMA — NBA Expected Field-Goal Percentage

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MeronDT/CMPE-255-Data-Mining-process/blob/main/semma/SEMMA_NBA_Expected_FG.ipynb)

**Question:** how likely is any NBA shot to go in, given where and how it is taken? Comparing a player's actual FG% with the expected FG% (xFG%) of his shots separates shot *making* from shot *selection*.

**Data:** every regular-season field-goal attempt 2019-20 → 2024-25 from stats.nba.com via [shufinskiy/nba_data](https://github.com/shufinskiy/nba_data) (Apache-2.0). Five seasons (1,031,740 shots) form the population; 2024-25 (219,527 shots) is held out entirely.

## SEMMA steps → what was done

| Step | Enterprise Miner nodes | In this project |
|---|---|---|
| **Sample** | Input Data · Sample · Data Partition | 200k stratified sample proven representative (KS p = 0.999); size justified by a learning curve; 60/20/20 partition **grouped by game** |
| **Explore** | StatExplore · MultiPlot · Variable Selection · Cluster | shot charts, FG% by distance/type/clock, mutual-information variable worth, location clusters; caught `EVENT_TYPE` = target leakage |
| **Modify** | Drop · Transform · Replacement · Binning · Impute | engineered geometry (distance, angle, corner three, 3PT flag), clock flags, distance bins — written as reusable score code (`shot_features.py`) |
| **Model** | Regression · Decision Tree · Neural Network · Gradient Boosting · Ensemble | five models vs a zone-average baseline, tuned on the validation partition |
| **Assess** | Model Comparison · Cutoff · Score · Segment Profile | champion chosen by log loss; test + unseen-season check; decile calibration; player shot-making leaderboard |

## Results

| | Log loss | ROC-AUC | Mean xFG / actual FG |
|---|---|---|---|
| Zone-average baseline (validation) | 0.6572 | 0.634 | — |
| **Gradient boosting** (validation) | **0.6346** | **0.665** | 46.9 % / 46.8 % |
| Gradient boosting (test) | 0.6345 | 0.663 | 46.9 % / 46.4 % |
| Gradient boosting (**unseen 2024-25**) | 0.6377 | 0.657 | 46.4 % / 46.7 % |

- Calibrated within **0.9 percentage points** in every decile of the 2024-25 season.
- Shot making over expected, 2024-25: **Jokić +323 points**, Durant +228, Gilgeous-Alexander +197, Curry +143 — and it is a repeatable skill (**r = 0.68** season to season).

## Files

| Path | What |
|---|---|
| `SEMMA_NBA_Expected_FG.ipynb` | the full project, executed with outputs |
| `report/` | the notebook as an HTML and PDF report |
| `artifacts/figures/`, `artifacts/reports/` | every chart and table |
| `artifacts/app/` | Streamlit app: score any shot + leaderboard (`app.py`, `shot_features.py`, model) |
| `critiques/` | AI critic reviews and resulting changes |
| `article/medium_article.md` | Medium article draft |
| `video/video_script.md` | walkthrough video script |

**App:** `<deployed URL>` · **Article:** `<Medium link>` · **Video:** `<YouTube link>`

**SAS Enterprise Miner:** the notebook's appendix exports the exact modeling sample and lists the node-by-node steps to rebuild the flow (available through SAS OnDemand for Academics when the instructor registers the class).
