import pandas as pd
import streamlit as st
from statsbombpy import sb
import plotly.graph_objects as go

@st.cache_data
def fetch_and_preprocess_data(selected_competition, selected_season):
    try:
        competitions = sb.competitions()
        st.write("Fetched Competitions:", competitions)

        selected_data = competitions[
            (competitions['competition_name'] == selected_competition) &
            (competitions['season_name'] == selected_season)
        ]

        if selected_data.empty:
            st.error(f"No data available for {selected_competition} {selected_season}.")
            return pd.DataFrame(), pd.DataFrame()

        competition_id = selected_data['competition_id'].iloc[0]
        season_id = selected_data['season_id'].iloc[0]

        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        st.write("Fetched Matches:", matches)

        if matches.empty:
            st.error("No match data found.")
            return pd.DataFrame(), pd.DataFrame()

        match_ids = matches['match_id'].tolist()
        events_list = []
        for match_id in match_ids:
            try:
                events = sb.events(match_id=match_id)
                st.write(f"Fetched Events for Match {match_id}:", events.head())
                events_list.append(events)
            except Exception as e:
                st.warning(f"Could not fetch events for match {match_id}: {e}")

        if not events_list:
            st.error("No event data available.")
            return pd.DataFrame(), matches

        events = pd.concat(events_list, ignore_index=True)
        relevant_columns = ['match_id', 'team', 'player', 'type', 'x', 'y', 'outcome', 'pass_end_x', 'pass_end_y']
        available_columns = [col for col in relevant_columns if col in events.columns]
        missing_columns = [col for col in relevant_columns if col not in events.columns]

        if missing_columns:
            st.warning(f"The following columns are missing: {missing_columns}")

        events = events[available_columns]

        return events, matches

    except Exception as e:
        st.error(f"Error in fetch_and_preprocess_data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Sidebar: Select Competition and Season
try:
    competitions = sb.competitions()
    available_competitions = competitions['competition_name'].unique()
    selected_competition = st.sidebar.selectbox("Select Competition", available_competitions)

    available_seasons = competitions[competitions['competition_name'] == selected_competition]['season_name'].unique()
    selected_season = st.sidebar.selectbox("Select Season", available_seasons)

    events_data, matches_data = fetch_and_preprocess_data(selected_competition, selected_season)

    if not events_data.empty and not matches_data.empty:
        st.title(f"{selected_competition} {selected_season} Analysis")

        teams = events_data['team'].unique()
        selected_team = st.sidebar.selectbox("Select Team", teams)

        players = events_data[events_data['team'] == selected_team]['player'].unique()
        selected_player = st.sidebar.selectbox("Select Player", players)

        st.title(f"{selected_player}'s Performance")
        st.write(f"Team: {selected_team}")

        st.header("Radar Plot")
        position_skills = ["x", "y", "pass_end_x", "pass_end_y"]

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

        st.header("Percentile Rankings")
        percentile_skills = ["x", "y", "pass_end_x", "pass_end_y"]
        for skill in percentile_skills:
            value = player_data[skill].mean()
            st.write(f"### {skill}: {value:.2f}")
            st.progress(int((value / 100) * 100))
    else:
        st.error("Unable to load data. Please ensure the competition and season are available.")
except Exception as e:
    st.error(f"Error running app: {e}")
