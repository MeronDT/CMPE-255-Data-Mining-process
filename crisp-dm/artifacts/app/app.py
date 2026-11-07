import datetime as dt
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from booking_features import RAW_FIELDS, RAW_CATEGORICAL   # score code - must sit next to this file (the pickled model refers to it)

HERE = Path(__file__).parent
st.set_page_config(page_title="Cancellation Risk", page_icon="🏨")

@st.cache_resource
def load():
    return joblib.load(HERE / "model.joblib"), json.loads((HERE / "model_metadata.json").read_text(encoding="utf-8"))

model, meta = load()
threshold = meta["decision_threshold"]
options = {f["name"]: set(f["options"]) for f in meta["raw_fields"] if f["type"] == "categorical"}
st.title("🏨 Hotel booking cancellation risk")
st.caption(f"{meta['model_type']} · trained on {meta['trained_on']} · test ROC-AUC {meta['test_metrics']['roc_auc']:.3f}")
st.info(f"Recommended use: {meta['overbooking_rule']} Guests are not contacted on the basis of this score.")

def score(df):
    p = model.predict_proba(df[RAW_FIELDS])[:, 1]
    return pd.DataFrame({"cancel_probability": p.round(4), "watch_list": (p >= threshold).astype(int)})

single, batch = st.tabs(["Score one booking", "Score the day's bookings (CSV)"])
with single:
    row, cols = {}, st.columns(2)
    arrival = cols[0].date_input("Arrival date", dt.date(2017, 8, 15))
    row.update({"arrival_date_month": arrival.strftime("%B"), "arrival_date_week_number": arrival.isocalendar()[1],
                "arrival_date_day_of_month": arrival.day})
    fields = [f for f in meta["raw_fields"] if f["type"] != "date"]
    for i, f in enumerate(fields):
        with cols[(i + 1) % 2]:
            if f["type"] == "numeric":
                if f["integer"]:
                    row[f["name"]] = st.number_input(f["name"], 0, int(f["max"]), int(f["default"]), help=f["meaning"])
                else:
                    row[f["name"]] = st.number_input(f["name"], 0.0, f["max"], f["default"], help=f["meaning"])
            elif f["type"] == "agent":
                a = st.selectbox("travel agent ID", f["options"], help=f["meaning"])
                row["agent"] = np.nan if a == "none" else float(a)
            elif f["type"] == "company":
                row["company"] = 1.0 if st.checkbox("booked and paid by a company", help=f["meaning"]) else np.nan
            else:
                row[f["name"]] = st.selectbox(f["name"], f["options"], help=f["meaning"])
    if st.button("Estimate cancellation risk", type="primary"):
        out = score(pd.DataFrame([row])).iloc[0]
        st.metric("Probability of cancellation", f"{out['cancel_probability']:.1%}")
        st.write("This booking adds its probability to the night's expected cancellations." +
                 (" It is also on the watch list (high risk)." if out["watch_list"] else ""))
with batch:
    st.write("Upload the day's bookings with the raw booking-system columns: " + ", ".join(RAW_FIELDS))
    up = st.file_uploader("CSV of bookings", type="csv")
    if up is not None:
        data = pd.read_csv(up)
        missing = [c for c in RAW_FIELDS if c not in data.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            unknown = {c: sorted(set(data[c].dropna().astype(str)) - options[c]) for c in options if c in data}
            unknown = {c: v for c, v in unknown.items() if v}
            if unknown:
                st.warning(f"Values never seen in training (scored as 'other'): {unknown}")
            result = pd.concat([data.reset_index(drop=True), score(data)], axis=1)
            per_date = (result.groupby(["hotel", "arrival_date_month", "arrival_date_day_of_month"])["cancel_probability"]
                              .agg(bookings="size", expected_cancellations="sum").reset_index())
            per_date["recommended_extra_rooms"] = np.round(per_date["expected_cancellations"]).astype(int)
            st.subheader("Recommended overbooking per arrival date")
            st.dataframe(per_date, hide_index=True)
            st.subheader("Bookings")
            st.dataframe(result.head(500))
            st.download_button("Download scored bookings", result.to_csv(index=False), "scored_bookings.csv")
