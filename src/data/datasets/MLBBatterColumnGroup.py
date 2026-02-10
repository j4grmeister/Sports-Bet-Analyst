from data.Column import Column
from data.ColumnGroup import ColumnGroup
import data.columns.mlb_player_functions as PlayerCol

class MLBBatterColumnGroup(ColumnGroup):
    def __init__(self, name, **kwargs):
        if "order" not in kwargs:
            kwargs["order"] = 1
        super().__init__(name, **kwargs)

        #add columns
        self.add_column(Column("AVG", PlayerCol.get_stat_moving_avg_func("AVG", "batting"), archive_id="player_stats"))
        self.add_column(Column("OBP", PlayerCol.get_stat_moving_avg_func("OBP", "batting"), archive_id="player_stats"))
        self.add_column(Column("SLG", PlayerCol.get_stat_moving_avg_func("SLG", "batting"), archive_id="player_stats"))
        self.add_column(Column("OPS", PlayerCol.get_stat_moving_avg_func("OPS", "batting"), archive_id="player_stats"))
        self.add_column(Column("HR", PlayerCol.get_stat_moving_avg_func("HR", "batting"), archive_id="player_stats"))
        self.add_column(Column("RBI", PlayerCol.get_stat_moving_avg_func("RBI", "batting"), archive_id="player_stats"))
        self.add_column(Column("K", PlayerCol.get_stat_moving_avg_func("K", "batting"), archive_id="player_stats"))
    
    def before_iterate(self, *args):
        box = args[0]
        TEAM = "home" if self._keys["is_home_team"] else "away"
        batter = box[f"{TEAM}Batters"][self._keys["order"]]
        player_id = batter["personId"]
        self.update_keys({"player_id": player_id})