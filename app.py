import pandas as pd
import streamlit as st
import plotly.express as px
from statsbombpy import sb
from mplsoccer import VerticalPitch

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Soccer Team Shooting Report", page_icon="⚽")

# Function to load matches
@st.cache_data
def load_matches(competition_id, season_id):
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        return matches
    except Exception as e:
        st.error(f"Error loading matches: {e}")
        return pd.DataFrame()

# Function to load events for a match
@st.cache_data
def load_events(match_id):
    try:
        events = sb.events(match_id)
        return events
    except Exception as e:
        st.error(f"Error loading events: {e}")
        return pd.DataFrame()

# Main app
st.title("Soccer Team Shooting Report")

# Sidebar for competition, season, and match selection
with st.sidebar:
    st.header("Match Selection")

    # Step 1: Select competition and season
    competitions = sb.competitions()
    competition_options = competitions[["competition_id", "competition_name"]].drop_duplicates()
    competition_id = st.selectbox("Select Competition", competition_options["competition_id"].unique(), 
                                  format_func=lambda x: competition_options[competition_options["competition_id"] == x]["competition_name"].values[0])

    if competition_id:
        seasons = competitions[competitions["competition_id"] == competition_id][["season_id", "season_name"]]
        season_id = st.selectbox("Select Season", seasons["season_id"].unique(), 
                                 format_func=lambda x: seasons[seasons["season_id"] == x]["season_name"].values[0])

        if season_id:
            # Step 2: Select match
            matches = load_matches(competition_id=competition_id, season_id=season_id)
            if matches.empty:
                st.error("No matches found for the selected competition and season.")
            else:
                match_options = matches[["match_id", "home_team", "away_team", "match_date"]]
                match_id = st.selectbox(
                    "Select Match",
                    match_options["match_id"],
                    format_func=lambda x: f"{match_options[match_options['match_id'] == x]['home_team'].values[0]} vs {match_options[match_options['match_id'] == x]['away_team'].values[0]}"
                )

if competition_id and season_id and match_id:
    # Load events for the selected match
    events = load_events(match_id)

    if events.empty:
        st.error("No events found for the selected match.")
    else:
        # Debug: Display the available columns
        st.write("**Available Columns in Events Data:**", events.columns.tolist())

        # Step 3: Toggle between team stats
        team_selector = st.radio("Select Team", ["Home Team", "Away Team"])
        if team_selector == "Home Team":
            team = matches[matches["match_id"] == match_id]["home_team"].values[0]
        else:
            team = matches[matches["match_id"] == match_id]["away_team"].values[0]

        st.subheader(f"{team} Shooting Report")

        # Filter events for the selected team
        team_data = events[events["team"] == team]

        if "type" not in team_data.columns or "shot_outcome" not in team_data.columns or "location" not in team_data.columns:
            st.error("The events data does not contain required columns for analysis (e.g., 'type', 'shot_outcome', 'location').")
        else:
            # Shooting metrics
            shots_taken = len(team_data[team_data["type"] == "Shot"])
            shots_on_target = len(team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "On Target")])
            goals = len(team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "Goal")])
            xg = team_data[team_data["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in team_data.columns else 0
            conversion_rate = goals / shots_taken * 100 if shots_taken > 0 else 0

            # Display shooting metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Shots Taken", shots_taken)
            col2.metric("Shots on Target", shots_on_target)
            col3.metric("Shot Conversion Rate (%)", f"{conversion_rate:.2f}")
            col4.metric("Goals", goals)
            col5.metric("Expected Goals (xG)", f"{xg:.2f}")

            # Match date
            match_date = matches[matches["match_id"] == match_id]["match_date"].values[0]
            st.write(f"**Match Date:** {match_date}")

            # Shooting visuals
            st.write("### Shooting Locations")
            pitch = VerticalPitch(pitch_type="statsbomb", half=True)
            fig, ax = pitch.draw(figsize=(10, 7))

            # Add shot dots
            shot_data = team_data[team_data["type"] == "Shot"]
            for _, shot in shot_data.iterrows():
                if pd.notnull(shot["location"]) and len(shot["location"]) == 2:
                    x, y = shot["location"]  # Extract x and y from location
                    color = (
                        "green" if shot["shot_outcome"] == "Goal" else 
                        "yellow" if shot["shot_outcome"] == "On Target" else "red"
                    )
                    pitch.scatter(x, y, color=color, s=100, ax=ax)

            st.pyplot(fig)

            st.write("### Shot Outcomes in Goal")
            goal = VerticalPitch(pitch_type="statsbomb", half=True, goal_type='line')
            fig_goal, ax_goal = goal.draw(figsize=(10, 5))

            for _, shot in shot_data.iterrows():
                if pd.notnull(shot["shot_end_location"]) and len(shot["shot_end_location"]) == 2:
                    end_x, end_y = shot["shot_end_location"]  # Extract x and y from shot_end_location
                    color = (
                        "green" if shot["shot_outcome"] == "Goal" else 
                        "yellow" if shot["shot_outcome"] == "On Target" else "red"
                    )
                    goal.scatter(end_x, end_y, color=color, s=100, ax=ax_goal)

            st.pyplot(fig_goal)
