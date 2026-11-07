# CRISP-DM — Predicting Hotel Booking Cancellations

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MeronDT/CMPE-255-Data-Mining-process/blob/main/crisp-dm/CRISP_DM_Hotel_Cancellations.ipynb)

**Business problem:** 37 % of bookings at two Portuguese hotels are cancelled. The goal is to score each booking's cancellation risk **at booking time**, so the hotel can request deposits, send reminders and set overbooking levels on evidence.

**Data:** *Hotel booking demand datasets* — António, de Almeida & Nunes, *Data in Brief* 22 (2019), [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126). 119,390 bookings (resort + city hotel), arrivals July 2015 – August 2017.

## CRISP-DM phases → what was done

| Phase | Highlights |
|---|---|
| 1 · Business Understanding | business and data mining success criteria fixed up front; € cost/benefit model (avg booking ≈ €358) |
| 2 · Data Understanding | two inconsistent source files; automatic leakage detector; Non Refund anomaly investigated |
| 3 · Data Preparation | every inclusion/exclusion justified ("known at booking time?"); integration validated against the published file; time-based split |
| 4 · Modeling | baseline, logistic regression, random forest, gradient boosting; **time-series cross-validation** (shuffled CV was 0.09 too optimistic) |
| 5 · Evaluation | cost-optimal threshold chosen on training data; test period used once; per-hotel results; leakage sensitivity test |
| 6 · Deployment | Streamlit app (single + batch scoring); PSI-based monitoring plan; final report |

## Results (test period: 23,795 bookings, Apr–Aug 2017, never used for training or tuning)

| Criterion | Target | Result |
|---|---|---|
| ROC-AUC | ≥ 0.85 | **0.868** ✅ |
| Precision at threshold 0.34 | ≥ 0.75 | **0.772** ✅ |
| Recall | — | 0.683 |
| Net value per 1,000 bookings | > "flag all" | **≈ €19,700** (flag all: −€18,300) ✅ |

Top drivers: country, deposit type, travel agent, special requests, lead time. **Open question:** if `country` is only confirmed at check-in it leaks the outcome; without it ROC-AUC drops by 0.035, so the model is approved on the condition this is checked with the hotel.

## Files

| Path | What |
|---|---|
| `CRISP_DM_Hotel_Cancellations.ipynb` | the full project, executed with outputs — every CRISP-DM task and output |
| `report/` | the notebook as an HTML and PDF report (the CRISP-DM final report) |
| `artifacts/figures/`, `artifacts/reports/` | every chart and table |
| `artifacts/app/` | Streamlit app (`app.py`, model, `sample_bookings.csv` for batch testing) |
| `critiques/` | AI critic reviews and resulting changes |
| `article/medium_article.md` | Medium article draft |
| `video/video_script.md` | walkthrough video script |

**App:** `<deployed URL>` · **Article:** `<Medium link>` · **Video:** `<YouTube link>`
