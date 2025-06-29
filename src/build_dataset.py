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

import models.mlb_model as mlb_model

import ui

DATA_START_DATE = "01/01/2024"
DATA_END_DATE = "01/01/2025"

# get all the MLB data
all_games = statsapi.schedule(start_date=DATA_START_DATE, end_date=DATA_END_DATE)



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

    for column in mlb_model.columns:
        value = column.generator.generate(boxscore, game)
        if column.in_dataset:
            row.append(value)

    data_table.append(row)
    game_index += 1
ui.print_progress_bar(game_index, total_games)
print()


with open("data/training_dataset.csv", "w", newline='') as csvfile:
    fieldnames = []
    for column in mlb_model.columns:
        if column.in_dataset:
            fieldnames.append(column.name)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
    writer.writeheader()
    for row in data_table:
        row_dict = {}
        for col in range(len(fieldnames)):
            row_dict[fieldnames[col]] = row[col]
        writer.writerow(row_dict)