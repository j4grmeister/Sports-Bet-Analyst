class BettingStrategy:
    def __init__(self):
        self._bankroll = 0
        self._history = []
        self._transaction_count = 0

    def set_balance(self, bankroll):
        self._bankroll = bankroll

    def implied_proba(odds):
        return 1/odds

    def payout(bet, odds):
        return round(bet * odds, 2)

    def _calculate_transaction(transaction):
        pass

    def place_bet(self, supp, home_odds, away_odds, predicted_outcome, predicted_proba):
        transaction = {
            "supplemental_data": supp,
            "date": "",
            "bankroll_start": self._bankroll,
            "home_team": "",
            "away_team": "",
            "home_odds": home_odds,
            "away_odds": away_odds,
            "implied_home_proba": BettingStrategy.implied_proba(home_odds),
            "implied_away_proba": BettingStrategy.implied_proba(away_odds),
            "predicted_outcome": predicted_outcome,
            "predicted_proba": predicted_proba,
            "bet_amount": 0,
            "payout": 0
        }
        self._calculate_transaction(transaction)
        self._bankroll -= transaction["bet_amount"]
        self._bankroll = round(self._bankroll, 2)
        self._history.append(transaction)
        self._transaction_count += 1
        return self._transaction_count - 1

    def evaluate_outcome(self, transaction_num, y):
        transaction = self._history[transaction_num]
        transaction["game_outcome"] = y
        transaction["bet_outcome"] = "W" if y == transaction["predicted_outcome"] else "L"
        if transaction["bet_outcome"]== "W":
            self._bankroll += transaction["payout"]
            self._bankroll = round(self._bankroll, 2)
        transaction["bankroll_final"] = self._bankroll
        if transaction["bet_amount"] != 0:
            return transaction