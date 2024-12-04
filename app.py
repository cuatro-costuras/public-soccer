import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Function to retrieve leagues, seasons, and matches dynamically (placeholder for real data)
def load_competitions():
    # Placeholder for dynamic retrieval; replace with actual API calls
    return [
        {"competition": "Premier League", "seasons": ["2022/2023", "2023/2024"]},
        {"competition": "La Liga", "seasons": ["2022/2023", "2023/2024"]},
        {"competition": "Bundesliga", "seasons": ["2022/2023", "2023/2024"]},
    ]

def load_matches(competition, season):
    # Placeholder for dynamic retrieval; replace with actual API calls
    return [
        {"home_team": "Team A", "away_team": "Team B", "score": "2-1"},
        {"home_team": "Team C", "away_team": "Team D", "score": "1-1"},
        {"home_team": "Team E", "away_team": "Team F", "score": "3-2"},
    ]

# Visualization for shot locations on the field
def plot_field_shots(field_shots):
    fig, ax = plt.subplots(figsize=(12, 8))  # Landscape mode
    pitch = VerticalPitch(pitch_color='grass', line_color='white', pitch_type='statsbomb')
    pitch.draw(ax=ax)

    for shot in field_shots:
        x, y, outcome = shot['x'], shot['y'], shot['outcome']
        color = 'green' if outcome == 'goal' else 'blue' if outcome == 'saved' else 'red'
        ax.scatter(x, y, c=color, edgecolors='black', s=100)

    ax.legend(['Goal (Green)', 'Saved (Blue)', 'Missed (Red)'], loc='upper left', fontsize=10)
    ax.set_title("Shot Location(s) On Field", fontsize=14)
    return fig

# Visualization for shot locations in the goal
def plot_goal_shots(goal_shots):
    fig, ax = plt.subplots(figsize=(8, 4))
    goal_width, goal_height = 7.32, 2.44  # Dimensions in meters

    # Draw the goal
    ax.plot([0, goal_width], [0, 0], color="black", lw=2)  # Bottom
    ax.plot([0, goal_width], [goal_height, goal_height], color="black", lw=2)  # Top
    ax.plot([0, 0], [0, goal_height], color="black", lw=2)  # Left
    ax.plot([goal_width, goal_width], [0, goal_height], color="black", lw=2)  # Right

    # Extend the axes for shots outside the goal
    ax.set_xlim(-1, goal_width + 1)
    ax.set_ylim(-1, goal_height + 1)

    for shot in goal_shots:
        x, y, outcome = shot['x'], shot['y'], shot['outcome']
        color = 'green' if outcome == 'goal' else 'blue' if outcome == 'saved' else 'red'
        ax.scatter(x, y, c=color, edgecolors='black', s=100)

    ax.legend(['Goal (Green)', 'Saved (Blue)', 'Missed (Red)'], loc='upper left', fontsize=10)
    ax.set_title("Shot Location(s) On Goal", fontsize=14)
    return fig

# Streamlit App
st.title("Soccer Match Analysis")
st.markdown("Analyze team performance and shot locations in a soccer match.")

# Step 1: Select League and Season
competitions = load_competitions()
league_names = [comp['competition'] for comp in competitions]
selected_league = st.selectbox("Select League", league_names)

selected_season = st.selectbox(
    "Select Season",
    next(comp['seasons'] for comp in competitions if comp['competition'] == selected_league),
)

# Step 2: Select Match
matches = load_matches(selected_league, selected_season)
match_labels = [f"{match['home_team']} vs {match['away_team']} (Score: {match['score']})" for match in matches]
selected_match = st.selectbox("Select Match", match_labels)

# Extract match details
if selected_match:
    match = next(
        match for match in matches if f"{match['home_team']} vs {match['away_team']} (Score: {match['score']})" == selected_match
    )
    home_team, away_team, score = match['home_team'], match['away_team'], match['score']
    st.markdown(f"### Match: {home_team} vs {away_team} | Score: {score}")

    # Step 3: Select Team to Analyze
    st.markdown("### Select Team to Analyze")
    col1, col2 = st.columns(2)
    selected_team = None
    if col1.button(home_team):
        selected_team = home_team
    elif col2.button(away_team):
        selected_team = away_team

    # Display Analysis
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
        st.markdown("### Shot Location(s) On Field")
        field_fig = plot_field_shots(FIELD_SHOTS)
        st.pyplot(field_fig)

        st.markdown("### Shot Location(s) On Goal")
        goal_fig = plot_goal_shots(GOAL_SHOTS)
        st.pyplot(goal_fig)

    else:
        st.warning("Please select a team to analyze.")
else:
    st.warning("Please select a match.")
