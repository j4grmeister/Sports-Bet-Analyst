import sys
import os

from models.Model import Model
from models.predictors.MLBPredictor import MLBPredictor
from models.strategies.MLBModifiedKellyStrategy import MLBModifiedKellyStrategy
from data.odds import OddsArchive

def main():
    #available_cash = float(sys.argv[1])
    available_cash = float(10)
    OddsArchive()

    predictor = MLBPredictor.read_file("MLBModel")
    betting_strategy = MLBModifiedKellyStrategy()
    model = Model(predictor, betting_strategy)
    
    model.betting_strategy.set_balance(available_cash)
    
    out_str = ""
    for predicted_winner, odds, bet_amount, kelly_fraction in model.get_next_bets():
        odds_str = f"+{int(odds)}" if odds > 0 else str((int(odds)))
        out_str += f"{odds_str} {predicted_winner}    ${bet_amount} ({kelly_fraction})\n"
    print(out_str)

if __name__ == "__main__":
    main()