from models.BettingStrategy import BettingStrategy

class MLBModifiedKellyStrategy(BettingStrategy):
    def __init__(self):
        super().__init__()

    def calculate_bet(self, sportsbook_odds, predicted_outcome, predicted_probability):
        pass