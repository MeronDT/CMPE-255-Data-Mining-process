import json
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
st.set_page_config(page_title="Cancellation Risk", page_icon="🏨")

@st.cache_resource
def load():
    return joblib.load(HERE / "model.joblib"), json.loads((HERE / "model_metadata.json").read_text())

model, meta = load()
features = meta["features"]
threshold = meta["decision_threshold"]

st.title("🏨 Hotel booking cancellation risk")
st.caption(f"{meta['model_type']} · test ROC-AUC {meta['test_metrics']['roc_auc']:.3f} · "
           f"bookings with risk ≥ {threshold:.0%} are flagged")

def score(df):
    p = model.predict_proba(df[[f["name"] for f in features]])[:, 1]
    return pd.DataFrame({"cancel_probability": p.round(4), "flag": (p >= threshold).astype(int)})

single, batch = st.tabs(["Score one booking", "Score a CSV of bookings"])
with single:
    row, cols = {}, st.columns(2)
    for i, f in enumerate(features):
        with cols[i % 2]:
            if f["type"] == "numeric":
                if f["integer"]:
                    row[f["name"]] = st.number_input(f["name"], int(f["min"]), int(f["max"]), int(f["default"]), help=f["meaning"])
                else:
                    row[f["name"]] = st.number_input(f["name"], float(f["min"]), float(f["max"]), float(f["default"]), help=f["meaning"])
            else:
                row[f["name"]] = st.selectbox(f["name"], f["categories"], help=f["meaning"])
    if st.button("Estimate cancellation risk", type="primary"):
        out = score(pd.DataFrame([row])).iloc[0]
        st.metric("Probability of cancellation", f"{out['cancel_probability']:.1%}")
        if out["flag"]:
            st.error("High risk — consider a deposit request, reminder, or counting it in overbooking.")
        else:
            st.success("Low risk — no action needed.")
with batch:
    up = st.file_uploader("CSV with the same columns as the training data", type="csv")
    if up is not None:
        data = pd.read_csv(up)
        missing = [f["name"] for f in features if f["name"] not in data.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            result = pd.concat([data.reset_index(drop=True), score(data)], axis=1)
            st.write(f"{result['flag'].sum():,} of {len(result):,} bookings flagged")
            st.dataframe(result.head(500))
            st.download_button("Download scored bookings", result.to_csv(index=False), "scored_bookings.csv")
