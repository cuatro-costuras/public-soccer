from statsbombpy import sb
import pandas as pd

# Fetch match events
events_df = sb.competition_events(
    country="Germany",
    division="1. Bundesliga",
    season="2023/2024",
    gender="male"
)

# Fetch 360 data and merge with events
frames_df = sb.competition_frames(
    country="Germany",
    division="1. Bundesliga",
    season="2023/2024",
    gender="male"
)
frames_df.rename(columns={'event_uuid': 'id'}, inplace=True)
merged_df = pd.merge(frames_df, events_df, how="left", on=["match_id", "id"])

# Save locally for faster access
merged_df.to_csv("data/merged_data.csv", index=False)
