from data.Column import Column
from data.ColumnGroup import ColumnGroup
from data.datasets.MLBPitcherColumnGroup import MLBPitcherColumnGroup
from data.datasets.MLBBatterColumnGroup import MLBBatterColumnGroup
import data.columns.mlb_team_functions as TeamCol

class MLBTeamColumnGroup(ColumnGroup):
    def __init__(self, team_name, **kwargs):
        super().__init__(team_name, **kwargs)
        
        self.add_column(Column("wOBA", TeamCol.get_team_wOBA_func(self.keys["is_home_team"]), archive_id="team_stats"))
        self.add_column(Column("OPS", TeamCol.get_team_OPS_func(self.keys["is_home_team"]), archive_id="team_stats"))
        self.add_column(Column("rolling_win_percent_10", TeamCol.get_team_rolling_win_percent_func(self.keys["is_home_team"], window_size=10), archive_id="team_wins"))
        
        self.add_column(MLBPitcherColumnGroup("starting_pitcher"))
        self.add_column(MLBBatterColumnGroup("batter_1", order=1))
        self.add_column(MLBBatterColumnGroup("batter_2", order=2))
        self.add_column(MLBBatterColumnGroup("batter_3", order=3))
        self.add_column(MLBBatterColumnGroup("batter_4", order=4))
        self.add_column(MLBBatterColumnGroup("batter_5", order=5))
        self.add_column(MLBBatterColumnGroup("batter_6", order=6))
        self.add_column(MLBBatterColumnGroup("batter_7", order=7))
        self.add_column(MLBBatterColumnGroup("batter_8", order=8))
        self.add_column(MLBBatterColumnGroup("batter_9", order=9))