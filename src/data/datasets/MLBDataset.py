from data.Dataset import Dataset
from data.Column import Column
from data.datasets.MLBTeamColumnGroup import MLBTeamColumnGroup

import data.columns.mlb_team_functions as TeamCol

class MLBDataset(Dataset):
    def __init__(self):
        super().__init__()

        self.add_ghost_column(Column("home_team_stats_ghost", TeamCol.get_team_fetch_all_stats_func(True), archive_id="team_stats"))
        self.add_ghost_column(Column("away_team_stats_ghost", TeamCol.get_team_fetch_all_stats_func(False), archive_id="team_stats"))

        #self.add_column(Column("datetime", MLBCol.date))
        self.add_column(MLBTeamColumnGroup("home_team", is_home_team=True))
        self.add_column(MLBTeamColumnGroup("away_team", is_home_team=False))
        
        self.output_column = "home_team_win"
        self.add_column(Column(self.output_column, TeamCol.home_team_win))