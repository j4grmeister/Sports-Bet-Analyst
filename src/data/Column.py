class Column:
    _column_count = 0
    _archives = {}

    def __init__(self, name, generation_function, archive_id=None, **kwargs):
        self.name = name
        self._keys = kwargs
        self.generation_function = generation_function
        
        #TODO: error check that generation_function has the correct signature
        
        if archive_id != None:
            #TODO: error check type of id
            self.archive_id = archive_id
        else:
            self.archive_id = Column._column_count
            Column._column_count += 1
        if self.archive_id not in Column._archives:
            Column._archives[self.archive_id] = {}

    def width(self):
        return 1

    def update_keys(self, kv):
        self._keys.update(kv)

    def next(self, *args):
        self.before_iterate(*args)
        value = self.generation_function(Column._archives[self.archive_id], *args, **self._keys)
        return (value)
    
    def next_dict(self, *args):
        self.before_iterate(*args)
        value = self.generation_function(Column._archives[self.archive_id], *args, **self._keys)
        return {self.name: value}
    
    def before_iterate(self, *args):
        pass