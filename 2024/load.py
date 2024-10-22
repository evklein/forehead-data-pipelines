import pandas as pd
import sqlite3

connection = sqlite3.connect("../data/db.sqlite3")

og_rounds_df = pd.read_sql_query("SELECT * FROM round_round", connection)
og_putts_df = pd.read_sql_query("SELECT * FROM round_putt", connection)
og_strokes_df = pd.read_sql_query("SELECT * FROM round_stroke", connection)

connection.close()
