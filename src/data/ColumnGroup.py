import copy

from data.Column import Column

class ColumnGroup(Column):

    def __init__(self, name, **kwargs):
        self.child_name_delimiter = "_"
        self.name = name
        self._keys = kwargs
        self.columns = []
    
    def _deep_rename_child_columns(self, child):
        if issubclass(type(child), ColumnGroup):
            for col in child.columns:
                self._deep_rename_child_columns(col)
        child.name = self.name + self.child_name_delimiter + child.name

    def add_column(self, column):
        col_copy = copy.deepcopy(column)
        self._deep_rename_child_columns(col_copy)
        col_copy.update_keys(self._keys)
        self.columns.append(col_copy)

    def width(self):
        width = 0
        for col in self.columns:
            width += col.width()
        return width
    
    def update_keys(self, kv):
        super().update_keys(kv)
        for col in self.columns:
            col.update_keys(kv)
    
    def headers(self):
        headers = []
        for col in self.columns:
            if issubclass(type(col), ColumnGroup):
                headers.extend(col.headers())
            else:
                headers.append(col.name)
        return tuple(headers)
    
    def next(self, *args):
        self.before_iterate(*args)
        values = []
        for col in self.columns:
            val = col.next(*args)
            values.extend(val)
        return tuple(values)

    def next_dict(self, *args):
        self.before_iterate(*args)
        values = {}
        for col in self.columns:
            vals = col.next_dict(*args)
            values.update(vals)
        return values