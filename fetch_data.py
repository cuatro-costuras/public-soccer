from statsbombpy import sb
import pandas as pd
import os

# Ensure 'data/' folder exists
if not os.path.exists("data"):
    os.makedirs("data")

try:
    # Fetch match events
    events_df = sb.competition_events(
        country="Germany",
        division="1. Bundesliga",
        season="2023/2024",
        gender="male"
    )
    print("Successfully fetched events data.")
except Exception as e:
    print(f"Error fetching events data: {e}")
    events_df = pd.DataFrame()

try:
    # Fetch 360 data and merge with events
    frames_df = sb.competition_frames(
        country="Germany",
        division="1. Bundesliga",
        season="2023/2024",
        gender="male"
    )
    frames_df.rename(columns={'event_uuid': 'id'}, inplace=True)
    merged_df = pd.merge(frames_df, events_df, how="left", on=["match_id", "id"])
    print("Successfully merged events and 360 data.")
except Exception as e:
    print(f"Error fetching or merging 360 data: {e}")
    merged_df = pd.DataFrame()

# Save merged data to 'data/' folder
if not merged_df.empty:
    merged_df.to_csv("data/merged_data.csv", index=False)
    print("Data saved to 'data/merged_data.csv'")
else:
    print("Merged data is empty. No file was saved.")
