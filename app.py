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
competition_id = st.selectbox("Select Competition", competition_options["competition_id"].unique())

if competition_id:
    seasons = competitions[competitions["competition_id"] == competition_id][["season_id", "season_name"]]
    season_id = st.selectbox("Select Season", seasons["season_id"].unique())

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
                        # Extract players and positions
                        roster = events[events["team"] == team][["player", "position_name"]].drop_duplicates()
                        st.table(roster)
                    except KeyError:
                        st.error("The required columns for roster are not available in the events data.")

                    # Step 4: Select a player
                    selected_player = st.selectbox("Select a Player", roster["player"].unique())
                    if selected_player:
                        player_events = events[events["player"] == selected_player]

                        # Step 5: Player profile
                        st.subheader(f"{selected_player} - Shooting Report")
                        date = matches[matches["match_id"] == match_id]["match_date"].values[0]
                        st.write(f"Match Date: {date}")

                        shots = player_events[player_events["type"] == "Shot"]
                        goals = shots[shots["shot_outcome"] == "Goal"]
                        shots_on_target = shots[shots["shot_outcome"].isin(["Goal", "Saved"])]
                        expected_goals = shots["shot_statsbomb_xg"].sum()

                        metrics = {
                            "Shots Taken": len(shots),
                            "Shots on Target": len(shots_on_target),
                            "Shot Conversion Rate (%)": (len(goals) / len(shots) * 100) if len(shots) > 0 else 0,
                            "Goals per Game": len(goals),
                            "Expected Goals (xG)": expected_goals,
                        }

                        col1, col2, col3, col4, col5 = st.columns(5)
                        col1.metric("Shots Taken", metrics["Shots Taken"])
                        col2.metric("Shots on Target", metrics["Shots on Target"])
                        col3.metric("Conversion Rate (%)", f"{metrics['Shot Conversion Rate (%)']:.2f}")
                        col4.metric("Goals per Game", metrics["Goals per Game"])
                        col5.metric("Expected Goals (xG)", f"{metrics['Expected Goals (xG'):.2f}")

                        # Step 6: Visualizations
                        st.write("### Shooting Visualizations")

                        # Soccer pitch plot
                        pitch = VerticalPitch(pitch_type='statsbomb', half=True)
                        fig, ax = pitch.draw(figsize=(10, 6))
                        for _, shot in shots.iterrows():
                            color = "green" if shot["shot_outcome"] == "Goal" else ("yellow" if shot["shot_outcome"] == "Saved" else "red")
                            pitch.scatter(shot["location"][0], shot["location"][1], ax=ax, color=color, s=100)
                        st.pyplot(fig)

                        # Soccer goal plot
                        fig, ax = pitch.draw_goal(figsize=(10, 6))
                        for _, shot in shots.iterrows():
                            color = "green" if shot["shot_outcome"] == "Goal" else ("yellow" if shot["shot_outcome"] == "Saved" else "red")
                            pitch.scatter(shot["shot_end_location"][0], shot["shot_end_location"][1], ax=ax, color=color, s=100)
                        st.pyplot(fig)
