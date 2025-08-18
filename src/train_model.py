import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.calibration import FrozenEstimator
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import brier_score_loss, accuracy_score
from xgboost import XGBClassifier
import models.mlb_model as mlb_model
import joblib

DATASET_FILEPATH = "data/training_dataset.csv"

df = pd.read_csv(DATASET_FILEPATH)

X = df.drop(mlb_model.output_column_name, axis = 1)
for drop_column in mlb_model.non_training_columns:
    X = X.drop(drop_column, axis = 1)
y = df[mlb_model.output_column_name]

X_train, X_cal, y_train, y_cal = train_test_split(X, y, test_size=.2, random_state=42)
#time_series_split = TimeSeriesSplit()

#X_train = X
#y_train = y

model = XGBClassifier(eval_metric="logloss", n_estimators=50)
model.fit(X_train, y_train)

#calibrated_model = CalibratedClassifierCV(estimator=model, cv=3, method="sigmoid")
#calibrated_model = FrozenEstimator(model)
#calibrated_model.fit(X_train, y_train)

uncalibrated_probs = model.predict_proba(X_cal)[:, 1].reshape(-1, 1)

calibrator = SGDClassifier(loss='log_loss', alpha=1e-3, max_iter=1000)
calibrator.partial_fit(uncalibrated_probs, y_cal, classes=np.array([0, 1]))

#y_proba = calibrated_model.predict_proba(X_test)[:, 1]
#y_pred = calibrated_model.predict(X_test)
#print("Brier Score:", brier_score_loss(y_test, y_proba))
#print("Accuracy:", accuracy_score(y_test, y_pred))

#joblib.dump(calibrated_model, "xgb_calibrated_model.joblib")
joblib.dump(model, "xgb_model.joblib")
joblib.dump(calibrator, "model_calibrator.joblib")