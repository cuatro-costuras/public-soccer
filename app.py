import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Function to dynamically generate the soccer goal visualization
def plot_goal_visualization(goal_data):
    fig, ax = plt.subplots(figsize=(6, 4))
    pitch = VerticalPitch(half=True, goal_type='box', pitch_color='white', line_color='black')
    pitch.draw(ax=ax)

    # Goal dimensions
    goal_width = 7.32  # in meters
    goal_height = 2.44  # in meters
    ax.set_xlim([-1, goal_width + 1])  # Extra space for missed shots
    ax.set_ylim([0, goal_height + 1])

    # Plot each shot
    for shot in goal_data:
        x, y = shot['x'], shot['y']
        outcome = shot['outcome']
        if outcome == 'goal':
            color = 'green'
        elif outcome == 'saved':
            color = 'blue'
        else:  # Missed shot
            color = 'red'
        ax.scatter(x, y, c=color, edgecolors='black', linewidth=0.5, s=100)

    # Add labels and legend
    ax.set_title('Shot Locations in Goal')
    ax.set_xlabel('Goal Width (meters)')
    ax.set_ylabel('Goal Height (meters)')
    ax.legend(['Goal (Green)', 'Saved (Blue)', 'Missed (Red)'], loc='upper left')

    st.pyplot(fig)

# Sample data for the shot visualizations
field_shots = [
    {'x': 20, 'y': 30, 'outcome': 'goal'},
    {'x': 30, 'y': 50, 'outcome': 'saved'},
    {'x': 40, 'y': 25, 'outcome': 'miss'}
]

goal_shots = [
    {'x': 1.5, 'y': 1.2, 'outcome': 'goal'},
    {'x': 6.5, 'y': 2.0, 'outcome': 'saved'},
    {'x': 0.0, 'y': 3.0, 'outcome': 'miss'}
]

# Streamlit App
st.title("Soccer Match Analysis")
st.markdown("Analyze team performance and shot locations in a soccer match.")

# Dropdowns for league, season, and match
league = st.selectbox("Select League", ["League A", "League B", "League C"])
season = st.selectbox("Select Season", ["2022/2023", "2023/2024"])
match = st.selectbox("Select Match", ["Team A vs Team B", "Team C vs Team D"])

# Button for selecting team
st.markdown("### Select Team to Analyze")
col1, col2 = st.columns(2)
if col1.button("Team A"):
    selected_team = "Team A"
elif col2.button("Team B"):
    selected_team = "Team B"

if 'selected_team' in locals():
    st.markdown(f"### Analyzing: {selected_team}")

    # Displaying match score
    st.markdown(f"**Match Score:** Team A 2 - 1 Team B")

    # Metrics at the top
    st.markdown("### Performance Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Shots", len(field_shots))
    col2.metric("Shots on Target", sum(1 for shot in field_shots if shot['outcome'] in ['goal', 'saved']))
    col3.metric("Shot Conversion Rate", "50%")
    col4.metric("Goals", sum(1 for shot in field_shots if shot['outcome'] == 'goal'))
    col5.metric("Expected Goals (xG)", "1.25")  # Example xG value

    # Visualizations
    st.markdown("### Shot Locations on the Field")
    field_fig, field_ax = plt.subplots(figsize=(10, 6))
    field_pitch = VerticalPitch(pitch_color='grass', line_color='white', pitch_type='statsbomb')
    field_pitch.draw(ax=field_ax)

    # Plot field shots
    for shot in field_shots:
        x, y, outcome = shot['x'], shot['y'], shot['outcome']
        color = 'green' if outcome == 'goal' else 'blue' if outcome == 'saved' else 'red'
        field_ax.scatter(x, y, c=color, edgecolors='black', s=100)
    st.pyplot(field_fig)

    st.markdown("### Shot Locations in the Goal")
    plot_goal_visualization(goal_shots)

else:
    st.markdown("Please select a team to analyze.")
