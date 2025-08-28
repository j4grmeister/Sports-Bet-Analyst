import csv
import statsapi
from datetime import datetime

from data.Dataset import Dataset
from data.Column import Column
from data.datasets.MLBTeamColumnGroup import MLBTeamColumnGroup

import data.columns.mlb_team_functions as TeamCol
import data.columns.mlb_player_functions as PlayerCol

import ui

class MLBDataset(Dataset):
    output_column = "home_team_win"
    non_training_columns = ["datetime", "home_team", "away_team"]

    def __init__(self):
        super().__init__()

        self.add_ghost_column(Column("home_team_stats_ghost", TeamCol.get_team_fetch_all_stats_func(True), archive_id="team_stats"))
        self.add_ghost_column(Column("away_team_stats_ghost", TeamCol.get_team_fetch_all_stats_func(False), archive_id="team_stats"))
        self.add_ghost_column(Column("home_team_stats_ghost", PlayerCol.get_player_fetch_all_stats_func(True), archive_id="player_stats"))
        self.add_ghost_column(Column("away_team_stats_ghost", PlayerCol.get_player_fetch_all_stats_func(False), archive_id="player_stats"))

        self.add_column(Column("datetime", TeamCol.date))
        self.add_column(Column("home_team", TeamCol.get_team_func(True)))
        self.add_column(Column("away_team", TeamCol.get_team_func(False)))
        self.add_column(MLBTeamColumnGroup("home_team", is_home_team=True))
        self.add_column(MLBTeamColumnGroup("away_team", is_home_team=False))
        
        self.add_column(Column(self.output_column, TeamCol.home_team_win))
    
    def build_dataset(self, filename, start_date, end_date, verbose=False):
        # get all the MLB data
        if verbose:
            print("Fetching MLB schedule")
        all_games = statsapi.schedule(start_date=start_date, end_date=end_date)

        args_array = []

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
        dataset = self.iterate_dict(args_array, verbose=verbose)


        with open(filename, "w", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers(), delimiter=",")
            writer.writeheader()
            writer.writerows(dataset)

    def build_upcoming_rows(self, verbose=False):
        if verbose:
            print("Fetching MLB schedule")
        today = datetime.today()
        today_formatted = today.strftime("%m/%d/%Y")
        print(today_formatted)
        all_games = statsapi.schedule(start_date=today_formatted, end_date=today_formatted)

        args_array = []

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
            
            if not (game_status == "Warmup" or game_status == "Scheduled" or game_status == "Pre-Game"):
                continue

            if game_type == "E":
                continue
            if home_pitcher == "" or away_pitcher == "":
                continue

            boxscore = statsapi.boxscore_data(game_id)

            if len(boxscore[f"homeBatters"]) <= 1 or len(boxscore[f"awayBatters"]) <= 1:
                continue

            args_array.append((boxscore, game))

        if verbose:
            ui.print_progress_bar(total_games, total_games)
        dataset = self.iterate_dict(args_array, peek=True, verbose=verbose)
        return dataset
