from models.Model import Model
from models.predictors.MLBPredictor import MLBPredictor
from models.BettingStrategy import BettingStrategy

if __name__ == "__main__":
    #predictor = MLBPredictor("MLBModel")
    predictor = MLBPredictor.read_file("MLBModel")
    betting_strategy = BettingStrategy()
    model = Model(predictor, betting_strategy)

    #model.train(verbose=True)
    results = model.test(verbose=True)
    for key in results:
        print(f"{key}: {results[key]}")
    #MLBPredictor.write_file(model.predictor)