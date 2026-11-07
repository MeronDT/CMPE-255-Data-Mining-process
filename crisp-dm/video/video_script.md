# Video script: CRISP-DM, hotel booking cancellations (about 12 minutes)

Each segment has **SHOW** (what is on screen and what to click) and **SAY** (narration you can read as written; about 140 words a minute). Section names match the notebook headings, so the Colab *Table of contents* panel (left sidebar, ☰ icon) is the fastest way to jump.

## Before you record

- The repo is **public** (the Colab badge and the article images need it).
- The Streamlit app is deployed (entry point `crisp-dm/artifacts/app/app.py`, Python 3.13), and you have `crisp-dm/artifacts/app/sample_bookings.csv` downloaded.
- Open three browser tabs:
  1. the notebook in Colab (README → *Open in Colab*);
  2. the GitHub repo at `crisp-dm/`;
  3. the app.
- The saved outputs are already in the notebook. If you'd like to show it running, do *Runtime → Run all* well before recording (it takes several minutes).
- If you re-run in Colab, the last digit of some numbers can differ slightly because Colab's library versions differ. Narrate from the saved outputs, which match this script, the report and the article.
- Record at 1080p with the browser zoomed to about 125 %. Collapse the code cells you don't talk about (*View → Collapse sections* or the arrow next to each heading).

---

### 1. Introduction (0:00–0:40)

**SHOW:** Colab, title cell at the top of the notebook.

**SAY:**
> Hi, I'm Meron Tesfandrias, and this is my CRISP-DM project for CMPE 255. Over two years, thirty-seven percent of all bookings at two Portuguese hotels were cancelled. Hotels protect themselves by overbooking: they sell more rooms than they have, usually using a rule of thumb like "about forty percent of tonight's bookings won't show". If the rule is too generous, a guest gets walked to another hotel. If it's too cautious, rooms stay empty. My question: can the bookings themselves tell us how many cancellations to expect each night? I'll go through all six CRISP-DM phases in this notebook and finish with the deployed app.

### 2. How the notebook follows CRISP-DM (0:40–1:20)

**SHOW:** Open the *Table of contents* panel and scroll slowly: Phase → task (1.1, 1.2 …) → "Output:" headings. Then click any "🔍 Critic review" heading and show its table for a second.

**SAY:**
> CRISP-DM has six phases, from business understanding to deployment. What people often skip is that every phase is split into generic tasks, and every task has named outputs. I used those outputs as the headings of the notebook, so you can see in the table of contents that none was skipped. At the end of every phase there's a critic review. Each phase was critiqued three times by an expert-persona reviewer. The first round was in my drafting session, and rounds two and three were fresh, independent sessions that saw only the finished notebook. Each table lists what the critic found and what I changed.

### 3. Phase 1: Business understanding (1:20–2:50)

**SHOW:**
1. Phase 1 → **Output: Business objectives** and **Business success criteria**.
2. Scroll to **Output: Costs and benefits** (the cost table).
3. Then **1.3 → Output: Data mining success criteria** (AUC 0.85, precision 0.75, recall 0.50).

**SAY:**
> The business objective is one decision: how many extra rooms to sell each night. CRISP-DM asks for a cost-benefit assessment before touching the data, and I got that wrong in my first draft. An overbooked room only gets re-sold, and a guest only gets walked, if the hotel actually fills up that night. I assumed that happens half the time, and in my first version I applied that to the walk cost but not to the re-sale. Done consistently, a correct call is worth fifty euros and a wrong one costs a hundred. That's a two-to-one ratio, and it sets the decision threshold later.
>
> The second lesson: the benchmark is what the hotel does today, its rule of thumb. It isn't "flag every booking", which loses money by construction. And I translated the goals into data mining criteria for a per-booking classifier: ROC-AUC at least 0.85, precision at least 0.75, recall at least 0.50.

### 4. Phase 2: Data understanding (2:50–5:00)

**SHOW:**
1. **2.1 Collect initial data**: the two source files and the format problems.
2. **2.3 Explore data**: the cancellation-rate charts by deposit type, segment and month.
3. The Non Refund / duplicate-rows output (first table under the "Investigate the 'Non Refund' anomaly" cell).
4. **Pause here:** the second table in the same output, rows = market segment, columns = Canceled / Check-Out / No-Show. Point at the **Groups** row: 0.968, 0.288, 0.973.
5. **2.4 Verify data quality → Output: Data quality report**.

**SAY:**
> The data is public: 119,390 bookings from a resort hotel and a city hotel, July 2015 to August 2017. It came as two files with inconsistent formats, with "NULL" stored as text and padded strings. That's routine. Three findings weren't.
>
> First, non-refundable deposits cancel 99.4 percent of the time. That's the opposite of what a non-refundable deposit should do. Almost all of them are group or tour-operator bookings, and 98 percent are exact duplicate rows. They look like block allocations being released, not guests losing their money.
>
> Second, some columns are recorded after the fact. `reservation_status` literally says "Canceled". And not one of the 7,416 bookings with a parking space was cancelled, because parking is recorded on arrival. Both are excluded.
>
> The third is the important one. Nationality was the model's strongest input: 62 percent of cancelled bookings are Portuguese, against 28 percent of arrived ones. A reviewer asked whether nationality is filled in by default and only corrected at check-in. This table tests that. Within each market segment, bookings that never reached the front desk, so both cancellations *and* no-shows, are Portuguese far more often than bookings that checked out. For groups it's 97 and 97 percent, against 29. A real nationality effect wouldn't make no-shows look like cancellations. A default value would. So `country` is excluded too.

### 5. Phase 3: Data preparation (5:00–6:00)

**SHOW:**
1. **3.1 Select data → Output: Rationale for inclusion/exclusion** (the exclusion table).
2. **3.3 Construct data** (the score-code cell that writes `booking_features.py`).
3. **3.5 Format data**: the time-based split printout.

**SAY:**
> Every excluded column has a written reason in this table: leaks, IDs, and fields that aren't known at booking time. About 27 percent of rows are exact duplicates. With no booking ID they can't be proven to be errors, and they're mostly multi-room group bookings, so I kept them. That choice matters in the next phase.
>
> The feature construction is written as score code, a small module called `booking_features.py`. The model pipeline calls it first, so the deployed app accepts the 24 raw fields a booking system exports. The split is by time. Everything arriving before 23 April 2017 is for training, and the latest 20 percent of arrivals are the test period, because a deployed model always predicts the future.

### 6. Phase 4: Modeling (6:00–7:30)

**SHOW:**
1. **4.2 Generate test design**: the fold dates printout (fold 1 … fold 5).
2. **4.3 Build model**: the cross-validation table (baselines at the top: 0.50, 0.66, 0.69; then models; Random Forest 0.844) and the bar chart below it.
3. **4.4 → Output: Revised parameter settings**: point at "0.956".

**SAY:**
> Here's the validation trap. My first version used ordinary shuffled cross-validation and got ROC-AUC 0.956. On the later test period it scored 0.868. Shuffling mixes future bookings into training, and identical duplicate rows land on both sides of a fold, so the model is rewarded for recognising bookings it has already seen. So I switched to time-series cross-validation with fold edges on date boundaries. Each fold trains on earlier arrivals and validates on the next block.
>
> Three baselines keep the comparison honest: the majority class, lead time alone, and the hotel's simplest rule, flag every non-refundable booking. Logistic regression, a random forest and gradient boosting got the same tuning budget. Without nationality, the random forest wins with a cross-validated AUC of 0.844, ahead on most folds.

### 7. Phase 5: Evaluation (7:30–10:00)

**SHOW:**
1. **5.1 Evaluate results**: the criteria table with confidence intervals (AUC 0.827 not met, precision 0.831 met, recall 0.471 not met).
2. The four-panel figure (confusion matrix, ROC, precision-recall, calibration).
3. The **business impact** output: scroll to the per-night policy table (rule of thumb €13,429; counting flags €11,538; model expected cancellations €16,804).
4. **Output: Approved models**, then **5.3 → Output: Decision**.
5. Optional: the sensitivity table (approved set 0.863 vs "+ country" 0.897).

**SAY:**
> Phase 5 asks whether the results meet the business criteria, and I want to be honest. As a per-booking classifier, the model misses two of its three targets. Test AUC is 0.827 against a target of 0.85. Recall is 0.47 against 0.50. Precision, at 0.83, is the only one met. Outside the non-refundable blocks it's weaker still. Once the nationality leak is gone, telling individual guests apart is hard. That sensitivity table shows the leak was worth about 0.034 AUC.
>
> But the hotel doesn't decide per booking. It decides how many extra rooms to sell each night, and on the same night missed cancellations and false alarms cancel out. So I added up the calibrated probabilities of each night's bookings to get an expected number of cancellations, and simulated every policy over the 262 hotel-nights in the test period.
>
> The hotel's current rule earns 13,429 euros per thousand bookings and is off by 9.4 rooms a night on average. Counting the model's flagged bookings does *worse*: 11,538. The model's expected cancellations earn 16,804 euros and are off by only 4.6 rooms. That's about 3,400 euros more per thousand bookings than today's rule, with a 95 percent confidence interval of 2,400 to 4,300, entirely above zero.
>
> So the CRISP-DM output here is a decision, not more tuning. The model is approved for the nightly overbooking forecast, as a randomised pilot. The individual flags are not approved for decisions. They're only a watch list.

### 8. Phase 6: Deployment, in the app (10:00–11:15)

**SHOW:**
1. Switch to the app tab. Point at the caption (model type, test ROC-AUC).
2. Tab **Score the day's bookings (CSV)** → upload `sample_bookings.csv`.
3. Show **Recommended overbooking per arrival date**, then the **Bookings** table, then **Download scored bookings**.
4. Tab **Score one booking**: change *deposit type* or *lead time*, click **Estimate cancellation risk**, and show the probability.

**SAY:**
> This is the deployed Streamlit app. A revenue manager uploads the day's booking file in the hotel's own export format. For each hotel and arrival date, it returns the recommended number of extra rooms to sell. That's the sum of the probabilities, the thing we actually validated. Below that is a watch list of bookings, and the scored file can be downloaded. If a category value appears that the model has never seen, the app warns about it instead of failing silently.
>
> I can also score a single booking. Notice there's no nationality field, and the app says guests are never contacted based on this score.

### 9. Monitoring and wrap-up (11:15–12:00)

**SHOW:**
1. Notebook **6.2 → Output: Monitoring and maintenance plan** (the PSI output).
2. Then the GitHub repo tab: `critiques/`, `report/`, `article/`.

**SAY:**
> The pilot is randomised by arrival date: on half the dates the model sets the overbooking level, and on the other half the current rule does. Monitoring uses the population stability index, compares each month with the same month last year because the data is seasonal, and has alarms that don't need outcomes, since those only arrive after the stay.
>
> What did CRISP-DM buy me? Pricing the real decision turned a failing classifier into a forecast that beats the incumbent. Asking "is this known at booking time?", and testing it, removed the most predictive field. And honest validation moved the AUC from 0.956, to 0.868, to 0.827. Each step down was a step closer to what the hotel would actually get. The critiques, the HTML and PDF report, and the Medium article are all in this repo. Thanks for watching.
