import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from statsbombpy import sb

# Streamlit Page Config
st.set_page_config(page_title="Soccer Team Shooting Report", layout="wide")

# Functions to load and process data
@st.cache_data
def load_competitions():
    return sb.competitions()

@st.cache_data
def load_matches(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

@st.cache_data
def load_events(match_id):
    return sb.events(match_id=match_id)

# Load Competitions
competitions = load_competitions()

# Sidebar for competition and season selection
st.sidebar.header("Select Competition and Season")
competition_options = competitions[["competition_name", "season_name", "competition_id", "season_id"]]
selected_competition = st.sidebar.selectbox("Competition", competitions["competition_name"].unique())
available_seasons = competitions[competitions["competition_name"] == selected_competition]["season_name"]
selected_season = st.sidebar.selectbox("Season", available_seasons)

# Filter competition and season
competition_data = competition_options[
    (competition_options["competition_name"] == selected_competition) &
    (competition_options["season_name"] == selected_season)
]
if not competition_data.empty:
    competition_id = competition_data["competition_id"].values[0]
    season_id = competition_data["season_id"].values[0]
    matches = load_matches(competition_id, season_id)

    # Match Selection
    st.sidebar.header("Select Match")
    if matches.empty:
        st.sidebar.error("No matches available for this competition and season.")
    else:
        matches["match_name"] = matches["home_team"] + " vs " + matches["away_team"]
        selected_match = st.sidebar.selectbox("Match", matches["match_name"].unique())
        match_data = matches[matches["match_name"] == selected_match]
        if not match_data.empty:
            match_id = match_data["match_id"].values[0]
            events = load_events(match_id)

            # Team Selection
            st.sidebar.header("Select Team")
            teams = events["team"].unique()
            selected_team = st.sidebar.radio("Team", teams)

            # Filter events for the selected team
            team_data = events[events["team"] == selected_team]

            # Metrics Section
            st.title(f"{selected_team} Shooting Report")
            st.header(f"Match: {selected_match}")

            total_shots = len(team_data[team_data["type"] == "Shot"])
            shots_on_target = len(
                team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "On Target")]
            )
            goals = len(
                team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "Goal")]
            )
            expected_goals = team_data["shot_statsbomb_xg"].sum()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Shots", total_shots)
            col2.metric("Shots on Target", shots_on_target)
            col3.metric("Goals", goals)
            col4.metric("Expected Goals (xG)", f"{expected_goals:.2f}")

            # Visualization: Shot Locations on the Pitch
            st.subheader("Shot Locations on Pitch")
            pitch_shots = team_data[team_data["type"] == "Shot"]

            # Validate shot locations
            pitch_shots = pitch_shots[pitch_shots["location"].notnull()]
            pitch_shots = pitch_shots[pitch_shots["location"].apply(lambda loc: len(loc) == 2)]
            if not pitch_shots.empty:
                pitch_shots["x"] = pitch_shots["location"].apply(lambda loc: loc[0])
                pitch_shots["y"] = pitch_shots["location"].apply(lambda loc: loc[1])
                pitch_shots["color"] = pitch_shots["shot_outcome"].map({
                    "Goal": "green", 
                    "On Target": "yellow", 
                    "Off Target": "red"
                })

                pitch_fig = go.Figure()
                pitch_fig.add_trace(
                    go.Scatter(
                        x=pitch_shots["x"],
                        y=pitch_shots["y"],
                        mode="markers",
                        marker=dict(size=10, color=pitch_shots["color"]),
                        text=pitch_shots["shot_outcome"],
                        hoverinfo="text"
                    )
                )
                pitch_fig.update_layout(
                    title="Shots on the Pitch",
                    xaxis=dict(title="Width of the Pitch (yards)", range=[0, 120]),
                    yaxis=dict(title="Length of the Pitch (yards)", range=[0, 80]),
                    template="plotly_white",
                    showlegend=False
                )
                st.plotly_chart(pitch_fig)

            # Visualization: Shot Locations in the Goal
            st.subheader("Shot Locations in the Goal")
            goal_shots = team_data[team_data["type"] == "Shot"]
            goal_shots = goal_shots[goal_shots["shot_end_location"].notnull()]
            goal_shots = goal_shots[goal_shots["shot_end_location"].apply(lambda loc: len(loc) >= 2)]
            if not goal_shots.empty:
                goal_shots["x"] = goal_shots["shot_end_location"].apply(lambda loc: loc[0])
                goal_shots["y"] = goal_shots["shot_end_location"].apply(lambda loc: loc[1])
                goal_shots["color"] = goal_shots["shot_outcome"].map({
                    "Goal": "green", 
                    "On Target": "yellow", 
                    "Off Target": "red"
                })

                goal_fig = go.Figure()
                goal_fig.add_trace(
                    go.Scatter(
                        x=goal_shots["x"],
                        y=goal_shots["y"],
                        mode="markers",
                        marker=dict(size=10, color=goal_shots["color"]),
                        text=goal_shots["shot_outcome"],
                        hoverinfo="text"
                    )
                )
                goal_fig.update_layout(
                    title="Shots in the Goal",
                    xaxis=dict(title="Width of the Goal (yards)", range=[-10, 10]),
                    yaxis=dict(title="Height of the Goal (yards)", range=[0, 8]),
                    template="plotly_white",
                    showlegend=False
                )
                st.plotly_chart(goal_fig)
            else:
                st.warning("No valid shot end locations available.")
