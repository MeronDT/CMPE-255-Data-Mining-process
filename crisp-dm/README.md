# CRISP-DM — Predicting Hotel Booking Cancellations

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MeronDT/CMPE-255-Data-Mining-process/blob/main/crisp-dm/CRISP_DM_Hotel_Cancellations.ipynb)

**Business problem:** 37 % of bookings at two Portuguese hotels are cancelled. The hotels overbook each night by a fixed historical rate. The goal is to estimate each booking's cancellation probability **at booking time**, and add the probabilities up into an expected number of cancellations per night, so the overbooking level follows the bookings actually on the books.

**Data:** *Hotel booking demand datasets* — António, de Almeida & Nunes, *Data in Brief* 22 (2019), [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126). 119,390 bookings (resort + city hotel), arrivals July 2015 – August 2017.

## CRISP-DM phases → what was done

| Phase | Highlights |
|---|---|
| 1 · Business Understanding | one decision (the nightly overbooking level); cost model with both outcomes weighted by the chance the hotel fills up; the hotel's current rule of thumb as benchmark; legal constraint on nationality |
| 2 · Data Understanding | two inconsistent source files; leakage screens over every attribute; a within-segment test showing **nationality was probably defaulted for guests who never arrived**; Non Refund and duplicate-row investigations; like-for-like drift |
| 3 · Data Preparation | every inclusion/exclusion justified (nationality excluded as leakage); construction written as score code inside the pipeline (the model takes 24 raw booking fields); integration validated against the published file; time-based split |
| 4 · Modeling | three baselines incl. a "flag every Non Refund booking" rule; logistic regression, random forest, gradient boosting with equal tuning budgets; date-aligned **time-series cross-validation** (shuffled CV was 0.09 too optimistic) |
| 5 · Evaluation | isotonic calibration; bootstrap confidence intervals; **per-night simulation against the current overbooking rule**; results without the Non Refund blocks, per hotel and per booking-date band; leakage sensitivity |
| 6 · Deployment | Streamlit app (recommended extra rooms per arrival date from the day's booking file); randomised pilot design; drift monitoring with responses that need no outcomes; final report |

## Results (test period: 23,795 bookings, Apr–Aug 2017)

**The decision the hotel makes, per night** (262 hotel-nights, assumed costs):

| Overbooking policy (per 1,000 bookings) | Net value | vs current rule (95 % CI) | Error, rooms per night |
|---|---|---|---|
| Current rule of thumb (historical rate × bookings) | €13,429 | — | 9.4 |
| **Model: expected cancellations (sum of probabilities)** | **€16,804** | **+€3,375 (+2,445 to +4,324)** | **4.6** |
| Model: count of flagged bookings | €11,538 | −€1,891 | 16.1 |

**The per-booking classifier** misses two of its three targets once the leaking nationality field is removed. So individual flags are information only.

| Criterion | Target | Test (95 % CI) | Cross-validation |
|---|---|---|---|
| ROC-AUC | ≥ 0.85 | 0.827 (0.810–0.846) | 0.841 |
| Precision at threshold 0.67 | ≥ 0.75 | 0.831 (0.797–0.858) | 0.949 |
| Recall at threshold 0.67 | ≥ 0.50 | 0.471 (0.422–0.525) | 0.405 |

Top drivers: deposit type, special requests, lead time, travel agent, customer type.

**Caveats:**
- **Assumptions.** Costs, demand and recording practices are assumed, because no hotel contact was available.
- **Non Refund blocks.** Much of the per-booking signal comes from the anomalous Non Refund blocks.
- **New bookings.** Short-notice bookings are harder to predict.
- **Test period.** It was scored in iteration 1, and its results were visible during the review rounds, so cross-validation is reported alongside.

## Files

| Path | What |
|---|---|
| `CRISP_DM_Hotel_Cancellations.ipynb` | the full project, executed with outputs — every CRISP-DM task and output |
| `report/` | the notebook as an HTML and PDF report (the CRISP-DM final report) |
| `artifacts/figures/`, `artifacts/reports/` | every chart and table |
| `artifacts/app/` | Streamlit app (`app.py`, score code `booking_features.py`, model, `sample_bookings.csv` for batch testing) |
| `critiques/` | three rounds of expert-critic reviews and the changes they led to |
| `article/medium_article.md` | Medium article |
| `video/video_script.md` | walkthrough video script |

**App:** [cmpe-255-data-mining-process-hotel-cancellations.streamlit.app](https://cmpe-255-data-mining-process-hotel-cancellations.streamlit.app/) · **Article:** `<Medium link>` · **Video:** `<YouTube link>`
