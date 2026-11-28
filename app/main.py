import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from app.components.queries import get_state_quarter_metrics
from app.components.filters import year_filter, quarter_filter, state_filter

st.title("India Digital Spending & Tax Health Monitor")

df = get_state_quarter_metrics()
year = year_filter(df)
st.write("Selected year:", year)

quarter=quarter_filter(df)
st.write("Selected quarter:", quarter)

state=state_filter(df)
st.write("Selected state:", state)