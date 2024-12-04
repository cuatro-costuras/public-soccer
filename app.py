import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch, FontManager
import matplotlib.pyplot as plt

# Sample data for leagues, seasons, and matches
LEAGUES = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
SEASONS = ["2022/2023", "2023/2024"]
MATCHES = {
    "Premier League": [("Team A vs Team B", "2-1"), ("Team C vs Team D", "1-1")],
    "La Liga": [("Team E vs Team F", "3-2"), ("Team G vs Team H", "0-0")],
    "Bundesliga": [("Team I vs Team J", "4-3"), ("Team K vs Team L", "2-2")],
    # Add more matches as needed
}

# Sample shot data
FIELD_SHOTS = [
    {'x': 20, 'y': 30, 'outcome': 'goal'},
    {'x': 30, 'y': 50, 'outcome': 'saved'},
    {'x': 40, 'y': 25, 'outcome': 'miss'}
]

GOAL_SHOTS = [
    {'x': 1.5, 'y': 1.2, 'outcome': 'goal'},
    {'x': 6.5, 'y': 2.0, 'outcome': 'saved'},
    {'x': 3.0, 'y': 0.0, 'outcome': 'miss'}
]

# Function to plot the soccer field with shot locations
def plot_field_shots(field_shots):
    fig, ax = plt.subplots(figsize=(10, 6))
    pitch = VerticalPitch(pitch_color='grass', line_color='white', pitch_type='statsbomb')
    pitch.draw(ax=ax)

    for shot in field_shots:
        x, y, outcome = shot['x'], shot['y'], shot['outcome']
        color = 'green' if outcome == 'goal' else 'blue' if outcome == 'saved' else 'red'
        ax.scatter(x, y, c=color, edgecolors='black', s=100)

    ax.legend(['Goal (Green)', 'Saved (Blue)', 'Missed (Red)'], loc='upper left', fontsize=10)
    ax.set_title("Shot Locations on Field", fontsize=14)
    return fig

# Function to plot the soccer goal with shot locations
def plot_goal_shots(goal_shots):
    fig, ax = plt.subplots(figsize=(8, 4))
    goal_width, goal_height = 7.32, 2.44  # Dimensions in meters
    pitch = VerticalPitch(pitch_color='white', line_color='black', goal_type='box')
    pitch.goal(ax=ax)

    # Extend axes for shots outside the goal
    ax.set_xlim(-1, goal_width + 1)
    ax.set_ylim(-1, goal_height + 1)

    for shot in goal_shots:
        x, y, outcome = shot['x'], shot['y'], shot['outcome']
        color = 'green' if outcome == 'goal' else 'blue' if outcome == 'saved' else 'red'
        ax.scatter(x, y, c=color, edgecolors='black', s=100)

    ax.legend(['Goal (Green)', 'Saved (Blue)', 'Missed (Red)'], loc='upper left', fontsize=10)
    ax.set_title("Shot Locations in Goal", fontsize=14)
    return fig

# Streamlit App
st.title("Soccer Match Analysis")
st.markdown("Analyze team performance and shot locations in a soccer match.")

# Dropdowns for league, season, and match
selected_league = st.selectbox("Select League", LEAGUES)
selected_season = st.selectbox("Select Season", SEASONS)

# Filter matches based on league and season
if selected_league in MATCHES:
    matches = MATCHES[selected_league]
    match_labels = [f"{match[0]} (Score: {match[1]})" for match in matches]
    selected_match = st.selectbox("Select Match", match_labels)
else:
    st.error("No matches available for the selected league and season.")

# Extract match teams and score
if selected_match:
    match_teams, match_score = selected_match.split(" (Score: ")
    match_score = match_score.rstrip(")")
    home_team, away_team = match_teams.split(" vs ")

    # Display match score
    st.markdown(f"### Match Score: {home_team} {match_score} {away_team}")

    # Team selection buttons
    st.markdown("### Select Team to Analyze")
    col1, col2 = st.columns(2)
    selected_team = None
    if col1.button(home_team):
        selected_team = home_team
    elif col2.button(away_team):
        selected_team = away_team

    if selected_team:
        st.markdown(f"### Analyzing: {selected_team}")

        # Performance Metrics
        st.markdown("### Performance Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Shots", len(FIELD_SHOTS))
        col2.metric("Shots on Target", sum(1 for shot in FIELD_SHOTS if shot['outcome'] in ['goal', 'saved']))
        col3.metric("Shot Conversion Rate", f"{round((sum(1 for shot in FIELD_SHOTS if shot['outcome'] == 'goal') / len(FIELD_SHOTS)) * 100, 2)}%")
        col4.metric("Goals", sum(1 for shot in FIELD_SHOTS if shot['outcome'] == 'goal'))
        col5.metric("Expected Goals (xG)", "1.25")  # Placeholder

        # Visualizations
        st.markdown("### Shot Locations on the Field")
        field_fig = plot_field_shots(FIELD_SHOTS)
        st.pyplot(field_fig)

        st.markdown("### Shot Locations in the Goal")
        goal_fig = plot_goal_shots(GOAL_SHOTS)
        st.pyplot(goal_fig)

    else:
        st.warning("Please select a team to analyze.")
else:
    st.warning("Please select a match.")
