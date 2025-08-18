import statsapi
import requests
import json


#sched = statsapi.schedule(start_date='06/17/2020', end_date='06/30/2025',team=143,opponent=121)
#print(sched)

config = {}
with open("config.json", "r") as config_file:
    config = json.load(config_file)

API_KEY = config["odds_api_key"]

url = endpoint = f"https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/odds?apiKey={API_KEY}&regions=us&markets=h2h&date=2025-04-20T12:00:00Z"
response = requests.get(url)

file = open("out.json", "w")
file.write(response.text)
file.close()