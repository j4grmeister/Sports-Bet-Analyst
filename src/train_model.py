import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, accuracy_score
from xgboost import XGBClassifier
import joblib

df = pd.DataFrame({
    "home_offense_wOBA": np.random.normal(.32, .01, 500),
    "away_offense_wOBA": np.random.normal(.31, .01, 500),
    "home_bullpen_era": np.random.normal(4, .5, 500),
    "away_bullpen_era": np.random.normal(4.2, .5, 500),
    "humidity": np.random.normal(60, 10, 500),
    "injured_home_key_players": np.random.randint(0, 3, 500),
    "home_team_last10_win_pct": np.random.uniform(.4, .7, 500),
    "away_team_last10_win_pct": np.random.uniform(.4, 7, 500),
    "home_win": np.random.binomial(1, .52, 500)
})

X = df.drop("home_win", axis = 1)
y = df["home_win"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)

model = XGBClassifier(user_label_encoder=False, eval_metric="logloss", n_estimators=50)
model.fit(X_train, y_train)

calibrated_model = CalibratedClassifierCV(estimator=model, cv=3, method="sigmoid")
calibrated_model.fit(X_train, y_train)

y_proba = calibrated_model.predict_proba(X_test)[:, 1]
y_pred = calibrated_model.predict(X_test)
print("Brier Score:", brier_score_loss(y_test, y_proba))
print("Accuracy:", accuracy_score(y_test, y_pred))

print(y_proba)
print(y_pred)

joblib.dump(calibrated_model, "xgb_calibrated_model.joblib")