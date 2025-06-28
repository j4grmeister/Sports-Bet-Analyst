import statsapi
import requests
import json


#sched = statsapi.schedule(start_date='06/17/2020', end_date='06/30/2025',team=143,opponent=121)
#print(sched)

boxscore = statsapi.boxscore("775300")
boxscore_data = statsapi.boxscore_data("775300")
file = open("out.json", "w")
file.write(json.dumps(boxscore_data))
file.close()
print(boxscore)


API_KEY = ""

url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={API_KEY}&regions=us"
response = requests.get(url)

file = open("out.json", "w")
file.write(response.text)
file.close()
"""