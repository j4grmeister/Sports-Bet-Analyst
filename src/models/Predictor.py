import os
import joblib

import pandas as pd

class Predictor:
    def __init__(self, dirpath, dataset):
        self.__init_helper(dirpath, dataset)

    def __init__(self, dirpath):
        self.__init_helper(dirpath, None)

    def __init_helper(self, dirpath, dataset):
        self.dirpath = dirpath
        self.save_filepath = os.path.join(dirpath, "predictor.joblib")
        self.dataset = dataset
        self.loaded_X = pd.DataFrame()
        self.loaded_supp = pd.DataFrame()
        self.loaded_y = pd.DataFrame()

    def _preprocess(self, X):
        return X

    def _extract_supplemental_data(self, df):
        X = df
        supp = df
        for column in self.dataset.headers():
            if column in self.dataset.non_training_columns or column == self.dataset.output_column:
                X = X.drop(column, axis=1)
            if column not in self.dataset.non_training_columns:
                supp = supp.drop(column, axis=1)
        return X, supp

    def train(self, verbose=False):
        pass

    def load(self, df):
        X, self.loaded_supp = self._extract_supplemental_data(df)
        self.loaded_X = self._preprocess(X)

    def load_test(self, verbose=False):
        if not os.path.exists(self.testing_dataset_filepath):
            self.dataset.build_dataset(self.testing_dataset_filepath, self.testing_start_date, self.testing_end_date, verbose=verbose)
        df = pd.read_csv(self.testing_dataset_filepath)
        self.loaded_y = df[self.dataset.output_column]
        self.load(df)
    
    def flush_data(self):
        self.loaded_X = pd.DataFrame()
        self.loaded_supp = pd.DataFrame()
        self.loaded_y = pd.DataFrame()

    def test(self, verbose=False):
        return {}

    def has_next(self):
        return self.loaded_X.size != 0

    def next(self):
        return None, None, None, None

    def write_file(predictor):
        joblib.dump(predictor, predictor.save_filepath)

    def read_file(filepath):
        return joblib.load(filepath)