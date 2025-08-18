import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, accuracy_score
from xgboost import XGBClassifier
import csv

import statsapi

import models.mlb_model as mlb_model

import ui

def build_mlb_dataset(filename, start_date, end_date, verbose=False):
    # get all the MLB data
    all_games = statsapi.schedule(start_date=start_date, end_date=end_date)

    data_table = []

    game_index = 0
    total_games = len(all_games)
    for game in all_games:
        game_index += 1
        #TODO: Skip some games (ex. exhibition, canceled, etc.)

        if verbose:
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
    if verbose:
        ui.print_progress_bar(total_games, total_games)
        print()


    with open(filename, "w", newline='') as csvfile:
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

if __name__ == "__main__":
    build_mlb_dataset("data/training_dataset.csv", "01/01/2024", "01/01/2025", verbose=True)