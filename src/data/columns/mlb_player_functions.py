import datetime
import copy
import logging

import smath.mlb as mlb

ROLLING_WINDOW_SIZE = 10

logger = logging.getLogger("mlb.player_functions")

def _update_stat_totals(archive):
    for key in archive:
        if key.startswith("_"):
            val_key = key[1:]
            archive[val_key] = archive[key]
            archive[key] += archive[f"W_{val_key}_0"]

def _calc_additional_batter_stats(archive):
    AVG = mlb.AVG(archive["W_H_0"], archive["W_AB_0"])
    OBP = mlb.OBP(archive["W_H_0"], archive["W_BB_0"], archive["W_HBP_0"], archive["W_AB_0"], archive["W_SF_0"])
    SLG = mlb.SLG(archive["W_TB_0"], archive["W_AB_0"])
    OPS = mlb.OPS(archive["W_H_0"], archive["W_BB_0"], archive["W_HBP_0"], archive["W_AB_0"], archive["W_SF_0"], archive["W_TB_0"])
    archive["W_AVG_0"] = AVG
    archive["W_OBP_0"] = OBP
    archive["W_SLG_0"] = SLG
    archive["W_OPS_0"] = OPS

def _calc_additional_pitcher_stats(archive):
    ERA = mlb.ERA(archive["W_ER_0"], archive["W_IP_0"])
    WHIP = mlb.WHIP(archive["W_BB_0"], archive["W_H_0"], archive["W_IP_0"])
    K9 = mlb.K9(archive["W_K_0"], archive["W_IP_0"])
    KBB = mlb.KBB(archive["W_K_0"], archive["W_BB_0"])
    archive["W_ERA_0"] = ERA
    archive["W_WHIP_0"] = WHIP
    archive["W_K9_0"] = K9
    archive["W_KBB_0"] = KBB

def _update_stat_windows(archive):
    if archive["W_AB_0"] != 0: # Only update if the player played this game\
        keys = list(archive.keys())
        for key in keys:
            if key.startswith("W_") and key.endswith("_0"):
                val_key = key[2:-2]
                logger.debug(f"Updating {val_key} window")
                for i in reversed(range(ROLLING_WINDOW_SIZE)):
                    left = f"W_{val_key}_{i}"
                    right = f"W_{val_key}_{i+1}"
                    if left not in archive:
                        logger.debug(f"No {left} found, setting {right} to 0")
                        archive[right] = 0
                    else:
                        logger.debug(f"Setting {right} to {archive[left]}")
                        archive[right] = archive[left]
    else:
        keys = list(archive.keys())
        for key in keys:
            if key.startswith("W_") and key.endswith("_0"):
                val_key = key[2:-2]
                for i in reversed(range(ROLLING_WINDOW_SIZE)):
                    right = f"W_{val_key}_{i+1}"
                    if right not in archive:
                        archive[right] = 0

def get_player_fetch_all_stats_func(is_home_team):
    TEAM = "home" if is_home_team else "away"

    def fetch_all_player_stats(archive, *args, **kwargs):
        if "names" not in archive:
            archive["names"] = {}
        if "stats" not in archive:
            archive["stats"] = {}

        box = args[0]
        players = box[TEAM]["players"]
        for player in players.values():
            player_archive = None
            player_id = player["person"]["id"]
            player_fullName = player["person"]["fullName"]
            if player_id not in archive["stats"]:
                archive["names"][player_fullName] = {"id": player_id}

                archive["stats"][player_id] = {}
                player_archive = archive["stats"][player_id]

                # Add the stats
                player_archive["batting"] = {}
                player_archive["batting"]["NIBB"] = 0
                player_archive["batting"]["HBP"] = 0
                player_archive["batting"]["1B"] = 0
                player_archive["batting"]["2B"] = 0
                player_archive["batting"]["3B"] = 0
                player_archive["batting"]["HR"] = 0
                player_archive["batting"]["AB"] = 0
                player_archive["batting"]["BB"] = 0
                player_archive["batting"]["IBB"] = 0
                player_archive["batting"]["SF"] = 0
                player_archive["batting"]["H"] = 0
                player_archive["batting"]["TB"] = 0
                player_archive["batting"]["K"] = 0
                player_archive["batting"]["SB"] = 0
                player_archive["batting"]["RBI"] = 0

                player_archive["pitching"] = {}
                player_archive["pitching"]["NIBB"] = 0
                player_archive["pitching"]["HBP"] = 0
                player_archive["pitching"]["1B"] = 0
                player_archive["pitching"]["2B"] = 0
                player_archive["pitching"]["3B"] = 0
                player_archive["pitching"]["HR"] = 0
                player_archive["pitching"]["H"] = 0
                player_archive["pitching"]["BB"] = 0
                player_archive["pitching"]["IBB"] = 0
                player_archive["pitching"]["IP"] = 0
                player_archive["pitching"]["P"] = 0
                player_archive["pitching"]["ER"] = 0
                player_archive["pitching"]["K"] = 0
                player_archive["pitching"]["AB"] = 0
                player_archive["pitching"]["CINT"] = 0
            
                for key in list(player_archive["batting"].keys()):
                    player_archive["batting"][f"_{key}"] = player_archive["batting"][key]
                for key in list(player_archive["pitching"].keys()):
                    player_archive["pitching"][f"_{key}"] = player_archive["pitching"][key]
                

                player_archive["info"] = {
                    "id": player_id,
                    "name": player_fullName
                }

                player_archive["batting"]["info"] = player_archive["info"]
                player_archive["pitching"]["info"] = player_archive["info"]
            else:
                player_archive = archive["stats"][player_id]
            
            box_name = box["playerInfo"][f"ID{player_id}"]["boxscoreName"]

            game_box_info = box["gameBoxInfo"]
            IBB_players_str = None
            HBP_players_str = None
            SF_players_str = None

            # Batting stats
            player_batting = player["stats"]["batting"]
            if len(player_batting) > 0:
                B2 = player_batting["doubles"]
                B3 = player_batting["triples"]
                HR = player_batting["homeRuns"]
                H = player_batting["hits"]
                B1 = H - B2 - B3 - HR
                AB = player_batting["atBats"]
                BB = player_batting["baseOnBalls"]
                TB = B1 + 2*B2 + 3*B3 + 4*HR            
                K = player_batting["strikeOuts"]
                SB = player_batting["stolenBases"]
                RBI = player_batting["rbi"]
                IBB = 0
                HBP = 0
                SF = 0
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
                if IBB_players_str != None:
                    IBB_players_arr = IBB_players_str.split(";")
                    for player_str in IBB_players_arr:
                        player_name = player_str.split("(by")[0].strip()
                        if player_name == box_name:
                            IBB += 1
                if HBP_players_str != None:
                    HBP_players_arr = HBP_players_str.split(";")
                    for player_str in HBP_players_arr:
                        player_name = player_str.split("(by")[0].strip()
                        if player_name == box_name:
                            HBP += 1
                if SF_players_str != None:
                    SF_players_arr = SF_players_str.split(";")
                    for player_str in SF_players_arr:
                        player_name = player_str.strip()
                        if player_name == box_name:
                            SF += 1
                NIBB = BB - IBB
                # Update the team's season stats
                player_archive["batting"]["W_NIBB_0"] = NIBB
                player_archive["batting"]["W_HBP_0"] = HBP
                player_archive["batting"]["W_1B_0"] = B1
                player_archive["batting"]["W_2B_0"] = B2
                player_archive["batting"]["W_3B_0"] = B3
                player_archive["batting"]["W_HR_0"] = HR
                player_archive["batting"]["W_AB_0"] = AB
                player_archive["batting"]["W_BB_0"] = BB
                player_archive["batting"]["W_IBB_0"] = IBB
                player_archive["batting"]["W_SF_0"] = SF
                player_archive["batting"]["W_H_0"] = H
                player_archive["batting"]["W_TB_0"] = TB
                player_archive["batting"]["W_K_0"] = K
                player_archive["batting"]["W_SB_0"] = SB
                player_archive["batting"]["W_RBI_0"] = RBI
                _update_stat_totals(player_archive["batting"])
                _calc_additional_batter_stats(player_archive["batting"])
                _update_stat_windows(player_archive["batting"])


            # Pitching stats
            player_pitching = player["stats"]["pitching"]
            if len(player_pitching) > 0:
                B2 = player_pitching["doubles"]
                B3 = player_pitching["triples"]
                HR = player_pitching["homeRuns"]
                H = player_pitching["hits"]
                B1 = H - B2 - B3 - HR
                AB = player_pitching["atBats"]
                P = player_pitching["numberOfPitches"]
                IP = float(player_pitching["inningsPitched"])
                #print(f"P: {P}; IP: {IP}")
                ER = player_pitching["earnedRuns"]
                K = player_pitching["strikeOuts"]
                BB = player_pitching["baseOnBalls"]
                IBB = 0
                HBP = 0
                CINT = 0
                info_list = box[TEAM]["info"]
                for info in info_list:
                    if info["title"] == "FIELDING":
                        field_list = info["fieldList"]
                        for field in field_list:
                            value = field["value"]
                            if "catcher interference" in value and box_name in value:
                                CINT += 1
                if IBB_players_str != None:
                    IBB_players_arr = IBB_players_str.split(";")
                    for player_str in IBB_players_arr:
                        player_name = player_str.split("(by ")[1].split(")")[0].strip()
                        if player_name == box_name:
                            IBB += 1
                if HBP_players_str != None:
                    HBP_players_arr = HBP_players_str.split(";")
                    for player_str in HBP_players_arr:
                        player_name = player_str.split("(by ")[1].split(")")[0].strip()
                        if player_name == box_name:
                            HBP += 1
                NIBB = BB - IBB
                player_archive["pitching"]["W_NIBB_0"] = NIBB
                player_archive["pitching"]["W_HBP_0"] = HBP
                player_archive["pitching"]["W_1B_0"] = B1
                player_archive["pitching"]["W_2B_0"] = B2
                player_archive["pitching"]["W_3B_0"] = B3
                player_archive["pitching"]["W_HR_0"] = HR
                player_archive["pitching"]["W_BB_0"] = BB
                player_archive["pitching"]["W_IBB_0"] = IBB
                player_archive["pitching"]["W_IP_0"] = IP
                player_archive["pitching"]["W_P_0"] = P
                player_archive["pitching"]["W_ER_0"] = ER
                player_archive["pitching"]["W_K_0"] = K
                player_archive["pitching"]["W_AB_0"] = AB
                player_archive["pitching"]["W_CINT_0"] = CINT
                player_archive["pitching"]["W_H_0"] = H
                _update_stat_totals(player_archive["pitching"])
                _calc_additional_pitcher_stats(player_archive["pitching"])
                _update_stat_windows(player_archive["pitching"])
    return fetch_all_player_stats

def _stat_moving_avg(archive, stat):
    logger.debug(f"Calculating moving {stat} average for {archive["info"]["name"]}({archive["info"]["id"]})")
    stat_avg = 0
    den = 0
    for i in range(ROLLING_WINDOW_SIZE):
        key = f"W_{stat}_{i+1}"
        if key in archive:
            stat_avg += archive[key]
            den += 1
    if den == 0:
        logger.info(str(archive))
        return 0
    stat_avg /= den
    return stat_avg

def _stat_moving_total(archive, stat):
    stat_total = 0
    for i in range(ROLLING_WINDOW_SIZE):
        stat_total += archive[f"W_{stat}_{i+1}"]
    return stat_total

def get_stat_moving_avg_func(key, position):
    def calc_stat_moving_avg(archive, *args, **kwargs):
        if "player_id" not in kwargs:
            return 0
        player_id = kwargs["player_id"]
        if player_id not in archive["stats"]:
            return 0
        player_archive = archive["stats"][player_id][position]
        return _stat_moving_avg(player_archive, key)
    return calc_stat_moving_avg

def get_stat_moving_total_func(key, position):
    def calc_stat_moving_total(archive, *args, **kwargs):
        if "player_id" not in kwargs:
            return 0
        player_id = kwargs["player_id"]
        if player_id not in archive["stats"]:
            return 0
        player_archive = archive["stats"][player_id][position]
        return _stat_moving_total(player_archive, key)
    return calc_stat_moving_total

def get_raw_stat_func(key, position):
    def calc_raw_stat(archive, *args, **kwargs):
        if "player_id" not in kwargs:
            return 0
        player_id = kwargs["player_id"]
        if player_id not in archive["stats"]:
            return 0
        player_archive = archive["stats"][player_id][position]
        stat = player_archive[key]
        return stat
    return calc_raw_stat

def calc_pitcher_ERA(archive, *args, **kwargs):
    if "player_id" not in kwargs:
        return 0
    player_id = kwargs["player_id"]
    if player_id not in archive["stats"]:
        return 0
    player_archive = archive["stats"][player_id]["pitching"]
    ER = player_archive["ER"]
    IP = player_archive["IP"]
    pitcher_ERA = mlb.ERA(ER, IP)
    return pitcher_ERA

def calc_pitcher_WHIP(archive, *args, **kwargs):
    if "player_id" not in kwargs:
        return 0
    player_id = kwargs["player_id"]
    if player_id not in archive["stats"]:
        return 0
    player_archive = archive["stats"][player_id]["pitching"]
    BB = player_archive["BB"]
    H = player_archive["H"]
    IP = player_archive["IP"]
    pitcher_WHIP = mlb.WHIP(BB, H, IP)
    return pitcher_WHIP
    
def calc_pitcher_K9(archive, *args, **kwargs):
    if "player_id" not in kwargs:
        return 0
    player_id = kwargs["player_id"]
    if player_id not in archive["stats"]:
        return 0
    player_archive = archive["stats"][player_id]["pitching"]
    K = player_archive["K"]
    IP = player_archive["IP"]
    pitcher_K9 = mlb.K9(K, IP)
    return pitcher_K9
    
def calc_pitcher_KBB(archive, *args, **kwargs):
    if "player_id" not in kwargs:
        return 0
    player_id = kwargs["player_id"]
    if player_id not in archive["stats"]:
        return 0
    player_archive = archive["stats"][player_id]["pitching"]
    K = player_archive["K"]
    BB = player_archive["BB"]
    pitcher_KBB = mlb.KBB(K, BB)
    return pitcher_KBB