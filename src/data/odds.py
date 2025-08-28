import requests
import os
import json

config = {}
with open("config.json", "r") as config_file:
    config = json.load(config_file)

API_KEY = config["odds_api_key"]

ARCHIVE_FILEPATH = "data/odds_archive.json"

def dec_to_american_odds(dec):
    if dec >= 2:
        return (dec - 1) * 100
    else:
        return (-100) / (dec - 1)

class OddsArchive:
    instance = None
    TIME_OF_DAY = "12:00:00Z"

    def __init__(self, archive_filepath=ARCHIVE_FILEPATH):
        self.archive_filepath = archive_filepath
        self.archive = None
        OddsArchive.instance = self

    def load_archive(self):
        if not os.path.exists(self.archive_filepath):
            self.archive = {}
            return
        with open(self.archive_filepath, "r") as f:
            self.archive = json.load(f)
    
    def save_archive(self):
        if self.archive == None:
            return
        with open(self.archive_filepath, "w") as f:
            json.dump(self.archive, f)
    
    def get_odds(self, date, home_team, away_team):
        if self.archive == None:
            self.load_archive()
        if date not in self.archive:
            endpoint = f"https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/odds?apiKey={API_KEY}&regions=us&markets=h2h&date={date}T{self.TIME_OF_DAY}"
            response = requests.get(endpoint)
            response_json = json.loads(response.text)
            with open("test.json", "w") as f:
                f.write(response.text)

            date_odds = []
            for game in response_json["data"]:
                date_odds.append(game)
            self.archive[date] = date_odds

            self.save_archive()

        possible_games = []
        for game in self.archive[date]:
            #print(game["home_team"], home_team, game["away_team"], away_team)
            if game["home_team"] == home_team and game["away_team"] == away_team:
                possible_games.append(game)
        if len(possible_games) != 1:
            return None, None
        game = possible_games[0]
        home_odds = None
        away_odds = None
        for bookmaker in game["bookmakers"]:
            if bookmaker["key"] == "draftkings":
                for outcome in bookmaker["markets"][0]["outcomes"]:
                    if outcome["name"] == home_team:
                        home_odds = outcome["price"]
                    elif outcome["name"] == away_team:
                        away_odds = outcome["price"]
        if home_odds == None or away_odds == None:
            return None, None
        return home_odds, away_odds
    
    def get_live_odds(self, home_team, away_team):
        endpoint = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?apiKey={API_KEY}&regions=us&markets=h2h"
        response = requests.get(endpoint)
        games = json.loads(response.text)
        possible_games = []
        for game in games:
            if game["home_team"] == home_team and game["away_team"] == away_team:
                possible_games.append(game)
        if len(possible_games) != 1:
            return None, None
        game = possible_games[0]
        home_odds = None
        away_odds = None
        for bookmaker in game["bookmakers"]:
            if bookmaker["key"] == "draftkings":
                for outcome in bookmaker["markets"][0]["outcomes"]:
                    if outcome["name"] == home_team:
                        home_odds = outcome["price"]
                    elif outcome["name"] == away_team:
                        away_odds = outcome["price"]
        if home_odds == None or away_odds == None:
            return None, None
        return home_odds, away_odds
        