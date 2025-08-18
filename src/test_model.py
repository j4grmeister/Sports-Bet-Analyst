import os
import csv
import pandas as pd
import numpy as np
from sklearn.metrics import brier_score_loss, accuracy_score
import joblib
import statsapi

import models.mlb_model as mlb_model
from data.odds import OddsArchive

import build_dataset
import ui

def test_model(test_data_filename, training_batch_size=10, test_profits=False, bet_proba_margin=3, starting_bankroll=100, verbose=False, stats_filename=None):
    df = pd.read_csv(test_data_filename)

    odds_archive = None

    csv_headers = [
        "date",
        "bankroll_start",
        "home_team",
        "away_team",
        "odds",
        "probability",
        "bet_amount",
        "payout",
        "winning_team",
        "outcome",
        "bankroll_final"
    ]
    
    csvfile = None
    csv_writer = None
    if stats_filename != None and test_profits:
        csvfile = open(stats_filename, "w", newline='')
        csv_writer = csv.DictWriter(csvfile, fieldnames=csv_headers, delimiter=",")
        csv_writer.writeheader()

    if test_profits:
        odds_archive = OddsArchive()
        team_dict = {}

    model = joblib.load("xgb_model.joblib")
    calibrator = joblib.load("model_calibrator.joblib")

    y_proba_list = []
    y_pred_list = []

    n_of_games = df.shape[0]
    batch_start = None
    batch_end = 0
    bankroll = starting_bankroll
    for i in range(n_of_games):
        if verbose:
            ui.print_progress_bar(i, n_of_games)
        row = df.iloc[[i]]
        X = row.drop(mlb_model.output_column_name, axis = 1)
        for drop_column in mlb_model.non_training_columns:
            X = X.drop(drop_column, axis = 1)
        y = row[mlb_model.output_column_name].item()
        datetime = row["datetime"].item()

        y_proba_raw = model.predict_proba(X)[:, 1].reshape(-1, 1)
        y_pred_raw = model.predict(X).reshape(-1, 1)

        y_proba = calibrator.predict_proba(y_proba_raw)[:, 1].item()
        y_pred = calibrator.predict(y_pred_raw).item()
        #y_proba = min(y_proba, .55) if y_pred == 1 else max(y_proba, 1-.55)
        #print(f"{y_proba_raw} -> {y_proba}")
        calibrator.partial_fit(y_proba_raw, np.array([y]))
        y_proba_raw = y_proba_raw.item()

        y_proba_list.append(y_proba)
        y_pred_list.append(y_pred)

        if test_profits and bankroll > 0:
            #print(f"${bankroll}")
            pay_ratio = 0
            bet_size = 0
            bet_payout = 0
            bet_proba = 0
            bet_outcome = None # 1 = home, 0 = away
            bet_odds = 0
            implied_proba = 0

            home_team_id = X["home_team"].item()
            away_team_id = X["away_team"].item()
            if home_team_id not in team_dict:
                team_dict[home_team_id] = statsapi.lookup_team(home_team_id)[0]["name"]
            if away_team_id not in team_dict:
                team_dict[away_team_id] = statsapi.lookup_team(away_team_id)[0]["name"]
            home_team = team_dict[home_team_id]
            away_team = team_dict[away_team_id]
            game_date = datetime.split("T")[0]
            home_odds, away_odds = odds_archive.get_odds(game_date, home_team, away_team)
            if home_odds != None and away_odds != None:
                

                home_prob_imp = 1/home_odds
                away_prob_imp = 1/away_odds
                

                #print(f"Payroll: ${bankroll}")
                #if (y_pred == y):   
                    #print(f"Odds: {home_prob_imp*100} vs {away_prob_imp*100}")
                    #print(f"Pred: {y_pred}")
                    #print(f"Proba: {y_proba*100} vs {(1-y_proba)*100}")
                
                if y_pred == 1:
                    # BET HOME
                    bet_outcome = 1
                    implied_proba = home_prob_imp
                    bet_proba = y_proba
                    pay_ratio = min(home_odds-1, 2.5)
                    bet_odds = home_odds
                elif y_pred == 0:
                    # BET AWAY
                    bet_outcome = 0
                    implied_proba = away_prob_imp
                    bet_proba = 1-y_proba
                    pay_ratio = min(away_odds-1, 2.5)
                    bet_odds = away_odds
                
                if (bet_proba - implied_proba)*100 >= bet_proba_margin or (implied_proba >= .65):
                #if (bet_proba - implied_proba)*100 >= bet_proba_margin: 
                    bet_size = round(bankroll * (bet_proba - (1-bet_proba)/pay_ratio), 2)
                    bet_payout = round(bet_size *  bet_odds, 2)

                #print(f"Outcome: {y}")
                if bet_size > 0:
                    #print(f"Bet: ${bet_size}")
                    starting_bankroll = bankroll

                    bankroll -= bet_size
                    if bet_outcome == y:
                        bankroll += bet_payout
                    bankroll = round(bankroll, 2)
                    #print(f"{y_proba_raw} -> {y_proba}")
                    #print(f"Bankroll: ${bankroll}")

                    american_odds = (bet_odds - 1) * 100 if bet_odds >= 2 else (-100)/(bet_odds - 1)

                    csv_row = {
                        "date": game_date,
                        "bankroll_start": starting_bankroll,
                        "home_team": home_team,
                        "away_team": away_team,
                        "odds": round(american_odds),
                        "probability": bet_proba,
                        "bet_amount": bet_size,
                        "payout": bet_payout,
                        "winning_team": home_team if y == 1 else away_team,
                        "outcome": "W" if bet_outcome == y else "L",
                        "bankroll_final": bankroll
                    }
                    if csvfile != None:
                        csv_writer.writerow(csv_row)
                #print()
                #print()

        batch_end = i
        if i % training_batch_size == 0:
            if batch_start != None:
                batch = df.iloc[batch_start:batch_end]
                X_batch = batch.drop(mlb_model.output_column_name, axis = 1)
                for drop_column in mlb_model.non_training_columns:
                    X_batch = X_batch.drop(drop_column, axis = 1)
                y_batch = batch[mlb_model.output_column_name]
                model.fit(X_batch, y_batch, xgb_model=model.get_booster())
            batch_start = batch_end
    if batch_start != None:
        batch = df.iloc[batch_start:batch_end]
        X_batch = batch.drop(mlb_model.output_column_name, axis = 1)
        for drop_column in mlb_model.non_training_columns:
            X_batch = X_batch.drop(drop_column, axis = 1)
        y_batch = batch[mlb_model.output_column_name]
        model.fit(X_batch, y_batch, xgb_model=model.get_booster())       
    if verbose:
        ui.print_progress_bar(n_of_games, n_of_games)
        print()
        if test_profits:
           print(f"${bankroll}")

    y = df[mlb_model.output_column_name]

    brier_score = brier_score_loss(y, y_proba_list)
    accuracy = accuracy_score(y, y_pred_list)
    if verbose:
        print("Brier Score:", brier_score)
        print("Accuracy:", accuracy)
        if test_profits:
            #print("Profit:", bankroll - starting_bankroll)
            csvfile.close()

if __name__ == "__main__":
    data_filename = "data/testing_dataset.csv"
    if not os.path.exists(data_filename):
        build_dataset.build_mlb_dataset(data_filename, "01/01/2025", "01/01/2026", verbose=True)
    test_model(data_filename, test_profits=True, starting_bankroll=10, bet_proba_margin=3, verbose=True, stats_filename="bets.csv")