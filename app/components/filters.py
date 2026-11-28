import streamlit as st


def year_filter(df):
    years = sorted(df["year"].unique())
    return st.sidebar.selectbox("Year", years, index=len(years) - 1)

def quarter_filter(df):
    quarters = sorted(df["quarter"].unique())
    return st.sidebar.selectbox("Quarter", quarters, index=len(quarters) - 1)


def state_filter(df):
    states = ["All states"] + sorted(df["state_name"].unique())
    return st.sidebar.selectbox("State", states, index=0)
