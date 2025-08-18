class ColumnGenerator:
    generator_count = 0
    archives = {}

    def __init__(self, generation_function, id=None):
        #TODO: error check that generation_function has the correct signature
        
        if id != None:
            #TODO: error check type of id
            self.id = id
        else:
            self.id = ColumnGenerator.generator_count
            ColumnGenerator.generator_count += 1
        
        self.generation_function = generation_function
        self.test = 0

        if self.id not in ColumnGenerator.archives:
            ColumnGenerator.archives[self.id] = {}


    # Iteratively generates the entire column of data
    def generate(self, *args):
        value = self.generation_function(ColumnGenerator.archives[self.id], args)
        return value