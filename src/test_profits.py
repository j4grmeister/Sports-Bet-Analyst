import os

from models.Model import Model
from models.predictors.MLBPredictor import MLBPredictor
from models.strategies.MLBModifiedKellyStrategy import MLBModifiedKellyStrategy
from data.odds import OddsArchive

if __name__ == "__main__":
    OddsArchive()

    predictor = MLBPredictor.read_file("MLBModel")
    betting_strategy = MLBModifiedKellyStrategy()
    model = Model(predictor, betting_strategy)

    results = model.test_profits(os.path.join("MLBModel", "bets.csv"), verbose=True)
    for key in results:
        print(f"{key}: {results[key]}") 
    MLBPredictor.write_file(model.predictor)