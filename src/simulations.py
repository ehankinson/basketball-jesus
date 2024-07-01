import copy
import json
import time
import bisect
import random
import pickle
import concurrent
import concurrent.futures
from season_data import rank_bracket_team
from tournament import bracket_generator, double_bracket_generator

with open(f"data/json/teams.json", "r") as j:
    nba_teams = json.load(j)

def find_game(team: str, team_bin_pct: dict, team_bins: dict, league_stats: dict, league_bin_pct: dict, league_bins: dict, side_of_ball: str):
    pct = random.random()
    team_pct_values = list(team_bin_pct.values())
    if pct > team_pct_values[-1]:
        key_index = len(team_pct_values) - 1
    else:
        key_index = bisect.bisect_right(team_pct_values, pct)
    team_bin_list = list(team_bins.keys())
    while len(team_bins[team_bin_list[key_index]]) == 0:
        key_index -= 1
    game = random.choice(team_bins[team_bin_list[key_index]])
    game_stats = league_stats[team][game][side_of_ball]
    sorted_league_bins = sorted(league_bins)
    index = bisect.bisect_right(sorted_league_bins, round(game_stats['STRS'], 3))
    game_percentile = league_bin_pct[index] if index < len(league_bin_pct) else league_bin_pct[len(league_bin_pct) - 1]
    return game_stats, game_percentile
   
def league_bin_games(season_data: dict):
    data = {}
    min_value = None
    max_value = None
    for team in nba_teams:
        if team not in season_data:
            continue
        for game in season_data[team]:
            game_value = season_data[team][game]['offense']['STRS']
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
    for key in off_stats:
        if key in {'%', 'FP', 'GmSc', 'STRS', 'PTS', 'FGM', 'FGA', 'TRB', 'MP'}: 
            continue
        return_stats[key] = int(round((off_stats[key] + def_stats[key]) / 2, 0))
    return_stats['PTS'] = return_stats['2PM'] * 2 + return_stats['3PM'] * 3 + return_stats['FTM']
    return_stats['TRB'] = return_stats['ORB'] + return_stats['DRB']
    return_stats['FGM'] = return_stats['2PM'] + return_stats['3PM']
    return_stats['FGA'] = return_stats['2PA'] + return_stats['3PA']
    return return_stats

def simulate_game(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, team1_list = None, team2_list = None, opened = False, results = None, idx = None):
    if not opened:
        file_league1_type = league_type1.replace('.', '')
        file_league2_type = league_type2.replace('.', '')
        with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
            team1_stats = pickle.load(pkl)
        team1_league_bin_pct, team1_league_bins = league_bin_games(team1_stats)
        team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
        team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
        with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
            team2_stats = pickle.load(pkl)
        team2_league_bin_pct, team2_league_bins = league_bin_games(team2_stats) 
        team2_bin_off_pct, team2_bins_off = bin_games(team2, team2_stats, 'offense')
        team2_bin_def_pct, team2_bins_def = bin_games(team2, team2_stats, 'defense')
    else:
        team1_league_bin_pct, team1_league_bins, team1_bin_off_pct, team1_bins_off, team1_bin_def_pct, team1_bins_def, team1_stats = team1_list
        team2_league_bin_pct, team2_league_bins, team2_bin_off_pct, team2_bins_off, team2_bin_def_pct, team2_bins_def, team2_stats = team2_list
    team1_off, team1_off_pct = find_game(team1, team1_bin_off_pct, team1_bins_off, team1_stats, team1_league_bin_pct, team1_league_bins, 'offense')
    team1_def, team1_def_pct = find_game(team1, team1_bin_def_pct, team1_bins_def, team1_stats, team1_league_bin_pct, team1_league_bins, 'defense')
    team2_off, team2_off_pct = find_game(team2, team2_bin_off_pct, team2_bins_off, team2_stats, team2_league_bin_pct, team2_league_bins, 'offense')
    team2_def, team2_def_pct = find_game(team2, team2_bin_def_pct, team2_bins_def, team2_stats, team2_league_bin_pct, team2_league_bins, 'defense')
    new_team1_stats = simulation_game_stats(team1_off, team1_off_pct, team2_def, 1 - team2_def_pct)
    new_team2_stats = simulation_game_stats(team2_off, team2_off_pct, team1_def, 1 - team1_def_pct)
    if results != None:
        results[idx] = [new_team1_stats, new_team2_stats]
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

def best_of(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, games: int, teams_sim_stats = None, league_sim_stats = None, results = None, idx = None):
    game_wins = {f"{team1}'{year1}": {'wins': 0, 'losses': 0}, f"{team2}'{year2}": {'wins': 0, 'losses': 0}}
    half_point = round(games / 2, 0)
    team1_total_stats = {}
    team2_total_stats = {}
    team1_key = f"{team1}-{year1}-{league_type1}"
    league1_key = f"{year1}-{league_type1}"
    team1_list = [league_sim_stats[league1_key]['league_bins']['pct'], league_sim_stats[league1_key]['league_bins']['stats'], teams_sim_stats[team1_key]['off']['pct'], teams_sim_stats[team1_key]['off']['stats'], teams_sim_stats[team1_key]['def']['pct'], teams_sim_stats[team1_key]['def']['stats'], league_sim_stats[league1_key]['league']]
    team2_key = f"{team2}-{year2}-{league_type2}"
    league2_key = f"{year2}-{league_type2}"
    team2_list = [league_sim_stats[league2_key]['league_bins']['pct'], league_sim_stats[league2_key]['league_bins']['stats'], teams_sim_stats[team2_key]['off']['pct'], teams_sim_stats[team2_key]['off']['stats'], teams_sim_stats[team2_key]['def']['pct'], teams_sim_stats[team2_key]['def']['stats'], league_sim_stats[league2_key]['league']]
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

def run_sim_in_parallel(edit_bracket: dict, round_id: int, winners: list, losers: list, games_to_simulate, teams_sim_stats, league_sin_stats, playoff_stats, return_dict):
    threads = []
    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for idx, game_id in enumerate(edit_bracket[round_id]):
            game_stats = edit_bracket[round_id][game_id]
            home_team = game_stats[0]
            away_team = game_stats[1]
            results.append([home_team, away_team, game_id])
            threads.append(executor.submit(best_of, home_team[0], home_team[1], home_team[2], away_team[0], away_team[1], away_team[2], games_to_simulate, teams_sim_stats, league_sin_stats, results, idx))
        for idx, thing in enumerate(concurrent.futures.as_completed(threads)):
            home_team_stats, away_team_stats, wins_dict = thing.result()
            wins_keys = list(wins_dict.keys())
            team_to_check = wins_keys[0][:3]
            year_to_check = wins_keys[0][4:len(wins_keys[0])]
            for idx, team in enumerate(results):
                if (team[0][0] == team_to_check and team[0][1] == year_to_check) or (team[1][0] == team_to_check and team[1][1] == year_to_check):
                    home_team = team[0]
                    away_team = team[1]
                    game_id = team[2]
                    results.pop(idx)
                    break
            home_key = f"{home_team[0]}-{home_team[1]}-{home_team[2]}"
            away_key = f"{away_team[0]}-{away_team[1]}-{away_team[2]}"
            if home_key not in playoff_stats:
                playoff_stats[home_key] = {'offense': {}, 'defense': {}, 'record': {'wins': 0, 'losses': 0, 'best_round': 0}, 'info': {'name': home_team[0], 'year': home_team[1], 'league_type': home_team[2]}}
            if away_key not in playoff_stats:
                playoff_stats[away_key] = {'offense': {}, 'defense': {}, 'record': {'wins': 0, 'losses': 0, 'best_round': 0}, 'info': {'name': away_team[0], 'year': away_team[1], 'league_type': away_team[2]}}
            two_team_update_dict(home_key, away_key, home_team, away_team, home_team_stats, away_team_stats, playoff_stats)
            win_year, lose_year = check_round_winner(home_key, away_key, home_team, away_team, wins_dict, edit_bracket, playoff_stats, winners, losers, round_id, game_id)
            wins_key = f"{home_team[0]}'{home_team[1]}"
            playoff_stats[home_key]['record']['wins'] += wins_dict[wins_key]['wins']
            playoff_stats[home_key]['record']['losses'] += wins_dict[wins_key]['losses']
            playoff_stats[away_key]['record']['losses'] += wins_dict[wins_key]['wins']
            playoff_stats[away_key]['record']['wins'] += wins_dict[wins_key]['losses']
            return_dict[round_id][game_id] = {'winner': winners[-1][0][0], 'winner_year': win_year, 'wins': max(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses']), 'loser': losers[-1], 'loser_year': lose_year, 'losses': min(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses'])}
        
def run_single_thread(edit_bracket: dict, round_id: str, winners: list, losers: list, games_to_simulate: int, teams_sim_stats: dict, league_sim_stats: dict, playoff_stats: dict, return_dict: dict):
    for game_id in edit_bracket[round_id]:
        game = edit_bracket[round_id][game_id]
        home_team = game[0]
        away_team = game[1]
        home_team_stats, away_team_stats, wins_dict = best_of(home_team[0], home_team[1], home_team[2], away_team[0], away_team[1], away_team[2], games_to_simulate, teams_sim_stats, league_sim_stats)
        home_key = f"{home_team[0]}-{home_team[1]}-{home_team[2]}"
        away_key = f"{away_team[0]}-{away_team[1]}-{away_team[2]}"
        two_team_update_dict(home_key, away_key, home_team, away_team, home_team_stats, away_team_stats, playoff_stats)
        win_year, lose_year = check_round_winner(home_key, away_key, home_team, away_team, wins_dict, edit_bracket, playoff_stats, winners, losers, round_id, game_id)
        wins_key = f"{home_team[0]}'{home_team[1]}"
        playoff_stats[home_key]['record']['wins'] += wins_dict[wins_key]['wins']
        playoff_stats[home_key]['record']['losses'] += wins_dict[wins_key]['losses']
        playoff_stats[away_key]['record']['losses'] += wins_dict[wins_key]['wins']
        playoff_stats[away_key]['record']['wins'] += wins_dict[wins_key]['losses']
        return_dict[round_id][game_id] = {'winner': winners[-1][0][0], 'winner_year': win_year, 'wins': max(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses']), 'loser': losers[-1], 'loser_year': lose_year, 'losses': min(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses'])}

def simulate_bracket(teams: list, bracket: dict[list], games_to_simulate: int):
    playoff_stats = {}
    return_dict = {}
    edit_bracket = copy.deepcopy(bracket)
    teams_sim_stats, league_sim_stats = populate_team_and_league_dict(teams)
    for idx, round_id in enumerate(edit_bracket):
        return_dict[round_id] = {}
        if round_id != "round1":
            for winner, loser in zip(winners, losers):
                id_pos = winner[1]
                for game_id in edit_bracket[round_id]:
                    if id_pos in edit_bracket[round_id][game_id]:
                        if edit_bracket[round_id][game_id][0] == id_pos:
                            edit_bracket[round_id][game_id][0] = winner[0]
                        else:
                            edit_bracket[round_id][game_id][1] = winner[0]
                del teams_sim_stats[f"{loser[0]}-{loser[1]}-{loser[2]}"]
        winners = []
        losers = []
        simulate_games(games_to_simulate, round_id, winners, losers, edit_bracket, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
    return return_dict, playoff_stats

def simulate_games(games_to_simulate: int, round_id: str, winners: list, losers: list, edit_bracket: dict, teams_sim_stats: dict, league_sim_stats: dict, playoff_stats: dict, return_dict: dict):
    if games_to_simulate <= 4500:
        run_single_thread(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
    elif games_to_simulate >= 10000:
        if len(edit_bracket[round_id]) > 1:
            run_sim_in_parallel(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
        else:
            run_single_thread(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
    else:
        if len(edit_bracket[round_id]) > 16: 
            run_sim_in_parallel(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
        else:
            run_single_thread(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)

def populate_team_and_league_dict(teams: list):
    if isinstance(teams, dict):
        teams = list(teams.values())
    teams_sim_stats = {}
    league_sim_stats = {}
    for team_attributes in teams:
        team = team_attributes[0]
        year = team_attributes[1]
        league_type = team_attributes[2]
        team_key = f"{team}-{year}-{league_type}"
        file_league_type = league_type.replace('.', '')
        with open(f"data/pickle/{year} NBA Team Stats {file_league_type}.pickle", "rb") as pkl:
            team_stats = pickle.load(pkl)
        team_bin_off_pct, team_bins_off = bin_games(team, team_stats, 'offense')
        team_bin_def_pct, team_bins_def = bin_games(team, team_stats, 'defense')
        teams_sim_stats[team_key] = {'off': {'stats': team_bins_off, 'pct': team_bin_off_pct}, 'def': {'stats': team_bins_def, 'pct': team_bin_def_pct}}

        league_key = f"{year}-{league_type}"
        if league_key not in league_sim_stats:
            team_league_bin_pct, team_league_bins = league_bin_games(team_stats)
            league_sim_stats[league_key] = {'league_bins': {'stats': team_league_bins, 'pct': team_league_bin_pct}, 'league': team_stats}
    return teams_sim_stats, league_sim_stats

def two_team_update_dict(home_key: str, away_key: str, home_team: list, away_team: list, home_team_stats: dict, away_team_stats: dict, playoff_stats: dict):
    for home_stats_key, away_stats_key in zip(home_team_stats, away_team_stats):
        home_key = f"{home_team[0]}-{home_team[1]}-{home_team[2]}"
        away_key = f"{away_team[0]}-{away_team[1]}-{away_team[2]}"
        if home_key not in playoff_stats:
            playoff_stats[home_key] = {'offense': {}, 'defense': {}, 'record': {'wins': 0, 'losses': 0, 'best_round': 0}, 'info': {'name': home_team[0], 'year': home_team[1], 'league_type': home_team[2]}}
        if away_key not in playoff_stats:
            playoff_stats[away_key] = {'offense': {}, 'defense': {}, 'record': {'wins': 0, 'losses': 0, 'best_round': 0}, 'info': {'name': away_team[0], 'year': away_team[1], 'league_type': away_team[2]}}
        if home_stats_key not in playoff_stats[home_key]['offense']:
            playoff_stats[home_key]['offense'][home_stats_key] = 0
        if home_stats_key not in playoff_stats[away_key]['defense']:
            playoff_stats[away_key]['defense'][home_stats_key] = 0
        if away_stats_key not in playoff_stats[away_key]['offense']:
            playoff_stats[away_key]['offense'][away_stats_key] = 0
        if away_stats_key not in playoff_stats[home_key]['defense']:
            playoff_stats[home_key]['defense'][away_stats_key] = 0
        playoff_stats[home_key]['offense'][home_stats_key] += home_team_stats[home_stats_key]
        playoff_stats[away_key]['defense'][home_stats_key] += home_team_stats[home_stats_key]
        playoff_stats[away_key]['offense'][away_stats_key] += away_team_stats[away_stats_key]
        playoff_stats[home_key]['defense'][away_stats_key] += away_team_stats[away_stats_key]

def check_round_winner(home_key: str, away_key: str, home_team: list, away_team: list, wins_dict: dict, edit_bracket: dict, playoff_stats: dict, winners: list, losers: list, round_id: str, game_id: int):
    wins_key = f"{home_team[0]}'{home_team[1]}"
    if wins_dict[wins_key]['wins'] > wins_dict[wins_key]['losses']:
        winners.append([home_team, game_id])
        losers.append(away_team)
        win_year = home_team[1]
        lose_year = away_team[1]
        if int(round_id[-1]) == len(edit_bracket) - 1:
            playoff_stats[home_key]['record']['best_round'] = f"won {round_id}"
            playoff_stats[away_key]['record']['best_round'] = f"loss {round_id}"
        else:
            playoff_stats[home_key]['record']['best_round'] = round_id
            playoff_stats[away_key]['record']['best_round'] = round_id
        game_string = f"The home team: {home_team[0]}'{home_team[1]} {home_team[2]}, with {wins_dict[wins_key]['wins']} wins and the away team: {away_team[0]}'{away_team[1]} {away_team[2]}, with {wins_dict[wins_key]['losses']} in {round_id}\n"
    else:
        winners.append([away_team, game_id])
        losers.append(home_team)
        win_year = away_team[1]
        lose_year = home_team[1]
        if int(round_id[-1]) == len(edit_bracket) - 1:
            playoff_stats[home_key]['record']['best_round'] = f"loss {round_id}"
            playoff_stats[away_key]['record']['best_round'] = f"won {round_id}"
        else:
            playoff_stats[home_key]['record']['best_round'] = round_id
            playoff_stats[away_key]['record']['best_round'] = round_id
        game_string = f"The away team: {away_team[0]}'{away_team[1]} {away_team[2]}, with {wins_dict[wins_key]['losses']} wins and the home team: {home_team[0]}'{home_team[1]} {home_team[2]}, with {wins_dict[wins_key]['wins']} in {round_id}\n"
    print(game_string)
    return win_year, lose_year

def multi_bracket_sim(teams: list, amount_of_bracket_sims: int, series_length: int):
    multi_bracket_dict = {}
    ranked_list = []
    bracket = bracket_generator(len(teams), teams)
    for _ in range(amount_of_bracket_sims):
        return_dict, playoff_stats = simulate_bracket(teams, bracket, series_length)
        for key in playoff_stats:
            if key not in multi_bracket_dict:
                multi_bracket_dict[key] = {}
            add_round = playoff_stats[key]['record']['best_round']
            if add_round not in multi_bracket_dict[key]:
                multi_bracket_dict[key][add_round] = 1
                continue
            multi_bracket_dict[key][add_round] += 1
    for key in multi_bracket_dict:
        add_list = {'name': key[:3], 'year': key[4:11], 'league_type': key[-3:]}
        sorted_rounds = sorted(multi_bracket_dict[key], reverse=True)
        for round_id in sorted_rounds:
            add_list[round_id] = multi_bracket_dict[key][round_id]
        ranked_list.append(add_list)
    return ranked_list

if __name__ == '__main__':
    teams = [
        ['BOS', '2023-24', '0.0'],
        ['OKC', '2023-24', '0.0'],
        ['DEN', '2023-24', '0.0'],
        ['NYK', '2023-24', '0.0'],
        ['MIL', '2023-24', '0.0'],
        ['MIN', '2023-24', '0.0'],
        ['LAC', '2023-24', '0.0'],
        ['CLE', '2023-24', '0.0'],
        ['ORL', '2023-24', '0.0'],
        ['DAL', '2023-24', '0.0'],
        ['PHO', '2023-24', '0.0'],
        ['IND', '2023-24', '0.0'],
        ['PHI', '2023-24', '0.0'],
        ['LAL', '2023-24', '0.0'],
        ['NOP', '2023-24', '0.0'],
        ['MIA', '2023-24', '0.0'],
        ['BOS', '2022-23', '0.0'],
        ['OKC', '2022-23', '0.0'],
        ['DEN', '2022-23', '0.0'],
        ['NYK', '2022-23', '0.0'],
        ['MIL', '2022-23', '0.0'],
        ['MIN', '2022-23', '0.0'],
        ['LAC', '2022-23', '0.0'],
        ['CLE', '2022-23', '0.0'],
        ['ORL', '2022-23', '0.0'],
        ['DAL', '2022-23', '0.0'],
        ['PHO', '2022-23', '0.0'],
        ['IND', '2022-23', '0.0'],
        ['PHI', '2022-23', '0.0'],
        ['LAL', '2022-23', '0.0'],
        ['NOP', '2022-23', '0.0'],
        ['MIA', '2022-23', '0.0'],
        ['BOS', '2021-22', '0.0'],
        ['OKC', '2021-22', '0.0'],
        ['DEN', '2021-22', '0.0'],
        ['NYK', '2021-22', '0.0'],
        ['MIL', '2021-22', '0.0'],
        ['MIN', '2021-22', '0.0'],
        ['LAC', '2021-22', '0.0'],
        ['CLE', '2021-22', '0.0'],
        ['ORL', '2021-22', '0.0'],
        ['DAL', '2021-22', '0.0'],
        ['PHO', '2021-22', '0.0'],
        ['IND', '2021-22', '0.0'],
        ['PHI', '2021-22', '0.0'],
        ['LAL', '2021-22', '0.0'],
        ['NOP', '2021-22', '0.0'],
        ['MIA', '2021-22', '0.0'],
        ['BOS', '2020-21', '0.0'],
        ['OKC', '2020-21', '0.0'],
        ['DEN', '2020-21', '0.0'],
        ['NYK', '2020-21', '0.0'],
        ['MIL', '2020-21', '0.0'],
        ['MIN', '2020-21', '0.0'],
        ['LAC', '2020-21', '0.0'],
        ['CLE', '2020-21', '0.0'],
        ['ORL', '2020-21', '0.0'],
        ['DAL', '2020-21', '0.0'],
        ['PHO', '2020-21', '0.0'],
        ['IND', '2020-21', '0.0'],
        ['PHI', '2020-21', '0.0'],
        ['LAL', '2020-21', '0.0'],
        ['NOP', '2020-21', '0.0'],
        ['MIA', '2020-21', '0.0'],
        ['BOS', '2018-19', '0.0'],
        ['OKC', '2018-19', '0.0'],
        ['DEN', '2018-19', '0.0'],
        ['NYK', '2018-19', '0.0'],
        ['MIL', '2018-19', '0.0'],
        ['MIN', '2018-19', '0.0'],
        ['LAC', '2018-19', '0.0'],
        ['CLE', '2018-19', '0.0'],
        ['ORL', '2018-19', '0.0'],
        ['DAL', '2018-19', '0.0'],
        ['PHO', '2018-19', '0.0'],
        ['IND', '2018-19', '0.0'],
        ['PHI', '2018-19', '0.0'],
        ['LAL', '2018-19', '0.0'],
        ['NOP', '2018-19', '0.0'],
        ['MIA', '2018-19', '0.0'],
        ['BOS', '2017-18', '0.0'],
        ['OKC', '2017-18', '0.0'],
        ['DEN', '2017-18', '0.0'],
        ['NYK', '2017-18', '0.0'],
        ['MIL', '2017-18', '0.0'],
        ['MIN', '2017-18', '0.0'],
        ['LAC', '2017-18', '0.0'],
        ['CLE', '2017-18', '0.0'],
        ['ORL', '2017-18', '0.0'],
        ['DAL', '2017-18', '0.0'],
        ['PHO', '2017-18', '0.0'],
        ['IND', '2017-18', '0.0'],
        ['PHI', '2017-18', '0.0'],
        ['LAL', '2017-18', '0.0'],
        ['NOP', '2017-18', '0.0'],
        ['MIA', '2017-18', '0.0'],
        ['BOS', '2016-17', '0.0'],
        ['OKC', '2016-17', '0.0'],
        ['DEN', '2016-17', '0.0'],
        ['NYK', '2016-17', '0.0'],
        ['MIL', '2016-17', '0.0'],
        ['MIN', '2016-17', '0.0'],
        ['LAC', '2016-17', '0.0'],
        ['CLE', '2016-17', '0.0'],
        ['ORL', '2016-17', '0.0'],
        ['DAL', '2016-17', '0.0'],
        ['PHO', '2016-17', '0.0'],
        ['IND', '2016-17', '0.0'],
        ['PHI', '2016-17', '0.0'],
        ['LAL', '2016-17', '0.0'],
        ['NOP', '2016-17', '0.0'],
        ['MIA', '2016-17', '0.0'],
        ['BOS', '2015-16', '0.0'],
        ['OKC', '2015-16', '0.0'],
        ['DEN', '2015-16', '0.0'],
        ['NYK', '2015-16', '0.0'],
        ['MIL', '2015-16', '0.0'],
        ['MIN', '2015-16', '0.0'],
        ['LAC', '2015-16', '0.0'],
        ['CLE', '2015-16', '0.0'],
        ['ORL', '2015-16', '0.0'],
        ['DAL', '2015-16', '0.0'],
        ['PHO', '2015-16', '0.0'],
        ['IND', '2015-16', '0.0'],
        ['PHI', '2015-16', '0.0'],
        ['LAL', '2015-16', '0.0'],
        ['NOP', '2015-16', '0.0'],
        ['MIA', '2015-16', '0.0'],
    ]
    print(len(teams))
    games = 7
    bracket = bracket_generator(len(teams), teams)
   
            
 
