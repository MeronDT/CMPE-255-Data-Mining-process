import json
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
st.set_page_config(page_title="Retail insights", page_icon="🛍️")

@st.cache_resource
def load():
    meta = json.loads((HERE / "metadata.json").read_text())
    rules = pd.read_csv(HERE / "rules.csv")
    customers = pd.read_csv(HERE / "customer_segments.csv", dtype={"Customer ID": str})
    return meta, rules, customers, joblib.load(HERE / "segmenter.joblib")

meta, rules, customers, segmenter = load()
st.title("🛍️ Customer segments & product recommendations")
st.caption(f"Online Retail II · {len(customers):,} customers · {len(rules):,} association rules · data up to {meta['snapshot']}")
seg_info = meta["segments"]

recs, lookup, new_cust, overview = st.tabs(["Product recommendations", "Customer lookup", "Segment a new customer", "Segments overview"])
with recs:
    products = sorted(set(" + ".join(rules["antecedent"]).split(" + ")))
    product = st.selectbox("Customer has this product in the basket", products)
    only_valid = st.checkbox("Only rules that met the full thresholds again in the following year", value=True)
    hits = rules[rules["antecedent"].apply(lambda a: product in a.split(" + "))]
    if only_valid:
        hits = hits[hits["validated_next_year"]]
    if hits.empty:
        st.info("No strong associations for this product.")
    else:
        st.dataframe(hits[["antecedent", "consequent", "confidence", "lift"]].head(15), hide_index=True)
        top = hits.iloc[0]
        st.success(f"Suggest **{top['consequent']}** — bought in {top['confidence']:.0%} of baskets containing "
                   f"{top['antecedent']} ({top['lift']:.1f}x more often than average).")
with lookup:
    cid = st.text_input("Customer ID", value=customers["Customer ID"].iloc[0])
    row = customers[customers["Customer ID"] == cid.strip()]
    if row.empty:
        st.warning("Customer not found.")
    else:
        r = row.iloc[0]; s = seg_info[r["segment"]]
        st.subheader(s["name"]); st.write(f"**Recommended action:** {s['action']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Days since last order", int(r["recency_days"])); c2.metric("Orders", int(r["frequency"])); c3.metric("Spend (GBP)", f"{r['monetary']:,.0f}")
with new_cust:
    c1, c2, c3 = st.columns(3)
    rec = c1.number_input("Days since last order", 0, 1000, 30)
    freq = c2.number_input("Number of orders", 1, 500, 3)
    mon = c3.number_input("Total spend (GBP)", 1.0, 1e6, 500.0)
    cluster = int(segmenter.predict(pd.DataFrame([{"recency_days": rec, "frequency": freq, "monetary": mon}]))[0])
    seg = meta["cluster_to_segment"][str(cluster)]
    st.subheader(seg_info[seg]["name"]); st.write(f"**Recommended action:** {seg_info[seg]['action']}")
with overview:
    st.dataframe(pd.DataFrame(meta["profiles"]), hide_index=True)
