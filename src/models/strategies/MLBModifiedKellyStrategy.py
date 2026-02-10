from models.BettingStrategy import BettingStrategy

class MLBModifiedKellyStrategy(BettingStrategy):
    def __init__(self):
        super().__init__()
        self.bet_proba_margin = 0

    def _calculate_transaction(self, transaction):
        y_pred = transaction["predicted_outcome"]
        y_proba = transaction["predicted_proba"]
        home_prob_imp = transaction["implied_home_proba"]
        away_prob_imp = transaction["implied_away_proba"]
        home_odds = transaction["home_odds"]
        away_odds = transaction["away_odds"]

        transaction["kelly_fraction"] = 0

        if y_pred == 1:
            # BET HOME
            implied_proba = home_prob_imp
            bet_proba = y_proba
            pay_ratio = min(home_odds-1, 2.5)
            #pay_ratio = home_odds-1
            bet_odds = home_odds
        elif y_pred == 0:
            # BET AWAY
            implied_proba = away_prob_imp
            bet_proba = 1-y_proba
            pay_ratio = min(away_odds-1, 2.5)
            #pay_ratio = away_odds-1
            bet_odds = away_odds


        #if y_pred == 0 and implied_proba < .55:
            #return
        
        #if y_pred == 1 and implied_proba > .55:
            #return

        if y_pred == 0:
            return

        #if (bet_proba - implied_proba)*100 >= self.bet_proba_margin and implied_proba >= .5:
        #if (bet_proba - implied_proba)*100 >= self.bet_proba_margin:
        if True:
            #bet_proba = .58995
            bet_proba = min(bet_proba, .58995)
            #bet_proba = min(bet_proba, .65)
            
            kelly_fraction = max(0, bet_proba - (1-bet_proba)/pay_ratio)
            bet_size = round(self._available_cash * kelly_fraction, 2)
            bet_payout = BettingStrategy.payout(bet_size, bet_odds)
            
            transaction["bet_amount"] = bet_size
            transaction["kelly_fraction"] = kelly_fraction
            transaction["payout"] = bet_payout
