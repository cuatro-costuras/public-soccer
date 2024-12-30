import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Load data from the existing repository
@st.cache
def load_data():
    # Ensure the path matches the location in your repository
    return pd.read_csv("data/merged_data.csv")

data = load_data()

# Sidebar for filtering
st.sidebar.header("Filters")
league = st.sidebar.selectbox("Select League", options=["1. Bundesliga"])  # Assuming one league for now
team = st.sidebar.selectbox("Select Team", options=data['team_name'].unique())
player = st.sidebar.selectbox("Select Player", options=data[data['team_name'] == team]['player_name'].unique())

# Display player profile
st.title(f"{player}'s Performance")
st.write(f"Team: {team} | League: {league}")

# Radar Plot: Position-Specific Skills
st.header("Position-Specific Radar Plot")
position = data[data['player_name'] == player]['position'].iloc[0]
st.write(f"Position: {position}")

# Define radar plot stats by position
radar_stats = {
    "Forward": ["Goals Scored", "xG per 90", "Shots on Target %", "Dribbles Completed", "Key Passes"],
    "Midfielder": ["Pass Completion %", "Progressive Carries", "xA", "Duels Won", "Interceptions"],
    "Defender": ["Clearances", "Aerial Duels Won", "Interceptions", "Blocks", "Tackles Won"],
    "Goalkeeper": ["Saves %", "Clean Sheets", "Goals Prevented", "Distribution Accuracy", "xG Against"],
}
radar_traits = radar_stats.get(position, [])

# Generate radar data
radar_values = [data[data['player_name'] == player][trait].iloc[0] for trait in radar_traits]
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=radar_values,
    theta=radar_traits,
    fill='toself',
    name=player
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
st.plotly_chart(fig)

# Percentile Rankings
st.header("Overall Percentile Rankings")
percentile_traits = ["Passing Accuracy", "Progressive Passes", "Key Passes", "Tackles Won", "Interceptions"]
st.write("Percentiles for both offensive and defensive skills:")
for trait in percentile_traits:
    value = data[data['player_name'] == player][trait].iloc[0]
    st.write(f"### {trait}: {value}")
    st.progress(int(value))
