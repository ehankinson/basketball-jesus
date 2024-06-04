import csv
import json
import time
import random
import pickle
import numpy as np

with open(f"data/json/teams.json", "r") as j:
    teams = json.load(j)

def find_game(team: str, team_bin_pct: dict, team_bins: dict, league_stats: dict, league_bin_pct: dict, league_bins: dict, side_of_ball: str):
    pct = random.random()
    team_key = None
    for count, key in enumerate(team_bin_pct):
        if count == len(team_bin_pct) - 1:
            team_key = len(team_bin_pct) - 1
            break
        if pct <= team_bin_pct[key]:
            team_key = key
            break
    for count, key in enumerate(team_bins):
        if count == team_key:
            if len(team_bins[key]) == 0:
                game = random.choice(team_bins[list(team_bins.keys())[count - 1]])
            else:
                game = random.choice(team_bins[key])
            game_stats = league_stats[team][game][side_of_ball]
            break
    for count, key in enumerate(league_bins):
        if game_stats['STRS'] < key:
            game_percentile = league_bin_pct[count]
            break
    return game_stats, game_percentile

def league_bin_games(season_data: dict, side_of_ball: str):
    data = {}
    min_value = None
    max_value = None
    for team in teams:
        if team not in season_data:
            continue
        for game in season_data[team]:
            game_value = season_data[team][game][side_of_ball]['STRS']
            if min_value == None:
                min_value = game_value
            if max_value == None:
                max_value = game_value
            if game_value < min_value:
                min_value = game_value
            if game_value > max_value:
                max_value = game_value
            data[f"{team}-{game}"] = game_value
    sqrt_bins = int(len(data) ** 0.5)
    difference = max_value - min_value
    bin_size = difference / sqrt_bins
    bins = {}
    previous_key = min_value
    for _ in range(sqrt_bins):
        new_key = previous_key + bin_size
        bins[new_key] = []
        previous_key = new_key
    for game_key in data:
        game_value = data[game_key]
        for key in bins.keys():
            if game_value <= key:
                bins[key].append(game_value)
                break
    bin_pct = {}
    total_pct = 0
    for bin_number, key in enumerate(bins.keys()):
        total_pct += len(bins[key]) / len(data)
        bin_pct[bin_number] = total_pct  
    return bin_pct, bins

def bin_games(team: str, season_data: dict, side_of_ball: str):
    data = {}
    min_value = None
    max_value = None
    for game in season_data[team]:
        game_value = season_data[team][game][side_of_ball]['STRS']
        if min_value == None:
            min_value = game_value
        if max_value == None:
            max_value = game_value
        if game_value < min_value:
            min_value = game_value
        if game_value > max_value:
            max_value = game_value
        data[game] = round(game_value, 3)
    min_value = round(min_value, 3)
    max_value = round(max_value, 3)
    sqrt_bins = int(len(data) ** 0.5)
    difference = max_value - min_value
    bin_size = round(difference / sqrt_bins, 3)
    bins = {}
    previous_key = min_value
    for _ in range(sqrt_bins):
        new_key = round(previous_key + bin_size, 3)
        bins[new_key] = []
        previous_key = new_key
    for game in data:
        game_value = round(data[game], 3)
        if game_value > 158:
            a = 5
        for key in bins.keys():
            if game_value <= key:
                bins[key].append(game)
                break
    bin_pct = {}
    total_pct = 0
    for bin_number, key in enumerate(bins.keys()):
        total_pct += len(bins[key]) / len(data)
        bin_pct[bin_number] = total_pct  
    return bin_pct, bins

def simulation_game_stats(off_stats: dict, off_stats_pct: float, def_stats: dict, def_stats_pct: float):
    return_stats = {}
    total_pct = off_stats_pct + def_stats_pct
    off_pct = off_stats_pct / total_pct
    for key in off_stats:
        if '%' in key or 'FP' == key or 'GmSc' == key or 'STRS' == key or 'PTS' == key or 'FGM' == key or 'FGA' == key or 'TRB' == key or 'MP' == key:
            continue
        new_avg = int(round(off_stats[key] * off_pct + def_stats[key] * (1 - off_pct), 0))
        return_stats[key] = new_avg
    return_stats['PTS'] = return_stats['2PM'] * 2 + return_stats['3PM'] * 3 + return_stats['FTM']
    return_stats['TRB'] = return_stats['ORB'] + return_stats['DRB']
    return_stats['FGM'] = return_stats['2PM'] + return_stats['3PM']
    return_stats['FGA'] = return_stats['2PA'] + return_stats['3PA']
    return return_stats

def simulate_game(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, team1_list = None, team2_list = None, opened = False):
    if not opened:
        file_league1_type = league_type1.replace('.', '')
        file_league2_type = league_type2.replace('.', '')
        with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
            team1_stats = pickle.load(pkl)
        team1_league_bin_off_pct, team1_league_bins_off = league_bin_games(team1_stats, 'offense')
        team1_league_bin_def_pct, team1_league_bins_def = league_bin_games(team1_stats, 'defense')
        team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
        team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
        with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
            team2_stats = pickle.load(pkl)
        team2_league_bin_off_pct, team2_league_bins_off = league_bin_games(team2_stats, 'offense')
        team2_league_bin_def_pct, team2_league_bins_def = league_bin_games(team2_stats, 'defense')    
        team2_bin_off_pct, team2_bins_off = bin_games(team2, team2_stats, 'offense')
        team2_bin_def_pct, team2_bins_def = bin_games(team2, team2_stats, 'defense')
    else:
        team1_league_bin_off_pct = team1_list[0]
        team1_league_bins_off = team1_list[1]
        team1_league_bin_def_pct = team1_list[2]
        team1_league_bins_def = team1_list[3]
        team1_bin_off_pct = team1_list[4]
        team1_bins_off = team1_list[5]
        team1_bin_def_pct = team1_list[6]
        team1_bins_def = team1_list[7]
        team1_stats = team1_list[8]
        team2_league_bin_off_pct = team2_list[0]
        team2_league_bins_off = team2_list[1]
        team2_league_bin_def_pct = team2_list[2]
        team2_league_bins_def = team2_list[3]
        team2_bin_off_pct = team2_list[4]
        team2_bins_off = team2_list[5]
        team2_bin_def_pct = team2_list[6]
        team2_bins_def = team2_list[7]
        team2_stats = team2_list[8]
    team1_off, team1_off_pct = find_game(team1, team1_bin_off_pct, team1_bins_off, team1_stats, team1_league_bin_off_pct, team1_league_bins_off, 'offense')
    team1_def, team1_def_pct = find_game(team1, team1_bin_def_pct, team1_bins_def, team1_stats, team1_league_bin_def_pct, team1_league_bins_def, 'defense')
    team2_off, team2_off_pct = find_game(team2, team2_bin_off_pct, team2_bins_off, team2_stats, team2_league_bin_off_pct, team2_league_bins_off, 'offense')
    team2_def, team2_def_pct = find_game(team2, team2_bin_def_pct, team2_bins_def, team2_stats, team2_league_bin_def_pct, team2_league_bins_def, 'defense')
    new_team1_stats = simulation_game_stats(team1_off, team1_off_pct, team2_def, 1 - team2_def_pct)
    new_team2_stats = simulation_game_stats(team2_off, team2_off_pct, team1_def, 1 - team1_def_pct)
    return new_team1_stats, new_team2_stats

def multi_game_simulation(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, games: int):
    game_wins = {f"{team1}'{year1}": {'wins': 0, 'losses': 0}, f"{team2}'{year2}": {'wins': 0, 'losses': 0}}
    team1_total_stats = {}
    team2_total_stats = {}
    file_league1_type = league_type1.replace('.', '')
    file_league2_type = league_type2.replace('.', '')
    with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
        team1_stats = pickle.load(pkl)
    team1_league_bin_off_pct, team1_league_bins_off = league_bin_games(team1_stats, 'offense')
    team1_league_bin_def_pct, team1_league_bins_def = league_bin_games(team1_stats, 'defense')
    team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
    team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
    team1_list = [team1_league_bin_off_pct, team1_league_bins_off, team1_league_bin_def_pct, team1_league_bins_def, team1_bin_off_pct, team1_bins_off, team1_bin_def_pct, team1_bins_def, team1_stats]
    with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
        team2_stats = pickle.load(pkl)
    team2_league_bin_off_pct, team2_league_bins_off = league_bin_games(team2_stats, 'offense')
    team2_league_bin_def_pct, team2_league_bins_def = league_bin_games(team2_stats, 'defense')    
    team2_bin_off_pct, team2_bins_off = bin_games(team2, team2_stats, 'offense')
    team2_bin_def_pct, team2_bins_def = bin_games(team2, team2_stats, 'defense')
    team2_list = [team2_league_bin_off_pct, team2_league_bins_off, team2_league_bin_def_pct, team2_league_bins_def, team2_bin_off_pct, team2_bins_off, team2_bin_def_pct, team2_bins_def, team2_stats]
    for _ in range(games):
        team1_game_stats, team2_game_stats = simulate_game(team1, year1, league_type1, team2, year2, league_type2, team1_list, team2_list, True)
        update_stats_dict(team1_total_stats, team1_game_stats)
        update_stats_dict(team2_total_stats, team2_game_stats)
        if team1_game_stats['PTS'] > team2_game_stats['PTS']:
            game_wins[f"{team1}'{year1}"]['wins'] += 1
            game_wins[f"{team2}'{year2}"]['losses'] += 1
        else:
            game_wins[f"{team2}'{year2}"]['wins'] += 1
            game_wins[f"{team1}'{year1}"]['losses'] += 1
    return team1_total_stats, team2_total_stats, game_wins

def best_of(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, games: int):
    game_wins = {f"{team1}'{year1}": {'wins': 0, 'losses': 0}, f"{team2}'{year2}": {'wins': 0, 'losses': 0}}
    half_point = round(games / 2, 0)
    team1_total_stats = {}
    team2_total_stats = {}
    file_league1_type = league_type1.replace('.', '')
    file_league2_type = league_type2.replace('.', '')
    with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
        team1_stats = pickle.load(pkl)
    team1_league_bin_off_pct, team1_league_bins_off = league_bin_games(team1_stats, 'offense')
    team1_league_bin_def_pct, team1_league_bins_def = league_bin_games(team1_stats, 'defense')
    team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
    team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
    team1_list = [team1_league_bin_off_pct, team1_league_bins_off, team1_league_bin_def_pct, team1_league_bins_def, team1_bin_off_pct, team1_bins_off, team1_bin_def_pct, team1_bins_def, team1_stats]
    with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
        team2_stats = pickle.load(pkl)
    team2_league_bin_off_pct, team2_league_bins_off = league_bin_games(team2_stats, 'offense')
    team2_league_bin_def_pct, team2_league_bins_def = league_bin_games(team2_stats, 'defense')    
    team2_bin_off_pct, team2_bins_off = bin_games(team2, team2_stats, 'offense')
    team2_bin_def_pct, team2_bins_def = bin_games(team2, team2_stats, 'defense')
    team2_list = [team2_league_bin_off_pct, team2_league_bins_off, team2_league_bin_def_pct, team2_league_bins_def, team2_bin_off_pct, team2_bins_off, team2_bin_def_pct, team2_bins_def, team2_stats]
    for _ in range(games):
        team1_game_stats, team2_game_stats = simulate_game(team1, year1, league_type1, team2, year2, league_type2, team1_list, team2_list, True)
        update_stats_dict(team1_total_stats, team1_game_stats)
        update_stats_dict(team2_total_stats, team2_game_stats)
        if team1_game_stats['PTS'] > team2_game_stats['PTS']:
            game_wins[f"{team1}'{year1}"]['wins'] += 1
            game_wins[f"{team2}'{year2}"]['losses'] += 1
        else:
            game_wins[f"{team2}'{year2}"]['wins'] += 1
            game_wins[f"{team1}'{year1}"]['losses'] += 1
        if game_wins[f"{team1}'{year1}"]['wins'] == half_point or game_wins[f"{team1}'{year1}"]['losses'] == half_point:
            break
    return team1_total_stats, team2_total_stats, game_wins

def update_stats_dict(team_tot_stats: dict, team_game_stats: dict):
    for key in team_game_stats.keys():
        if key not in team_tot_stats:
            team_tot_stats[key] = team_game_stats[key]
        else:
            team_tot_stats[key] += team_game_stats[key]

if __name__ == '__main__':
    team1 = 'MIA'
    team2 = 'BOS'
    year1 = '2023-24'
    year2 = '2023-24'
    league_type1 = '0.0'
    league_type2 = '0.0'
    games = 7
    start_time = time.time()
    team1_stats, team2_stats, game_wins = best_of(team1=team1, year1=year1, league_type1=league_type1, team2=team2, year2=year2, league_type2=league_type2, games=games)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")
    print(f"{team1}-{team1_stats}")
    print(f"{team2}-{team2_stats}")
    team1_name = f"{team1}'{year1}"
    team2_name = f"{team2}'{year2}"
    print(f"{team1_name} has {game_wins[team1_name]['wins']} wins and {team2_name} has {game_wins[team2_name]['wins']}")


    
    