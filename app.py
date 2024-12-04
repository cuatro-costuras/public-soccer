import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# Simulated loading functions (replace with actual StatsBombPy calls)
@st.cache_data
def load_matches():
    # Simulate match data (replace with real data)
    return pd.DataFrame({
        "match_id": [1, 2, 3, 4],
        "competition": ["Premier League", "La Liga", "Bundesliga", "Serie A"],
        "season": ["2022/2023", "2022/2023", "2023/2024", "2023/2024"],
        "home_team": ["Chelsea", "Barcelona", "Bayern Munich", "Juventus"],
        "away_team": ["Arsenal", "Real Madrid", "Dortmund", "Inter Milan"],
        "home_score": [2, 1, 3, 0],
        "away_score": [1, 2, 2, 2]
    })

@st.cache_data
def load_events(match_id):
    # Simulate events data (replace with real data)
    return pd.DataFrame({
        "type": ["Shot", "Pass", "Shot", "Shot"],
        "team": ["Chelsea", "Chelsea", "Arsenal", "Arsenal"],
        "location": [[30, 40], [50, 60], [40, 20], [60, 30]],
        "shot_end_location": [[3, 2], [None], [1, -1], [2, 1]],
        "shot_statsbomb_xg": [0.5, None, 0.8, 0.2],
        "shot_outcome": ["Goal", None, "Missed", "Saved"],
    })

# Step 1: Select Match
st.sidebar.title("Soccer Match Analysis")
matches = load_matches()

# Dropdowns for competition and season
competition = st.sidebar.selectbox("Select Competition", matches["competition"].unique())
season = st.sidebar.selectbox("Select Season", matches["season"].unique())

# Filter matches based on selection
filtered_matches = matches[(matches["competition"] == competition) & (matches["season"] == season)]

if not filtered_matches.empty:
    match_row = st.sidebar.selectbox(
        "Select Match",
        filtered_matches.index,
        format_func=lambda x: f"{filtered_matches.loc[x, 'home_team']} vs {filtered_matches.loc[x, 'away_team']}"
    )
    selected_match = filtered_matches.loc[match_row]

    # Display match score
    st.title(f"{selected_match['home_team']} {selected_match['home_score']} - {selected_match['away_score']} {selected_match['away_team']}")

    # Step 2: Load Events for Selected Match
    events = load_events(selected_match["match_id"])

    # Step 3: Select Team with Buttons
    st.write(f"### Analyze Team Performance")
    col1, col2 = st.columns(2)
    selected_team = None

    if col1.button(f"Analyze {selected_match['home_team']}"):
        selected_team = selected_match["home_team"]
    if col2.button(f"Analyze {selected_match['away_team']}"):
        selected_team = selected_match["away_team"]

    if selected_team:
        st.write(f"### Selected Team: {selected_team}")

        # Filter events for selected team
        team_events = events[events["team"] == selected_team]

        # Ensure valid shot data
        if "type" in team_events.columns and "location" in team_events.columns:
            shot_data = team_events[(team_events["type"] == "Shot") & team_events["location"].notnull()]

            # Calculate Metrics
            total_shots = len(shot_data)
            shots_on_target = len(shot_data[shot_data["shot_outcome"].isin(["Goal", "Saved"])])
            goals = len(shot_data[shot_data["shot_outcome"] == "Goal"])
            xg = shot_data["shot_statsbomb_xg"].sum()
            shot_conversion_rate = goals / total_shots * 100 if total_shots > 0 else 0

            # Display metrics as boxes
            box1, box2, box3, box4, box5 = st.columns(5)
            box1.metric("Total Shots", total_shots)
            box2.metric("Shots on Target", shots_on_target)
            box3.metric("Shot Conversion Rate", f"{shot_conversion_rate:.2f}%")
            box4.metric("Goals", goals)
            box5.metric("Expected Goals (xG)", f"{xg:.2f}")

            # Step 4: Visualize Shots on Soccer Pitch
            st.write("### Shot Locations on Field")
            pitch = Pitch(pitch_type="statsbomb", line_color="black")
            fig, ax = pitch.draw(figsize=(10, 6))

            # Add shots to pitch
            for _, shot in shot_data.iterrows():
                x, y = shot["location"]
                outcome = shot["shot_outcome"]
                color = "green" if outcome == "Goal" else "red" if outcome == "Missed" else "blue"
                pitch.scatter(x, y, s=100, color=color, ax=ax)

            st.pyplot(fig)

            # Add legend for colors
            st.write("#### Key for Field Visualization")
            st.write("- **Green**: Goal")
            st.write("- **Red**: Missed")
            st.write("- **Blue**: Saved")

            # Step 5: Visualize Shots on Goal
            st.write("### Shot Locations on Goal")
            fig_goal, ax_goal = plt.subplots(figsize=(6, 4))
            ax_goal.set_xlim(-3, 3)
            ax_goal.set_ylim(0, 2.5)

            for _, shot in shot_data.iterrows():
                if shot["shot_end_location"]:
                    x, y = shot["shot_end_location"]
                    outcome = shot["shot_outcome"]
                    color = "green" if outcome == "Goal" else "red" if outcome == "Missed" else "blue"
                    ax_goal.scatter(x, y, color=color, s=100)

            ax_goal.set_title("Shot Placement in Goal")
            ax_goal.set_xlabel("Width of Goal")
            ax_goal.set_ylabel("Height of Goal")

            st.pyplot(fig_goal)

            # Add legend for goal visualization
            st.write("#### Key for Goal Visualization")
            st.write("- **Green**: Goal")
            st.write("- **Red**: Missed")
            st.write("- **Blue**: Saved")

        else:
            st.write("No valid shot data available for the selected team.")
else:
    st.sidebar.write("No matches found for the selected competition and season.")
