# Score code for the NBA xFG% model: the Modify step, shared by the notebook and the app.
import numpy as np
import pandas as pd

RAW_INPUTS = ["LOC_X", "LOC_Y", "ACTION_TYPE", "PERIOD", "MINUTES_REMAINING", "SECONDS_REMAINING"]
NUMERIC = ["dist_ft", "angle_deg", "abs_angle", "is_three", "is_corner_three", "secs_left_period",
           "PERIOD", "is_overtime", "clutch", "heave"]
CATEGORICAL = ["action", "distance_bin"]
BIN_EDGES = [-0.1, 4, 10, 16, 23.75, 30, 100]
BIN_LABELS = ["0-4 ft", "4-10 ft", "10-16 ft", "16-23.75 ft", "23.75-30 ft", "30+ ft"]


def engineer(raw):
    # Transform raw shot records (RAW_INPUTS) into model inputs. Stateless, so it is safe to reuse anywhere.
    d = pd.DataFrame(raw).copy()
    x, y = d["LOC_X"].astype(float), d["LOC_Y"].astype(float)       # tenths of feet, hoop at (0, 0)
    out = pd.DataFrame(index=d.index)
    out["dist_ft"] = np.hypot(x, y) / 10
    out["angle_deg"] = np.degrees(np.arctan2(x, y))                  # 0 = straight on, +/-90 = along the baseline
    out["abs_angle"] = out["angle_deg"].abs()
    corner = (x.abs() >= 220) & (y <= 92.5)
    out["is_corner_three"] = corner.astype(int)
    out["is_three"] = (corner | (np.hypot(x, y) >= 237.5)).astype(int)
    out["secs_left_period"] = d["MINUTES_REMAINING"].astype(int) * 60 + d["SECONDS_REMAINING"].astype(int)
    out["PERIOD"] = d["PERIOD"].astype(int)
    out["is_overtime"] = (out["PERIOD"] > 4).astype(int)
    out["clutch"] = ((out["PERIOD"] >= 4) & (out["secs_left_period"] <= 120)).astype(int)
    out["heave"] = ((out["secs_left_period"] <= 3) & (out["dist_ft"] >= 30)).astype(int)
    out["action"] = d["ACTION_TYPE"].astype(str)
    out["distance_bin"] = pd.cut(out["dist_ft"], BIN_EDGES, labels=BIN_LABELS).astype(str)
    return out[NUMERIC + CATEGORICAL]


class AveragedModel:
    # Ensemble node: averages the predicted probabilities of already-fitted pipelines.
    def __init__(self, models):
        self.models = models
        self.classes_ = np.array([0, 1])

    def predict_proba(self, X):
        p = np.mean([m.predict_proba(X)[:, 1] for m in self.models], axis=0)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
