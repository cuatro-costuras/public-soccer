import pandas as pd
import streamlit as st
from statsbombpy import sb

# Helper Functions
def get_competitions():
    competitions = sb.competitions()
    return competitions

def get_matches(competition_id, season_id):
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    return matches

def get_events(match_id):
    events = sb.events(match_id=match_id)
    return events

# Streamlit UI
st.title("Retrieve Column Names and Sample Data for StatsBombPy")

# Step 1: Select Competition
competitions = get_competitions()
competitions["label"] = competitions["competition_name"] + " - " + competitions["season_name"]
competition = st.selectbox("Select Competition", competitions["label"].unique())
selected_competition = competitions[competitions["label"] == competition].iloc[0]
competition_id = selected_competition["competition_id"]
season_id = selected_competition["season_id"]

# Step 2: Select Match
matches = get_matches(competition_id, season_id)
matches["label"] = matches["home_team"] + " vs " + matches["away_team"]
match = st.selectbox("Select Match", matches["label"].unique())
selected_match = matches[matches["label"] == match].iloc[0]
match_id = selected_match["match_id"]

# Step 3: Display Column Names and Samples
events = get_events(match_id)

st.write("### Matches DataFrame Columns")
st.write(matches.columns.tolist())
st.write("### Matches DataFrame Sample")
st.write(matches.head())

st.write("### Events DataFrame Columns")
st.write(events.columns.tolist())
st.write("### Events DataFrame Sample")
st.write(events.head())
