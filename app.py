import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Mock data-loading functions for matches and events
def load_competitions():
    return pd.DataFrame({
        "competition": ["Premier League", "La Liga"],
        "seasons": [["2022/2023", "2023/2024"], ["2022/2023"]],
    })

def load_matches(competition, season):
    matches = {
        "Premier League_2022/2023": [
            {"match_id": 1, "home_team": "Manchester City", "away_team": "Liverpool"},
            {"match_id": 2, "home_team": "Chelsea", "away_team": "Arsenal"}
        ],
        "La Liga_2022/2023": [
            {"match_id": 3, "home_team": "Real Madrid", "away_team": "Atletico Madrid"},
            {"match_id": 4, "home_team": "Barcelona", "away_team": "Sevilla"}
        ],
    }
    key = f"{competition}_{season}"
    return pd.DataFrame(matches.get(key, []))

def load_events():
    return pd.DataFrame({
        "match_id": [1, 1, 1, 2, 2, 3, 3],
        "team": ["Manchester City", "Manchester City", "Liverpool", "Chelsea", "Arsenal", "Real Madrid", "Atletico Madrid"],
        "type": ["Shot", "Shot", "Shot", "Shot", "Shot", "Shot", "Shot"],
        "outcome": ["goal", "saved", "missed", "goal", "missed", "saved", "missed"],
        "x": [30, 50, 70, 40, 60, 20, 80],
        "y": [20, 40, 60, 30, 70, 10, 90],
        "goal_x": [2.5, 4.5, 7, 3, 6, 5, 8],
        "goal_y": [1, 1.5, 3, 0.5, 2, 2.5, 1],
    })

def load_team_events(team_name, match_id):
    events = load_events()
    return events[(events["team"] == team_name) & (events["match_id"] == match_id)]

# Visualization Functions
def plot_field_shots(events, goal_center):
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = VerticalPitch(pitch_color='grass', line_color='white', pitch_type='statsbomb')
    pitch.draw(ax=ax)
    
    for _, row in events.iterrows():
        color = "green" if row["outcome"] == "goal" else "blue" if row["outcome"] == "saved" else "red"
        ax.scatter(row["x"], row["y"], c=color, edgecolors='black', s=100)
        if goal_center:
            ax.plot([row["x"], goal_center[0]], [row["y"], goal_center[1]], color=color, linestyle="dotted", lw=1.5)

    legend_patches = [
        Rectangle((0, 0), 1, 1, color="green", label="Goal"),
        Rectangle((0, 0), 1, 1, color="blue", label="Saved"),
        Rectangle((0, 0), 1, 1, color="red", label="Missed"),
    ]
    ax.legend(handles=legend_patches, loc='upper left', fontsize=10)
    ax.set_title("Shot Location(s) On Field", fontsize=14)
    return fig

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
        if 0 <= row["goal_x"] <= goal_width and 0 <= row["goal_y"] <= goal_height:
            color = "green" if row["outcome"] == "goal" else "blue"
        else:
            color = "red"
        ax.scatter(row["goal_x"], row["goal_y"], c=color, edgecolors='black', s=100)
    
    legend_patches = [
        Rectangle((0, 0), 1, 1, color="green", label="Goal"),
        Rectangle((0, 0), 1, 1, color="blue", label="Saved"),
        Rectangle((0, 0), 1, 1, color="red", label="Missed"),
    ]
    ax.legend(handles=legend_patches, loc='upper left', fontsize=10)
    ax.set_title("Shot Location(s) On Goal", fontsize=14)
    return fig

# Streamlit App
st.title("Soccer Match Analysis")

# Sidebar: Select League, Season, and Match
st.sidebar.title("Match Analysis")
competitions_df = load_competitions()
league_options = competitions_df["competition"].tolist()
selected_league = st.sidebar.selectbox("Select League", league_options)

if selected_league:
    season_options = competitions_df[competitions_df["competition"] == selected_league]["seasons"].values[0]
    selected_season = st.sidebar.selectbox("Select Season", season_options)

    matches_df = load_matches(selected_league, selected_season)
    if not matches_df.empty:
        match_labels = matches_df.apply(lambda row: f"{row['home_team']} vs {row['away_team']}", axis=1)
        selected_match = st.sidebar.selectbox("Select Match", match_labels)

        if selected_match:
            selected_row = matches_df.loc[matches_df.apply(
                lambda row: f"{row['home_team']} vs {row['away_team']}", axis=1) == selected_match].iloc[0]
            home_team = selected_row["home_team"]
            away_team = selected_row["away_team"]
            match_id = selected_row["match_id"]

            # Team Selection
            st.markdown("### Select Team to Analyze")
            col1, col2 = st.columns(2)
            selected_team = None
            goal_center = None
            if col1.button(home_team):
                selected_team = home_team
                goal_center = (105, 34)  # Goal for attacking direction
            if col2.button(away_team):
                selected_team = away_team
                goal_center = (0, 34)  # Goal for defending direction

            if selected_team:
                team_events = load_team_events(selected_team, match_id)
                st.markdown(f"### Analyzing: {selected_team}")

                # Performance Metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                total_shots = len(team_events)
                shots_on_target = team_events[team_events["outcome"].isin(["goal", "saved"])].shape[0]
                goals = team_events[team_events["outcome"] == "goal"].shape[0]
                expected_goals = team_events[team_events["outcome"] == "goal"].shape[0] * 0.35  # Placeholder for xG calculation
                shot_conversion_rate = f"{(goals / total_shots * 100):.2f}%" if total_shots > 0 else "0%"

                col1.metric("Total Shots", total_shots)
                col2.metric("Shots on Target", shots_on_target)
                col3.metric("Shot Conversion Rate", shot_conversion_rate)
                col4.metric("Goals", goals)
                col5.metric("Expected Goals (xG)", f"{expected_goals:.2f}")

                # Visualizations
                col1, col2 = st.columns(2)
                with col1:
                    field_fig = plot_field_shots(team_events, goal_center)
                    st.pyplot(field_fig)
                with col2:
                    goal_fig = plot_goal_shots(team_events)
                    st.pyplot(goal_fig)
            else:
                st.warning("Please select a team to analyze.")
        else:
            st.warning("Please select a match.")
    else:
        st.warning("No matches available for the selected season.")
else:
    st.warning("Please select a league.")
