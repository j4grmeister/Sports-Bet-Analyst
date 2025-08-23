import os
import joblib

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from models.Predictor import Predictor
from data.datasets.MLBDataset import MLBDataset

class MLBPredictor(Predictor):
    def __init__(self, dirpath):
        super().__init__(dirpath)
        self.dataset = MLBDataset()
        self.training_dataset_filepath = os.path.join(dirpath, "training_dataset.csv")
        self.testing_dataset_filepath = os.path.join(dirpath, "testing_dataset.csv")

        self.training_start_date = "01/01/2024"
        self.training_end_date = "01/01/2025"
        self.testing_start_date = "01/01/2025"
        self.testing_end_date = "01/01/2026"

        self.model = XGBClassifier(eval_metric="logloss", n_estimators=50)
        self.calibrator = SGDClassifier(loss='log_loss', alpha=1e-3, max_iter=1000)
        self.scaler = StandardScaler()

    def _predict(self, X):
        y_pred_raw = self.model.predict(X).reshape(-1, 1)
        y_proba_raw = self.model.predict_proba(X)[:,1].reshape(-1, 1)
        y_pred = self.calibrator.predict(y_pred_raw)
        y_proba = self.calibrator.predict_proba(y_proba_raw)[:,1]
        return y_pred, y_proba
    
    def _preprocess(self, X):
        return pd.DataFrame(self.scaler.transform(X))
    
    def train(self, verbose=False):
        if not os.path.exists(self.training_dataset_filepath):
            self.dataset.build_dataset(self.training_dataset_filepath, self.training_start_date, self.training_end_date, verbose=verbose)

        df = pd.read_csv(self.training_dataset_filepath)

        X = df.drop(self.dataset.output_column, axis = 1)
        for drop_column in self.dataset.non_training_columns:
            X = X.drop(drop_column, axis = 1)
        y = df[self.dataset.output_column]

        self.scaler.fit(X)

        X_train, X_cal, y_train, y_cal = train_test_split(X, y, test_size=.2, random_state=34)

        X_train_scaled = self.scaler.transform(X_train)
        X_cal_scaled = self.scaler.transform(X_cal)

        self.model.fit(X_train_scaled, y_train)

        uncalibrated_probs = self.model.predict_proba(X_cal_scaled)[:, 1].reshape(-1, 1)

        self.calibrator.partial_fit(uncalibrated_probs, y_cal, classes=np.array([0, 1]))

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
        joblib.dump(predictor.model, os.path.join(predictor.dirpath, "model.joblib"))
        joblib.dump(predictor.calibrator, os.path.join(predictor.dirpath, "calibrator.joblib"))
        joblib.dump(predictor.scaler, os.path.join(predictor.dirpath, "scaler.joblib"))

    def read_file(filepath):
        predictor = MLBPredictor(filepath)
        predictor.model = joblib.load(os.path.join(filepath, "model.joblib"))
        predictor.calibrator = joblib.load(os.path.join(filepath, "calibrator.joblib"))
        predictor.scaler = joblib.load(os.path.join(filepath, "scaler.joblib"))
        return predictor