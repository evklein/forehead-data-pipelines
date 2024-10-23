import pandas as pd
import numpy as np
import sqlite3

# Load data from SQLite
connection = sqlite3.connect("../data/db.sqlite3")
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
strokes_per_round = og_strokes.groupby('rnd_id').size().reset_index(name='num_strokes')
putts_per_round = og_putts.groupby('rnd_id').size().reset_index(name='num_putts')
penalties_per_round = og_strokes.where(og_strokes['penalty'] == True).groupby('rnd_id').size().reset_index(name='num_penalties')
gir_per_round = og_round_stats.where(og_round_stats['gir'] == True).groupby('rnd_id').size().reset_index(name='num_gir')
gld_per_round = og_round_stats.where(og_round_stats['gld'] == True).groupby('rnd_id').size().reset_index(name='num_gld')

# Merge this with the og_rounds DataFrame to include round details
new_rounds = pd.merge(og_rounds, strokes_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, putts_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, penalties_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, gir_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication

new_rounds = pd.merge(new_rounds, gld_per_round, left_on='id', right_on='rnd_id', how='left')
new_rounds.drop(columns='rnd_id', inplace=True)  # Drop 'rnd_id' to avoid duplication


# Fill NaN values with 0 if some rounds don't have any putts
new_rounds['num_putts'].fillna(0, inplace=True)
new_rounds.sort_values(by='date_played', inplace=True, ascending=False)

print(new_rounds[['course_id', 'date_played', 'num_strokes', 'num_putts', 'num_penalties', 'num_gir', 'num_gld']].head(10))
print(f"Average putts: {np.mean(new_rounds[['num_putts']])}")

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
