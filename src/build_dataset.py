import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, accuracy_score
from xgboost import XGBClassifier
import joblib
import json
import csv

import statsapi

from data.ColumnGenerator import ColumnGenerator
import data.columns.mlb_functions as MLBCol
import ui

DATA_START_DATE = "01/01/2024"
DATA_END_DATE = "01/01/2025"

# get all the MLB data
all_games = statsapi.schedule(start_date=DATA_START_DATE, end_date=DATA_END_DATE)


dummy_home_team_stats = ColumnGenerator("DUMMY_COLUMN", MLBCol.get_team_fetch_all_stats_func(True), id="TeamStats")
dummy_away_team_stats = ColumnGenerator("DUMMY_COLUMN", MLBCol.get_team_fetch_all_stats_func(False), id="TeamStats")

home_team = ColumnGenerator("home_team", MLBCol.get_team_func(True))
away_team = ColumnGenerator("away_team", MLBCol.get_team_func(False))
home_team_wOBA = ColumnGenerator("home_team_wOBA", MLBCol.get_team_wOBA_func(True), id="TeamStats")
away_team_wOBA = ColumnGenerator("away_team_wOBA", MLBCol.get_team_wOBA_func(False), id="TeamStats")
home_team_OPS = ColumnGenerator("home_team_OPS", MLBCol.get_team_OPS_func(True), id="TeamStats")
away_team_OPS = ColumnGenerator("away_team_OPS", MLBCol.get_team_OPS_func(False), id="TeamStats")
home_team_starting_pitcher = ColumnGenerator("home_team_starting_pitcher", MLBCol.get_team_starting_pitcher_func(True))
away_team_starting_pitcher = ColumnGenerator("away_team_starting_pitcher", MLBCol.get_team_starting_pitcher_func(False))
home_team_rolling_win_percent_10 = ColumnGenerator("home_team_rolling_win_percent_10", MLBCol.get_team_rolling_win_percent_func(True, window_size=10), id="TeamWins")
away_team_rolling_win_percent_10 = ColumnGenerator("away_team_rolling_win_percent_10", MLBCol.get_team_rolling_win_percent_func(False, window_size=10), id="TeamWins")

home_team_win = ColumnGenerator("home_team_win", MLBCol.home_team_win)

column_generators = [
    home_team,
    away_team,
    home_team_wOBA,
    away_team_wOBA,
    home_team_OPS,
    away_team_OPS,
    home_team_starting_pitcher,
    away_team_starting_pitcher,
    home_team_rolling_win_percent_10,
    away_team_rolling_win_percent_10,
    home_team_win
]

data_table = []

game_index = 0
total_games = len(all_games)
for game in all_games:
    #TODO: Skip some games (ex. exhibition, canceled, etc.)

    ui.print_progress_bar(game_index, total_games)
    game_id = game["game_id"]
    game_status = game["status"]
    game_type = game["game_type"]
    
    if game_status != "Final":
        continue
    if game_type == "E":
        continue

    boxscore = statsapi.boxscore_data(game_id)
    row = []

    ###############
    # DO NOT REMOVE
    # These are dummy columns. Other columns are dependent on them
    dummy_home_team_stats.generate(boxscore)
    dummy_away_team_stats.generate(boxscore)
    ###############
    for column in column_generators:
        value = column.generate(boxscore, game)
        row.append(value)

    data_table.append(row)
    game_index += 1
ui.print_progress_bar(game_index, total_games)
print()


with open("data/training_dataset.csv", "w", newline='') as csvfile:
    fieldnames = []
    for column in column_generators:
        fieldnames.append(column.name)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
    writer.writeheader()
    for row in data_table:
        row_dict = {}
        for col in range(len(fieldnames)):
            row_dict[fieldnames[col]] = row[col]
        writer.writerow(row_dict)