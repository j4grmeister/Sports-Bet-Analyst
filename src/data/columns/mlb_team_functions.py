import datetime

import smath.mlb as mlb

ROLLING_WINDOW_SIZE = 10

def _update_stat_totals(archive):
    for key in archive:
        if key.startswith("_"):
            val_key = key[1:]
            archive[val_key] = archive[key]
            archive[key] += archive[f"W_{val_key}_0"]

def _calc_additional_stats(archive):
    wOBA = mlb.wOBA(archive["W_NIBB_0"], archive["W_HBP_0"], archive["W_1B_0"], archive["W_2B_0"], archive["W_3B_0"], archive["W_HR_0"], archive["W_AB_0"], archive["W_BB_0"], archive["W_IBB_0"], archive["W_SF_0"])
    OPS = mlb.OPS(archive["W_H_0"], archive["W_BB_0"], archive["W_HBP_0"], archive["W_AB_0"], archive["W_SF_0"], archive["W_TB_0"])
    archive["W_wOBA_0"] = wOBA
    archive["W_OPS_0"] = OPS

def _update_stat_windows(archive):
    if archive["W_AB_0"] != 0: # Only update if the player played this game
        keys = list(archive.keys())
        for key in keys:
            if key.startswith("W_") and key.endswith("_0"):
                val_key = key[2:-2]
                for i in reversed(range(ROLLING_WINDOW_SIZE)):
                    left = f"W_{val_key}_{i}"
                    right = f"W_{val_key}_{i+1}"
                    if left not in archive:
                        archive[right] = 0
                    else:
                        archive[right] = archive[left]

def get_team_fetch_all_stats_func(is_home_team):
    TEAM = "home" if is_home_team else "away"

    def fetch_all_team_stats(archive, *args, **kwargs):
        box = args[0]

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
                team_archive[f"W_{key}_1"] = team_archive[key]

            team_archive["id"] = team_id
            team_archive["teamName"] = team_name
            team_archive["gamesPlayed"] = 1
        else:
            team_archive = archive[team_id]
            team_archive["gamesPlayed"] += 1

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
        team_archive["W_NIBB_0"] = NIBB
        team_archive["W_HBP_0"] = HBP
        team_archive["W_1B_0"] = B1
        team_archive["W_2B_0"] = B2
        team_archive["W_3B_0"] = B3
        team_archive["W_HR_0"] = HR
        team_archive["W_AB_0"] = AB
        team_archive["W_BB_0"] = BB
        team_archive["W_IBB_0"] = IBB
        team_archive["W_SF_0"] = SF
        team_archive["W_H_0"] = H
        team_archive["W_TB_0"] = TB
        _update_stat_totals(team_archive)
        _calc_additional_stats(team_archive)
        _calc_avgs(team_archive)
        _update_stat_windows(team_archive)

    return fetch_all_team_stats

def _calc_avgs(archive):
    keys = list(archive.keys())
    for key in keys:
        if key.startswith("W_") and key.endswith("_0"):
            stat = key[2:-2]
            new_key = f"{stat}_AVG"
            archive[new_key] = _stat_moving_avg(archive, stat)

def _stat_moving_avg(archive, stat):
    stat_avg = 0
    den = 0
    for i in range(ROLLING_WINDOW_SIZE):
        key = f"W_{stat}_{i+1}"
        if key in archive:
            stat_avg += archive[key]
            den += 1
    if den == 0:
        return 0
    stat_avg /= den
    return stat_avg

def _stat_moving_total(archive, stat):
    stat_total = 0
    for i in range(ROLLING_WINDOW_SIZE):
        stat_total += archive[f"W_{stat}_{i+1}"]
    return stat_total

def get_stat_moving_avg_func(key, is_home_team):
    TEAM = "home" if is_home_team else "away"

    def calc_stat_moving_avg(archive, *args, **kwargs):
        box = args[0]
        team_id = box["teamInfo"][TEAM]["id"]
        if team_id not in archive:
            return 0
        team_archive = archive[team_id]
        new_key = f"{key}_AVG"
        if new_key in team_archive:
            return team_archive[new_key]
        else:
            return 0
        #return _stat_moving_avg(player_archive, key)
    return calc_stat_moving_avg

def get_stat_moving_total_func(key, is_home_team):
    TEAM = "home" if is_home_team else "away"
    def calc_stat_moving_total(archive, *args, **kwargs):
        box = args[0]
        team_id = box["teamInfo"][TEAM]["id"]
        if team_id not in archive:
            return 0
        team_archive = archive[team_id]
        return _stat_moving_total(team_archive, key)
    return calc_stat_moving_total

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

    def calc_team_wOBA(archive, *args, **kwargs):
        box = args[0]

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

    def calc_team_OPS(archive, *args, **kwargs):
        box = args[0]

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

    def get_team_starting_pitcher(archive, *args, **kwargs):
        box = args[0]
        summary = args[1]

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

    def get_team(archive, *args, **kwargs):
        summary = args[1]
        
        team_id = summary[f"{TEAM}_id"]
        return team_id
    
    return get_team

def get_team_rolling_win_percent_func(is_home_team, window_size=10):
    TEAM = "home" if is_home_team else "away"

    def get_team_rolling_win_percent(archive, *args, **kwargs):
        summary = args[1]

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

def date(archive, *args, **kwargs):
    summary = args[1]
    #game_datetime = datetime.fromisoformat(summary["game_datetime"])
    game_datetime = summary["game_datetime"]
    #date = game_datetime.date()
    #time = game_datetime.time()
    return game_datetime

def home_team_win(archive, *args, **kwargs):
    summary = args[1]
    # Error check in case this is live data (no winning team yet)
    if "winning_team" not in summary:
        return -1
    winning_team = summary["winning_team"]
    team_name = summary["home_name"]
    is_home_win = winning_team == team_name
    return 1 if is_home_win else 0

def get_raw_stat_func(key, is_home_team):
    TEAM = "home" if is_home_team else "away"
    def calc_raw_stat(archive, *args, **kwargs):
        summary = args[1]
        team_id = summary[f"{TEAM}_id"]
        team_archive = archive[team_id]
        stat = 0
        if key in team_archive:
            stat = team_archive[key]
        return stat
    return calc_raw_stat