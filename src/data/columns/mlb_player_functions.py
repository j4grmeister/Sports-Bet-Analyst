import datetime

import smath.mlb as mlb

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

                player_archive["id"] = player_id
                player_archive["fullName"] = player_fullName
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
                player_archive["batting"]["NIBB"] = player_archive["batting"]["_NIBB"]
                player_archive["batting"]["HBP"] = player_archive["batting"]["_HBP"]
                player_archive["batting"]["1B"] = player_archive["batting"]["_1B"]
                player_archive["batting"]["2B"] = player_archive["batting"]["_2B"]
                player_archive["batting"]["3B"] = player_archive["batting"]["_3B"]
                player_archive["batting"]["HR"] = player_archive["batting"]["_HR"]
                player_archive["batting"]["AB"] = player_archive["batting"]["_AB"]
                player_archive["batting"]["BB"] = player_archive["batting"]["_BB"]
                player_archive["batting"]["IBB"] = player_archive["batting"]["_IBB"]
                player_archive["batting"]["SF"] = player_archive["batting"]["_SF"]
                player_archive["batting"]["H"] = player_archive["batting"]["_H"]
                player_archive["batting"]["TB"] = player_archive["batting"]["_TB"]
                player_archive["batting"]["K"] = player_archive["batting"]["_K"]
                player_archive["batting"]["SB"] = player_archive["batting"]["_SB"]
                player_archive["batting"]["RBI"] = player_archive["batting"]["_RBI"]
                # Update the team's season stats
                player_archive["batting"]["_NIBB"] += NIBB
                player_archive["batting"]["_HBP"] += HBP
                player_archive["batting"]["_1B"] += B1
                player_archive["batting"]["_2B"] += B2
                player_archive["batting"]["_3B"] += B3
                player_archive["batting"]["_HR"] += HR
                player_archive["batting"]["_AB"] += AB
                player_archive["batting"]["_BB"] += BB
                player_archive["batting"]["_IBB"] += IBB
                player_archive["batting"]["_SF"] += SF
                player_archive["batting"]["_H"] += H
                player_archive["batting"]["_TB"] += TB
                player_archive["batting"]["_K"] += K
                player_archive["batting"]["_SB"] += SB
                player_archive["batting"]["_RBI"] += RBI

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
                player_archive["pitching"]["NIBB"] = player_archive["pitching"]["_NIBB"]
                player_archive["pitching"]["HBP"] = player_archive["pitching"]["_HBP"]
                player_archive["pitching"]["1B"] = player_archive["pitching"]["_1B"]
                player_archive["pitching"]["2B"] = player_archive["pitching"]["_2B"]
                player_archive["pitching"]["3B"] = player_archive["pitching"]["_3B"]
                player_archive["pitching"]["HR"] = player_archive["pitching"]["_HR"]
                player_archive["pitching"]["BB"] = player_archive["pitching"]["_BB"]
                player_archive["pitching"]["IBB"] = player_archive["pitching"]["_IBB"]
                player_archive["pitching"]["IP"] = player_archive["pitching"]["_IP"]
                player_archive["pitching"]["P"] = player_archive["pitching"]["_P"]
                player_archive["pitching"]["ER"] = player_archive["pitching"]["_ER"]
                player_archive["pitching"]["K"] = player_archive["pitching"]["_K"]
                player_archive["pitching"]["AB"] = player_archive["pitching"]["_AB"]
                player_archive["pitching"]["CINT"] = player_archive["pitching"]["_CINT"]
                player_archive["pitching"]["H"] = player_archive["pitching"]["_H"]
                player_archive["pitching"]["_NIBB"] += NIBB
                player_archive["pitching"]["_HBP"] += HBP
                player_archive["pitching"]["_1B"] += B1
                player_archive["pitching"]["_2B"] += B2
                player_archive["pitching"]["_3B"] += B3
                player_archive["pitching"]["_HR"] += HR
                player_archive["pitching"]["_BB"] += BB
                player_archive["pitching"]["_IBB"] += IBB
                player_archive["pitching"]["_IP"] += IP
                player_archive["pitching"]["_P"] += P
                player_archive["pitching"]["_ER"] += ER
                player_archive["pitching"]["_K"] += K
                player_archive["pitching"]["_AB"] += AB
                player_archive["pitching"]["_CINT"] += CINT
                player_archive["pitching"]["_H"] += H

    return fetch_all_player_stats


def calc_pitcher_ERA(archive, *args, **kwargs):
    if "player_id" not in kwargs:
        return 0
    player_id = kwargs["player_id"]
    if player_id not in archive["stats"]:
        print(1)
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