import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, accuracy_score
from xgboost import XGBClassifier
import csv
import logging

import statsapi

from data.datasets.MLBDataset import MLBDataset

import ui

def build_mlb_dataset(filename, start_date, end_date, verbose=False):
    # get all the MLB data
    if verbose:
        print("Fetching MLB schedule")
    all_games = statsapi.schedule(start_date=start_date, end_date=end_date)

    args_array = []
    mlb_schema = MLBDataset()

    #data_table = []

    if verbose:
        print("Compiling MLB game data")

    game_index = 0
    total_games = len(all_games)                                                                                                                                                                                                                                        
    for game in all_games:
        #TODO: Skip some games (ex. exhibition, canceled, etc.)

        if verbose:
            ui.print_progress_bar(game_index, total_games)
        game_index += 1
        game_id = game["game_id"]
        game_status = game["status"]
        game_type = game["game_type"]
        home_pitcher = game["home_probable_pitcher"]
        away_pitcher = game["away_probable_pitcher"]
        
        if game_status != "Final":
            continue
        if game_type == "E":
            continue
        if home_pitcher == "" or away_pitcher == "":
            continue

        boxscore = statsapi.boxscore_data(game_id)
        args_array.append((boxscore, game))

        """
        for column in mlb_model.columns:
            value = column.generator.generate(boxscore, game)
            if column.in_dataset:
                row.append(value)
                """

        #data_table.append(row)
    if verbose:
        ui.print_progress_bar(total_games, total_games)
    dataset = mlb_schema.iterate_dict(args_array, verbose=verbose)


    with open(filename, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=mlb_schema.headers(), delimiter=",")
        writer.writeheader()
        writer.writerows(dataset)

if __name__ == "__main__":
    logging.basicConfig(filename="logs/build_dataset.log", level=logging.INFO)
    build_mlb_dataset("data/training_dataset.csv", "01/01/2024", "01/01/2025", verbose=True)
    #build_mlb_dataset("data/test_dataset.csv", "07/25/2025", "08/09/2025", verbose=True)