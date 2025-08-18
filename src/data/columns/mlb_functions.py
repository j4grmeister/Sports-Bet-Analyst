import datetime

import smath.mlb as mlb

def get_team_fetch_all_stats_func(is_home_team):
    TEAM = "home" if is_home_team else "away"

    def fetch_all_team_stats(archive, *args):
        box = args[0][0]

        # Fetch the correct team's archive or create it if it does not exist
        team_archive = None
        team_id = box["teamInfo"][TEAM]["id"]
        team_name = box["teamInfo"][TEAM]["teamName"]
        if team_id not in archive:
            archive[team_id] = {}
            team_archive = archive[team_id]
            # Add the stats
            team_archive["NIBB"] = 0
            team_archive["HBP"] = 0
            team_archive["1B"] = 0
            team_archive["2B"] = 0
            team_archive["3B"] = 0
            team_archive["HR"] = 0
            team_archive["AB"] = 0
            team_archive["BB"] = 0
            team_archive["IBB"] = 0
            team_archive["SF"] = 0
            team_archive["H"] = 0
            team_archive["TB"] = 0

            for key in list(team_archive.keys()):
                team_archive[f"_{key}"] = team_archive[key]

            team_archive["id"] = team_id
            team_archive["teamName"] = team_name
        else:
            team_archive = archive[team_id]

        # Calculate the most recent game's stats
        team_batting = box[TEAM]["teamStats"]["batting"]
        B2 = team_batting["doubles"]
        B3 = team_batting["triples"]
        HR = team_batting["homeRuns"]
        H = team_batting["hits"]
        B1 = H - B2 - B3 - HR
        AB = team_batting["atBats"]
        BB = team_batting["baseOnBalls"]
        TB = B1 + 2*B2 + 3*B3 + 4*HR

        # These ones are a little more complicated. Need to compare the gameBoxInfo to the player names
        IBB = 0
        HBP = 0
        SF = 0
        
        game_box_info = box["gameBoxInfo"]
        IBB_players_str = None
        HBP_players_str = None
        SF_players_str = None
        for stat in game_box_info:
            match(stat["label"]):
                case "IBB":
                    IBB_players_str = stat["value"]
                case "HBP":
                    HBP_players_str = stat["value"]
                case _:
                    pass
        for info_section in box[TEAM]["info"]:
            if info_section["title"] == "BATTING":
                for field_list_entry in info_section["fieldList"]:
                    if field_list_entry["label"] == "SF":
                        SF_players_str = field_list_entry["value"][:-1] # Temove the "." at the end of this string
                        break
                break

        IBB_players = []
        if IBB_players_str != None:
            IBB_players_arr = IBB_players_str.split(";")
            for player_str in IBB_players_arr:
                player_name = player_str.split("(by")[0].strip()
                IBB_players.append(player_name)
        HBP_players = []
        if HBP_players_str != None:
            HBP_players_arr = HBP_players_str.split(";")
            for player_str in HBP_players_arr:
                player_name = player_str.split("(by")[0].strip()
                HBP_players.append(player_name)
        SF_players = []
        if SF_players_str != None:
            SF_players_arr = SF_players_str.split(";")
            for player_str in SF_players_arr:
                player_name = player_str.strip()
                SF_players.append(player_name)

        team_lineup = box[TEAM]["players"]
        for id_str in team_lineup:
            player = team_lineup[id_str]
            player_name = player["person"]["fullName"]
            box_name = box["playerInfo"][id_str]["boxscoreName"]
            if box_name in IBB_players:
                IBB += 1
            if box_name in HBP_players:
                HBP += 1
            if box_name in SF_players:
                SF += 1

        NIBB = BB - IBB

        # Retain the team's old season stats for calcuation
        # keys beginning with "_" indicate the future state of the stat
        # (After this game takes place)
        team_archive["NIBB"] = team_archive["_NIBB"]
        team_archive["HBP"] = team_archive["_HBP"]
        team_archive["1B"] = team_archive["_1B"]
        team_archive["2B"] = team_archive["_2B"]
        team_archive["3B"] = team_archive["_3B"]
        team_archive["HR"] = team_archive["_HR"]
        team_archive["AB"] = team_archive["_AB"]
        team_archive["BB"] = team_archive["_BB"]
        team_archive["IBB"] = team_archive["_IBB"]
        team_archive["SF"] = team_archive["_SF"]
        team_archive["H"] = team_archive["_H"]
        team_archive["TB"] = team_archive["_TB"]

        # Update the team's season stats
        team_archive["_NIBB"] += NIBB
        team_archive["_HBP"] += HBP
        team_archive["_1B"] += B1
        team_archive["_2B"] += B2
        team_archive["_3B"] += B3
        team_archive["_HR"] += HR
        team_archive["_AB"] += AB
        team_archive["_BB"] += BB
        team_archive["_IBB"] += IBB
        team_archive["_SF"] += SF
        team_archive["_H"] += H
        team_archive["_TB"] += TB

    return fetch_all_team_stats

def get_team_wOBA_func(is_home_team):
    """Generate the column generator function for team wOBA, agnostic of team.
    This generator function must be initialized with the same ID as fetch_all_team_stats

    Parameters
    ----------
    is_home_team : bool
        Is this the home team?

    Returns
    -------
    function
        The column generator function for team wOBA
    """
    TEAM = "home" if is_home_team else "away"

    def calc_team_wOBA(archive, *args):
        box = args[0][0]

        team_id = box["teamInfo"][TEAM]["id"]
        team_archive = archive[team_id]

        NIBB = team_archive["NIBB"]
        HBP = team_archive["HBP"]
        B1 = team_archive["1B"]
        B2 = team_archive["2B"]
        B3 = team_archive["3B"]
        HR = team_archive["HR"]
        AB = team_archive["AB"]
        BB = team_archive["BB"]
        IBB = team_archive["IBB"]
        SF = team_archive["SF"]

        team_wOBA = mlb.wOBA(NIBB, HBP, B1, B2, B3, HR, AB, BB, IBB, SF)
        return team_wOBA

    return calc_team_wOBA


def get_team_OPS_func(is_home_team):
    TEAM = "home" if is_home_team else "away"

    def calc_team_OPS(archive, *args):
        box = args[0][0]

        team_id = box["teamInfo"][TEAM]["id"]
        team_archive = archive[team_id]

        H = team_archive["H"]
        BB = team_archive["BB"]
        HBP = team_archive["HBP"]
        AB = team_archive["AB"]
        SF = team_archive["SF"]
        TB = team_archive["TB"]

        team_OPS = mlb.OPS(H, BB, HBP, AB, SF, TB)
        return team_OPS
    
    return calc_team_OPS

def get_team_starting_pitcher_func(is_home_team):
    TEAM = "home" if is_home_team else "away"

    def get_team_starting_pitcher(archive, *args):
        box = args[0][0]
        summary = args[0][1]

        pitcher_name = summary[f"{TEAM}_probable_pitcher"]
        player_info = box["playerInfo"]
        for id_str in player_info:
            player = player_info[id_str]
            if player["fullName"] == pitcher_name:
                player_id = player["id"]
                return player_id
        return 0

    return get_team_starting_pitcher

def get_team_func(is_home_team):
    TEAM = "home" if is_home_team else "away"

    def get_team(archive, *args):
        summary = args[0][1]
        
        team_id = summary[f"{TEAM}_id"]
        return team_id
    
    return get_team

def get_team_rolling_win_percent_func(is_home_team, window_size=10):
    TEAM = "home" if is_home_team else "away"

    def get_team_rolling_win_percent(archive, *args):
        summary = args[0][1]

        team_id = summary[f"{TEAM}_id"]
        team_archive = None
        if team_id not in archive:
            archive[team_id] = {}
            team_archive = archive[team_id]
            team_archive["history"] = [None for i in range(window_size)]
        else:
            team_archive = archive[team_id]

        def win_percent(window):
            sum = 0
            den = len(window)
            for is_win in window:
                sum += 1 if is_win else 0
                den -= 1 if is_win == None else 0
            if den == 0:
                return 0
            win_percent = sum / den
            return win_percent
        
        percent = win_percent(team_archive["history"])

        if summary["status"] == "Final":
            winning_team = summary["winning_team"]
            team_name = summary[f"{TEAM}_name"]
            is_win = winning_team == team_name

            for i in range(len(team_archive["history"])-1):
                team_archive["history"][i] = team_archive["history"][i+1]
            team_archive["history"][-1] = is_win

        return percent

    return get_team_rolling_win_percent

def date(archive, *args):
    summary = args[0][1]
    #game_datetime = datetime.fromisoformat(summary["game_datetime"])
    game_datetime = summary["game_datetime"]
    #date = game_datetime.date()
    #time = game_datetime.time()
    return game_datetime

def home_team_win(archive, *args):
    summary = args[0][1]
    winning_team = summary ["winning_team"]
    team_name = summary["home_name"]
    is_home_win = winning_team == team_name
    return 1 if is_home_win else 0