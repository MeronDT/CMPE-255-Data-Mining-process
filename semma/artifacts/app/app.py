import json
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.patches import Arc, Circle, Rectangle
from shot_features import engineer   # score code - must sit next to this file

HERE = Path(__file__).parent
st.set_page_config(page_title="NBA xFG%", page_icon="🏀")

@st.cache_resource
def load():
    return joblib.load(HERE / "model.joblib"), json.loads((HERE / "model_metadata.json").read_text())

model, meta = load()
st.title("🏀 NBA expected field-goal %")
st.caption(f"{meta['champion']} · trained on {meta['trained_on']}")

def court(ax):
    for p in [Circle((0, 0), 7.5, fill=False), Rectangle((-80, -47.5), 160, 190, fill=False),
              Arc((0, 142.5), 120, 120, theta1=0, theta2=180), Arc((0, 0), 80, 80, theta1=0, theta2=180),
              Rectangle((-220, -47.5), 0, 140), Rectangle((220, -47.5), 0, 140), Arc((0, 0), 475, 475, theta1=22, theta2=158),
              Rectangle((-250, -47.5), 500, 470, fill=False)]:
        p.set_edgecolor("#555"); ax.add_patch(p)
    ax.set_xlim(-250, 250); ax.set_ylim(-47.5, 422.5); ax.set_aspect("equal"); ax.axis("off")

shot, board = st.tabs(["Evaluate a shot", "2024-25 shot-making leaderboard"])
with shot:
    left, right = st.columns([1, 1])
    with left:
        x_ft = st.slider("Feet left (-) / right (+) of the hoop", -25.0, 25.0, 0.0, 0.5)
        y_ft = st.slider("Feet out from the hoop", -4.0, 40.0, 15.0, 0.5)
        action = st.selectbox("Shot type", meta["actions"], index=0)
        period = st.selectbox("Period", [1, 2, 3, 4, 5], index=0, format_func=lambda p: f"Q{p}" if p <= 4 else "OT")
        minutes = st.number_input("Minutes left in period", 0, 12 if period <= 4 else 5, 6)
        seconds = st.number_input("Seconds", 0, 59, 0)
    raw = pd.DataFrame([{"LOC_X": x_ft * 10, "LOC_Y": y_ft * 10, "ACTION_TYPE": action, "PERIOD": period,
                         "MINUTES_REMAINING": minutes, "SECONDS_REMAINING": seconds}])
    feats = engineer(raw).iloc[0]
    xfg = float(model.predict_proba(raw)[0, 1])
    value = 3 if feats["is_three"] else 2
    with right:
        fig, ax = plt.subplots(figsize=(4, 4))
        court(ax); ax.scatter([x_ft * 10], [y_ft * 10], s=120, c="#E4572E", zorder=5)
        st.pyplot(fig)
    c1, c2, c3 = st.columns(3)
    c1.metric("Expected FG%", f"{xfg:.1%}")
    c2.metric("Shot value", f"{value} pts" + (" (corner)" if feats["is_corner_three"] else ""))
    c3.metric("Expected points", f"{xfg * value:.2f}")
    st.caption(f"Distance {feats['dist_ft']:.1f} ft · angle {feats['angle_deg']:.0f}°")
with board:
    lb = pd.read_csv(HERE / "leaderboard.csv")
    st.write("Players with 500+ attempts. **Points over expected** = actual points from field goals minus the points "
             "an average shooter would score on the same shots.")
    st.dataframe(lb[["PLAYER_NAME", "team", "FGA", "FG_pct", "xFG_pct", "FG_over_expected", "points_over_expected"]],
                 hide_index=True)
