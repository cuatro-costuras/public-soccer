import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from statsbombpy import sb

# Streamlit Page Config
st.set_page_config(page_title="Soccer Team Shooting Report", layout="wide")

# Functions to load and process data
@st.cache_data
def load_matches(competition_id, season_id):
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        return matches
    except Exception as e:
        st.error(f"Error loading matches: {e}")
        return pd.DataFrame()

@st.cache_data
def load_events(match_id):
    try:
        events = sb.events(match_id=match_id)
        return events
    except Exception as e:
        st.error(f"Error loading events: {e}")
        return pd.DataFrame()

# Main App
st.sidebar.title("Soccer Team Shooting Report")

# Competition and Season Selection
competition_id = st.sidebar.selectbox("Select Competition", options=[11], format_func=lambda x: "German Bundesliga")
season_id = st.sidebar.selectbox("Select Season", options=[4], format_func=lambda x: "2023/2024")

matches = load_matches(competition_id, season_id)

if matches.empty:
    st.error("No matches found for the selected competition and season.")
else:
    # Format match options for dropdown
    match_options = matches[["home_team", "away_team", "match_id"]]
    match_options["match_name"] = match_options["home_team"] + " vs " + match_options["away_team"]
    selected_match = st.sidebar.selectbox(
        "Select Match",
        options=match_options["match_id"],
        format_func=lambda x: match_options.loc[match_options["match_id"] == x, "match_name"].iloc[0]
    )

    events = load_events(selected_match)

    if events.empty:
        st.error("No events found for the selected match.")
    else:
        # Team Selection
        team = st.sidebar.radio(
            "Select Team",
            options=events["team"].unique(),
            format_func=lambda x: x
        )
        team_data = events[events["team"] == team]

        # Metrics
        st.title(f"Shooting Report for {team}")
        shots = team_data[team_data["type"] == "Shot"]

        if shots.empty:
            st.warning("No shots found for this team in the selected match.")
        else:
            # Process and Validate Shot Data
            def extract_coordinates(location_column, index):
                return location_column.apply(lambda loc: loc[index] if isinstance(loc, list) and len(loc) > index else np.nan)

            shots["x"] = extract_coordinates(shots["location"], 0)
            shots["y"] = extract_coordinates(shots["location"], 1)
            shots = shots.dropna(subset=["x", "y"])  # Remove invalid coordinates

            # Add color mapping for shot outcomes
            outcome_color_map = {
                "Goal": "green",
                "On Target": "yellow",
                "Off Target": "red",
                "Blocked": "orange"
            }
            shots["outcome_color"] = shots["shot_outcome"].map(outcome_color_map).fillna("grey")

            # Validate `outcome_color`
            valid_colors = {"green", "yellow", "red", "orange", "grey"}
            shots = shots[shots["outcome_color"].isin(valid_colors)]

            # Calculate Metrics
            shots_taken = len(shots)
            shots_on_target = len(shots[shots["shot_outcome"].isin(["On Target", "Goal"])])
            shot_conversion_rate = len(shots[shots["shot_outcome"] == "Goal"]) / shots_taken * 100 if shots_taken > 0 else 0
            goals_per_game = len(shots[shots["shot_outcome"] == "Goal"])
            expected_goals = shots["shot_statsbomb_xg"].sum()

            # Display Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Shots Taken", shots_taken)
            col2.metric("Shots on Target", shots_on_target)
            col3.metric("Shot Conversion Rate", f"{shot_conversion_rate:.2f}%")
            col4.metric("Goals", goals_per_game)
            col5.metric("Expected Goals (xG)", f"{expected_goals:.2f}")

            # Visualize Shot Locations on Field
            st.subheader("Shot Locations on Field")
            pitch_fig = px.scatter(
                shots,
                x="x",
                y="y",
                color="outcome_color",
                labels={"x": "Field Length", "y": "Field Width", "outcome_color": "Shot Outcome"},
                title="Shots Taken",
                color_discrete_map=outcome_color_map,
                hover_data=["shot_outcome", "shot_statsbomb_xg"]
            )
            st.plotly_chart(pitch_fig, use_container_width=True)

            # Visualize Shot Outcomes on Goal
            st.subheader("Shot Outcomes on Goal")
            goal_shots = shots[shots["shot_end_location"].notnull()]
            goal_shots["goal_x"] = extract_coordinates(goal_shots["shot_end_location"], 0)
            goal_shots["goal_y"] = extract_coordinates(goal_shots["shot_end_location"], 1)
            goal_shots = goal_shots.dropna(subset=["goal_x", "goal_y"])  # Remove invalid goal locations

            goal_fig = px.scatter(
                goal_shots,
                x="goal_x",
                y="goal_y",
                color="outcome_color",
                labels={"goal_x": "Goal Width", "goal_y": "Goal Height", "outcome_color": "Shot Outcome"},
                title="Shot Outcomes on Goal",
                color_discrete_map=outcome_color_map,
                hover_data=["shot_outcome", "shot_statsbomb_xg"]
            )
            st.plotly_chart(goal_fig, use_container_width=True)
