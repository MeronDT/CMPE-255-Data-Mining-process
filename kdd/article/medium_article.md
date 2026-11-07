# From a Million Receipts to Knowledge: A KDD Walkthrough on Online Retail Data

*Customer segments and "bought together" rules, discovered in one year and tested on the next.*

`<cover image: artifacts/figures/evaluation_segments.png>`

Most data mining tutorials end when the algorithm runs. The **Knowledge Discovery in Databases (KDD)** process, as defined by Fayyad, Piatetsky-Shapiro and Smyth in 1996, insists on more: a pattern only counts as *knowledge* if it is **valid, novel, potentially useful and ultimately understandable**. In this project I took that definition literally, and it changed the results.

## The data and the goals

The UCI *Online Retail II* dataset holds every transaction line of a UK online giftware retailer from December 2009 to December 2011: **1,067,371 lines**, about 5,900 customers (many of them wholesalers), about 4,700 products, and a sharp Christmas peak.

KDD starts by understanding the domain and the end users. Here there are two:

- **Marketing** wants to know *what kinds of customers we have*, so goal 1 is customer segmentation.
- **Merchandising** wants to sell more per order, so goal 2 is product associations.

Before mining anything, I wrote down how each of Fayyad's four criteria would be *tested*. The most important decision was this one: **valid means still true the following year.** Patterns would be mined on December 2009 – November 2010 and checked on December 2010 – December 2011.

## Selection and preprocessing: where the real work was

The data comes as an Excel file with **two sheets**, one per year. Pandas reads only the first by default, which quietly loses half the data. After loading both sheets, preprocessing removed:

- 19,494 **cancellation** lines (invoice numbers starting with "C"), kept aside to compute each customer's return rate;
- 13,653 purchases that were later **cancelled in full**;
- 4,320 lines that aren't products: postage, bank charges, Amazon fees, manual adjustments, tests;
- 6,111 lines with zero or negative quantity or price (stock write-offs and corrections);
- 33,203 exact **duplicate** lines.

That left 990,590 clean lines. One decision deserves a mention: 23 % of lines have no customer ID. They're useless for segmentation but perfectly good *baskets*, so they were kept for the association rules.

## Transformation: two views of the same data

- **A customer table.** For each customer: **R**ecency, **F**requency, **M**onetary value, plus tenure and return rate. RFM spans several orders of magnitude (1 to 172 orders, £2 to £319k), so it was log-transformed and standardised before clustering.
- **A basket matrix.** One row per invoice, one column per product. Products in fewer than 1 % of baskets can never be part of a frequent itemset (the Apriori property), so removing them shrank 4,047 products to 717 without losing a single possible rule.

## Data mining

**Segments:** K-means on the log-RFM table. Silhouette scores favoured k = 2, but two segments ("good" and "bad") is too coarse to act on. Within 3–6, k = 4 scored best. To check the segments weren't an artefact, I re-ran the clustering on ten bootstrap resamples: they agreed with the original at an adjusted Rand index of **0.94**.

**Rules:** FP-Growth with support ≥ 1 %, confidence ≥ 40 % and lift ≥ 3 found **579 rules** in a few seconds.

## Interpretation and evaluation: the part most projects skip

### The segments

| Segment | Profile (medians) | Customers | Revenue |
|---|---|---|---|
| **Champions** | ordered 8 days ago, 9 orders, £3,447 | 17 % | **64 %** |
| **Loyal but cooling** | 4 orders, £1,293, last order 57 days ago | 28 % | 25 % |
| **New customers** | 2 orders, £492, only ~2 months' tenure | 20 % | 6 % |
| **Lapsed one-off buyers** | 1 order, £259, 166 days ago | 35 % | 6 % |

**Are they valid?** The segments were built only from 2009-10 data, yet they predict 2010-11 behaviour almost perfectly:

| | Champions | Loyal but cooling | New | Lapsed one-off |
|---|---|---|---|---|
| Bought again next year | **96 %** | 74 % | 66 % | 40 % |
| Share of next year's revenue | 67 % | 21 % | 7 % | 5 % |

The segments are real. They also point at the money: "Loyal but cooling" customers still delivered a fifth of next year's revenue, so reactivating them is worth far more than chasing lapsed buyers.

### The rules

**Valid?** Re-measured on the following year's baskets, **86 %** of rules still met the *full* thresholds (lift ≥ 3, confidence ≥ 40 %), and the median rule's lift changed by just +5 %.

**Novel?** Here KDD's criterion bites. Most strong rules are obvious: *pink regency teacup → green regency teacup*, children's garden trowel → children's garden fork. They're true, but a merchandiser already knows them. Filtering out rules whose products differ only in colour or design (425 of the 579) left 154 cross-product rules, and the genuinely interesting ones among them:

- **Matching-design sets across product types:** red spotty paper napkins + cups → red spotty paper plates (84 % confidence, 36× lift, still 33× the next year); polkadot bowls → polkadot cups.
- **Themed bundles:** vintage Christmas napkins → Christmas cake cases.

The insight: customers shop by *collection*, not just by product type. That's an argument for "shop the collection" pages and bundles.

## The critic loop: three things I got wrong

I had Claude review each stage as a KDD expert. The first evaluation had three real problems, all fixed:

1. **Misleading labels.** A median split called a 2-order customer "frequent". Labelling against tertiles revealed that segment is actually *new* customers (median tenure 57 days).
2. **A too-lenient validity test.** I had halved the thresholds for next year, so 99 % of rules "held". With the original thresholds it's 86 %, a more honest number.
3. **A naive novelty test.** Word-matching called *key fob "garage"* and *key fob "shed"* different categories. The fix compares product types after stripping colours and designs.

## Acting on the knowledge

KDD's last step is to act. The validated segments, each with a recommended action, and the 396 strictly validated rules are packaged in a Streamlit app for marketing staff. Pick a product to see what to recommend, look up a customer's segment, or classify a new customer from three numbers. `<app link>`

Because the product range and seasonality change every year (only 717 of 4,047 products reach 1 % of baskets), segments and rules should be re-mined quarterly and re-validated before each Christmas season.

## What KDD added

Compared with CRISP-DM's business focus and SEMMA's modeling focus, KDD's distinctive contribution is its definition of **knowledge**. Asking "is this valid, novel, useful and understandable?", and testing each one, turned 579 rules into a short list a merchandiser would actually use, and turned four clusters into segments with proven predictive value.

*Code, notebook, figures and app: [github.com/MeronDT/CMPE-255-Data-Mining-process](https://github.com/MeronDT/CMPE-255-Data-Mining-process). Video walkthrough: `<YouTube link>`.*

*AI disclosure: built with help from Claude (Anthropic) for code, drafting and expert critique; all results were produced by running the code.*
