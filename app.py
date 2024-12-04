import pandas as pd
import streamlit as st
import plotly.express as px
from statsbombpy import sb
from mplsoccer import VerticalPitch

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Soccer Player Shooting Report", page_icon="⚽")

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
st.title("Soccer Player Shooting Report")

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
            match_options = matches[["match_id", "home_team", "away_team"]]
            match_id = st.selectbox(
                "Select Match",
                match_options["match_id"],
                format_func=lambda x: f"{match_options[match_options['match_id'] == x]['home_team'].values[0]} vs {match_options[match_options['match_id'] == x]['away_team'].values[0]}"
            )

            if match_id:
                # Load events for the selected match
                events = load_events(match_id)

                if events.empty:
                    st.error("No events found for the selected match.")
                else:
                    # Step 3: Toggle between team rosters
                    team_selector = st.radio("Select Team", ["Home Team", "Away Team"])
                    if team_selector == "Home Team":
                        team = matches[matches["match_id"] == match_id]["home_team"].values[0]
                    else:
                        team = matches[matches["match_id"] == match_id]["away_team"].values[0]

                    st.subheader(f"{team} Roster")

                    # Display roster
                    try:
                        # Extract players and positions from events DataFrame
                        if "player_name" in events.columns and "position_name" in events.columns:
                            roster = events[events["team"] == team][["player_name", "position_name"]].drop_duplicates()
                            st.table(roster)
                        else:
                            st.error("The events data does not contain 'player_name' or 'position_name' columns.")
                    except Exception as e:
                        st.error(f"Error extracting roster: {e}")

                    # Step 4: Select a player
                    if "player_name" in events.columns:
                        selected_player = st.selectbox("Select a Player", roster["player_name"].unique())
                    else:
                        selected_player = None
                        st.error("No players available for selection.")

                    # Step 5: Display player shooting report
                    if selected_player:
                        player_data = events[events["player_name"] == selected_player]
                        st.subheader(f"Shooting Report for {selected_player}")
                        
                        # Date of match
                        match_date = matches[matches["match_id"] == match_id]["match_date"].values[0]
                        st.write(f"**Match Date:** {match_date}")

                        # Shooting metrics
                        shots_taken = len(player_data[player_data["type"] == "Shot"])
                        shots_on_target = len(player_data[(player_data["type"] == "Shot") & (player_data["outcome"] == "On Target")])
                        goals = len(player_data[(player_data["type"] == "Shot") & (player_data["outcome"] == "Goal")])
                        xg = player_data[player_data["type"] == "Shot"]["xg"].sum()
                        conversion_rate = goals / shots_taken * 100 if shots_taken > 0 else 0

                        col1, col2, col3, col4, col5 = st.columns(5)
                        col1.metric("Shots Taken", shots_taken)
                        col2.metric("Shots on Target", shots_on_target)
                        col3.metric("Shot Conversion Rate (%)", f"{conversion_rate:.2f}")
                        col4.metric("Goals per Game", f"{goals:.2f}")
                        col5.metric("Expected Goals (xG)", f"{xg:.2f}")

                        # Step 6: Shooting visuals
                        st.write("### Shooting Locations")
                        pitch = VerticalPitch(pitch_type="statsbomb", half=True)
                        fig, ax = pitch.draw(figsize=(10, 7))

                        # Add shot dots
                        shot_data = player_data[player_data["type"] == "Shot"]
                        for _, shot in shot_data.iterrows():
                            color = (
                                "green" if shot["outcome"] == "Goal" else 
                                "yellow" if shot["outcome"] == "On Target" else "red"
                            )
                            pitch.scatter(shot["x"], shot["y"], color=color, s=100, ax=ax)

                        st.pyplot(fig)

                        st.write("### Shot Outcomes in Goal")
                        goal = VerticalPitch(pitch_type="statsbomb", half=True, goal_type='line')
                        fig_goal, ax_goal = goal.draw(figsize=(10, 5))

                        for _, shot in shot_data.iterrows():
                            color = (
                                "green" if shot["outcome"] == "Goal" else 
                                "yellow" if shot["outcome"] == "On Target" else "red"
                            )
                            goal.scatter(shot["end_x"], shot["end_y"], color=color, s=100, ax=ax_goal)

                        st.pyplot(fig_goal)
