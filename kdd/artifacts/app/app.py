import json
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
st.set_page_config(page_title="Retail insights", page_icon="🛍️")

@st.cache_resource
def load():
    meta = json.loads((HERE / "metadata.json").read_text(encoding="utf-8"))
    rules = pd.read_csv(HERE / "rules.csv")
    rules["ante_set"] = rules["antecedent"].str.split(" + ", regex=False).apply(frozenset)
    rules["cons_set"] = rules["consequent"].str.split(" + ", regex=False).apply(frozenset)
    customers = pd.read_csv(HERE / "customer_segments.csv", dtype={"Customer ID": str})
    return meta, rules, customers, joblib.load(HERE / "segmenter.joblib")

meta, rules, customers, segmenter = load()
st.title("🛍️ Customer segments & product recommendations")
st.caption(f"Online Retail II · {len(customers):,} customers active in {meta['window']} · {len(rules):,} association rules")
seg_info = meta["segments"]

recs, lookup, new_cust, overview = st.tabs(["Product recommendations", "Customer lookup", "Segment a customer", "Segments overview"])
with recs:
    only_valid = st.checkbox("Only rules that met support, confidence and lift again in the following year", value=True)
    hide_variants = st.checkbox("Hide colour/design variants of the same product (show cross-sell only)", value=False)
    pool = rules[rules["validated_next_year"]] if only_valid else rules
    if hide_variants:
        pool = pool[pool["rule_type"] == "cross-product"]
    products = sorted({p for s in pool["ante_set"] for p in s})
    basket = set(st.multiselect("Products in the customer's basket", products, default=products[:1]))
    hits = pool[pool["ante_set"].apply(lambda a: a <= basket) & pool["cons_set"].apply(lambda c: not (c & basket))]
    if not basket:
        st.info("Pick one or more products.")
    elif hits.empty:
        st.info("No association for this basket - every rule needs ALL of its 'if' products in the basket.")
    else:
        st.dataframe(hits[["antecedent", "consequent", "confidence", "lift", "rule_type"]].head(15), hide_index=True)
        top = hits.iloc[0]
        st.success(f"Suggest **{top['consequent']}**: bought in {top['confidence']:.0%} of baskets containing "
                   f"{top['antecedent']} ({top['lift']:.1f}x more often than average).")
with lookup:
    cid = st.text_input("Customer ID", value=customers["Customer ID"].iloc[0])
    row = customers[customers["Customer ID"] == cid.strip()]
    if row.empty:
        st.warning("Customer not found (only customers who ordered in the last 12 months are segmented).")
    else:
        r = row.iloc[0]; s = seg_info[r["segment"]]
        st.subheader(s["name"]); st.write(f"**Recommended action:** {s['action']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Days since last order", int(r["recency_days"])); c2.metric("Orders (12 months)", int(r["frequency"])); c3.metric("Spend, 12 months (GBP)", f"{r['monetary']:,.0f}")
        st.write(f"**RFM score:** better than {int(r['rfm_score_pct'])} % of customers. Use it to rank customers *within* a segment "
                 "(it predicts next-year activity slightly better than the segment alone).")
with new_cust:
    st.write("Enter the customer's activity over the **last 12 months** (the window the segments were built and validated on).")
    c1, c2, c3 = st.columns(3)
    rec = c1.number_input("Days since last order", 0, 365, 30)
    freq = c2.number_input("Orders in the last 12 months", 1, 500, 3)
    mon = c3.number_input("Spend in the last 12 months (GBP)", 1.0, 1e6, 500.0)
    cluster = int(segmenter.predict(pd.DataFrame([{"recency_days": rec, "frequency": freq, "monetary": mon}]))[0])
    seg = meta["cluster_to_segment"][str(cluster)]
    st.subheader(seg_info[seg]["name"]); st.write(f"**Recommended action:** {seg_info[seg]['action']}")
with overview:
    st.write(f"Segment profiles for customers active in {meta['window']} (medians; labels use the discovery-year tertiles).")
    st.dataframe(pd.DataFrame(meta["profiles"]), hide_index=True)
    pick = st.selectbox("Export a segment's customer list (ranked by RFM score)", sorted(seg_info))
    lst = customers[customers["segment"] == pick].sort_values("rfm_score_pct", ascending=False)
    st.download_button(f"Download {pick} ({len(lst):,} customers)", lst.to_csv(index=False), f"segment_{pick}.csv")
