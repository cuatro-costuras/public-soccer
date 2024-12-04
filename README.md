# Soccer Team Shooting Report App

## Overview
The **Soccer Team Shooting Report App** is an interactive tool designed to analyze shooting performance for professional soccer teams using **StatsBomb Open Data**. The app allows users to explore team-level shooting tendencies in specific matches, showcasing shooting statistics and visualizing shot locations on the pitch and within the goal.

This updated version features enhanced dropdown functionality for selecting competitions, seasons, and matches, and introduces improved visualizations of shots using **Plotly**.

---

## Features
1. **Competition and Season Selection:**
   - Users can choose from available competitions and seasons.
   - Matches are dynamically filtered based on the selected competition and season.

2. **Match and Team Selection:**
   - Dropdowns allow users to select a specific match.
   - Radio buttons enable selection between the home and away teams for the chosen match.

3. **Shooting Metrics:**
   - Key shooting metrics are displayed at the top of the app:
     - **Total Shots**
     - **Shots on Target**
     - **Shot Conversion Rate**
     - **Goals per Game**
     - **Expected Goals (xG)**

4. **Shot Visualizations:**
   - **Pitch Visualization:**
     - A soccer pitch graphic shows the locations where shots were taken.
     - Shot outcomes are color-coded:
       - Green: Goal
       - Yellow: On target but saved
       - Red: Missed or off target
   - **Goal Visualization:**
     - A goal graphic shows the final placement of shots within or outside the goal.
     - Outcomes are similarly color-coded for clarity.

5. **Dynamic Filtering:**
   - Visualizations and metrics dynamically update based on the selected team and match.

---

## Requirements
- **Python**: 3.8+
- **Libraries**:
  - `streamlit`
  - `statsbombpy`
  - `pandas`
  - `plotly`

---

## Usage
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/your-username/soccer-team-shooting-report.git
   cd soccer-team-shooting-report
