import os

from models.Model import Model
from models.predictors.MLBPredictor import MLBPredictor
from models.strategies.MLBModifiedKellyStrategy import MLBModifiedKellyStrategy
from data.odds import OddsArchive

if __name__ == "__main__":
    OddsArchive()

    predictor = MLBPredictor("MLBModel")
    betting_strategy = MLBModifiedKellyStrategy()
    model = Model(predictor, betting_strategy)

    results = Model.optimize_hyper_params(model, "brier_score", max_evals=1000)
    for key in results:
        print(f"{key}: {results[key]}") 