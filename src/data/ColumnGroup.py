import copy

from data.Column import Column

class ColumnGroup(Column):

    def __init__(self, name, **kwargs):
        self.child_name_delimiter = "_"
        self.name = name
        self.keys = kwargs
        self.columns = []
    
    def add_column(self, column):
        col_copy = copy.deepcopy(column)
        col_copy.name = self.name + self.child_name_delimiter + col_copy.name
        col_copy.keys.update(self.keys)
        self.columns.append(col_copy)

    def width(self):
        width = 0
        for col in self.columns:
            width += col.width()
        return width
    
    def headers(self):
        headers = []
        for col in self.columns:
            if issubclass(type(col), ColumnGroup):
                headers.extend(col.headers())
            headers.append(col.name)
        return tuple(headers)
    
    def next(self, *args):
        values = []
        for col in self.columns:
            val = col.next(*args)
            values.extend(val)
        return tuple(values)

    def next_dict(self, *args):
        values = {}
        for col in self.columns:
            vals = col.next_dict(*args)
            values.update(vals)
        return values