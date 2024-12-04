import pandas as pd
import streamlit as st
from statsbombpy import sb
from mplsoccer import Pitch

# Helper Functions
def get_competitions():
    competitions = sb.competitions()
    competitions["label"] = competitions["competition_name"] + " - " + competitions["season_name"]
    return competitions

def get_matches(competition_id, season_id):
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    matches["label"] = matches["home_team"] + " vs " + matches["away_team"]
    return matches

def get_events(match_id):
    events = sb.events(match_id=match_id)
    return events

# Streamlit UI
st.title("Soccer Team Stats Analysis")

# Step 1: Select Competition
competitions = get_competitions()
competition = st.sidebar.selectbox("Select Competition", competitions["label"].unique())
selected_competition = competitions[competitions["label"] == competition].iloc[0]
competition_id = selected_competition["competition_id"]
season_id = selected_competition["season_id"]

# Step 2: Select Match
matches = get_matches(competition_id, season_id)
match = st.sidebar.selectbox("Select Match", matches["label"].unique())
selected_match = matches[matches["label"] == match].iloc[0]
match_id = selected_match["match_id"]

# Step 3: Analyze Events
events = get_events(match_id)

# Filter events for the selected team
team = st.sidebar.selectbox("Select Team", [selected_match["home_team"], selected_match["away_team"]])
team_events = events[events["team"] == team]

# Team Stats
total_shots = len(team_events[team_events["type"] == "Shot"])
shots_on_target = len(team_events[(team_events["type"] == "Shot") & (team_events["shot_outcome"].isin(["On Target", "Goal"]))])
goals = len(team_events[(team_events["type"] == "Shot") & (team_events["shot_outcome"] == "Goal")])
expected_goals = team_events[team_events["type"] == "Shot"]["shot_statsbomb_xg"].sum()

# Display Stats
st.subheader(f"{team} - Match Stats")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shots", total_shots)
col2.metric("Shots on Target", shots_on_target)
col3.metric("Goals", goals)
col4.metric("Expected Goals (xG)", f"{expected_goals:.2f}")

# Visualization: Shot Locations
st.subheader("Shot Locations")
shot_data = team_events[team_events["type"] == "Shot"].dropna(subset=["location"])
shot_data["x"] = shot_data["location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
shot_data["y"] = shot_data["location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

pitch = Pitch(pitch_type="statsbomb", orientation="horizontal", line_color="black", figsize=(10, 6))
fig, ax = pitch.draw()

for _, shot in shot_data.iterrows():
    color = "green" if shot["shot_outcome"] == "Goal" else "yellow" if shot["shot_outcome"] == "On Target" else "red"
    pitch.scatter(shot["x"], shot["y"], s=100, color=color, ax=ax)

st.pyplot(fig)

# Visualization: Shot Outcomes on Goal
st.subheader("Shot Outcomes on Goal")
goal_data = team_events[team_events["type"] == "Shot"].dropna(subset=["shot_end_location"])
goal_data["x"] = goal_data["shot_end_location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
goal_data["y"] = goal_data["shot_end_location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

goal_pitch = Pitch(goal_type="statsbomb", orientation="horizontal", line_color="black", figsize=(10, 6))
fig, ax = goal_pitch.draw()

for _, shot in goal_data.iterrows():
    color = "green" if shot["shot_outcome"] == "Goal" else "yellow" if shot["shot_outcome"] == "On Target" else "red"
    goal_pitch.scatter(shot["x"], shot["y"], s=100, color=color, ax=ax)

st.pyplot(fig)
