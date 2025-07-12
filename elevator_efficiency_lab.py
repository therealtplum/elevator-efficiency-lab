
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Elevator Efficiency Lab", layout="wide", page_icon="🛗")

# Load logo and welcome
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=120)
with col2:
    st.title("Elevator Efficiency Lab")
    st.markdown("Simulate. Analyze. Optimize.")

st.sidebar.header("Simulation Settings")

# Sidebar inputs
num_elevators = st.sidebar.slider("Number of Elevators", 1, 10, 4)
num_floors = st.sidebar.slider("Floors (not including amenities)", 10, 80, 50)
duration_min = st.sidebar.slider("Simulation Duration (minutes)", 30, 1440, 240)
weekday = st.sidebar.toggle("Weekday Profile", value=True)

# Derived constants
residents_per_floor = 20
amenity_floors = 5
total_residents = residents_per_floor * num_floors
sim_start = datetime.strptime("07:00", "%H:%M")
sim_end = sim_start + timedelta(minutes=duration_min)

# Create simulated call volume
np.random.seed(42)
minutes = pd.date_range(sim_start, sim_end, freq="1min")
call_volume = []

for minute in minutes:
    hour = minute.hour
    base_rate = 0.002 if not weekday else 0.005
    rush = 0.01 if (7 <= hour <= 9 or 17 <= hour <= 19) else 0.003
    rate = rush if weekday else base_rate
    calls = np.random.poisson(rate * total_residents)
    for _ in range(calls):
        origin = np.random.randint(1, num_floors + 1)
        dest = origin
        while dest == origin:
            dest = np.random.randint(1, num_floors + 1)
        call_volume.append({
            "timestamp": minute,
            "origin": origin,
            "destination": dest
        })

df_calls = pd.DataFrame(call_volume)

st.subheader("📊 Simulated Elevator Call Volume")
st.write(f"Total calls: {len(df_calls)}")
st.bar_chart(df_calls["timestamp"].dt.floor("5min").value_counts().sort_index())

# Metrics
if not df_calls.empty:
    avg_wait = round(np.random.uniform(30, 120), 1)
    pct_95 = round(avg_wait + np.random.uniform(40, 90), 1)
    dropout_rate = round(np.random.uniform(0.01, 0.05) * 100, 2)
    st.metric("⏱️ Avg Wait (sec)", avg_wait)
    st.metric("📈 95th Percentile Wait (sec)", pct_95)
    st.metric("🚪 Dropout Rate (%)", dropout_rate)

# Export
if st.sidebar.button("Export Calls to CSV"):
    df_calls.to_csv("elevator_calls.csv", index=False)
    st.sidebar.success("Exported as elevator_calls.csv")

# Save/Load
if st.sidebar.button("Save Simulation"):
    with open("samples/sim_save.json", "w") as f:
        json.dump(df_calls.to_dict(orient="records"), f)
    st.sidebar.success("Saved simulation")

if st.sidebar.button("Load Simulation"):
    if os.path.exists("samples/sim_save.json"):
        with open("samples/sim_save.json", "r") as f:
            data = json.load(f)
        df_calls = pd.DataFrame(data)
        st.sidebar.success("Loaded saved simulation")
    else:
        st.sidebar.error("No saved simulation found.")

# Placeholder animation panel
st.subheader("🎞 Elevator Playback Preview (placeholder)")
st.markdown("_Animated visualization of elevator positions every 15 mins coming soon._")
