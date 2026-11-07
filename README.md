# Three Data Mining Methodologies, Three Projects

One end-to-end project for each classic data mining process model — **CRISP-DM**, **SEMMA** and **KDD** — each on a different real dataset, each taken all the way to a deployed app.

| Methodology | Project | Dataset | Mining task | Deployed app |
|---|---|---|---|---|
| [CRISP-DM](crisp-dm/) | Predicting hotel booking cancellations | Hotel Booking Demand (António, de Almeida & Nunes, 2019) — 119,390 bookings | Classification | `<Streamlit URL>` |
| [SEMMA](semma/) | NBA expected field-goal % (shot quality) | NBA shot-chart detail 2019-20 → 2024-25 — 1.25 M shots | Probability estimation | `<Streamlit URL>` |
| [KDD](kdd/) | Customer segments & product associations | UCI Online Retail II — 1,044,848 distinct transaction lines | Clustering + association rules | `<Streamlit URL>` |

## Results at a glance

| Project | Key result (on data never used for training or tuning) |
|---|---|
| **CRISP-DM** · hotel cancellations | A calibrated random forest's probabilities, summed per arrival date, forecast cancellations with half the error of the hotel's current overbooking rule (4.6 vs 9.4 rooms per night). That is worth **+€3,400 per 1,000 bookings** (95 % CI +€2,400 to +€4,300). As a per-booking classifier it misses its targets (ROC-AUC 0.83), because guest nationality was excluded as leakage |
| **SEMMA** · NBA xFG% | Gradient boosting beats the zone and zone × shot-family baselines on the unseen 2024-25 season (log loss 0.637 vs 0.658 / 0.647), calibrated within **1.5 pts** in every decile. Shot-making over expected persists (**r = 0.70**), less than raw FG%. Jokić +327 points in 2024-25 |
| **KDD** · online retail | 4 stable segments (bootstrap ARI 0.92): **96 %** of "Champions" buy again next year vs 40 % of lapsed buyers, though a plain RFM score ranks customers slightly better. **59 %** of 598 association rules meet all three thresholds again the following year (12 % for near-miss rules) |


## How the three methodologies differ — as seen in these projects

| | CRISP-DM | SEMMA | KDD |
|---|---|---|---|
| Origin | Industry consortium (SPSS, NCR, Daimler-Chrysler, OHRA), 1996–2000 | SAS Institute, for SAS Enterprise Miner | Fayyad, Piatetsky-Shapiro & Smyth, 1996 |
| Starts with | **Business understanding** — objectives, costs, success criteria | Data already chosen; starts with **sampling** | **Domain understanding** and end-user goals |
| Emphasis | business value end to end, documented outputs per task | the technical modeling core, tool-driven (nodes) | turning data into *valid, novel, useful, understandable* knowledge |
| Ends with | **Deployment** + monitoring plan | **Assess** (deployment is outside the model) | **Acting on knowledge** / consolidating it |
| What it forced in this repo | a € cost model of the real (nightly) decision against the hotel's current rule; time-ordered validation; a leakage test that removed the top predictor | a representative sample proven with statistics; competing model families compared on a validation partition; score code | patterns mined on one year and **re-tested on the next**; novelty test for rules |

The three are compared in detail by Azevedo & Santos (2008), *KDD, SEMMA and CRISP-DM: a parallel overview*, IADIS European Conference on Data Mining.

## Repository layout

```
<methodology>/
├── <notebook>.ipynb      # the full project, executed, with all outputs (open in Colab with the badge in the folder README)
├── report/               # the notebook exported as an HTML and PDF report
├── artifacts/
│   ├── figures/          # every chart produced by the notebook
│   ├── reports/          # every table produced by the notebook (CSV)
│   └── app/              # the deployable Streamlit app (app.py + model + requirements.txt)
├── critiques/            # three rounds of expert-critic reviews (round_1-3.md) and the responses to them
├── article/              # Medium article draft
└── video/                # walkthrough video script
```

## Running the projects

Each notebook downloads its own data (no Kaggle login needed) and runs top to bottom on free Google Colab: open the notebook in Colab → *Runtime → Run all*.

| Notebook | Run time on free Colab |
|---|---|
| CRISP-DM | ≈ 7–10 min |
| SEMMA | ≈ 4–6 min |
| KDD | ≈ 4–7 min |

To run an app locally: `cd <methodology>/artifacts/app && pip install -r requirements.txt && streamlit run app.py`.
To deploy for free: [share.streamlit.io](https://share.streamlit.io) → *Create app* → this repo → `<methodology>/artifacts/app/app.py` → under *Advanced settings* choose **Python 3.13** (the version the models were saved with).

## How AI was used

Following the assignment brief, Claude (Anthropic) was used to plan each project, generate and debug code, and draft the narrative. It also acted as an expert critic of every phase, over **three rounds**:
- **Round 1** ran in the drafting session.
- **Rounds 2 and 3** were run by fresh, independent Claude sessions given the expert-persona prompt shown in each notebook. They saw only the executed notebook, its figures and the app files.

Each round's full review and the point-by-point response are in the project's `critiques/` folder. Several findings changed the results, not just the wording: corrupted figures, a leaking nationality field, overlapping source sheets, players matched by misspelled names, and overstated validity claims. All code was executed end to end and its outputs checked; numbers quoted in the text are taken from those outputs.

## Data sources and licences

- Hotel Booking Demand — N. António, A. de Almeida, L. Nunes, *Data in Brief* 22 (2019) 41–49, [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126); mirrored on Kaggle as [`jessemostipak/hotel-booking-demand`](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) and by [TidyTuesday](https://github.com/rfordatascience/tidytuesday/tree/main/data/2020/2020-02-11) (the copy the notebook downloads).
- NBA shot-chart detail — stats.nba.com via [shufinskiy/nba_data](https://github.com/shufinskiy/nba_data) (Apache-2.0).
- Online Retail II — D. Chen, [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) (CC BY 4.0); mirrored on Kaggle as [`mashlyn/online-retail-ii-uci`](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci).
