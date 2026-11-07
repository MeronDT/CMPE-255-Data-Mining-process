# Score code for the hotel-cancellation model: raw booking fields -> model inputs (Phase 3.3 Construct data).
import numpy as np
import pandas as pd

RAW_FIELDS = ["hotel", "lead_time", "arrival_date_month", "arrival_date_week_number", "arrival_date_day_of_month",
              "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children", "babies", "meal",
              "market_segment", "distribution_channel", "is_repeated_guest", "previous_cancellations",
              "previous_bookings_not_canceled", "reserved_room_type", "deposit_type", "agent", "company",
              "days_in_waiting_list", "customer_type", "adr", "total_of_special_requests"]
RAW_CATEGORICAL = ["hotel", "arrival_date_month", "meal", "market_segment", "distribution_channel",
                   "reserved_room_type", "deposit_type", "customer_type"]
NUMERIC = ["lead_time", "arrival_date_week_number", "arrival_date_day_of_month", "stays_in_weekend_nights",
           "stays_in_week_nights", "adults", "children", "babies", "is_repeated_guest", "previous_cancellations",
           "previous_bookings_not_canceled", "days_in_waiting_list", "adr", "total_of_special_requests",
           "total_nights", "total_guests", "has_kids", "has_company"]
CATEGORICAL = RAW_CATEGORICAL + ["agent_id"]


def prepare(raw):
    # Raw booking rows (RAW_FIELDS) -> model inputs. Stateless, so it is safe inside the pipeline.
    d = pd.DataFrame(raw).copy()
    for c in RAW_FIELDS:
        if c not in RAW_CATEGORICAL:
            d[c] = pd.to_numeric(d[c], errors="coerce")        # 'NULL' agent/company ids become missing
    d["children"] = d["children"].fillna(0)                      # 4 bookings: no children recorded
    d["meal"] = d["meal"].replace({"Undefined": "SC"})           # both mean 'no meal package'
    d["total_nights"] = d["stays_in_week_nights"] + d["stays_in_weekend_nights"]
    d["total_guests"] = d["adults"] + d["children"] + d["babies"]
    d["has_kids"] = ((d["children"] + d["babies"]) > 0).astype(int)
    d["agent_id"] = d["agent"].map(lambda a: "none" if pd.isna(a) else str(int(a)))
    d["has_company"] = d["company"].notna().astype(int)
    out = d[NUMERIC + CATEGORICAL].copy()
    out[CATEGORICAL] = out[CATEGORICAL].astype(object).where(out[CATEGORICAL].notna(), np.nan)
    return out


class CalibratedModel:
    # Deployed model: the evaluated pipeline's scores mapped through an isotonic calibration fitted on
    # out-of-fold training predictions, so the output can be read (and summed) as a probability.
    def __init__(self, model, calibrator):
        self.model, self.calibrator = model, calibrator
        self.classes_ = np.array([0, 1])

    def predict_proba(self, X):
        p = np.clip(self.calibrator.predict(self.model.predict_proba(X)[:, 1]), 0, 1)
        return np.column_stack([1 - p, p])
