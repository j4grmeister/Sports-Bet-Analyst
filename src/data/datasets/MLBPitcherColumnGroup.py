from data.ColumnGroup import ColumnGroup

class MLBPitcherColumnGroup(ColumnGroup):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        #add columns