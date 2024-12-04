import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# Load data functions (replace these with your actual data loading methods)
@st.cache_data
def load_matches():
    # Replace with your data loading logic
    matches = pd.read_csv("matches.csv")
    return matches

@st.cache_data
def load_events():
    # Replace with your data loading logic
    events = pd.read_csv("events.csv")
    return events

# Filter events by team and match
def load_team_events(team_name, match_id):
    events = load_events()
    team_events = events[(events["team"] == team_name) & (events["match_id"] == match_id)]
    if team_events.empty:
        st.error(f"No events found for {team_name} in match {match_id}. Check event data.")
    return team_events

# Plot field shots
def plot_field_shots(events):
    pitch = Pitch(pitch_type="statsbomb", orientation="horizontal", line_color="black", figsize=(10, 6))
    fig, ax = pitch.draw()

    for _, shot in events.iterrows():
        x, y = shot["location"][0], shot["location"][1]
        color = "green" if shot["outcome"] == "goal" else "blue" if shot["outcome"] == "saved" else "red"
        pitch.scatter(x, y, color=color, ax=ax, s=100)

    return fig

# Plot goal shots
def plot_goal_shots(events):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 3)
    ax.set_aspect("equal")

    # Draw the goal
    ax.plot([0, 8], [0, 0], color="black", lw=2)
    ax.plot([0, 0], [0, 3], color="black", lw=2)
    ax.plot([8, 8], [0, 3], color="black", lw=2)
    ax.plot([0, 8], [3, 3], color="black", lw=2)

    for _, shot in events.iterrows():
        x, y = shot["goal_x"], shot["goal_y"]
        color = "green" if shot["outcome"] == "goal" else "blue" if shot["outcome"] == "saved" else "red"
        ax.scatter(x, y, color=color, s=100)

    return fig

# Streamlit app layout
st.set_page_config(layout="wide", page_title="Soccer Match Analysis")

# Sidebar for competition and match selection
st.sidebar.title("Match Analysis")
matches = load_matches()

# Competition and season dropdown
competition = st.sidebar.selectbox("Select Competition", matches["competition"].unique())
season = st.sidebar.selectbox("Select Season", matches[matches["competition"] == competition]["season"].unique())

# Match selection
selected_matches = matches[(matches["competition"] == competition) & (matches["season"] == season)]
match_options = selected_matches[["home_team", "away_team", "match_id"]].apply(
    lambda x: f"{x['home_team']} vs {x['away_team']} (ID: {x['match_id']})", axis=1
)
selected_match = st.sidebar.selectbox("Select Match", match_options)
match_id = int(selected_match.split("ID: ")[1])

# Teams selection
match_row = selected_matches[selected_matches["match_id"] == match_id].iloc[0]
home_team, away_team = match_row["home_team"], match_row["away_team"]
col1, col2 = st.columns(2)
with col1:
    if st.button(home_team):
        selected_team = home_team
with col2:
    if st.button(away_team):
        selected_team = away_team

# Display match score
st.title(f"Match: {home_team} vs {away_team}")
st.subheader(f"Score: {match_row['home_score']} - {match_row['away_score']}")

# Team-specific analysis
if "selected_team" in locals():
    st.header(f"Analysis for {selected_team}")
    team_events = load_team_events(selected_team, match_id)

    # Calculate performance metrics
    total_shots = len(team_events[team_events["type"] == "Shot"])
    shots_on_target = team_events[
        (team_events["type"] == "Shot") & (team_events["outcome"].isin(["goal", "saved"]))
    ].shape[0]
    goals = team_events[(team_events["type"] == "Shot") & (team_events["outcome"] == "goal")].shape[0]
    expected_goals = team_events["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in team_events else 0.0
    shot_conversion_rate = f"{(goals / total_shots * 100):.2f}%" if total_shots > 0 else "0%"

    # Performance metrics
    st.columns(5)[0].metric("Total Shots", total_shots)
    st.columns(5)[1].metric("Shots on Target", shots_on_target)
    st.columns(5)[2].metric("Shot Conversion Rate", shot_conversion_rate)
    st.columns(5)[3].metric("Goals", goals)
    st.columns(5)[4].metric("Expected Goals (xG)", f"{expected_goals:.2f}")

    # Shot locations on field
    st.subheader("Shot Location(s) On Field")
    st.pyplot(plot_field_shots(team_events))

    # Shot locations on goal
    st.subheader("Shot Location(s) On Goal")
    st.pyplot(plot_goal_shots(team_events))
