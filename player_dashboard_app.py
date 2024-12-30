import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Load data from the saved CSV
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("data/merged_data.csv")
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the pre-saved data
data = load_data()

# App layout
if not data.empty:
    st.title("Bundesliga 2023/2024 Player Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    teams = data['team'].unique()
    selected_team = st.sidebar.selectbox("Select Team", teams)

    players = data[data['team'] == selected_team]['player'].unique()
    selected_player = st.sidebar.selectbox("Select Player", players)

    # Display Player Profile
    st.header(f"{selected_player}'s Performance")
    st.write(f"Team: {selected_team}")

    # Radar Plot
    st.header("Radar Plot")
    # Define skills for the radar plot (adjust based on available columns)
    skills = ["x", "y", "pass_end_x", "pass_end_y"]
    player_data = data[data['player'] == selected_player]

    # Ensure columns are available
    available_skills = [skill for skill in skills if skill in player_data.columns]
    if not available_skills:
        st.warning("No valid data for radar plot.")
    else:
        average_skills = [player_data[skill].mean() for skill in available_skills]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=average_skills,
            theta=available_skills,
            fill='toself',
            name=selected_player
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig)

    # Percentile Rankings
    st.header("Percentile Rankings")
    # Define skills for percentile rankings
    percentile_skills = ["x", "y", "pass_end_x", "pass_end_y"]

    for skill in percentile_skills:
        if skill in player_data.columns:
            value = player_data[skill].mean()
            st.write(f"### {skill}: {value:.2f}")
            st.progress(min(int((value / 100) * 100), 100))
else:
    st.error("No data available. Please ensure 'merged_data.csv' is correctly placed in the 'data/' folder.")
