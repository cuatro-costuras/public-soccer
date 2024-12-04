import pandas as pd
import streamlit as st
import plotly.express as px
from statsbombpy import sb

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Soccer Team Shooting Report", page_icon="⚽")

# Helper Functions
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
st.title("Soccer Team Shooting Report")

# Fetch competitions and seasons
competitions = sb.competitions()
selected_competition = st.sidebar.selectbox("Select Competition", competitions["competition_name"].unique())
filtered_competitions = competitions[competitions["competition_name"] == selected_competition]
selected_season = st.sidebar.selectbox("Select Season", filtered_competitions["season_name"].unique())

if selected_competition and selected_season:
    competition_id = filtered_competitions["competition_id"].iloc[0]
    season_id = filtered_competitions[filtered_competitions["season_name"] == selected_season]["season_id"].iloc[0]

    matches = load_matches(competition_id, season_id)

    if not matches.empty:
        matches["match_name"] = matches["home_team"] + " vs " + matches["away_team"]
        match_dropdown = matches.set_index("match_id")["match_name"].to_dict()
        selected_match_id = st.sidebar.selectbox("Select Match", options=list(match_dropdown.keys()), format_func=lambda x: match_dropdown[x])

        if selected_match_id:
            events = load_events(selected_match_id)
            teams = events["team"].unique()
            selected_team = st.sidebar.selectbox("Select Team", teams)

            if selected_team:
                st.header(f"Team Report: {selected_team}")
                team_data = events[events["team"] == selected_team]

                # Calculate Team Metrics
                total_shots = len(team_data[team_data["type"] == "Shot"])
                shots_on_target = len(team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "On Target")])
                goals = len(team_data[(team_data["type"] == "Shot") & (team_data["shot_outcome"] == "Goal")])
                xg = team_data["shot_statsbomb_xg"].sum()
                matches_played = matches[matches["home_team"] == selected_team].shape[0] + \
                                 matches[matches["away_team"] == selected_team].shape[0]
                goals_per_game = goals / matches_played if matches_played > 0 else 0

                # Display Metrics in Boxes
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Shots", total_shots)
                col2.metric("Shots on Target", shots_on_target)
                col3.metric("Shot Conversion Rate", f"{(goals / total_shots * 100) if total_shots > 0 else 0:.2f}%")
                col4.metric("Goals per Game", f"{goals_per_game:.2f}")
                col5.metric("Expected Goals (xG)", f"{xg:.2f}")

                # Visuals
                st.subheader("Shooting Locations")

                # Soccer Pitch Visual
                pitch_data = team_data[team_data["type"] == "Shot"]
                pitch_data = pitch_data[pitch_data["location"].notnull()]

                if not pitch_data.empty:
                    pitch_data["x"] = pitch_data["location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
                    pitch_data["y"] = pitch_data["location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

                    pitch_data["shot_color"] = pitch_data["shot_outcome"].map(
                        {"Goal": "green", "On Target": "yellow", "Off Target": "red"}
                    )

                    st.plotly_chart(
                        px.scatter(
                            pitch_data,
                            x="x",
                            y="y",
                            color="shot_color",
                            title="Shot Locations on the Pitch",
                            labels={"x": "Field Width", "y": "Field Length", "shot_color": "Shot Outcome"},
                            color_discrete_map={"green": "Goal", "yellow": "On Target", "red": "Off Target"},
                            size_max=10
                        ),
                        use_container_width=True
                    )

                # Goal Visual
                st.subheader("Shot Outcomes")
                goal_data = pitch_data.copy()

                goal_data["goal_x"] = goal_data["shot_end_location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
                goal_data["goal_y"] = goal_data["shot_end_location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

                if not goal_data.empty:
                    st.plotly_chart(
                        px.scatter(
                            goal_data,
                            x="goal_x",
                            y="goal_y",
                            color="shot_color",
                            title="Shot Outcomes on Goal",
                            labels={"goal_x": "Goal Width", "goal_y": "Goal Height", "shot_color": "Shot Outcome"},
                            color_discrete_map={"green": "Goal", "yellow": "On Target", "red": "Off Target"},
                            size_max=10
                        ),
                        use_container_width=True
                    )
                else:
                    st.write("No goal data available.")
            else:
                st.write("Please select a team.")
    else:
        st.error("No matches found for the selected competition and season.")
else:
    st.write("Please select a competition and season.")
