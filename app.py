import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Mock functions to load competitions, matches, and events dynamically
def load_competitions():
    return pd.DataFrame({
        "competition": ["Premier League", "La Liga", "Bundesliga"],
        "seasons": [["2022/2023", "2023/2024"], ["2022/2023"], ["2023/2024"]],
    })

def load_matches(competition, season):
    if competition == "Premier League" and season == "2022/2023":
        return pd.DataFrame({
            "home_team": ["Manchester City", "Chelsea"],
            "away_team": ["Liverpool", "Arsenal"],
            "score": ["3-1", "2-2"],
        })
    else:
        return pd.DataFrame({
            "home_team": ["Team A", "Team B"],
            "away_team": ["Team C", "Team D"],
            "score": ["0-0", "1-1"],
        })

def load_team_events(team_name):
    return pd.DataFrame({
        "x": [30, 50, 70],
        "y": [20, 40, 60],
        "outcome": ["goal", "saved", "missed"],
        "goal_x": [2.5, 4.5, 7],
        "goal_y": [1, 1.5, 3],
    })

# Visualization for shot locations on the field
def plot_field_shots(events):
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = VerticalPitch(pitch_color='grass', line_color='white', pitch_type='statsbomb')
    pitch.draw(ax=ax)
    for _, row in events.iterrows():
        color = "green" if row["outcome"] == "goal" else "blue" if row["outcome"] == "saved" else "red"
        ax.scatter(row["x"], row["y"], c=color, edgecolors='black', s=100)
    ax.legend(["Goal", "Saved", "Missed"], loc='upper left')
    ax.set_title("Shot Location(s) On Field", fontsize=14)
    return fig

# Visualization for shot locations in the goal
def plot_goal_shots(events):
    fig, ax = plt.subplots(figsize=(8, 4))
    goal_width, goal_height = 7.32, 2.44
    ax.plot([0, goal_width], [0, 0], color="black", lw=2)
    ax.plot([0, goal_width], [goal_height, goal_height], color="black", lw=2)
    ax.plot([0, 0], [0, goal_height], color="black", lw=2)
    ax.plot([goal_width, goal_width], [0, goal_height], color="black", lw=2)
    ax.set_xlim(-1, goal_width + 1)
    ax.set_ylim(-1, goal_height + 1)
    for _, row in events.iterrows():
        color = "green" if row["outcome"] == "goal" else "blue" if row["outcome"] == "saved" else "red"
        ax.scatter(row["goal_x"], row["goal_y"], c=color, edgecolors='black', s=100)
    ax.legend(["Goal", "Saved", "Missed"], loc='upper left')
    ax.set_title("Shot Location(s) On Goal", fontsize=14)
    return fig

# Streamlit App
st.title("Soccer Match Analysis")

# Step 1: Select League and Season
competitions_df = load_competitions()
league_options = competitions_df["competition"].tolist()
selected_league = st.selectbox("Select League", league_options)

if selected_league:
    season_options = competitions_df[competitions_df["competition"] == selected_league]["seasons"].values[0]
    selected_season = st.selectbox("Select Season", season_options)

    # Step 2: Select Match
    matches_df = load_matches(selected_league, selected_season)
    match_labels = matches_df.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (Score: {row['score']})", axis=1)
    selected_match = st.selectbox("Select Match", match_labels)

    if selected_match:
        selected_row = matches_df.loc[matches_df.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (Score: {row['score']})", axis=1) == selected_match].iloc[0]
        home_team = selected_row["home_team"]
        away_team = selected_row["away_team"]
        score = selected_row["score"]

        st.markdown(f"### Match: {home_team} vs {away_team} | Score: {score}")

        # Step 3: Select Team
        st.markdown("### Select Team to Analyze")
        col1, col2 = st.columns(2)
        selected_team = None
        if col1.button(home_team):
            selected_team = home_team
        elif col2.button(away_team):
            selected_team = away_team

        if selected_team:
            st.markdown(f"### Analyzing: {selected_team}")

            # Load Events for the Selected Team
            team_events = load_team_events(selected_team)

            # Performance Metrics
            st.markdown("### Performance Metrics")
            col1, col2, col3, col4, col5 = st.columns(5)
            total_shots = len(team_events)
            shots_on_target = team_events[team_events["outcome"].isin(["goal", "saved"])].shape[0]
            shot_conversion_rate = f"{(team_events[team_events['outcome'] == 'goal'].shape[0] / total_shots * 100):.2f}%" if total_shots > 0 else "0%"
            goals = team_events[team_events["outcome"] == "goal"].shape[0]
            expected_goals = 1.25  # Placeholder

            col1.metric("Total Shots", total_shots)
            col2.metric("Shots on Target", shots_on_target)
            col3.metric("Shot Conversion Rate", shot_conversion_rate)
            col4.metric("Goals", goals)
            col5.metric("Expected Goals (xG)", expected_goals)

            # Visualizations
            st.markdown("### Shot Location(s) On Field")
            field_fig = plot_field_shots(team_events)
            st.pyplot(field_fig)

            st.markdown("### Shot Location(s) On Goal")
            goal_fig = plot_goal_shots(team_events)
            st.pyplot(goal_fig)

        else:
            st.warning("Please select a team to analyze.")
    else:
        st.warning("Please select a match.")
