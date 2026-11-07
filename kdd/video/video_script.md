# Video walkthrough script — KDD: customer segments & product associations (≈ 11 min)

**Setup before recording:** the notebook open in Colab after *Run all* (outputs visible), the GitHub repo in a second tab, the deployed app in a third. Screen-record at 1080p; zoom the browser to ~125 %.

| Time | On screen | What to say (talking points) |
|---|---|---|
| 0:00–0:45 | Title cell | The data: two years of transactions from a UK online giftware retailer (about 1 M lines). Two questions: *which kinds of customers do we have?* and *which products are bought together?* |
| 0:45–1:45 | KDD steps table + Stage 0 | KDD (Fayyad et al., 1996) = turning data into knowledge that is **valid, novel, useful and understandable**. Show the tests and pass marks, especially "valid = still true the next year". |
| 1:45–2:45 | **Selection**: sheet counts, overlap message, monthly revenue chart | Both Excel sheets are read, and they **overlap** (1–9 Dec 2010 appears twice: 22,523 lines dropped). Strong Q4 peak. Two equal 12-month windows; the partial Dec 2011 point is marked. |
| 2:45–4:00 | **Preprocessing**: log table, anonymous-invoice table | Cancellations matched one-to-one to an earlier purchase **in the same year** (no leakage across the split). Postage, fees and bad prices removed; true duplicates are only 0.3 % of revenue → 997,638 clean lines. Anonymous invoices are much bigger; they are kept for baskets. |
| 4:00–5:15 | **Transformation**: RFM box plots, long-tail support plot | Why log + scaling before K-means. Only 714 of 4,047 products can be in a rule at 1 % support (Apriori property). |
| 5:15–6:30 | **Data mining**: k selection with stability, FP-Growth output | k = 4: best silhouette in the usable range and stable on held-out customers (ARI 0.92). Silhouette 0.34 means a useful partition, not natural clusters. 598 rules from 325 associations. |
| 6:30–9:15 | **Interpretation/evaluation**: profiles, next-year validity, RFM baselines, rule persistence, threshold grid, novelty + audit | Champions: 17 % of customers → 64 % of revenue; 96 % bought again vs 40 % of Lapsed. **Honest part:** a plain RFM score ranks customers better (0.765 vs 0.739), so segments are labels, not the best predictor. Rules: 59 % meet all three thresholds next year vs 12 % for near-misses (it was "86 %" before support was checked). Novelty: ~57 genuine cross-sells (napkins + cups → plates), but only a quarter of them hold up. Tell the critique stories (wrong segments in the app; sheet overlap). |
| 9:15–10:15 | The deployed app | Build a basket (red spotty napkins + cups) → plates; tick "hide variants"; look up a customer (segment + RFM score); export a segment list. |
| 10:15–11:00 | Repo + wrap-up | Where everything is; the critique files; what you'd do next (quarterly re-mining on a rolling 12-month window, an A/B test of the actions); how KDD differed from CRISP-DM and SEMMA. |
