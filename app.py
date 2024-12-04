import pandas as pd
import numpy as np
import streamlit as st
from statsbombpy import sb
from mplsoccer import Pitch

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Soccer Player Shooting Report", page_icon="⚽")

# Function to load competitions
@st.cache_data
def load_competitions():
    """
    Fetch available competitions.
    """
    try:
        return sb.competitions()
    except Exception as e:
        st.error(f"Error loading competitions: {e}")
        return pd.DataFrame()

# Function to load matches
@st.cache_data
def load_matches(competition_id, season_id):
    """
    Fetch matches for a given competition and season.
    """
    try:
        return sb.matches(competition_id=competition_id, season_id=season_id)
    except Exception as e:
        st.error(f"Error loading matches: {e}")
        return pd.DataFrame()

# Function to load events for a specific match
@st.cache_data
def load_match_events(match_id):
    """
    Fetch events for a specific match.
    """
    try:
        return sb.events(match_id=match_id)
    except Exception as e:
        st.error(f"Error loading match events: {e}")
        return pd.DataFrame()

# Main App
st.title("Soccer Player Shooting Report")

# Step 1: Select a competition and season
st.sidebar.header("Match Selector")
competitions = load_competitions()

if not competitions.empty:
    competition_name = st.sidebar.selectbox("Select Competition", competitions["competition_name"].unique())
    competition_data = competitions[competitions["competition_name"] == competition_name]
    season = st.sidebar.selectbox("Select Season", competition_data["season_name"])

    if competition_name and season:
        competition_id = competition_data["competition_id"].values[0]
        season_id = competition_data[competition_data["season_name"] == season]["season_id"].values[0]

        # Step 2: Load matches
        matches = load_matches(competition_id, season_id)
        if matches.empty:
            st.error("No matches found for the selected competition and season.")
        else:
            match = st.sidebar.selectbox(
                "Select Match",
                matches["match_id"].unique(),
                format_func=lambda x: f"{matches[matches['match_id'] == x]['home_team'].values[0]} vs {matches[matches['match_id'] == x]['away_team'].values[0]}"
            )

            if match:
                # Step 3: Load match events
                events = load_match_events(match)
                if events.empty:
                    st.error("No events found for the selected match.")
                else:
                    # Step 4: Toggle between team rosters
                    team_selector = st.radio("Select Team", ["Home Team", "Away Team"])
                    if team_selector == "Home Team":
                        team = matches[matches["match_id"] == match]["home_team"].values[0]
                    else:
                        team = matches[matches["match_id"] == match]["away_team"].values[0]

                    st.subheader(f"{team} Roster")
                    roster = events[events["team"] == team][["player_name", "position"]].drop_duplicates()
                    st.table(roster)

                    # Step 5: Select a player
                    player = st.selectbox("Select a Player", roster["player_name"].unique())

                    if player:
                        player_events = events[events["player_name"] == player]

                        # Player metrics
                        shots_taken = len(player_events[player_events["type"] == "Shot"])
                        shots_on_target = len(player_events[(player_events["type"] == "Shot") & (player_events["shot_outcome"] == "On Target")])
                        goals = len(player_events[(player_events["type"] == "Shot") & (player_events["shot_outcome"] == "Goal")])
                        games_played = len(player_events["match_id"].unique())
                        xg = player_events["shot_statsbomb_xg"].sum()

                        # Metrics boxes
                        st.subheader(f"Performance Metrics for {player}")
                        col1, col2, col3, col4, col5 = st.columns(5)
                        col1.metric("Shots Taken", shots_taken)
                        col2.metric("Shots on Target", shots_on_target)
                        col3.metric("Shot Conversion Rate", f"{(goals / shots_taken * 100):.1f}%" if shots_taken > 0 else "0%")
                        col4.metric("Goals per Game", f"{(goals / games_played):.2f}" if games_played > 0 else "0")
                        col5.metric("Expected Goals (xG)", f"{xg:.2f}")

                        # Step 6: Visualize shooting tendencies
                        st.subheader("Shooting Tendencies")
                        pitch = Pitch(pitch_type='statsbomb', line_color='black')

                        # Field positions for shots
                        st.write("Shot Locations on the Field")
                        fig, ax = pitch.draw(figsize=(10, 6))
                        for _, shot in player_events[player_events["type"] == "Shot"].iterrows():
                            color = "green" if shot["shot_outcome"] == "Goal" else "yellow" if shot["shot_outcome"] == "On Target" else "red"
                            pitch.scatter(shot["location_x"], shot["location_y"], c=color, ax=ax, s=100)
                        st.pyplot(fig)

                        # Goal visualization
                        st.write("Shot Outcomes in Goal")
                        goal_fig, goal_ax = pitch.draw(figsize=(10, 6), pitch_type="statsbomb", goal_type="statsbomb")
                        for _, shot in player_events[player_events["type"] == "Shot"].iterrows():
                            color = "green" if shot["shot_outcome"] == "Goal" else "yellow" if shot["shot_outcome"] == "On Target" else "red"
                            pitch.scatter(shot["shot_end_location_x"], shot["shot_end_location_y"], c=color, ax=goal_ax, s=100)
                        st.pyplot(goal_fig)
