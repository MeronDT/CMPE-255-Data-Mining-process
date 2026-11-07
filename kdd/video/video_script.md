# Video script: KDD, customer segments and product associations (about 11 minutes)

Each segment has **SHOW** (what is on screen and what to click) and **SAY** (narration you can read as written; about 140 words a minute). Section names match the notebook headings, so the Colab *Table of contents* panel (left sidebar, ☰ icon) is the fastest way to jump.

## Before you record

- The repo is **public** (the Colab badge and the article images need it).
- The Streamlit app is deployed (entry point `kdd/artifacts/app/app.py`, Python 3.13).
- Open three browser tabs:
  1. the notebook in Colab (README → *Open in Colab*);
  2. the GitHub repo at `kdd/`;
  3. the app.
- The saved outputs are already in the notebook. *Run all* downloads and reads a 45 MB Excel file, so if you want to show it running, start it well before recording.
- If you re-run in Colab, the last digit of some numbers can differ slightly because Colab's library versions differ. Narrate from the saved outputs, which match this script, the report and the article.
- Record at 1080p with the browser zoomed to about 125 %. Collapse the code cells you don't talk about.

---

### 1. Introduction (0:00–0:45)

**SHOW:** Colab, title cell.

**SAY:**
> Hi, I'm Meron Tesfandrias, and this is my KDD project for CMPE 255. The data is two years of transactions from a UK online giftware retailer: about a million lines, 5,900 customers, many of them wholesalers, and 4,700 products. I'm answering two questions. For marketing: what kinds of customers do we have? And for merchandising: which products are bought together? Most tutorials stop when the algorithm runs. KDD doesn't, and that's what this video is about.

### 2. KDD and how the patterns will be judged (0:45–1:45)

**SHOW:**
1. The KDD steps table in the title cell.
2. **Stage 0 → How the patterns will be evaluated (Fayyad's four criteria)**: the criteria / test / pass-mark table.
3. Briefly open the *Table of contents* to show the "🔍 Critic review" heading at the end of each stage.

**SAY:**
> KDD, Knowledge Discovery in Databases, comes from Fayyad, Piatetsky-Shapiro and Smyth in 1996. Its key idea is that a pattern only counts as knowledge if it's valid, novel, potentially useful, and understandable. I took that literally. Before mining anything, I wrote down how each criterion would be tested and what would count as a pass. The most important decision: valid means still true the following year. Patterns are mined on December 2009 to November 2010 and re-tested on December 2010 to November 2011, two equal twelve-month windows. Every stage also ends with a critic review. An expert-persona reviewer critiqued each stage three times, the last two rounds in fresh, independent sessions.

### 3. Selection (1:45–2:45)

**SHOW:** **Stage 1 — Selection**: the sheet row counts and the overlap message (22,523 lines dropped), then the monthly revenue chart, then **Target data set**.

**SAY:**
> The data comes as an Excel file with two sheets, one per year. Pandas reads only the first by default, which quietly loses half the data. Reading both has its own trap, which a reviewer caught in round three: the sheets overlap. The first runs to the 9th of December 2010 and the second starts on the 1st, so 22,523 lines were in the data twice. They're dropped when the file is loaded. The monthly revenue chart shows a strong fourth-quarter peak, which is why both windows are a full twelve months. The last, partial December is marked and left out.

### 4. Preprocessing (2:45–4:00)

**SHOW:** **Stage 2 — Preprocessing**: the cleaning log table (cancellations, matched purchases, non-product codes, invalid prices, duplicates → 997,638), then **Preprocessing decisions**.

**SAY:**
> Cleaning removed five kinds of lines. First, 19,165 cancellation lines, the invoices starting with C. Second, 5,825 purchases that were cancelled in full, each matched to one earlier purchase in the same year. My first version matched across years and ignored time order, which quietly let next year's data change this year's. Third, postage, bank charges and manual adjustments, which aren't products. Fourth, zero or negative quantities and prices. And fifth, 11,622 exact duplicates, only 0.3 percent of revenue. That leaves 997,638 clean lines. About 23 percent of lines have no customer ID. They're useless for segmentation but perfectly good baskets, so they're kept for the association rules.

### 5. Transformation (4:00–5:00)

**SHOW:**
1. **3.1 Customer table**: the RFM distribution figure.
2. **3.2 Basket matrix**: the product-support long-tail plot and the line "4,047 → 714 products".

**SAY:**
> The same data becomes two tables. The customer table has recency, frequency and monetary value, plus tenure and return rate. RFM spans several orders of magnitude, from 1 to 174 orders and from 2 to 319,000 pounds, so it's log-transformed and standardised before K-means, which is distance-based. The basket matrix has one row per invoice and one column per product. A product in fewer than one percent of baskets can never be part of a frequent itemset, by the Apriori property. So dropping those shrinks 4,047 products to 714 without losing a single rule at that support.

### 6. Data mining (5:00–6:15)

**SHOW:**
1. **4.1 Customer segmentation**: the k-selection table/plot (silhouette and bootstrap stability for k = 2–6).
2. **4.2 Association rules**: the FP-Growth output (598 rules from 325 itemsets).

**SAY:**
> For segments I ran K-means on the log-RFM table. The silhouette score favoured two clusters, but that just splits "active" from "not", which is too coarse to act on. Between three and six, four clusters had both the best silhouette, 0.34, and the best stability: refit on bootstrap resamples, they agreed on held-out customers with an adjusted Rand index of 0.92. A silhouette of 0.34 tells you these are a useful partition of a continuum, not natural clusters, and I say that in the report.
>
> For rules I used FP-Growth with support of at least one percent, confidence of at least 40 percent and lift of at least three. That gives 598 rules from 325 associations, since most pairs appear in both directions.

### 7. Interpretation and evaluation (6:15–9:15)

**SHOW:**
1. **5.1 Segment profiles**: the profile table and the segments figure (share of customers vs revenue).
2. **5.2 Are the segments valid?**: next-year activity by segment (96 / 74 / 65 / 40 %), then the AUC comparison (RFM quartiles 0.765 vs K-means 0.739).
3. **5.3 Are the rules valid?**: the strict-hold result (58.9 % vs 11.8 % near-miss) and the confidence/lift scatter, then the threshold grid.
4. **5.4 Are the rules novel?**: the variant vs cross-product table, the cross-product rule list (napkins + cups → plates at the top), then the audit output.
5. **Evaluation against the Stage 0 criteria** table.

**SAY:**
> Here's where KDD earns its name. The four segments are understandable. Champions are 17 percent of customers and 64 percent of revenue. Then there are loyal-but-cooling customers, new customers, and lapsed one-off buyers, who are 35 percent of customers but only 6 percent of revenue.
>
> Are they valid? They were built only from the first year, and they line up with the second year exactly in order: 96 percent of Champions bought again, against 74, 65 and 40 percent for the others. But do they beat the standard tool? No. A plain RFM score, cut into quartiles, ranks next-year activity better: AUC 0.765 against 0.739, and the gap's confidence interval excludes zero. My pass mark was "at least as good as an RFM score", so the clusters fail it. They still earn their place as labels with distinct actions, and the app shows each customer's RFM score beside the segment.
>
> The rules. My first draft said 86 percent of rules meet the thresholds again the next year. A reviewer pointed out that I'd re-checked confidence and lift but forgot support. With all three, the answer is 59 percent. To read that number you need a baseline: rules that just missed the thresholds in year one reach them in year two only 12 percent of the time. So the thresholds really do pick stable patterns.
>
> Novelty is where the criterion bites. Most strong rules are obvious, like a pink Regency teacup leading to the green one. True, but a merchandiser already knows that. I classified rules as same-product variants or cross-product rules, and hand-audited 40 of them. That suggests about 57 of the 325 associations are genuine cross-sells, like red spotty napkins and cups leading to the matching plates: 84 percent confidence and 36 times lift. The sobering part: only about a quarter of the cross-product associations hold up the next year. So only the validated ones get recommended.
>
> This table sums it up. One criterion failed: segments versus the RFM score. One is only partly met: novelty. And I'm reporting both.

### 8. Acting on the knowledge, in the app (9:15–10:15)

**SHOW:**
1. App tab **Product recommendations**. Leave "Only rules that met … again in the following year" ticked.
2. Clear the default product and pick **SET/20 RED RETROSPOT PAPER NAPKINS** and **SET/6 RED SPOTTY PAPER CUPS** → the suggestion is **SET/6 RED SPOTTY PAPER PLATES**. Then tick **Hide colour/design variants**.
3. Tab **Customer lookup**: the default ID 12347 is a Champion; show the action and the RFM score line.
4. Tab **Segment a customer**: enter 200 days / 1 order / £200 → *Lapsed one-off buyers*.
5. Tab **Segments overview**: the profile table and the export button.

**SAY:**
> KDD's last step is to act on the knowledge. The app ships the validated model, the same twelve-month segmenter, applied to each customer's most recent twelve months, and a check in the notebook confirms that every segment still matches its name.
>
> In the recommendations tab, I build a basket. With napkins and cups in it, the app suggests the matching plates. These rules are re-mined on both years for current products, which is why the confidence here is a little different from the notebook, and only rules that were validated on the following year are shown. A rule fires only when all of its "if" products are in the basket. I can also hide the colour variants to see only the cross-sells.
>
> Customer lookup gives the segment, the recommended action and the RFM score. A new customer can be segmented from three numbers. And marketing can export any segment's list, ranked by RFM score, for a campaign.

### 9. Wrap-up (10:15–11:00)

**SHOW:** GitHub repo tab: `critiques/round_2.md` (scroll to the "app showed the wrong segments" finding), then `report/`, `article/`.

**SAY:**
> The critique rounds changed the results, not just the wording. Round two found that cleaning leaked across the year split, that the validity test skipped support, and that the app showed the wrong segments: it had refit the model on two years and mapped the old names onto new clusters without checking. Round three found the sheet overlap and a coverage number that counted rules that didn't actually fire.
>
> Compared with CRISP-DM's business focus and SEMMA's modeling focus, KDD's contribution is its definition of knowledge. Testing each criterion separately exposed that my segments don't beat an RFM score, that most novel rules are unstable, and that the honest validity figure is 59 percent, not 86. Next steps would be re-mining quarterly on a rolling twelve-month window and A/B-testing the segment actions. The report, the critiques and the Medium article are all in the repo. Thanks for watching.
