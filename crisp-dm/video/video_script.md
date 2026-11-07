# Video walkthrough script — CRISP-DM: hotel booking cancellations (≈ 12 min)

**Setup before recording:** the notebook open in Colab after *Run all* (outputs visible), the GitHub repo in a second tab, the deployed app in a third. Screen-record at 1080p; zoom the browser to ~125 %.

| Time | On screen | What to say (talking points) |
|---|---|---|
| 0:00–0:45 | Title cell | The problem: 37 % of bookings at two Portuguese hotels are cancelled. Hotels overbook by a rule of thumb; too much and guests get walked, too little and rooms stay empty. Goal: forecast each night's cancellations from the bookings on the books. |
| 0:45–1:30 | CRISP-DM phase table | Six phases, each split into generic tasks with required outputs; the notebook has a heading for every output. CRISP-DM starts and ends with the business. |
| 1:30–3:00 | **Phase 1**: objectives, success criteria, cost table | One decision: the nightly overbooking level. Both outcomes depend on the hotel filling up (× 50 %), so a right call is +€50 and a wrong one −€100. The benchmark is the hotel's current rule, not "flag everything". |
| 3:00–5:15 | **Phase 2**: format problems, rate charts, like-for-like drift, Non Refund table, **country test**, leakage screens | Messy files. Non Refund cancels 99 %: 98 % duplicate group blocks. `reservation_status` and parking leak. **The key moment:** the within-segment table where no-shows and cancellations are ~95 % Portuguese vs ~25 % of check-outs, so nationality was defaulted and is excluded. |
| 5:15–6:15 | **Phase 3**: exclusion log, score-code cell, split | Every exclusion has a reason. The model takes the 24 raw booking-system fields through `booking_features.py`. Time-based split. |
| 6:15–7:45 | **Phase 4**: fold dates, CV table, tuning, paired comparison | The validation trap: shuffled CV said 0.956, the future said 0.868. Date-aligned time-series folds; three baselines incl. the Non Refund rule; the random forest wins (0.844 without nationality). |
| 7:45–10:15 | **Phase 5**: criteria table with CIs, Non Refund-free row, booking-date bands, **per-night policy table** | Be honest: as a per-booking classifier it misses AUC (0.827) and recall (0.47). Then the turn: summed per night, its expected cancellations beat the hotel's rule by €3,400 per 1,000 bookings (CI €2,400–€4,300) with half the error (4.6 vs 9.4 rooms). Counting flags is *worse*. Decision: approve the nightly forecast, not the flags. |
| 10:15–11:15 | The deployed app | Upload `sample_bookings.csv`: recommended extra rooms per arrival date. Score one booking; point out there is no nationality field and guests are never contacted. |
| 11:15–12:00 | Phase 6 monitoring + repo | Randomised pilot by arrival date; PSI with same-month comparison; alarm responses that need no outcomes; the three critique rounds; lessons learned. |
