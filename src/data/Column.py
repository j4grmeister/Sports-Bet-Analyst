class Column:

    def __init__(self, name, generator, in_dataset=True, out_column=False, training_data=True):
        self.name = name
        self.generator = generator
        self.in_dataset = in_dataset
        self.out_column = out_column
        self.training_data = training_data
        
