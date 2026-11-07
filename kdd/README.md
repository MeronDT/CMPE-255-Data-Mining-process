# KDD — Customer Segments & Product Associations (Online Retail II)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MeronDT/CMPE-255-Data-Mining-process/blob/main/kdd/KDD_Online_Retail.ipynb)

**Goals:** (G1) discover natural customer segments; (G2) discover products bought together — and prove both are *knowledge*: valid, novel, useful and understandable (Fayyad, Piatetsky-Shapiro & Smyth, 1996).

**Data:** [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) (CC BY 4.0) — 1,067,371 transaction lines of a UK online giftware retailer, Dec 2009 – Dec 2011. Patterns are mined on 2009-10 and **re-tested on 2010-11**.

## KDD steps → what was done

| Stage (Fayyad step) | In this project |
|---|---|
| 0 · Domain & goals (1) | two end users, two discovery goals, a concrete test for each of the four knowledge criteria |
| 1 · Selection (2) | both Excel sheets; discovery vs validation year |
| 2 · Preprocessing (3) | cancellations, later-cancelled purchases, non-product codes, invalid prices, duplicates → 990,590 clean lines |
| 3 · Transformation (4) | log-scaled RFM customer table; invoice × product basket matrix reduced by the Apriori property (4,047 → 717 products) |
| 4 · Data mining (5–7) | K-means (k = 4, bootstrap ARI 0.94); FP-Growth (579 rules) |
| 5 · Interpretation / evaluation (8) | segment profiles; next-year validity of segments and rules; novelty filter (variants vs cross-product) |
| → Act (9) | Streamlit app: recommendations, customer lookup, new-customer segmentation |

## Results

| Segment | Customers | Revenue (discovery yr) | Bought again next year |
|---|---|---|---|
| Champions | 17 % | 64 % | **96 %** |
| Loyal but cooling | 28 % | 25 % | 74 % |
| New customers | 20 % | 6 % | 66 % |
| Lapsed one-off buyers | 35 % | 6 % | 40 % |

- **86 %** of association rules meet the full thresholds (lift ≥ 3, confidence ≥ 0.4) again the following year.
- The novel rules link *matching-design sets* across product types (e.g. red spotty napkins + cups → plates, 84 % confidence, 36× lift).

## Files

| Path | What |
|---|---|
| `KDD_Online_Retail.ipynb` | the full project, executed with outputs |
| `report/` | the notebook as an HTML and PDF report |
| `artifacts/figures/`, `artifacts/reports/` | every chart and table |
| `artifacts/app/` | Streamlit app (`app.py`, rules, segments, segmenter) |
| `critiques/` | AI critic reviews and resulting changes |
| `article/medium_article.md` | Medium article draft |
| `video/video_script.md` | walkthrough video script |

**App:** `<deployed URL>` · **Article:** `<Medium link>` · **Video:** `<YouTube link>`
