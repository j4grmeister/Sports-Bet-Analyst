from data.ColumnGroup import ColumnGroup

class MLBBatterColumnGroup(ColumnGroup):
    def __init__(self, name, **kwargs):
        if "order" not in kwargs:
            kwargs["order"] = 1
        super().__init__(name, **kwargs)

        #add columns
        

    def before_iterate(self, *args):
        if "player_id" not in args:
            return
        self.update_keys({"player_id": args["player_id"]})