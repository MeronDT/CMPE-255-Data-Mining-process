# Video walkthrough script — KDD: customer segments & product associations (≈ 11 min)

**Setup before recording:** the notebook open in Colab after *Run all* (outputs visible), the GitHub repo in a second tab, the deployed app in a third. Screen-record at 1080p; zoom the browser to ~125 %.

| Time | On screen | What to say (talking points) |
|---|---|---|
| 0:00–0:45 | Title cell | The data: two years of transactions from a UK online giftware wholesaler (1.07 M lines). Two questions: *which kinds of customers do we have?* and *which products are bought together?* |
| 0:45–1:45 | KDD steps table + Stage 0 | KDD (Fayyad et al., 1996) = turning data into knowledge that is **valid, novel, useful and understandable**. Show the four tests you committed to *before* mining — especially "valid = still true the next year". |
| 1:45–2:45 | **Selection**: sheet counts, monthly revenue chart | Both Excel sheets read (a common trap is reading only the first). Strong Q4 peak. The red line splits discovery year (2009-10) from validation year (2010-11). |
| 2:45–4:00 | **Preprocessing**: log table | Walk the log: cancellations separated (19.5k lines), purchases cancelled later removed, postage/fees removed, bad prices removed, duplicates removed → 990k clean lines. 23 % of lines have no customer — used for baskets, not segments. |
| 4:00–5:15 | **Transformation**: RFM box plots, basket reduction | Why log + scaling before K-means. Why only 717 of 4,047 products are needed for rules (Apriori property). |
| 5:15–6:30 | **Data mining**: k selection, stability, FP-Growth output | k = 4 (best silhouette in the usable range); bootstrap ARI 0.94 = stable. FP-Growth: 579 rules in seconds. |
| 6:30–9:00 | **Interpretation/evaluation**: profiles table, PCA plot, revenue-share chart, next-year validity, rule validity scatter, cross-product rules | Name the segments: Champions (17 % of customers → 64 % of revenue), Loyal but cooling, New customers, Lapsed one-off. **Validity:** 96 % of Champions bought again vs 40 % of Lapsed. Rules: 86 % still pass the full thresholds next year. **Novelty:** most rules are colour variants; the interesting ones are matching-design sets (red spotty napkins + cups → plates). Mention the three things the AI critic made you fix. |
| 9:00–10:15 | The deployed app | Pick "PINK REGENCY TEACUP AND SAUCER" → recommendation; look up a customer; segment a new customer (400 days, 1 order → Lapsed one-off). |
| 10:15–11:00 | Repo + wrap-up | Where everything is; what you'd do next (product-mix features, quarterly re-mining); how KDD differed from CRISP-DM and SEMMA. |
