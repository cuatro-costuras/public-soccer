import os
import pandas as pd
import json

# Define file paths
BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/"
COMPETITIONS_FILE = f"{BASE_URL}competitions.json"
MATCHES_FOLDER = f"{BASE_URL}matches/"
EVENTS_FOLDER = f"{BASE_URL}events/"
THREE_SIXTY_FOLDER = f"{BASE_URL}three-sixty/"

# Ensure 'data/' folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Fetch competitions data
competitions = pd.read_json(COMPETITIONS_FILE)
competitions.to_csv("data/competitions.csv", index=False)
print("Competitions data saved.")

# Filter for Bundesliga 2023/2024 (or replace with available data)
competition_id = competitions[
    (competitions['competition_name'] == 'Bundesliga') &
    (competitions['season_name'] == '2023/2024')
]['competition_id']

if competition_id.empty:
    print("Bundesliga 2023/2024 data is not available.")
else:
    competition_id = competition_id.iloc[0]

    # Fetch matches for the competition
    matches_file = f"{MATCHES_FOLDER}{competition_id}.json"
    matches = pd.read_json(matches_file)
    matches.to_csv("data/matches.csv", index=False)
    print("Matches data saved.")

    # Fetch events for all matches
    events_list = []
    for match in matches['match_id']:
        events_file = f"{EVENTS_FOLDER}{match}.json"
        try:
            with open(events_file) as f:
                events = json.load(f)
                events_list.append(pd.DataFrame(events))
        except Exception as e:
            print(f"Error loading events for match {match}: {e}")

    if events_list:
        events = pd.concat(events_list, ignore_index=True)
        events.to_csv("data/events.csv", index=False)
        print("Events data saved.")
    else:
        print("No events data found.")
