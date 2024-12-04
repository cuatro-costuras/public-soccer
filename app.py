import streamlit as st
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch

# Function to load matches
@st.cache_data
def load_matches(competition, season):
    matches = sb.matches(competition=competition, season=season)
    return matches

# Function to load events for a specific match
@st.cache_data
def load_match_events(match_id):
    events = sb.events(match_id=match_id)
    return events

# Filter shots from event data
def filter_shots(events):
    shots = events[events['type'] == 'Shot']
    return shots

# Filter roster from event data
def get_roster(events, team_name):
    players = events[events['team'] == team_name][['player', 'position']].drop_duplicates()
    players.columns = ['Player Name', 'Position']
    return players

# Plot player shot data
def plot_shots_on_pitch(player_shots):
    pitch = Pitch(pitch_type='statsbomb', figsize=(10, 6), line_color='black')
    fig, ax = pitch.draw()
    colors = {'Goal': 'green', 'On Target': 'yellow', 'Off Target': 'red'}

    for i, shot in player_shots.iterrows():
        color = colors['Goal'] if shot['outcome'] == 'Goal' else (
            colors['On Target'] if shot['outcome'] == 'On Target' else colors['Off Target'])
        pitch.scatter(shot['location'][0], shot['location'][1], c=color, s=100, ax=ax)
    
    st.pyplot(fig)

# Plot player shots on goal
def plot_shots_on_goal(player_shots):
    pitch = Pitch(goal_type='statsbomb', pitch_type='goal', figsize=(10, 6), line_color='black')
    fig, ax = pitch.draw()
    colors = {'Goal': 'green', 'On Target': 'yellow', 'Off Target': 'red'}

    for i, shot in player_shots.iterrows():
        color = colors['Goal'] if shot['outcome'] == 'Goal' else (
            colors['On Target'] if shot['outcome'] == 'On Target' else colors['Off Target'])
        pitch.scatter(shot['shot_end_location'][0], shot['shot_end_location'][1], c=color, s=100, ax=ax)
    
    st.pyplot(fig)

# Main app
st.set_page_config(layout="wide", page_title="Soccer Player Shooting Report", page_icon="⚽")
st.title("Soccer Player Shooting Report")

# 1) Select a match
st.sidebar.header("Select Match")
competition = st.sidebar.selectbox("Competition", ["Women's World Cup", "World Cup", "Bundesliga"])
season = st.sidebar.selectbox("Season", ["2023", "2022", "2021"])
matches = load_matches(competition=competition, season=season)

match_selection = st.sidebar.selectbox(
    "Select Match",
    matches[['home_team', 'away_team', 'match_date']].apply(
        lambda row: f"{row['home_team']} vs {row['away_team']} ({row['match_date']})", axis=1
    )
)
selected_match_id = matches.loc[
    matches[['home_team', 'away_team', 'match_date']].apply(
        lambda row: f"{row['home_team']} vs {row['away_team']} ({row['match_date']})", axis=1
    ) == match_selection, 'match_id'
].values[0]

events = load_match_events(selected_match_id)

# 2) Toggle team roster
teams = events['team'].unique()
selected_team = st.sidebar.radio("Select Team", teams)
team_roster = get_roster(events, selected_team)

st.write(f"### Roster for {selected_team}")
st.table(team_roster)

# 3) Select player
selected_player = st.selectbox("Select Player", team_roster['Player Name'])

# 4) Player Profile
if selected_player:
    st.write(f"### Player Profile: {selected_player}")
    player_shots = filter_shots(events[events['player'] == selected_player])

    # Metrics
    shots_taken = len(player_shots)
    shots_on_target = len(player_shots[player_shots['outcome'].isin(['Goal', 'On Target'])])
    goals = len(player_shots[player_shots['outcome'] == 'Goal'])
    conversion_rate = (goals / shots_taken * 100) if shots_taken > 0 else 0
    goals_per_game = goals  # Adjust for multiple games if needed
    expected_goals = player_shots['shot_statsbomb_xg'].sum()

    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Shots Taken", shots_taken)
    col2.metric("Shots on Target", shots_on_target)
    col3.metric("Conversion Rate", f"{conversion_rate:.2f}%")
    col4.metric("Goals/Game", goals_per_game)
    col5.metric("Expected Goals (xG)", f"{expected_goals:.2f}")

    # Visuals
    st.write("### Shooting Visuals")
    st.write("#### Shot Locations on Field")
    plot_shots_on_pitch(player_shots)

    st.write("#### Shot Locations on Goal")
    plot_shots_on_goal(player_shots)
