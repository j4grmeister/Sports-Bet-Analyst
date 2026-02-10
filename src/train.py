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
    model.train(verbose=True)
    MLBPredictor.write_file(model.predictor)