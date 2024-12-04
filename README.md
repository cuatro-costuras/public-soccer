# Soccer Match Analysis App

## Overview

The **Soccer Match Analysis App** is an interactive Streamlit-based tool designed to analyze match data for soccer teams. This app is a demonstration showcasing how match and event data can be visualized and explored. The data used in this app is an example dataset and does not represent a full season's worth of real-world data for any league.

## Features

1. **League and Season Selection**:
   - Choose between the **Premier League** and **La Liga**.
   - Select from available mock seasons (e.g., `2022/2023`, `2023/2024`).

2. **Match Selection**:
   - Select matches from the chosen league and season.
   - View teams competing in the match.

3. **Team Analysis**:
   - Analyze the selected team's performance in the match.
   - Metrics include:
     - **Total Shots**
     - **Shots on Target**
     - **Shot Conversion Rate**
     - **Goals**
     - **Expected Goals (xG)**

4. **Data Visualizations**:
   - **Shot Location(s) On Field**: Displays where shots were taken on a soccer field, color-coded for outcomes:
     - Green = Goal
     - Red = Missed/Saved
   - **Shot Location(s) On Goal**: Visualizes the placement of shots in relation to the goal, using the same color-coding as above.

5. **Streamlined User Interface**:
   - Visualizations are displayed side by side for easy comparison.
   - Performance metrics are shown in a clean, horizontal layout.

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/soccer-match-analysis.git
   cd soccer-match-analysis
