import csv
import json
import time
import random
import pickle
import numpy as np
from tournament import bracket_generator

with open(f"data/json/teams.json", "r") as j:
    nba_teams = json.load(j)

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
                keys = list(team_bins.keys())
                key_index = keys.index(key)
                for team_bin in range(key_index - 1, -1, -1):
                    if len(team_bins[keys[team_bin]]) == 0:
                        continue
                    new_key = keys[team_bin]
                game = random.choice(team_bins[new_key])
            else:
                game = random.choice(team_bins[key])
            game_stats = league_stats[team][game][side_of_ball]
            break
    for count, key in enumerate(league_bins):
        if game_stats['STRS'] <= round(key, 3):
            game_percentile = league_bin_pct[count]
            break
    return game_stats, game_percentile

def league_bin_games(season_data: dict, side_of_ball: str):
    data = {}
    min_value = None
    max_value = None
    for team in nba_teams:
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
        max_stat = max(off_stats[key], def_stats[key])
        min_stat = min(off_stats[key], def_stats[key])
        new_avg = int(round(max_stat * off_pct + min_stat * (1 - off_pct), 0))
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

def best_of(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, games: int, teams_sim_stats = None):
    game_wins = {f"{team1}'{year1}": {'wins': 0, 'losses': 0}, f"{team2}'{year2}": {'wins': 0, 'losses': 0}}
    half_point = round(games / 2, 0)
    team1_total_stats = {}
    team2_total_stats = {}
    file_league1_type = league_type1.replace('.', '')
    file_league2_type = league_type2.replace('.', '')
    start_time = time.time()
    if team1 not in teams_sim_stats:
        with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
            team1_stats = pickle.load(pkl)
        team1_league_bin_off_pct, team1_league_bins_off = league_bin_games(team1_stats, 'offense')
        team1_league_bin_def_pct, team1_league_bins_def = league_bin_games(team1_stats, 'defense')
        team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
        team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
        teams_sim_stats[team1] = {'off': {'stats': team1_bins_off, 'pct': team1_bin_off_pct}, 'def': {'stats': team1_bins_def, 'pct': team1_bin_def_pct}, 'league_off': {'stats': team1_league_bins_off, 'pct': team1_league_bin_off_pct}, 'league_def': {'stats': team1_league_bins_def, 'pct': team1_league_bin_def_pct}, 'league': team1_stats}
    team1_list = [teams_sim_stats[team1]['league_off']['pct'], teams_sim_stats[team1]['league_off']['stats'], teams_sim_stats[team1]['league_def']['pct'], teams_sim_stats[team1]['league_def']['stats'], teams_sim_stats[team1]['off']['pct'], teams_sim_stats[team1]['off']['stats'], teams_sim_stats[team1]['def']['pct'], teams_sim_stats[team1]['def']['stats'], teams_sim_stats[team1]['league']]
    if team2 not in teams_sim_stats:
        with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
            team2_stats = pickle.load(pkl)
        team2_league_bin_off_pct, team2_league_bins_off = league_bin_games(team2_stats, 'offense')
        team2_league_bin_def_pct, team2_league_bins_def = league_bin_games(team2_stats, 'defense')    
        team2_bin_off_pct, team2_bins_off = bin_games(team2, team2_stats, 'offense')
        team2_bin_def_pct, team2_bins_def = bin_games(team2, team2_stats, 'defense')
        teams_sim_stats[team2] = {'off': {'stats': team2_bins_off, 'pct': team2_bin_off_pct}, 'def': {'stats': team2_bins_def, 'pct': team2_bin_def_pct}, 'league_off': {'stats': team2_league_bins_off, 'pct': team2_league_bin_off_pct}, 'league_def': {'stats': team2_league_bins_def, 'pct': team2_league_bin_def_pct}, 'league': team2_stats}
    team2_list = [teams_sim_stats[team2]['league_off']['pct'], teams_sim_stats[team2]['league_off']['stats'], teams_sim_stats[team2]['league_def']['pct'], teams_sim_stats[team2]['league_def']['stats'], teams_sim_stats[team2]['off']['pct'], teams_sim_stats[team2]['off']['stats'], teams_sim_stats[team2]['def']['pct'], teams_sim_stats[team2]['def']['stats'], teams_sim_stats[team2]['league']]
    end_time = time.time()
    print(f"Grabbing team bins took: {end_time - start_time} seconds")
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

def simulate_bracket(teams: list, bracket: dict[list], games_to_simulate: int):
    playoff_stats = {}
    teams_sim_stats = {}
    for round_id in bracket:
        if round_id != "round1":
            for winner in winners:
                id_pos = winner[1]
                for game_id in bracket[round_id]:
                    if id_pos in bracket[round_id][game_id]:
                        if bracket[round_id][game_id][0] == id_pos:
                            bracket[round_id][game_id][0] = winner[0]
                        else:
                            bracket[round_id][game_id][1] = winner[0]
        winners = []
        losers = []
        for game_id in bracket[round_id]:
            game = bracket[round_id][game_id]
            home_team = game[0]
            away_team = game[1]
            if games_to_simulate == 1:
                simulate_game()
            else:
                home_team_stats, away_team_stats, wins_dict = best_of(home_team[0], home_team[1], home_team[2], away_team[0], away_team[1], away_team[2], games_to_simulate, teams_sim_stats)
            for home_stats_key, away_stats_key in zip(home_team_stats, away_team_stats):
                if home_team[0] not in playoff_stats:
                    playoff_stats[home_team[0]] = {'offense': {}, 'defense': {}, 'record': {'wins': 0, 'losses': 0}}
                if away_team[0] not in playoff_stats:
                    playoff_stats[away_team[0]] = {'offense': {}, 'defense': {},  'record': {'wins': 0, 'losses': 0}}
                if home_stats_key not in playoff_stats[home_team[0]]['offense']:
                    playoff_stats[home_team[0]]['offense'][home_stats_key] = 0
                if home_stats_key not in playoff_stats[away_team[0]]['defense']:
                    playoff_stats[away_team[0]]['defense'][home_stats_key] = 0
                if away_stats_key not in playoff_stats[away_team[0]]['offense']:
                    playoff_stats[away_team[0]]['offense'][away_stats_key] = 0
                if away_stats_key not in playoff_stats[home_team[0]]['defense']:
                    playoff_stats[home_team[0]]['defense'][away_stats_key] = 0
                playoff_stats[home_team[0]]['offense'][home_stats_key] += home_team_stats[home_stats_key]
                playoff_stats[away_team[0]]['defense'][home_stats_key] += home_team_stats[home_stats_key]
                playoff_stats[away_team[0]]['offense'][away_stats_key] += away_team_stats[away_stats_key]
                playoff_stats[home_team[0]]['defense'][away_stats_key] += away_team_stats[away_stats_key]
            home_key = f"{home_team[0]}'{home_team[1]}"
            if wins_dict[home_key]['wins'] > wins_dict[home_key]['losses']:
                winners.append([home_team, game_id])
                losers.append(away_team[0])
                print(f"The home team: {home_team[0]}'{home_team[1]}, with {wins_dict[home_key]['wins']} wins and the away team: {away_team[0]}'{away_team[1]}, with {wins_dict[home_key]['losses']} in {round_id}")
            else:
                winners.append([away_team, game_id])
                losers.append(home_team[0])
                print(f"The away team: {away_team[0]}'{away_team[1]}, with {wins_dict[home_key]['losses']} wins and the home team: {home_team[0]}'{home_team[1]}, with {wins_dict[home_key]['wins']} in {round_id}")
            playoff_stats[home_team[0]]['record']['wins'] += wins_dict[home_key]['wins']
            playoff_stats[home_team[0]]['record']['losses'] += wins_dict[home_key]['losses']
            playoff_stats[away_team[0]]['record']['losses'] += wins_dict[home_key]['wins']
            playoff_stats[away_team[0]]['record']['wins'] += wins_dict[home_key]['losses']
    a = 5

if __name__ == '__main__':
    year = '2022-23'
    # year2 = '2016-17'
    league_type = '2.1'
    teams = [
        ['HOU', '2018-19', '1.0'], 
        ['TOR', '2018-19', '1.0'], 
        ['BOS', '2018-19', '1.0'], 
        ['GSW', '2018-19', '1.0'], 
        ['POR', '2018-19', '1.0'],
        ['PHI', '2018-19', '1.0'],
        ['CLE', '2018-19', '1.0'], 
        ['OKC', '2018-19', '1.0'], 
        ['UTA', '2018-19', '1.0'], 
        ['IND', '2018-19', '1.0'], 
        ['MIA', '2018-19', '1.0'], 
        ['NOP', '2018-19', '1.0'], 
        ['SAS', '2018-19', '1.0'], 
        ['MIL', '2018-19', '1.0'], 
        ['WAS', '2018-19', '1.0'], 
        ['MIN', '2018-19', '1.0']
    ]
    start_time = time.time()
    games = 7000
    bracket = bracket_generator(len(teams), teams)
    simulate_bracket(teams, bracket, games)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")
    # team1 = 'DEN'
    # team2 = 'NOP'
    # year1 = '2023-24'
    # year2 = '2023-24'
    # league_type1 = '0.0'
    # league_type2 = '0.0'
    # games = 10000
    
    # team1_stats, team2_stats, game_wins = multi_game_simulation(team1=team1, year1=year1, league_type1=league_type1, team2=team2, year2=year2, league_type2=league_type2, games=games)
    
    
    # print(f"{team1}-{team1_stats}")
    # print(f"{team2}-{team2_stats}")
    # team1_name = f"{team1}'{year1}"
    # team2_name = f"{team2}'{year2}"
    # print(f"{team1_name} has {game_wins[team1_name]['wins']} wins and {team2_name} has {game_wins[team2_name]['wins']}")


    
    