import pandas as pd
import streamlit as st
from statsbombpy import sb
import plotly.graph_objects as go

# Cache data to avoid repeated fetching
@st.cache_data
def fetch_and_preprocess_data():
    # Fetch all competitions
    competitions = sb.competitions()

    # Filter for Bundesliga 2023/2024
    bundesliga = competitions[
        (competitions['competition_name'] == 'Bundesliga') &
        (competitions['season_name'] == '2023/2024')
    ]

    if bundesliga.empty:
        st.error("No data found for Bundesliga 2023/2024. Please verify competition and season availability.")
        return pd.DataFrame(), pd.DataFrame()

    competition_id = bundesliga['competition_id'].iloc[0]
    season_id = bundesliga['season_id'].iloc[0]

    # Fetch matches for the Bundesliga 2023/2024 season
    matches = sb.matches(competition_id=competition_id, season_id=season_id)

    if matches.empty:
        st.error("No match data found for Bundesliga 2023/2024.")
        return pd.DataFrame(), pd.DataFrame()

    # Get all match IDs
    match_ids = matches['match_id'].tolist()

    # Fetch events for each match and combine into a single DataFrame
    events_list = []
    for match_id in match_ids:
        try:
            events = sb.events(match_id=match_id)
            events_list.append(events)
        except Exception as e:
            st.warning(f"Could not fetch events for match {match_id}: {e}")

    if not events_list:
        st.error("No event data available for the selected matches.")
        return pd.DataFrame(), matches

    events = pd.concat(events_list, ignore_index=True)

    # Select relevant columns and preprocess
    relevant_columns = ['match_id', 'team', 'player', 'type', 'x', 'y', 'outcome', 'pass_end_x', 'pass_end_y']
    events = events[relevant_columns]

    return events, matches

# Fetch data
events_data, matches_data = fetch_and_preprocess_data()

# App starts here
if not events_data.empty and not matches_data.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    teams = events_data['team'].unique()
    selected_team = st.sidebar.selectbox("Select Team", teams)

    players = events_data[events_data['team'] == selected_team]['player'].unique()
    selected_player = st.sidebar.selectbox("Select Player", players)

    # Display Player Profile
    st.title(f"{selected_player}'s Performance")
    st.write(f"Team: {selected_team}")

    # Position-Specific Radar Plot
    st.header("Radar Plot")
    position_skills = ["x", "y", "pass_end_x", "pass_end_y"]  # Replace with relevant skills

    # Generate Radar Data
    player_data = events_data[events_data['player'] == selected_player]
    average_skills = [player_data[col].mean() for col in position_skills]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=average_skills,
        theta=position_skills,
        fill='toself',
        name=selected_player
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    st.plotly_chart(fig)

    # Percentile Rankings
    st.header("Percentile Rankings")
    percentile_skills = ["x", "y", "pass_end_x", "pass_end_y"]  # Replace with relevant stats
    for skill in percentile_skills:
        value = player_data[skill].mean()
        st.write(f"### {skill}: {value:.2f}")
        st.progress(int((value / 100) * 100))
else:
    st.error("Unable to load data. Please ensure the competition and season are available.")
