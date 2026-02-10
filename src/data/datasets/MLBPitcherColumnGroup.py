from data.Column import Column
from data.ColumnGroup import ColumnGroup
import data.columns.mlb_player_functions as PlayerCol

class MLBPitcherColumnGroup(ColumnGroup):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        #add columns
        """
        self.add_column(Column("ERA", PlayerCol.calc_pitcher_ERA, archive_id="player_stats"))
        self.add_column(Column("WHIP", PlayerCol.calc_pitcher_WHIP, archive_id="player_stats"))
        self.add_column(Column("K9", PlayerCol.calc_pitcher_K9, archive_id="player_stats"))
        self.add_column(Column("KBB", PlayerCol.calc_pitcher_KBB, archive_id="player_stats"))
        """
        self.add_column(Column("ERA", PlayerCol.get_stat_moving_avg_func("ERA", "pitching"), archive_id="player_stats"))
        self.add_column(Column("WHIP", PlayerCol.get_stat_moving_avg_func("WHIP", "pitching"), archive_id="player_stats"))
        #self.add_column(Column("K9", PlayerCol.get_stat_moving_avg_func("K9", "pitching"), archive_id="player_stats"))
        self.add_column(Column("K", PlayerCol.get_stat_moving_avg_func("K", "pitching"), archive_id="player_stats"))
        self.add_column(Column("KBB", PlayerCol.get_stat_moving_avg_func("KBB", "pitching"), archive_id="player_stats"))
        self.add_column(Column("IP", PlayerCol.get_stat_moving_avg_func("IP", "pitching"), archive_id="player_stats"))
        self.add_column(Column("HR", PlayerCol.get_stat_moving_avg_func("HR", "pitching"), archive_id="player_stats"))
        
    def before_iterate(self, *args):
        summary = args[1]
        TEAM = "home" if self._keys["is_home_team"] else "away"
        probable_pitcher = summary[f"{TEAM}_probable_pitcher"]
        player_id = Column._archives["player_stats"]["names"][probable_pitcher]["id"]

        self.update_keys({"player_id": player_id})
