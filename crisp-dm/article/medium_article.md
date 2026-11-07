# Will This Guest Actually Show Up? Predicting Hotel Cancellations with CRISP-DM

*How a 25-year-old process model kept a machine learning project honest: a cost model, a validation trap, and a leakage question only the business can answer.*

`<cover image: artifacts/figures/eda_rates_categorical.png>`

Over two years, **37 % of all bookings** at two Portuguese hotels were cancelled — 42 % at the city hotel. Every late cancellation is a room that probably stays empty. The usual defence, overbooking by rule of thumb, has its own price: when more guests show up than expected, someone gets "walked" to another hotel.

What if each booking came with a risk score the moment it was made?

I built that model following **CRISP-DM** — the Cross-Industry Standard Process for Data Mining. Its six phases are well known. Less well known is that each phase has specific *tasks*, each with required *outputs*. Producing all of them is tedious, and it's exactly what stopped this project from fooling itself.

## Phase 1 — Business understanding: put a price on mistakes

The data is public (António, de Almeida & Nunes, *Data in Brief*, 2019): **119,390 bookings** for a resort hotel and a city hotel, July 2015 – August 2017.

Before touching the data, CRISP-DM asks for **business success criteria** and a **cost/benefit assessment**. The average booking is worth about **€358** (€101.8 per night × 3.43 nights). I assumed:

- catching a cancellation in time (deposit request, re-selling the room) is worth **+€100**;
- wrongly flagging a guest who then shows up, and overbooking against them, costs **−€100** (a replacement room, a taxi, an annoyed guest);
- missing a cancellation costs €0 extra — that's today's situation.

The model criteria were fixed up front too: **ROC-AUC ≥ 0.85**, and **precision ≥ 0.75**, because if most flags are wrong, staff will stop reading them.

## Phase 2 — Data understanding: two surprises

The data came as two files with inconsistent formats: "NULL" stored as text, padded strings, a column that was an integer in one file and a decimal in the other. Fixing that was routine. Two findings were not.

**Surprise 1: non-refundable deposits cancel 99.4 % of the time.** That's the opposite of what a non-refundable deposit should do. Profiling those 14,587 bookings showed they're 97 % Portuguese, 97 % group or tour-operator bookings, with zero special requests and a 183-day median lead time. These look like **block allocations released by tour operators**, not individual guests losing their money. It's a data-quality question for the hotel, not a behavioural insight.

**Surprise 2: some columns know the future.** A small leakage detector flagged attributes where a large group of bookings has a near-certain outcome. `reservation_status` literally contains "Canceled". The parking column is more subtle: **none** of the 7,416 bookings that requested parking were cancelled, which means parking is almost certainly recorded on arrival. Both were excluded. The rule for every column was a single question: *is this known when the booking is made?*

Otherwise the expected patterns showed up. Cancellation rises steadily with lead time, from 10 % for last-week bookings to 68 % for bookings made more than a year ahead. Groups and online travel agents cancel most; direct and corporate bookings least.

`<image: eda_month_leadtime.png>`

## Phase 3 — Data preparation: duplicates and a time-based split

Roughly 27 % of rows are exact duplicates. With no booking ID, there's no way to prove they're errors. Identical rows are plausibly separate rooms in one group booking, so I kept them. That decision came back to bite in Phase 4.

The data was split **by time**: everything arriving before 23 April 2017 for training, the latest 20 % of arrivals (23,795 bookings) for the final test. A model used in production always predicts bookings that arrive *after* the data it learned from, so the test should mimic that.

## Phase 4 — Modeling: the validation trap

I compared a majority-class baseline, logistic regression, a random forest and gradient boosting.

My first version used ordinary shuffled 5-fold cross-validation. The random forest scored **ROC-AUC 0.956**, which looked excellent. On the later test period it scored **0.868**.

That 0.09 gap is the story of this project. Shuffled folds mix future bookings into training, and the duplicate rows land on both sides of a fold, so the model is rewarded for recognising bookings it has already seen. Neither happens in real use.

Switching to **time-series cross-validation**, where each fold trains on earlier arrivals and validates on the next block, gave:

| Model | Time-series CV ROC-AUC |
|---|---|
| **Random forest** | **0.877** |
| Gradient boosting | 0.870 |
| Logistic regression | 0.861 |
| Majority class | 0.500 |

Now validation (0.877) predicts the test result (0.868). I'd only have caught this by holding out a genuinely later test period.

## Phase 5 — Evaluation: business value, not just accuracy

A random forest outputs a probability, and someone has to choose the cut-off. Using the cost model from Phase 1 on *training* data only, the best threshold was **0.34**, not the default 0.5.

On the untouched test period:

| | Target | Result |
|---|---|---|
| ROC-AUC | ≥ 0.85 | **0.868** ✅ |
| Precision | ≥ 0.75 | **0.772** ✅ |
| Recall | — | 0.683 |

In business terms, the model is worth about **€19,700 per 1,000 bookings** compared with doing nothing. The naive 0.5 threshold gives €17,000, and "flag every booking" *loses* €18,300. The city hotel is easier to predict than the resort (ROC-AUC 0.88 vs 0.86; recall 0.73 vs 0.55).

The strongest drivers are country, deposit type, travel agent, number of special requests and lead time.

### The question the data can't answer

Country is the single most important feature. It's also suspicious: 62 % of cancelled bookings are Portuguese, against 28 % of arrived ones. If a guest's nationality is only confirmed at check-in, cancelled bookings keep a default value, and the model is partly reading the outcome.

So I ran a sensitivity test, again on training data only:

| Attribute set | ROC-AUC (last training block) |
|---|---|
| Approved set | 0.897 |
| Without country | 0.862 |
| Without country, agent and special requests | 0.833 |
| *Plus* the excluded parking column | 0.905 |

Removing country costs 0.035. Adding back parking, which I'd excluded as leaky, would gain less than 0.01, so excluding it was cheap.

CRISP-DM's answer is a **decision**, not more modeling: approve the model *on the condition* that the hotel confirms when country is recorded. If it turns out to be corrected at check-in, the no-country version is the fallback.

## Phase 6 — Deployment and monitoring

The approved model is deployed as a Streamlit app. Staff can score a single booking or upload the day's bookings as a CSV and get each booking's cancellation probability and a flag. A typical booking scores about 54 %. A non-refundable booking made 300 days ahead scores 94 %. `<app link>`

The monitoring plan uses the **Population Stability Index**. One lesson from the demo: seasonal attributes look massively "drifted" when you compare a spring–summer test period with all-season training data. In production, compare each month with the same month last year, and watch the drift of the predicted scores themselves (PSI 0.118 here, a moderate shift).

## What CRISP-DM actually bought me

- **The cost model** turned a threshold into a business decision worth ~15 % more than the default.
- **The "known at booking time?" rule** removed two leaky columns and exposed a third risk.
- **The evaluation and review tasks** forced me to ask whether the validation mimicked real use. It didn't, and fixing it moved the reported performance from fantasy (0.956) to reality (0.868).

The phases sound bureaucratic. In practice, each required output is a question you'd otherwise skip.

*Code, notebook, figures, report and app: [github.com/MeronDT/CMPE-255-Data-Mining-process](https://github.com/MeronDT/CMPE-255-Data-Mining-process). Video walkthrough: `<YouTube link>`.*

*AI disclosure: built with help from Claude (Anthropic) for code, drafting and expert critique; all results were produced by running the code.*
