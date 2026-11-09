# KDD — Customer Segments & Product Associations (Online Retail II)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MeronDT/CMPE-255-Data-Mining-process/blob/main/kdd/KDD_Online_Retail.ipynb)

**Goals:** (G1) discover customer segments that each call for a different action; (G2) discover products bought together — and test whether both are *knowledge*: valid, novel, useful and understandable (Fayyad, Piatetsky-Shapiro & Smyth, 1996).

**Data:** [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) (CC BY 4.0), also on Kaggle as [`mashlyn/online-retail-ii-uci`](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci) — 1,067,371 transaction lines of a UK online giftware retailer, Dec 2009 – Dec 2011 (22,523 lines repeated across the two Excel sheets are counted once). Patterns are mined on Dec 2009 – Nov 2010 and **re-tested on Dec 2010 – Nov 2011**.

## KDD steps → what was done

| Stage (Fayyad step) | In this project |
|---|---|
| 0 · Domain & goals (1) | two end users, two discovery goals, a test and pass mark for each knowledge criterion |
| 1 · Selection (2) | both Excel sheets, overlap removed; two equal 12-month periods; no cleaning rule crosses the split |
| 2 · Preprocessing (3) | cancellations matched one-to-one within each period, non-product codes, invalid prices, duplicates → 997,638 clean lines |
| 3 · Transformation (4) | log-scaled RFM customer table; invoice × product basket matrix reduced by the Apriori property (4,047 → 714 products) |
| 4 · Data mining (5–7) | K-means (k = 4, out-of-bag bootstrap ARI 0.92); FP-Growth (598 rules from 325 itemsets) |
| 5 · Interpretation / evaluation (8) | segment profiles; next-year validity against RFM baselines; rule persistence against near-miss rules; threshold sensitivity; hand-audited novelty test |
| → Act (9) | Streamlit app: basket recommendations, customer lookup, segmentation on the last 12 months — the validated model |

## Results

| Segment | Customers | Revenue (discovery yr) | Bought again next year |
|---|---|---|---|
| Champions | 17 % | 64 % | **96 %** |
| Loyal but cooling | 28 % | 24 % | 74 % |
| New customers | 20 % | 6 % | 65 % |
| Lapsed one-off buyers | 35 % | 6 % | 40 % |

- **Segments.** They order next-year value correctly but are a *useful partition*, not natural clusters. A plain RFM score ranks next-year activity slightly better (AUC 0.765 vs 0.739), so they are valid as descriptions, not as the best predictor.
- **Rules.** **59 %** meet all three thresholds (support, confidence, lift) again the following year, against 12 % of near-miss rules.
- **Novelty.** About 57 of the 325 associations are genuine cross-sells (hand audit). They link *matching-design sets* across product types, e.g. red spotty napkins + cups → plates (84 % confidence, 36× lift). But only about a quarter of cross-product associations hold the next year, so only the validated ones are recommended.
- **App.** Each customer's segment comes with an RFM score (the better ranking tool) and a per-segment export for campaigns.

## Files

| Path | What |
|---|---|
| `KDD_Online_Retail.ipynb` | the full project, executed with outputs |
| `report/` | the notebook as an HTML and PDF report |
| `artifacts/figures/`, `artifacts/reports/` | every chart and table |
| `artifacts/app/` | Streamlit app (`app.py`, rules, segments, segmenter) |
| `critiques/` | three rounds of expert-critic reviews and the changes they led to |
| `article/medium_article.md` | Medium article |
| `video/video_script.md` | walkthrough video script |

**App:** [cmpe-255-data-mining-process-retail-segments.streamlit.app](https://cmpe-255-data-mining-process-retail-segments.streamlit.app/) · **Article:** [Medium article](https://medium.com/@meron.tesfandrias/from-a-million-receipts-to-knowledge-a-kdd-walkthrough-on-online-retail-data-cc0093504b3e) · **Video:** `<YouTube link>`
