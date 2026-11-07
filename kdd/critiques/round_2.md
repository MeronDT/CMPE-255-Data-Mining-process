# KDD critique — round 2

**Reviewer:** an independent Claude instance (Anthropic), started fresh. It had no access to the drafting conversation or to round 1. It received a plain-text export of the executed notebook (markdown, code and text outputs), the figure PNGs, and the app and report files. For each stage it adopted the expert-persona prompt shown in that stage's critic section of the notebook, and answered it.
**Date:** 6 November 2026. **Below:** the review exactly as returned, followed by the response to each point.

---


Reviewer stance: each stage is reviewed as the KDD authority the stage's critic prompt asks for. I checked the numbers in the packet against the executed outputs and against `artifacts/reports/*.csv`, `artifacts/app/*`. I did not read `critiques/`. Verification figures quoted below (e.g. "156 of 498") come from my own re-computation on `association_rules_evaluated.csv`, `customer_segments.csv`, `rules.csv` and `metadata.json`.

---

## Stage — Selection (incl. Stage 0 domain & goals) · grade B-

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The validation year is not "untouched".** The Selection table promises an untouched year, but the split (`DISCOVERY_END`) is applied only in Stage 3. Before that, cancellation matching (all years, no time ordering), canonical descriptions and duplicate removal were all computed on the pooled 2009–2011 data. So a 2011 cancellation can delete a 2010 purchase and change discovery-year RFM values. The project's main claim is out-of-time validity, so the split has to come before any data-dependent cleaning. | Split `raw` into discovery and validation in Stage 1. Run every data-dependent cleaning rule within each period, or only from past to future. Say so in the Target data set table. |
| 2 | Medium | **The anonymous-basket scope is asserted, not examined.** "An anonymous basket is still a basket" is a slogan. 22.8 % of lines have no Customer ID, and nobody checked whether those invoices differ: size, item count, a few giant batch-type invoices, dates. Very large no-ID invoices would inflate co-occurrence counts and bias the rules. | Compare the basket-size distributions of ID and no-ID invoices. Re-mine on ID-only invoices as a sensitivity check and report how many rules change. |
| 3 | Medium | **Wholesalers and 43 countries are noted in Stage 0 and then ignored.** Stage 0 says "many customers are wholesalers… order sizes vary enormously". Selection still mixes B2B and B2C customers and UK and export accounts in one population. The segments therefore partly sort customers by business type, not by behaviour. | Flag likely wholesalers (e.g. median line quantity or avg basket value above a threshold, or non-UK) and justify keeping them pooled. Alternatively segment UK customers separately and compare. |
| 4 | Medium | **Stage 0 has no success criteria set in advance.** The evaluation plan names tests but not pass marks: what persistence rate or ARI counts as "valid"? The validity thresholds were later chosen twice (halved, then "full"), which is exactly the post-hoc freedom pre-set criteria prevent. The "Potentially useful" test, "each segment gets a concrete action", is satisfied by definition. There is also no business objective that could be measured (e.g. a target retention or basket-size uplift). | Pre-state numeric pass/fail criteria (e.g. "≥ 70 % of rules meet all three thresholds next year"; "segments beat an RFM-score baseline on next-year AUC"). Make usefulness a measurable quantity, such as revenue at stake per segment or the share of baskets a validated rule applies to. |
| 5 | Low | **Unequal and partly hidden windows.** Discovery covers 12 months. Validation covers 12 months + 9 days, and the extra days are the start of the December peak. This slightly inflates "active next year". On the monthly-revenue figure the Dec 2011 point is a 9-day partial month that looks like a revenue collapse, and it is not labelled. | Cut validation at 30 Nov 2011 (or note the 9 extra days). Mark the last point as partial, or drop it. |
| 6 | Low | "Attributes: all 8 … all are needed for RFM and baskets" is inaccurate. Country is not used by either mining task, and Description serves only as a label. | Say which attributes each goal uses. Treat Country as descriptive only, or use it (see #3). |

Done well: both Excel sheets are loaded explicitly (avoiding the common first-sheet-only bug), and the 12-month seasonal split is well motivated by the revenue plot.
**Verdict:** a sound target set and a sensible temporal design, undermined by cleaning that runs across the split and by scoping decisions that are asserted rather than tested.

---

## Stage — Preprocessing · grade C+

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **`return_rate` is wrong in two ways, and a conclusion rests on it.** (a) Purchases that were fully cancelled are removed from `monetary` (the denominator), but their cancellations still count in `returned` (the numerator), so they are double-counted. (b) `cancellations` still contains non-product codes (`M`, `D`, `POST`, `AMAZONFEE`, `BANK CHARGES`…) and invalid prices, so manual adjustments and fees count as "returns". Evidence: in the final customer table 76 customers have return_rate > 0.5 and 28 are clipped at exactly 1.0. Stage 5's claim "return rates are similar (2–3 %) … so returns do not distinguish them" is drawn from this broken feature. | Compute returns only from product-code cancellations that were not matched and removed. Report the distribution before clipping. Re-check the Stage 5 claim. |
| 2 | High | **Cancellation matching is not what the prose says.** The prose says "Purchases that were later cancelled in full" are removed. The code (`k in cancel_keys`) (a) ignores time, so a purchase made after the cancellation also matches, and the match crosses the discovery/validation boundary (leakage, see Selection #1); and (b) is many-to-one. One cancellation of 12 units removes every 12-unit purchase of that product by that customer over two years. Nobody checked whether 13,653 removed lines is plausible against 19,494 cancellation lines. | Match each cancellation to the single most recent earlier purchase with the same customer, product and quantity (one-to-one, time-ordered, within the same period). Log matched and unmatched counts. |
| 3 | Medium | **Removing duplicates is not backed by evidence.** 33,203 lines (3.2 %) are deleted as "double entries" without a single example or check. In this dataset the same product often appears twice on one invoice as a genuine second scan. Deleting such lines cuts `monetary` for exactly the high-volume customers who matter most. | Show examples. Prefer aggregating identical invoice×product lines (summing quantity) over deleting them, or justify deletion with evidence such as identical lines appearing in pairs at the same second. |
| 4 | Medium | **Missing Customer IDs are handled by a slogan.** Keeping no-ID lines for baskets is reasonable, but the stage never profiles them (see Selection #2). The stated limitation, that segments describe registered customers only, is fine. The basket-side risk is not mentioned. | Add a short table comparing no-ID and ID invoices (lines per invoice, revenue per invoice, date spread), plus the sensitivity re-mine. |
| 5 | Low | **The price tail is not inspected.** The log10-price histogram reaches about 10³ (≈ £1,000 per unit) after cleaning, yet only the top-revenue lines are checked. A five-digit code with a £1,000 unit price in a giftware shop needs a look. | List the lines with the highest unit prices and confirm they are real products. |
| 6 | Low | `Description.astype(str)` turns missing values into the string `"nan"`, and canonical descriptions are computed across both periods. The impact is small but untidy. | Fill missing descriptions before casting. Compute canonical names from the discovery period, or accept this explicitly as a static lookup. |
| 7 | Low | The figure shows distributions after cleaning only, so it is not evidence for any cleaning rule. | Show before/after, or the counts behind each rule (e.g. a breakdown of non-product codes by type and revenue). |

Done well: the step-by-step removal log with counts, and the explicit list of non-product codes, are exemplary.
**Verdict:** well documented, but two of the rules, cancellation matching and return_rate, do something different from what the prose claims, and one of them leaks future data.

---

## Stage — Transformation · grade B-

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | Medium | **The known redundancy is left in place.** F and M correlate at 0.81 after transformation. The text admits that volume is "effectively weighted twice", then defers the fix to "an iteration". The PCA plot shows the result: the clusters are mostly slices along PC1, a single "value" axis, so the 4-segment solution is close to a 1-D binning plus a recency split. | Act on it here. Try R + a single volume factor (e.g. the mean of z(F) and z(M)), or PCA-whitened features, and show whether the segments change. |
| 2 | Medium | **The observation window confounds RFM.** Frequency and monetary are not normalised by tenure. A customer acquired in October has mechanically low F and M, so S3 ("new") is partly produced by the window, not by behaviour, and is mixed with genuinely low-value customers. `tenure_days` is computed but used only afterwards as a label. | Add orders per active month, or include tenure as a feature, or segment customers with tenure ≥ 90 days separately and treat new customers as a rule-based group. |
| 3 | Medium | **The domain feature that matters most is missing.** Stage 0 names wholesaling as the defining trait of this customer base. `avg_basket_value` and `distinct_products` are computed and then unused. Nothing in the representation separates a reseller from a gift buyer. | Test adding log(avg_basket_value) or a wholesaler flag. Report whether it produces a separate, actionable segment. |
| 4 | Medium | **`log1p` on recency is not justified.** Recency is bounded at 0–364 and only moderately skewed (median 47, mean 87). The log stretches 0–20 days and squashes 100–364 days, the range where "cooling" and "lapsed" are told apart. | Justify it with the boxplot, or use raw or rank-scaled recency, and show the effect on the segments. |
| 5 | Medium | **The item-support figure is corrupted.** `transformation_item_support.png` is drawn on top of the stale RFM box-plot figure: the left panel is the raw-RFM boxplot again, and the barh has no x-axis values, so no support value can be read. The figure that should show the long tail behind the 1 % cut does not. | Create a fresh figure (`fig, ax = plt.subplots()`) before `.plot.barh(ax=ax)`. Add a log-scale rank–support plot with the 1 % line marked. |
| 6 | Low | **Basket heterogeneity is not shown.** Invoices range from 1 line to hundreds (wholesale). A few huge invoices contribute many pairwise co-occurrences. Neither a basket-size distribution nor any cap is discussed. | Plot the number of items per invoice. Consider a sensitivity run that excludes the top 1 % of invoices by size. |

Done well: the Apriori-property argument for dropping items below 1 % is correct, and keeping every invoice so support denominators stay honest is exactly right.
**Verdict:** the representations fit both goals, but known weaknesses (F/M redundancy, the window confound, no wholesale feature) are acknowledged and not addressed, and one key figure is broken.

---

## Stage — Data mining · grade C+

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **The rule thresholds are arbitrary and their cost is hidden.** `MIN_SUPPORT=0.01`, `MIN_CONFIDENCE=0.40`, `MIN_LIFT=3.0` and `max_len=3` come with no rationale and no sensitivity analysis. 1 % support (≈195 invoices) limits rule mining to 717 of 4,047 products. In the delivered app only 184 products appear as antecedents, and only 129 have a validated rule, about 3 % of the catalogue. Coverage is never reported for a cross-selling tool. | Run a small grid (support 0.5/1/2 %, lift 2/3/5). Report the number of rules, the share that persist next year, and catalogue and basket coverage. Pick thresholds from that trade-off. |
| 2 | High | **The k choice and the "natural segments" claim are unsupported.** Silhouette is highest at k = 2 (0.414). `K_RANGE` excludes 2 in advance, and k = 4 wins with 0.341 among 3–6. The inertia curve has no knee, yet "silhouette + elbow" is cited. A silhouette of 0.34, plus a PCA plot showing one continuous cloud cut into wedges (with the visible streaks of discrete frequency values), indicates weak cluster structure. G1 promises *natural* segments. These are a useful partition of a continuum, not discovered groups. | State this honestly ("a partition for actionability, not natural clusters"). Justify k = 4 by interpretability and validation lift over k = 3 and k = 5. Optionally compare with a GMM/BIC or gap statistic. |
| 3 | Medium | **There is no baseline method.** Stage 0 names classic RFM scoring as "the established retail practice", yet K-means is never compared with it (e.g. RFM quintile scores, or monetary tertiles × recency). Without that comparison the mining step adds no evidence that clustering beats the standard tool. | Build the RFM-score segmentation in a few lines and compare it in Stage 5 on the same next-year metrics. |
| 4 | Medium | **The stability test is weak and partly misread.** Only 10 bootstrap resamples are used. ARI is computed on all customers, including in-bag ones. k is fixed, so the test says nothing about whether k = 4 is the stable choice. High ARI for K-means on a unimodal cloud with fixed k is expected and does not show that the clusters exist. Latent bug: the same `projector` object is shared by `segmenter` and every bootstrap pipeline (sklearn does not clone steps), so after the loop `segmenter`'s scaler is fitted on bootstrap sample 9 while its centroids come from the full data. It is not used for prediction afterwards, but it is a trap. | Run ≥ 50 resamples and score out-of-bag customers only. Compute stability for k = 2…6 to support the k choice. Use `sklearn.base.clone(projector)` inside each pipeline. |
| 5 | Medium | **The rule count is inflated by redundancy.** The 579 rules come from only 311 distinct itemsets. Every pair appears as both A→B and B→A, and 3-item rules sit next to their 2-item sub-rules. The top-10 table is really 5 associations shown twice. | Report itemsets, or keep one direction per pair (the higher-confidence one). Prune rules whose confidence does not beat their sub-rule's. |
| 6 | Low | **The environment does not match the pin.** The install line pins `mlxtend==0.23.4`, but the run used 0.25.0 (the `try` only installs when the import fails). The `except TypeError` fallback changes `association_rules` semantics between versions. | Pin and assert versions, or drop the fallback. |

Done well: matching algorithms to goals (K-means on log-RFM, FP-Growth for wide sparse baskets) is appropriate and clearly explained.
**Verdict:** the algorithms are right, but the parameters are unjustified, the k choice overrides the metric's own verdict, and no baseline shows that mining added value.

---

## Stage — Interpretation / Evaluation · grade C+

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | High | **"Meet the full thresholds again" is false.** `holds_strict` re-checks lift and confidence but **not support**. In `association_rules_evaluated.csv`, 156 of the 498 "strictly" holding rules have validation support < 1 %. Counting all three thresholds, about 342 of 579 rules (≈ 59 %) hold, not 86 %. The headline, the evaluation table, the README and the app checkbox ("met the full thresholds") all repeat the overstated figure. | Add `val_support >= MIN_SUPPORT` to `holds_strict`, then restate every number and the app label. Optionally report the lift/confidence-only rate separately and name it as such. |
| 2 | High | **Segment validity has no baseline, so it proves little.** "The ordering of the segments is exactly the ordering of their future value" is expected from any split sorted by past spend and recency: RFM's predictive power is the prior knowledge cited in Stage 0. The test cannot tell these clusters apart from monetary tertiles. | Compare the clusters with RFM-score and single-variable baselines on a predictive metric (AUC for next-year activity, Spearman correlation or R² for log next-year revenue). Claim validity only if the clusters match or beat them. |
| 3 | High | **The novelty classifier is unreliable and never audited.** In a random sample of 25 "cross-product" rules, roughly half are obvious variants: `JUMBO BAG OWLS → JUMBO STORAGE BAG SUKI`, `JUMBO BAG TOYS → JUMBO BAG STRAWBERRY`, `HEART OF WICKER LARGE (+…) → HEART OF WICKER SMALL`, cake-case → cake-case. The 154 "cross-product" rules are also only 96 distinct itemsets. The showcased "novel" finding (matching RETROSPOT/POLKADOT tableware) is the retailer's own designed collections, so it is hardly novel to the merchandiser, and that is never argued against prior knowledge. "S3 was not anticipated by a plain RFM view" is self-contradictory: S3 *is* a plain-RFM cluster. | Hand-label a random sample of 50 rules, report the classifier's precision and recall, and fix the patterns (e.g. treat `JUMBO … BAG`, `CAKE CASES`, `LUNCH BAG` as one type). Report deduplicated itemsets. Argue novelty against what the merchandiser already knows (the catalogue collections). |
| 4 | Medium | **The prose numbers have the wrong denominators or don't match.** (a) "96 % of Champions bought again … 67 % of next year's revenue": the denominator is revenue from *discovery-period customers only*, excluding customers acquired in 2011 and anonymous sales, so it is not "next year's revenue". The same applies to "S2 produced 21 %". (b) The evaluation table says "396 strictly validated rules". The strict test passes 498. 396 is the number of *re-mined two-year* rules that match a validated rule, and it comes from a Stage 9 output that does not exist yet at this point. | Relabel as "share of next-year revenue from discovery-year customers" and also give the share of all next-year revenue. Use 498 (or the corrected #1 figure) here and explain 396 in Stage 9. |
| 5 | Medium | **The rule-validity figure shows the wrong test.** Points are coloured by the lenient halved-threshold test (only 2 red points), while the text relies on the strict test. Lift, the main threshold, is not plotted at all. There is also no null reference: with largely the same catalogue in both years, how often would *any* above-threshold pair persist? | Colour by the corrected strict test, add a discovery-vs-validation lift panel, and compare persistence with rules just below threshold or with random pairs of matched support. |
| 6 | Medium | **Stability is presented as validity, and segment structure is never re-tested.** Bootstrap ARI is listed under "Valid", but it measures within-sample stability. The evaluation never checks whether the *same segments re-form* in the validation year. | Fit K-means on validation-year RFM and compare centroids and segment sizes with discovery. Alternatively, score validation customers with the discovery model and compare profiles. |
| 7 | Medium | **Usefulness is asserted, not quantified.** "Each segment has an action" is not evidence. Nothing is said about the revenue at stake per action or how often a validated rule would fire in a real basket. | Report, for example, S2's next-year revenue at risk (£1.38 M), and the share of validation-year baskets that contain a validated antecedent and lack its consequent (the cross-sell opportunity). |
| 8 | Low | **One label hides a borderline split, and the loop-backs are cosmetic.** S2 is called "high-spend" because its median (£1,293) is just above the £1,221 tertile cut, so about half of S2 is mid-spend. The documented loop-backs fixed labels and thresholds but not the substantive issues (F/M redundancy, k = 2, wholesalers), which are again deferred. | Label using the share of members in each tertile, not the median alone. Do at least one real loop back to Transformation (e.g. #1 there) and report whether the conclusions change. |

Done well: testing both segments and rules on the following year is the right design and is rarely attempted, and the profile table matches the outputs exactly.
**Verdict:** the evaluation design is the strongest idea in the project, but the headline rule result is overstated, segment validity lacks a baseline, and novelty rests on an unaudited heuristic.

---

## Stage — Acting on the knowledge · grade C

| # | Severity | Critique (what, where, why it matters) | Concrete fix |
|---|---|---|---|
| 1 | Critical | **The deployed segments are not the validated segments, and their labels are wrong.** The final model is re-fitted on a **24-month** window. It is mapped to S1–S4 by Hungarian matching of centroids that live in *two different standardisation spaces*, and the mapping is never checked. From `customer_segments.csv`: final "S2 · Loyal but cooling" has a median recency of **178 days** (lapsed by the discovery tertiles), final "S3 · New customers" has a median tenure of **225 days** ("new" means ≤ 90), and S4's median recency is 400 days. The app still shows discovery-year names, actions ("re-engage if no order in 60 days", "onboarding emails") and an Overview tab built from the **discovery** `prof` (726/1,193/821/1,478 customers) while it segments 5,830 customers. Marketing staff would act on wrong descriptions. | Either deploy the validated discovery-window model, re-scored on a trailing 12-month window as of the snapshot, or re-profile the final clusters, regenerate labels from the data and show *final* profiles in the app. Add an assertion that each mapped segment's medians fall in the band its label implies. |
| 2 | High | **The "Segment a new customer" inputs have no time window.** "Number of orders" and "Total spend" feed a model trained on 2-year totals, but the UI never says so. A user typing annual figures gets a segment based on half the volume. | Label the inputs ("in the last 12 months") and make the model's window match (see #1). |
| 3 | Medium | **Unvalidated and less useful patterns reach users.** "Re-mined on both years (now validated)" overclaims: the 2-year clusters and rule statistics are not themselves validated. 227 of 623 rules (36 %) are unvalidated and one checkbox away. 55 of the 184 products in the selector have no validated rule, so by default they show "No strong associations". `rule_type` is not exported, so the top suggestion, sorted by lift, is usually a colour variant, contradicting the "Conflicts to watch" note. | Drop products with no validated rule from the selector. Export `rule_type` and let staff filter to cross-product rules, or rank them first. Note in the UI that rule statistics are pooled over two years. |
| 4 | Medium | **Rules fire on a partial antecedent.** `product in a.split(" + ")` returns 2-item-antecedent rules when the basket has only one of the two items, so the confidence shown does not apply to that basket. | For a single-product input, show only 1-item-antecedent rules, or let the user enter the whole basket and require the full antecedent. |
| 5 | Medium | **There is no real maintenance or measurement plan.** "Re-mine quarterly" gives no procedure, owner, drift trigger or monitoring metric, and it conflicts with the project's own validation design: quarterly patterns cannot be validated a year ahead. There is no plan to measure whether the actions work (holdout or A/B campaign, uplift KPI tied to Stage 0 goals). | Specify the refresh: a rolling 12-month window, validation on the next quarter, alerts when the share of persisting rules or segment sizes drift by more than X. Add a campaign holdout design per segment. |
| 6 | Low | **The deliverable is unfinished and loosely packaged.** The README and header still show a `<deployed URL>` placeholder. `requirements.txt` leaves `streamlit` and `pandas` unpinned. A customer-level file is published (the data is public here, but a professional engagement should note the governance point). The S2 action trigger ("no order in 60 days") sits on top of a 57-day median, so most of the segment triggers it at once. | Deploy and link the app. Pin all versions. Add a data-governance note. Turn the action triggers into rules backed by data. |

Done well: the outputs map cleanly onto the two Stage 0 end users, only validated rules are shown by default, and the consolidation section checks the results against prior knowledge.
**Verdict:** the delivery mechanism is good, but the shipped segmentation is unvalidated, mislabelled relative to its own data, and documented with stale profiles.

---

## Overall grade: C+

The study design (out-of-time validation of both segments and rules, a novelty split, a deployed tool) is better than typical coursework. But several headline claims fail when checked against the project's own artifacts: "86 % meet the full thresholds" ignores support (≈ 59 % do), "natural segments" contradicts the silhouette evidence, cross-product novelty rests on an unaudited and visibly leaky classifier, and the app ships a re-fitted segmentation whose labels and profiles no longer describe its customers.

### Top 5 fixes, ranked by importance
1. **Fix the deployed segmentation.** Ship the validated 12-month model, re-scored on a trailing 12-month window, or re-profile and relabel the 2-year clusters. Show the *final* profiles in the Overview tab, check the centroid mapping against the medians, and state the input window in the "new customer" tab. (Final S2 has a median recency of 178 days and final S3 a median tenure of 225 days, yet they are labelled "cooling" and "new".)
2. **Make rule validation truly "full thresholds".** Add `val_support >= MIN_SUPPORT`, which brings the rate from 86 % to about 59 %, and correct the headline, README and app checkbox. Plot the strict test (with lift), and add a persistence baseline.
3. **Add baselines for segment validity and be honest about structure.** Compare the clusters with RFM-score and monetary-tertile segmentations on next-year AUC and revenue correlation. Reframe "natural segments" as an actionable partition, given that silhouette is best at k = 2 and only 0.34 at k = 4.
4. **Remove cross-period leakage and repair `return_rate`.** Split before cleaning. Match cancellations one-to-one, in time order and within each period. Compute returns from unmatched product-only cancellations, then re-check the "returns don't distinguish segments" claim.
5. **Audit the novelty classifier and the rule set.** Hand-label a sample and report its precision (about half of the sampled "cross-product" rules are variants such as JUMBO BAG ↔ JUMBO STORAGE BAG). Deduplicate symmetric and redundant rules (579 rules come from 311 itemsets). Justify the support, confidence and lift thresholds with a sensitivity and coverage table, and expose `rule_type` in the app.


---

# Responses to round 2 (what changed in the notebook)

The full notebook was re-run end to end after these changes. All numbers below come from the re-run.

## Selection
| # | Response |
|---|---|
| 1 | **Fixed.** Cancellation matching now runs within each period, in time order, one-to-one (`merge_asof`, most recent earlier purchase). Nothing from the validation year changes the discovery year. Canonical product descriptions are a static name lookup with no outcome information, which is accepted and stated. |
| 2 | **Fixed.** Anonymous vs identified invoices are profiled: anonymous invoices are larger (mean 77 products vs 21). Re-mining on ID-only invoices gives 429 rules, and 90 % of them are in the main set. |
| 3 | **Partly.** Shares of likely wholesalers (average basket > £1,000) and non-UK customers are reported per segment (0.7–8.4 %; 6–9 %). With so few, the pooled segmentation is kept; a UK-only re-run was not done. |
| 4 | **Fixed.** Pass marks were added to Stage 0, honestly labelled as set in revision 2 after the first results. Usefulness now includes revenue at stake and basket coverage. |
| 5 | **Fixed.** Validation now ends 30 Nov 2011 (12 months, like discovery). The partial December 2011 point is marked on the chart. |
| 6 | **Fixed.** The attribute roles are stated (country descriptive only). |

## Preprocessing
| # | Response |
|---|---|
| 1 | **Fixed.** `return_rate` = unmatched **product-code** cancellations ÷ (net spend + returned). There is no double counting and no clipping is needed (max 0.76). The Stage 5 claim was re-checked: return rates are 0.6–1.1 % in every segment. |
| 2 | **Fixed.** See Selection 1: 5,825 matched one-to-one, against 13,653 under the old rule, with matched and unmatched counts logged. |
| 3 | **Partly.** The revenue share removed (2.4 %) and the number of affected invoices are now printed, and the text calls deletion a judgement call. Aggregating instead of deleting was not adopted: baskets are binary, so the rules are identical either way, and monetary changes by ≤ 2.4 %. |
| 4 | **Fixed.** See Selection 2. |
| 5 | **Fixed.** The highest unit prices are listed: real furniture (a £295 kitchen cabinet). |
| 6 | **Fixed.** The string "nan" descriptions are now treated as missing. |
| 7 | **Not changed.** The log table already gives the count behind each rule. |

## Transformation
| # | Response |
|---|---|
| 1 | **Fixed (tested).** An alternative clustering on recency + one averaged volume factor was run (5.2). It agrees with the main clusters at ARI 0.73 and predicts next year no better (AUC 0.745 vs 0.739), so RFM is kept. |
| 2 | **Partly.** Tenure is used to label "new" customers (S3: 56 % joined in the last 90 days). Rates per active month were not added. The deployed segmentation uses the same 12-month window, so the window effect is the same in validation and in use. |
| 3 | **Partly.** The share of large-basket customers is reported per segment. No separate wholesaler segment emerges, and with ≤ 8.4 % per segment none was forced. |
| 4 | **Partly.** The log-recency choice is justified by the tertile labels and the next-year separation. A rank-scaled variant was not run. |
| 5 | **Fixed.** The root cause was a plotting bug in the original execution environment (figures were not closed). Every chart now has its own axes and `savefig` closes it. A log-log rank-support plot with the 1 % line was added. |
| 6 | **Fixed.** The basket-size distribution is printed (median 15, 99th percentile 177). |

## Data mining
| # | Response |
|---|---|
| 1 | **Fixed.** A threshold grid (support 0.5 / 1 / 2 % × lift 2 / 3 / 5) reports rules, itemsets, the share holding next year, products covered and the share of next-year baskets reached. 1 % is justified as the stability/coverage middle. |
| 2 | **Fixed.** "Natural segments" is reworded as "a useful partition of a continuum". k = 4 is justified by best-in-range silhouette **and** out-of-bag stability for every k (k = 4: 0.92; worst resample drops to 0.55 from k = 5). |
| 3 | **Fixed.** RFM-score quartiles, monetary tertiles and a continuous RFM score were compared on next-year AUC and Spearman. **The clusters lose to the RFM score (0.739 vs 0.765).** This is reported as a failed pass mark, and the conclusion is rewritten. |
| 4 | **Fixed.** 20 out-of-bag resamples for each k from 2 to 10, and the shared-`projector` bug fixed with `clone()`. |
| 5 | **Fixed.** Distinct itemsets are reported (598 rules from 325 itemsets). Examples are shown one direction per pair. |
| 6 | **Fixed.** The `except TypeError` fallback was removed. A version assert was added (mlxtend ≥ 0.23 has `num_itemsets`). |

## Interpretation / Evaluation
| # | Response |
|---|---|
| 1 | **Fixed.** `holds_strict` now includes support. **59 %** hold (not 86 %); conf + lift only is 85 %, reported separately. The headline, README and app label were corrected. |
| 2 | **Fixed.** See Data mining 3. The segments are called valid as descriptions and beaten as predictors. |
| 3 | **Fixed.** The classifier was improved with product-type nouns (bags, cake cases, cups …), and 40 sampled itemsets were hand-labelled: precision 95 % for variants, **70 %** for cross-product, so about 43 of 62 cross-product itemsets are genuine. Novelty is argued against the retailer's own collections ("confirmation with numbers"). The S3 claim was removed. |
| 4 | **Fixed.** Shares are given against returning-customer revenue **and** against all next-year revenue (Champions 66 % / 47 %). "396" is replaced by 498→352, explained in Step 9. |
| 5 | **Fixed.** The rule-validity figure is coloured by the corrected strict test and has a lift panel. The persistence baseline: near-miss rules reach the thresholds only 12 % of the time. |
| 6 | **Fixed.** The deployed segmentation is the discovery model scored on the latest 12 months. Its profiles are re-checked against the discovery cut-offs (all four agree, with similar sizes), which re-tests the structure on new data. |
| 7 | **Fixed.** Revenue at stake per segment (S2 £1.37 M next year) and basket coverage (69 %) are given. |
| 8 | **Fixed.** Labels show the share of members in the majority tertile (S2: high-spend 55 %). One real loop back to Transformation was run (Transformation 1). |

## Acting on the knowledge
| # | Response |
|---|---|
| 1 | **Fixed.** The app ships the **validated** 12-month segmenter, scored on each customer's last 12 months. The Hungarian centroid mapping was removed. Deployed profiles are shown in the Overview tab, and the label check passes for all four segments (S2 median recency 57 days, S3 median tenure 73 days). |
| 2 | **Fixed.** The new-customer inputs are labelled "last 12 months", matching the model's window. |
| 3 | **Fixed.** Only validated rules by default, and the product list holds only products that have a rule in the current filter. `rule_type` is exported, with a "hide variants" filter. The text no longer says "now validated" for re-mined statistics. |
| 4 | **Fixed.** Staff enter the whole basket; a rule fires only if all its antecedent items are present. |
| 5 | **Fixed.** Maintenance plan: rolling 12-month window, quarterly re-mine validated on the next quarter, drift alerts (persistence < 50 %, segment size ± 25 %), an owner, and an A/B hold-out design per segment. |
| 6 | **Partly.** pandas is pinned (`streamlit>=1.40`), the S2 action trigger is moved to 90 days, and a data-governance note was added. The app URL depends on the author's deployment, which follows this revision. |
