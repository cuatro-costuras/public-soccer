import pandas as pd
import streamlit as st
from statsbombpy import sb
import plotly.graph_objects as go

# Cache data to avoid repeated fetching
@st.cache_data
def fetch_and_preprocess_data():
    # Fetch Bundesliga competition details
    competitions = sb.competitions()
    bundesliga = competitions[(competitions['competition_name'] == 'Bundesliga') & 
                               (competitions['season_name'] == '2023/2024')].iloc[0]
    competition_id = bundesliga['competition_id']
    season_id = bundesliga['season_id']

    # Fetch matches for the Bundesliga 2023/2024 season
    matches = sb.matches(competition_id=competition_id, season_id=season_id)

    # Get all match IDs
    match_ids = matches['match_id'].tolist()

    # Fetch events for each match and combine into a single DataFrame
    events_list = [sb.events(match_id=match_id) for match_id in match_ids]
    events = pd.concat(events_list, ignore_index=True)

    # Select relevant columns and preprocess
    relevant_columns = ['match_id', 'team', 'player', 'type', 'x', 'y', 'outcome', 'pass_end_x', 'pass_end_y']
    events = events[relevant_columns]

    return events, matches

# Fetch data
events_data, matches_data = fetch_and_preprocess_data()

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
position_skills = ["pass_end_x", "pass_end_y", "x", "y"]  # Replace with relevant skills

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
