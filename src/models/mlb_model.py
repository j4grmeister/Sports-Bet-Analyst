from data.ColumnGenerator import ColumnGenerator
from data.Column import Column
import data.columns.mlb_functions as MLBCol

dummy_home_team_stats = Column("DUMMY_COLUMN", ColumnGenerator(MLBCol.get_team_fetch_all_stats_func(True), id="TeamStats"), in_dataset=False)
dummy_away_team_stats = Column("DUMMY_COLUMN", ColumnGenerator(MLBCol.get_team_fetch_all_stats_func(False), id="TeamStats"), in_dataset=False)

datetime = Column("datetime", ColumnGenerator(MLBCol.date), training_data=False)
home_team = Column("home_team", ColumnGenerator(MLBCol.get_team_func(True)))
away_team = Column("away_team", ColumnGenerator(MLBCol.get_team_func(False)))
home_team_wOBA = Column("home_team_wOBA", ColumnGenerator(MLBCol.get_team_wOBA_func(True), id="TeamStats"))
away_team_wOBA = Column("away_team_wOBA", ColumnGenerator(MLBCol.get_team_wOBA_func(False), id="TeamStats"))
home_team_OPS = Column("home_team_OPS", ColumnGenerator(MLBCol.get_team_OPS_func(True), id="TeamStats"))
away_team_OPS = Column("away_team_OPS", ColumnGenerator(MLBCol.get_team_OPS_func(False), id="TeamStats"))
home_team_starting_pitcher = Column("home_team_starting_pitcher", ColumnGenerator(MLBCol.get_team_starting_pitcher_func(True)))
away_team_starting_pitcher = Column("away_team_starting_pitcher", ColumnGenerator(MLBCol.get_team_starting_pitcher_func(False)))
home_team_rolling_win_percent_10 = Column("home_team_rolling_win_percent_10", ColumnGenerator(MLBCol.get_team_rolling_win_percent_func(True, window_size=10), id="TeamWins"))
away_team_rolling_win_percent_10 = Column("away_team_rolling_win_percent_10", ColumnGenerator(MLBCol.get_team_rolling_win_percent_func(False, window_size=10), id="TeamWins"))
home_team_win = Column("home_team_win", ColumnGenerator(MLBCol.home_team_win), out_column=True)

columns = [
    dummy_home_team_stats,
    dummy_away_team_stats,
    datetime,
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

output_column_name = "home_team_win"

non_training_columns = [
    "datetime"
]