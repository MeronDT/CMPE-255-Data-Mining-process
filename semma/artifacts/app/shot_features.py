# Score code for the NBA xFG% model: the Modify step, shared by the notebook and the app.
import numpy as np
import pandas as pd

RAW_INPUTS = ["LOC_X", "LOC_Y", "ACTION_TYPE", "PERIOD", "MINUTES_REMAINING", "SECONDS_REMAINING"]
NUMERIC = ["dist_ft", "log_dist", "abs_angle", "is_three", "is_corner_three", "secs_left_period", "PERIOD", "heave"]
CATEGORICAL = ["action", "action_family", "distance_bin"]
# finer bins near the rim, where FG% falls fastest (Explore finding 1)
BIN_EDGES = [-0.1, 1, 2, 3, 5, 10, 16, 23.75, 30, 100]
BIN_LABELS = ["0-1 ft", "1-2 ft", "2-3 ft", "3-5 ft", "5-10 ft", "10-16 ft", "16-23.75 ft", "23.75-30 ft", "30+ ft"]


def action_family(action):
    # Group the scorer's ACTION_TYPE labels into shot families, so rare labels (e.g. 'Running Alley Oop Dunk Shot')
    # are still recognised as what they are instead of being pooled with unrelated rare shots.
    if pd.isna(action):
        return np.nan
    a = str(action).lower()
    for family, keys in [("dunk", ["dunk"]), ("tip/putback", ["tip", "putback"]), ("alley-oop", ["alley oop"]),
                         ("layup", ["layup", "finger roll"]), ("hook", ["hook"]), ("floater", ["float"]),
                         ("bank shot", ["bank"]), ("fadeaway/turnaround", ["fadeaway", "turnaround"]),
                         ("pull-up/step-back", ["pull", "step back"]), ("jump shot", ["jump"])]:
        if any(k in a for k in keys):
            return family
    return "other"


def engineer(raw):
    # Transform raw shot records (RAW_INPUTS) into model inputs. Stateless, so it is safe to reuse anywhere.
    # Missing inputs stay missing (NaN) so the Impute step in the pipeline can handle them.
    d = pd.DataFrame(raw).copy()
    num = lambda c: pd.to_numeric(d[c], errors="coerce")
    x, y = num("LOC_X"), num("LOC_Y")                               # tenths of feet, hoop at (0, 0)
    has_loc = x.notna() & y.notna()
    out = pd.DataFrame(index=d.index)
    out["dist_ft"] = np.hypot(x, y) / 10
    out["log_dist"] = np.log1p(out["dist_ft"])
    out["abs_angle"] = np.degrees(np.arctan2(x, y)).abs()            # 0 = straight on, 90 = along the baseline
    corner = (x.abs() >= 220) & (y <= 92.5)
    out["is_corner_three"] = corner.astype(float).where(has_loc)
    out["is_three"] = (corner | (np.hypot(x, y) >= 237.5)).astype(float).where(has_loc)
    out["secs_left_period"] = num("MINUTES_REMAINING") * 60 + num("SECONDS_REMAINING")
    out["PERIOD"] = num("PERIOD")
    out["heave"] = ((out["secs_left_period"] <= 3) & (out["dist_ft"] >= 30)).astype(float).where(
        out["secs_left_period"].notna() & has_loc)
    out["action"] = d["ACTION_TYPE"].astype(object).where(d["ACTION_TYPE"].notna(), np.nan)
    out["action_family"] = out["action"].map(action_family)
    out["distance_bin"] = pd.cut(out["dist_ft"], BIN_EDGES, labels=BIN_LABELS).astype(object)
    out["distance_bin"] = out["distance_bin"].where(out["dist_ft"].notna(), np.nan)
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
