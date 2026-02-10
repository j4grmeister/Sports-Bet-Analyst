import os
import joblib

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from data.Column import Column
from models.Predictor import Predictor
from data.datasets.MLBDataset import MLBDataset

class MLBPredictor(Predictor):
    def __init__(self, dirpath):
        super().__init__(dirpath)
        self.dataset = MLBDataset()
        self.training_dataset_filepath = os.path.join(dirpath, "training_dataset.csv")
        self.testing_dataset_filepath = os.path.join(dirpath, "testing_dataset.csv")

        self.training_start_date = "01/01/2024"
        self.training_end_date = "12/31/2024"
        self.testing_start_date = "01/01/2025"
        self.testing_end_date = "12/31/2025"
        
        self.add_param("model.learning_rate", .1, .01, .1, .01, "loguniform")
        self.add_param("model.n_estimators", 94, 50, 1000, 1, "uniform")
        self.add_param("model.max_depth", 1, 3, 10, 1, "uniform")
        self.add_param("model.subsample", .8, .5, 1, .01, "uniform")
        self.add_param("model.colsample_bytree", .8, .5, 1, .01, "uniform")
        self.add_param("model.min_child_weight", 5, 1, 20, 1, "uniform")
        self.add_param("model.gamma", 1, 0, 10, .1, "uniform")
        self.add_param("model.reg_alpha", 1, 1e-5, 10, 1e-5, "loguniform")
        self.add_param("model.reg_lambda", 1, 1e-5, 10, 1e-5, "loguniform")
        #self.add_param("model.early_stopping_rounds", 10, 10, 50, 1, "uniform")
        
        
        #self.add_param("calibrator.alpha", .01, np.log(1e-2), np.log(1e2), 1e-2, "loguniform")
        #self.add_param("calibrator.max_iter", 700, 100, 2000, 100, "uniform")
        #self.add_param("train_test_size", .19, .01, .99, .01, "uniform")

        self.reset()

    def _predict(self, X):
        #y_pred_raw = self.model.predict(X).reshape(-1, 1)
        y_pred = self.model.predict(X)
        #y_proba_raw = self.model.predict_proba(X)[:,1].reshape(-1, 1)
        y_proba = self.model.predict_proba(X)[:,1]
        #y_pred = self.calibrator.predict(y_pred_raw)
        #y_proba = self.calibrator.predict_proba(y_proba_raw)[:,1]
        #print(y_pred)
        return y_pred, y_proba
    
    def _filter_rows(self, df):
        df_filtered = df[df["home_team_games_played"] >= 10]
        df_filtered = df_filtered[df_filtered["away_team_games_played"] >= 10]
        return df_filtered

    def _preprocess(self, X):
        return pd.DataFrame(self.scaler.transform(X))
    
    def reset(self):
        super().reset()
        #self.model = XGBClassifier(eval_metric="logloss", n_estimators=int(self.get_param("model.n_estimators")), random_state=34)
        #self.calibrator = SGDClassifier(loss='log_loss', alpha=self.get_param("calibrator.alpha"), max_iter=int(self.get_param("calibrator.max_iter")), class_weight="balanced", eta0=.1, learning_rate="constant", random_state=34)
        self.model = XGBClassifier(
            learning_rate=self.get_param("model.learning_rate"),
            eval_metric="logloss", 
            n_estimators=int(self.get_param("model.n_estimators")),
            max_depth=int(self.get_param("model.max_depth")),
            subsample=self.get_param("model.subsample"),
            colsample_bytree=self.get_param("model.colsample_bytree"),
            min_child_weight=int(self.get_param("model.min_child_weight")),
            gamma=self.get_param("model.gamma"),
            reg_alpha=self.get_param("model.reg_alpha"),
            reg_lambda=self.get_param("model.reg_lambda"),
            #early_stopping_rounds=self.get_param("model.early_stopping_rounds"),
            random_state=34)
        self.calibrator = None
        self.scaler = StandardScaler()
    
    def train(self, verbose=False):
        if not os.path.exists(self.training_dataset_filepath):
            self.dataset.build_dataset(self.training_dataset_filepath, self.training_start_date, self.training_end_date, verbose=verbose)

        df = pd.read_csv(self.training_dataset_filepath)
        
        df = df[df["home_team_games_played"] >= 10]
        df = df[df["away_team_games_played"] >= 10]

        X = df.drop(self.dataset.output_column, axis = 1)
        for drop_column in self.dataset.non_training_columns:
            X = X.drop(drop_column, axis = 1)
        y = df[self.dataset.output_column]


        self.scaler.fit(X)

        #X_train, X_cal, y_train, y_cal = train_test_split(X, y, test_size=self.get_param("train_test_size"), random_state=34)
        #X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=34)
        #X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=34)
        ##X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=34)
        #X_train_scaled = self.scaler.transform(X_train)
        #X_cal_scaled = self.scaler.transform(X_cal)

        ##X_train_scaled = self.scaler.transform(X_train)
        ##X_val_scaled = self.scaler.transform(X_val)
        X_scaled = self.scaler.transform(X)
        #X_test_scaled = self.scaler.transform(X_test)

        #self.model.fit(X_train_scaled, y_train)
        """
        self.model.fit(X_train_scaled, y_train,
            eval_set = [[X_train_scaled, y_train],
                [X_val_scaled, y_val]],
            verbose=verbose)
            """
        self.model.fit(X_scaled, y,
            verbose=verbose)

        #uncalibrated_probs = self.model.predict_proba(X_cal_scaled)[:, 1].reshape(-1, 1)

        #print(y_cal)

        #self.calibrator.partial_fit(uncalibrated_probs, y_cal, classes=np.array([0, 1]))
        #self.calibrator.fit(uncalibrated_probs, y_cal)
    
    def write_file(predictor):
        joblib.dump(predictor.model, os.path.join(predictor.dirpath, "model.joblib"))
        joblib.dump(predictor.calibrator, os.path.join(predictor.dirpath, "calibrator.joblib"))
        joblib.dump(predictor.scaler, os.path.join(predictor.dirpath, "scaler.joblib"))
        Column.save(os.path.join(predictor.dirpath, "column_archives.joblib"))

    def read_file(filepath):
        predictor = MLBPredictor(filepath)
        predictor.model = joblib.load(os.path.join(filepath, "model.joblib"))
        predictor.calibrator = joblib.load(os.path.join(filepath, "calibrator.joblib"))
        predictor.scaler = joblib.load(os.path.join(filepath, "scaler.joblib"))
        
        if os.path.exists(os.path.join(predictor.dirpath, "column_archives.joblib")):
            Column.load(os.path.join(predictor.dirpath, "column_archives.joblib"))
        return predictor