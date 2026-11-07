# KDD critique — round 1

**Reviewer:** Claude (Anthropic), prompted with the expert persona below, reviewing the complete first draft of `KDD_Online_Retail.ipynb` (all stages, code and outputs).
**Note on independence:** round 1 was run in the same Claude session that helped draft the notebook. Rounds 2 and 3 should be run in a **fresh** Claude chat (paste the revised stage + outputs) so the reviewer has not seen the drafting — record them in `round_2.md` / `round_3.md`.

**Prompt used (per stage):**
> You are a world-renowned authority on the Knowledge Discovery in Databases (KDD) process as defined by Fayyad, Piatetsky-Shapiro and Smyth, a sought-after keynote speaker, and the author of several award-winning books on KDD and data mining. Review the **[stage]** stage of my retail KDD project below. Check it against everything this KDD stage requires. List (1) anything missing, (2) anything weak or unjustified, (3) methodological errors, and (4) concrete fixes, ranked by importance. Grade it as strictly as you would a professional engagement.

---

## Stage 0 & Selection — grade A−

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | 22.9 % of clean lines have no Customer ID and are excluded from segmentation — possible bias (e.g. one-off guest checkouts). | Acknowledged in the text as a limitation; these lines *are* used for basket analysis, where a customer is not needed. |
| 2 | Low | Discovery and validation periods should each cover a full seasonal cycle. | They do (Dec–Nov and Dec–Dec), which matters given the strong Q4 peak. |

## Preprocessing — grade B+

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | Cancellations are matched only on exact (customer, product, quantity); partial returns remain as purchases. | Stated in the text; partial returns are captured instead by the `return_rate` feature. |
| 2 | Low | 33,203 exact duplicate lines removed — could some be genuine repeat lines? | Identical invoice, product, quantity, price and timestamp; treated as system double entries. Baskets are binary so rules are unaffected; monetary is slightly lower. |

## Transformation — grade B+

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | Frequency and monetary correlate at 0.81 after transformation, so K-means effectively weights "volume" twice. | Acknowledged; RFM is kept because it is the domain standard and keeps segments explainable. Suggested as an iteration (e.g. drop monetary or use PCA components). |

## Data mining — grade A−

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | Silhouette is highest at k = 2 (0.414); restricting the search to 3–6 must be justified. | Text justifies it on usefulness (two groups — "good" and "bad" customers — is too coarse to act on); k = 4 is best within 3–6 (0.341). Bootstrap stability ARI 0.94 shows the four segments are not an artefact. |

## Interpretation / evaluation — grade B−  (biggest issues)

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | **High** | Segment labels came from a median split, so S3 (median 2 orders) was called "frequent". Misleading labels undermine *understandable*. | **Fixed.** Labels now use customer tertiles (frequency cut-offs 1 and 4 orders) and flag new customers (tenure ≤ 90 days). S3 is now correctly "active · repeat · mid-spend · new" — a *new customer* segment (median tenure 57 days). |
| 2 | **High** | The validity test halves both thresholds next year (lift ≥ 1.5, confidence ≥ 0.2) — far too lenient, which is why 99 % of rules "hold". | **Fixed.** Added a strict test with the original thresholds: **86 %** of rules hold; median next-year lift is 1.05× the discovery lift. The app now promotes only strictly validated rules (396 of 623). |
| 3 | **High** | The novelty test counted "KEY FOB GARAGE → KEY FOB SHED" and dog/cat coffee mugs as cross-category — they are design variants of one product. | **Fixed.** New rule: same product type (shared first or last two product words, or ≥ 50 % word overlap after removing colours, designs and sizes) = *variant*. What remains as *cross-product* is genuinely different products, mostly matching-design sets (e.g. red retrospot plates → cups) and themed bundles (Christmas napkins → Christmas cake cases). |

## Acting on the knowledge — grade A−

| # | Severity | Critique | Response |
|---|---|---|---|
| 1 | Medium | Segment actions were placeholders. | **Fixed.** Named segments with concrete actions (Champions / Loyal but cooling / New customers / Lapsed one-off buyers). |
| 2 | Low | No refresh plan. | Text recommends quarterly re-mining given the strong seasonality. |

**Overall verdict after fixes:** all four Fayyad criteria are now tested rather than asserted. Main remaining limitation: RFM ignores *what* customers buy — a product-mix feature would make segments richer.
