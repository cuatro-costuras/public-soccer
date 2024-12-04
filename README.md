# Soccer Player Shooting Tendencies App

## Overview
This project uses StatsBomb data to analyze player shooting tendencies in professional soccer matches. The app provides visualizations and metrics for individual players, showcasing their shooting performance and tendencies during a match.

### Features
1. **Team and Player Selection**:
   - Toggle to select a team's roster for a specific match.
   - Select a player to view their shooting tendencies.

2. **Player Profile**:
   - Display key metrics such as:
     - Shots Taken
     - Shots on Target
     - Shot Conversion Rate
     - Goals per Game
     - Expected Goals (xG)

3. **Visualizations**:
   - **Soccer Field Plot**: Shows where the player was positioned when they took each shot.
   - **Goal Plot**: Displays where the shots landed in the goal (or missed).

### Data Source
Data is sourced using the [StatsBombPy](https://github.com/statsbomb/statsbombpy) library, which provides access to professional soccer data.

### Requirements
- **Python 3.8 or later**
- Dependencies:
  - `pandas`
  - `statsbombpy`
  - `mplsoccer`
  - `streamlit`
  - `plotly`

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/<your-repository>.git
   cd <your-repository>
