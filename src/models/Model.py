import csv

import statsapi

from datetime import datetime, timedelta

import numpy as np
from hyperopt import fmin, tpe, hp, Trials
from sklearn.metrics import accuracy_score, brier_score_loss
from data.odds import OddsArchive, dec_to_american_odds

import ui

class Model:
    def __init__(self, predictor, betting_strategy):
        self.predictor = predictor
        self.betting_strategy = betting_strategy

    def train(self, verbose=False):
        self.predictor.train(verbose=verbose)

    def test(self, verbose=False):
        self.predictor.load_test(verbose=verbose)
        return self.predictor.test(verbose=verbose)
    
    def test_profits(self, stats_filename, starting_bankroll=100, verbose=False):
        self.predictor.load_test(verbose=verbose)
        self.betting_strategy.set_balance(starting_bankroll)
        
        if verbose:
            print("Testing betting profits")
        
        csvfile = None
        csv_writer = None
        if stats_filename != None:
            csvfile = open(stats_filename, "w", newline='')
        
        team_dict = {}

        ongoing_games = []

        y_pred_list = []
        y_proba_list = []
        y_list = []

        write_headers = True
        i = 0
        n = self.predictor.data_length()
        while self.predictor.has_next():
            supp, y_pred, y_proba, y = self.predictor.next_test()
            
            if verbose:
                ui.print_progress_bar(i, n)
                i += 1

            datetime_str = supp["datetime"].item()
            home_team_id = supp["home_team"].item()
            away_team_id = supp["away_team"].item()
            if home_team_id not in team_dict:
                team_dict[home_team_id] = statsapi.lookup_team(home_team_id)[0]["name"]
            if away_team_id not in team_dict:
                team_dict[away_team_id] = statsapi.lookup_team(away_team_id)[0]["name"]
            home_team = team_dict[home_team_id]
            away_team = team_dict[away_team_id]
            game_date = datetime_str.split("T")[0]
            home_odds, away_odds = OddsArchive.instance.get_odds(game_date, home_team, away_team)

            datetime_str = datetime_str[:-1] + "+00:00"
            start_datetime_obj = datetime.fromisoformat(datetime_str)
            end_datetime_obj = start_datetime_obj + timedelta(hours=4)


            if home_odds == None or away_odds == None:
                continue

            transaction_index = 0
            while transaction_index < len(ongoing_games):
                transaction_num, transaction_end_time, transaction_y, transaction_home_team, transaction_away_team, transaction_game_date = ongoing_games[transaction_index]
                transaction_index += 1
                if start_datetime_obj >= transaction_end_time:
                    transaction_index -= 1
                    ongoing_games.pop(transaction_index)
                    transaction = self.betting_strategy.get_transaction(transaction_num)
                    updated_transaction = self.betting_strategy.evaluate_outcome(transaction_num, transaction_y)
                    if updated_transaction != None:
                        transaction = updated_transaction
                    else:
                        continue
                    y_pred_list.append(y_pred)
                    y_proba_list.append(y_proba)
                    y_list.append(y)
                    if "supplemental_data" in transaction:
                        transaction.pop("supplemental_data")
                    transaction["date"] = transaction_game_date
                    transaction["home_team"] = transaction_home_team
                    transaction["away_team"] = transaction_away_team
                    if write_headers:
                        csv_writer = csv.DictWriter(csvfile, fieldnames=list(transaction.keys()), delimiter=",")
                        csv_writer.writeheader()
                        write_headers = False
                    csv_writer.writerow(transaction)
                    if transaction["bankroll_final"] == 0:
                        break
            transaction_num = self.betting_strategy.place_bet(supp, home_odds, away_odds, y_pred, y_proba)
            ongoing_games.append([transaction_num, end_datetime_obj, y, home_team, away_team, game_date])
        for transaction_num, _, transaction_y, transaction_home_team, transaction_away_team, transaction_game_date in ongoing_games:
            transaction = self.betting_strategy.get_transaction(transaction_num)
            updated_transaction = self.betting_strategy.evaluate_outcome(transaction_num, transaction_y)
            if updated_transaction != None:
                transaction = updated_transaction
            else:
                continue
            y_pred_list.append(y_pred)
            y_proba_list.append(y_proba)
            y_list.append(y)
            if "supplemental_data" in transaction:
                transaction.pop("supplemental_data")
            transaction["date"] = transaction_game_date
            transaction["home_team"] = transaction_home_team
            transaction["away_team"] = transaction_away_team
            if write_headers:
                csv_writer = csv.DictWriter(csvfile, fieldnames=list(transaction.keys()), delimiter=",")
                csv_writer.writeheader()
                write_headers = False
            csv_writer.writerow(transaction)
        if verbose:
            ui.print_progress_bar(n, n)
        self.predictor.flush_data()
        csvfile.close()

        out_dict = {
            "accuracy": accuracy_score(y_list, y_pred_list),
            "brier_score": brier_score_loss(y_list, y_proba_list),
            "balance": self.betting_strategy.get_balance()
        }
        return out_dict
    
    def get_next_bets(self, verbose=False):
        bets = []
        
        self.predictor.load_upcoming(verbose=verbose)
        while self.predictor.has_next():
            supp, y_pred, y_proba = self.predictor.next()
            datetime_str = supp["datetime"].item()
            home_team_id = supp["home_team"].item()
            away_team_id = supp["away_team"].item()
            home_team = statsapi.lookup_team(home_team_id)[0]["name"]
            away_team = statsapi.lookup_team(away_team_id)[0]["name"]
            game_date = datetime_str.split("T")[0]
            #home_odds, away_odds = OddsArchive.instance.get_odds(game_date, home_team, away_team)
            home_odds, away_odds = OddsArchive.instance.get_live_odds(home_team, away_team)

            #print("pre odds")

            if home_odds == None or away_odds == None:
                continue

            #print("bet")
            transaction_num = self.betting_strategy.place_bet(supp, home_odds, away_odds, y_pred, y_proba)
            transaction = self.betting_strategy.get_transaction(transaction_num)
            #if transaction["bet_amount"] > 0:
            if True:
                transaction["home_team"] = home_team
                transaction["away_team"] = away_team

                #print(transaction)
                #print()

                bet_size = transaction["bet_amount"]
                pred_team_name = transaction["home_team"] if transaction["predicted_outcome"] == 1 else transaction["away_team"] if transaction["predicted_outcome"] == 0 else "NULL"
                dec_odds = transaction["home_odds"] if transaction["predicted_outcome"] == 1 else transaction["away_odds"] if transaction["predicted_outcome"] == 0 else "NULL"
                odds = dec_to_american_odds(dec_odds)
                kelly = transaction["kelly_fraction"]
                bets.append((pred_team_name, odds, bet_size, kelly))
        return bets
    
    def optimize_hyper_params(model, eval_metric, opt_func, max_evals=15):
        space = {}
        for name in model.predictor._params:
            match model.predictor._params[name]["distribution_type"]:
                case "uniform":
                    space[name] = hp.quniform(name, model.predictor._params[name]["min"], model.predictor._params[name]["max"], model.predictor._params[name]["q"])
                case "loguniform":
                    space[name] = hp.qloguniform(name, model.predictor._params[name]["min"], model.predictor._params[name]["max"], model.predictor._params[name]["q"])

        def eval_func(params):
            model.predictor.set_params(params)
            model.predictor.reset()
            model.train()
            metrics = None
            if eval_metric != "balance":
                metrics = model.test()
            else:
                metrics = model.test_profits("optimize_bets.csv")
            if opt_func == "min":
                return metrics[eval_metric]
            elif opt_func == "max":
                return metrics[eval_metric] * -1
                #return 1 - metrics[eval_metric]
            else:
                return 0

        trials = Trials()
        params = fmin(eval_func, space=space,  algo=tpe.suggest, max_evals=max_evals, trials=trials)
        return params