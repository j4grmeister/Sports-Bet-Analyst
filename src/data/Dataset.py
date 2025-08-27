import copy

from data.ColumnGroup import ColumnGroup
import ui

class Dataset:
    def __init__(self):
        self.ghost_columns = ColumnGroup("")
        self.columns = ColumnGroup("")
        self.ghost_columns.child_name_delimiter = ""
        self.columns.child_name_delimiter = ""
    
    def add_ghost_column(self, column):
        self.ghost_columns.add_column(column)

    def add_column(self, column):
        self.columns.add_column(column)

    def headers(self):
        return self.columns.headers()

    def next(self, *args):
        self.ghost_columns.next(*args[1:])
        return self.columns.next(*args[1:])
    
    def peek(self, *args):
        return self.columns.next(*args[1:])
    
    def next_dict(self, *args):
        self.ghost_columns.next_dict(*args[1:])
        return self.columns.next_dict(*args[1:])
    
    def peek_dict(self, *args):
        return self.columns.next_dict(*args[1:])

    def iterate_dict(self, args_array, peek=False, verbose=False):
        dataset = []
        if verbose:
            print("Building dataset")
        index = 0
        total_rows = len(args_array)
        for args in args_array:
            if verbose:
                ui.print_progress_bar(index, total_rows)
            index += 1

            row = self.peek_dict(self, *args) if peek else self.next_dict(self, *args)
            dataset.append(row)
        if verbose:
            ui.print_progress_bar(total_rows, total_rows)
        return dataset
    
    def build_dataset(self, filename, start_date, end_date, verbose=False):
        pass

    def build_upcoming_rows(self, verbose=False):
        pass