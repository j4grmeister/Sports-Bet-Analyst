import csv

from data.odds import OddsArchive

class Model:
    def __init__(self, predictor, betting_strategy):
        self.predictor = predictor
        self.betting_strategy = betting_strategy

    def train(self, verbose=False):
        self.predictor.train(verbose=verbose)

    def test(self, verbose=False):
        self.predictor.load_test(verbose=verbose)
        return self.predictor.test(verbose=verbose)
    
    def test_profits(self, bet_proba_margin=3, starting_bankroll=100, stats_filename=None, verbose=False):
        csv_headers = [
            "date",
            "bankroll_start",
            "home_team",
            "away_team",
            "odds",
            "probability",
            "bet_amount",
            "payout",
            "winning_team",
            "outcome",
            "bankroll_final"
        ]
        
        csvfile = None
        csv_writer = None
        if stats_filename != None:
            csvfile = open(stats_filename, "w", newline='')
            csv_writer = csv.DictWriter(csvfile, fieldnames=csv_headers, delimiter=",")
            csv_writer.writeheader()
        
        odds_archive = OddsArchive()
        team_dict = {}