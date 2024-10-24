import pandas as pd
import ast
import numpy as np
import sqlite3
from utils import geo

# Load data from SQLite
connection = sqlite3.connect("./data/db.sqlite3")
og_courses = pd.read_sql_query("SELECT * FROM course_course", connection)
og_course_tees = pd.read_sql_query("SELECT * FROM course_tee", connection)
og_course_holes = pd.read_sql_query("SELECT * FROM course_hole", connection)
og_rounds = pd.read_sql_query("SELECT * FROM round_round", connection)
og_round_stats = pd.read_sql_query("SELECT * FROM round_holestats", connection)
og_strokes = pd.read_sql_query("SELECT * FROM round_stroke", connection)
og_putts = pd.read_sql_query("SELECT * FROM round_putt", connection)
connection.close()

# Clean Rounds (Only take rounds with 18 hole scores)
og_rounds.drop(og_rounds[og_rounds.holes_completed != 18].index, inplace=True)

# Get Score
## here please
def parse_coordinates(coord_str):
    if pd.isnull(coord_str):
        return None  # Return None if the coordinate is null
    return ast.literal_eval(coord_str)

def parse_coordinates_with_parentheses(coord_str):
    if pd.isnull(coord_str):
        return None  # Return None if the coordinate is null
    return ast.literal_eval(coord_str[1:-1])


# Apply the function to both 'start_coordinate' and 'end_coordinate' columns
og_strokes['start_coordinate'] = og_strokes['start_coordinate'].apply(parse_coordinates)
og_strokes['end_coordinate'] = og_strokes['end_coordinate'].apply(parse_coordinates)

# Calculate the distance, returning 0 if any coordinate is None
og_strokes['distance'] = og_strokes.apply(
    lambda row: 0 if row['start_coordinate'] is None or row['end_coordinate'] is None
    else geo.get_distance_between_points_yards(
        row['start_coordinate'][0], row['start_coordinate'][1],  # start lat, long
        row['end_coordinate'][0], row['end_coordinate'][1]       # end lat, long
    ), axis=1
)

og_course_holes['center_green_point'] = og_course_holes['center_green_point'].apply(parse_coordinates_with_parentheses)
og_strokes = pd.merge(og_strokes, og_course_holes[['id', 'center_green_point']], left_on='hole_id', right_on='id', how='left')
# Now calculate the distance from start_coordinate to center_green_point (the green center)
og_strokes['distance_start_to_green_center'] = og_strokes.apply(
    lambda row: 0 if row['start_coordinate'] is None or row['center_green_point'] is None
    else geo.get_distance_between_points_yards(
        row['start_coordinate'][0], row['start_coordinate'][1],  # start lat, long
        row['center_green_point'][0], row['center_green_point'][1]  # green center lat, long
    ), axis=1
)

print(og_strokes.columns)

# Clean up by dropping the extra 'id' column if needed
og_strokes.drop(columns=['id_y'], inplace=True)

strokes_per_round = og_strokes.groupby('rnd_id').size().reset_index(name='num_strokes')
putts_per_round = og_putts.groupby('rnd_id').size().reset_index(name='# Putts')
score_df = pd.merge(strokes_per_round, putts_per_round, on='rnd_id', how='outer')
score_df['Score'] = score_df['num_strokes'].fillna(0) + score_df['# Putts'].fillna(0)

penalties_per_round = og_strokes.where(og_strokes['penalty'] == True).groupby('rnd_id').size().reset_index(name='# Penalties')
gir_per_round = (
    og_round_stats.where(og_round_stats['gir'] == True)
    .groupby('rnd_id')
    .size()
)

# Calculate percentage and handle cases where the count is 0
gir_per_round = (gir_per_round / 18 * 100).reset_index(name='GIR')

# Replace NaN values with 0 and round to one decimal place
gir_per_round['GIR'] = gir_per_round['GIR'].fillna(0).round(1).astype(str) + '%'
gld_per_round = og_round_stats.where(og_round_stats['gld'] == True).groupby('rnd_id').size().reset_index(name='Green Light Drives')
shots_inside_100 = og_strokes.where(og_strokes['distance_start_to_green_center'] < 100.0).groupby('rnd_id').size().reset_index(name='# Shots < 100 Yards')
shots_between_200_and_100 = og_strokes.where(
    (og_strokes['distance_start_to_green_center'] >= 100.0) & 
    (og_strokes['distance_start_to_green_center'] < 200.0)
).groupby('rnd_id').size().reset_index(name='# Shots 100-200 Yards')

num_drivers_hit = og_strokes.where(og_strokes['club'] == 'D').groupby('rnd_id').size().reset_index(name='# Drivers Hit')
drives = og_strokes[og_strokes['club'] == 'D']
avg_drive_distance_per_round = drives.groupby('rnd_id')['distance'].mean().reset_index(name='Avg. Driver Distance')

# Merge this with the og_rounds DataFrame to include round details

new_rounds = pd.merge(og_rounds, strokes_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, score_df, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, penalties_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, gir_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, gld_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, shots_inside_100, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, shots_between_200_and_100, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, num_drivers_hit, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication



new_rounds = pd.merge(new_rounds, avg_drive_distance_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, og_courses, left_on='course_id', right_on='id', how='left')
# new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = new_rounds.where(new_rounds['Score'] > 80)


# Fill NaN values with 0 if some rounds don't have any putts
new_rounds.sort_values(by='date_played', inplace=True, ascending=False)

og_strokes.sort_values(by='id_x', inplace=True, ascending=False)

new_rounds[['date_played', 'name', 'Score', '# Putts', '# Penalties', 'GIR', 'Green Light Drives', '# Shots 100-200 Yards', '# Shots < 100 Yards', '# Drivers Hit', 'Avg. Driver Distance']].to_csv('exports/2024.csv', index=True)
# Get # Putts

# Get GIR

# Get GLD

# Get % Scrambling

# Get # penalties

# Get # Shots inside 110 yards

# Avg Driving Distance

# Feet of Putts

# Round Strokes
# Cum. stroke

# Round putts
