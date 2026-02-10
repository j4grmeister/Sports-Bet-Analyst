import os
import joblib
import json

import pandas as pd
from sklearn.metrics import brier_score_loss, accuracy_score

config = {}
with open("config.json", "r") as config_file:
    config = json.load(config_file)

API_KEY = config["odds_api_key"]

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
        self._params = {}

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

    def reset(self):
        if "hyperparams" in config:
            for param in self._params:
                name = self._params[param]["name"]
                if name in config["hyperparams"]:
                    self._params[param]["value"] = config["hyperparams"][name]

    def data_length(self):
        return len(self.loaded_X)
    
    def add_param(self, name, value, min, max, q, distribution_type):
        if name not in self._params:
            self._params[name] = {
                "name": name,
                "value": value,
                "min": min,
                "max": max,
                "q": q,
                "distribution_type": distribution_type
            }

    def set_param(self, name, value):
        if name in self._params:
            self._params[name]["value"] = value
    
    def set_params(self, params):
        for key in params:
            self.set_param(key, params[key])
    
    def get_param(self, name):
        if name in self._params:
            return self._params[name]["value"]
        return None

    def train(self, verbose=False):
        pass

    def load(self, df):
        if df.empty:
            return
        X, self.loaded_supp = self._extract_supplemental_data(df)
        self.loaded_X = self._preprocess(X)

    def load_test(self, verbose=False):
        if not os.path.exists(self.testing_dataset_filepath):
            self.dataset.build_dataset(self.testing_dataset_filepath, self.testing_start_date, self.testing_end_date, verbose=verbose)
        df = pd.read_csv(self.testing_dataset_filepath)
        self.loaded_y = df[self.dataset.output_column]
        self.load(df)

    def load_upcoming(self, verbose=False):
        df = pd.DataFrame(self.dataset.build_upcoming_rows(verbose=verbose))
        # output column here is trash data. No need to drop it as it is dropped by self.load in self._extract_supplemental_data
        self.load(df)
    
    def flush_data(self):
        self.loaded_X = pd.DataFrame()
        self.loaded_supp = pd.DataFrame()
        self.loaded_y = pd.DataFrame()

    def test(self, verbose=False):
        if not self.has_next():
            return {}
        
        y_pred, y_proba = self._predict(self.loaded_X)


        out_dict = {
            "accuracy": accuracy_score(self.loaded_y, y_pred),
            "brier_score": brier_score_loss(self.loaded_y, y_proba)
        }
        self.flush_data()
        return out_dict

    def has_next(self):
        return self.loaded_X.size != 0

    def next(self):
        X = self.loaded_X.iloc[[0]]
        supp = self.loaded_supp.iloc[[0]]
        y_pred, y_proba = self._predict(X)
        self.loaded_X = self.loaded_X.iloc[1:]
        self.loaded_supp = self.loaded_supp.iloc[1:]
        return supp, y_pred.item(), y_proba.item()
    
    def next_test(self):
        supp, y_pred, y_proba = self.next()
        y = self.loaded_y.iloc[[0]]
        self.loaded_y = self.loaded_y.iloc[1:]
        return supp, y_pred, y_proba, y.item()

    def write_file(predictor):
        joblib.dump(predictor, predictor.save_filepath)

    def read_file(filepath):
        return joblib.load(filepath)