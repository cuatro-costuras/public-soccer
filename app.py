import pandas as pd
import numpy as np
import streamlit as st
from statsbombpy import sb
from mplsoccer import VerticalPitch

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Soccer Team Shooting Report", page_icon="⚽")

# Load matches
@st.cache_data
def load_matches(competition_id, season_id):
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        return matches
    except Exception as e:
        st.error(f"Error loading matches: {e}")
        return pd.DataFrame()

# Load event data
@st.cache_data
def load_event_data(match_id):
    try:
        events = sb.events(match_id=match_id)
        return events
    except Exception as e:
        st.error(f"Error loading event data: {e}")
        return pd.DataFrame()

# Main App
st.title("Soccer Team Shooting Report")

# Sidebar for competition and season selection
st.sidebar.header("Select Match Details")
competition = st.sidebar.selectbox("Competition", options=["Germany 1. Bundesliga"])
season = st.sidebar.selectbox("Season", options=["2023/2024"])

if competition and season:
    matches = load_matches(competition_id=11, season_id=season)  # Adjust competition ID and season ID as needed
    if not matches.empty:
        match = st.sidebar.selectbox("Match", options=matches["home_team"] + " vs " + matches["away_team"])
        if match:
            match_id = matches[matches["home_team"] + " vs " + matches["away_team"] == match]["match_id"].values[0]
            events = load_event_data(match_id)

            if not events.empty:
                # Sidebar team selection
                st.sidebar.subheader("Select Team")
                teams = events["team"].unique()
                team = st.sidebar.radio("Team", options=teams)

                # Filter data for the selected team
                team_data = events[events["team"] == team]

                # Display team name and shooting stats
                st.header(f"{team} Shooting Report")
                st.subheader(f"Match Date: {matches[matches['match_id'] == match_id]['match_date'].values[0]}")

                # Team shooting metrics
                shots_taken = len(team_data[team_data["type"] == "Shot"])
                shots_on_target = len(team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "On Target")])
                goals = len(team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "Goal")])
                shot_conversion_rate = (goals / shots_taken * 100) if shots_taken > 0 else 0
                expected_goals = team_data["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in team_data.columns else 0

                # Display shooting metrics in columns
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Shots Taken", shots_taken)
                col2.metric("Shots on Target", shots_on_target)
                col3.metric("Goals", goals)
                col4.metric("Shot Conversion Rate", f"{shot_conversion_rate:.2f}%")
                col5.metric("Expected Goals (xG)", f"{expected_goals:.2f}")

                # Soccer pitch plot
                st.subheader("Shot Locations on Field")
                pitch = VerticalPitch(pitch_color="grass", line_color="white")
                fig, ax = pitch.draw(figsize=(10, 7))

                shot_data = team_data[team_data["type"] == "Shot"]
                for _, shot in shot_data.iterrows():
                    if "location" in shot and pd.notnull(shot["location"]) and isinstance(shot["location"], list) and len(shot["location"]) == 2:
                        x, y = shot["location"]
                        color = "green" if shot["shot_outcome"] == "Goal" else (
                            "yellow" if shot["shot_outcome"] == "Saved" else "red"
                        )
                        pitch.scatter(x, y, color=color, s=100, ax=ax)
                    else:
                        st.warning(f"Skipping invalid shot data: {shot}")

                st.pyplot(fig)

                # Soccer goal plot
                st.subheader("Shot Outcomes on Goal")
                goal_fig, goal_ax = pitch.draw_goals(figsize=(10, 7))

                for _, shot in shot_data.iterrows():
                    if "shot_end_location" in shot and pd.notnull(shot["shot_end_location"]) and isinstance(shot["shot_end_location"], list) and len(shot["shot_end_location"]) == 2:
                        x, y = shot["shot_end_location"]
                        color = "green" if shot["shot_outcome"] == "Goal" else (
                            "yellow" if shot["shot_outcome"] == "Saved" else "red"
                        )
                        goal_ax.scatter(x, y, color=color, s=100)

                st.pyplot(goal_fig)
            else:
                st.error("No event data available for the selected match.")
    else:
        st.error("No matches found for the selected competition and season.")
else:
    st.error("Please select a competition and season.")
