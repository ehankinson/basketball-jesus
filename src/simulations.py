import os
import copy
import math
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
    NBA_TEAMS = json.load(j)

def find_game(team: str, team_bin_pct: dict, team_bins: dict, league_stats: dict, league_bin_pct: dict, league_bins: dict, side_of_ball: str):
    pct = random.random()
    # for idx in team_bin_pct:
    #     if pct < team_bin_pct[idx]:
    #         break
    # key_value = list(team_bins)[idx]
    # while len(team_bins[key_value]) == 0:
    #     key_index -= 1
    # game = random.choices(team_bins[key_value])[0]
    # game_stats = league_stats[team][game][side_of_ball]
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

def grab_min_max_values_from_games(team: str, season_data: dict, data: dict, side_of_ball: str):
    teams = [team] if team != 'ALL' else NBA_TEAMS
    is_all = team
    min_value = float('inf')
    max_value = float('-inf')
    for team in teams:
        if team not in season_data:
            continue
        for game in season_data[team]:
            game_value = season_data[team][game][side_of_ball]['STRS']
            if game_value < min_value:
                min_value = game_value
            if game_value > max_value:
                max_value = game_value
            if is_all == "ALL":
                data[f"{team}-{game}"] = game_value
            else:
                data[game] = game_value
    return round(min_value, 3), round(max_value, 3)

def calculate_histogram_data(data: dict, max_value: float, min_value: float):
    # amount_of_bins = math.ceil(math.log2(len(data)) + 1)
    amount_of_bins = math.ceil(2 * (len(data) ** (1/3)))
    difference = max_value - min_value
    bin_size = difference / amount_of_bins
    return amount_of_bins, bin_size

def calculate_bins(min_value: float, sqrt_bins: int, bin_size: int, data: dict,):
    bins = {}
    previous_key = min_value
    for _ in range(sqrt_bins):
        new_key = round(previous_key + bin_size, 3)
        bins[new_key] = []
        previous_key = new_key
    
    # Assign games to bins
    for game, value in data.items():
        game_value = round(value, 3)
        for key in bins:
            if game_value <= key:
                bins[key].append(game)
                break
    
    # Calculate bin percentages
    bin_pct = {}
    total_games = len(data)
    total_pct = 0
    for bin_number, key in enumerate(bins):
        total_pct += len(bins[key]) / total_games
        bin_pct[bin_number] = total_pct  
    
    return bin_pct, bins

def bin_games(team: str, season_data: dict, side_of_ball: str):
    data = {}
    min_value, max_value = grab_min_max_values_from_games(team, season_data, data, side_of_ball)
    sqrt_bins, bin_size = calculate_histogram_data(data, max_value, min_value)
    return calculate_bins(min_value, sqrt_bins, bin_size, data)

def simulation_game_stats(off_stats: dict, off_stats_pct: float, def_stats: dict, def_stats_pct: float):
    pct = random.random()
    total_pct = off_stats_pct + def_stats_pct
    new_off_pct = off_stats_pct / total_pct
    if pct < new_off_pct:
        return off_stats
    return def_stats
    # return_stats = {}
    # for key in off_stats:
    #     if key in {'%', 'FP', 'GmSc', 'STRS', 'PTS', 'FGM', 'FGA', 'TRB', 'MP'}: 
    #         continue
    #     return_stats[key] = int(round((off_stats[key] + def_stats[key]) / 2, 0))
    # return_stats['PTS'] = return_stats['2PM'] * 2 + return_stats['3PM'] * 3 + return_stats['FTM']
    # return_stats['TRB'] = return_stats['ORB'] + return_stats['DRB']
    # return_stats['FGM'] = return_stats['2PM'] + return_stats['3PM']
    # return_stats['FGA'] = return_stats['2PA'] + return_stats['3PA']
    # return return_stats

def simulate_game(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, team1_list = None, team2_list = None, opened = False, results = None, idx = None, team1_file = None, team2_file = None):
    if not opened:
        file_league1_type = league_type1.replace('.', '')
        file_league2_type = league_type2.replace('.', '')
        with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
            team1_stats = pickle.load(pkl)
        team1_league_bin_pct, team1_league_bins = bin_games('ALL', team1_stats, 'offense')
        team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
        team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
        with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
            team2_stats = pickle.load(pkl)
        team2_league_bin_pct, team2_league_bins = bin_games('ALL', team2_stats, 'offense')
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
    team1_league_bin_off_pct, team1_league_bins_off = bin_games('ALL', team1_stats, 'offense')
    team1_bin_off_pct, team1_bins_off = bin_games(team1, team1_stats, 'offense')
    team1_bin_def_pct, team1_bins_def = bin_games(team1, team1_stats, 'defense')
    team1_list = [team1_league_bin_off_pct, team1_league_bins_off, team1_bin_off_pct, team1_bins_off, team1_bin_def_pct, team1_bins_def, team1_stats]
    with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
        team2_stats = pickle.load(pkl)
    team2_league_bin_off_pct, team2_league_bins_off = bin_games('ALL', team1_stats, 'offense')  
    team2_bin_off_pct, team2_bins_off = bin_games(team2, team2_stats, 'offense')
    team2_bin_def_pct, team2_bins_def = bin_games(team2, team2_stats, 'defense')
    team2_list = [team2_league_bin_off_pct, team2_league_bins_off, team2_bin_off_pct, team2_bins_off, team2_bin_def_pct, team2_bins_def, team2_stats]
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
    team1_file = []
    team2_file = []
    if league_sim_stats != None:
        team1_key = f"{team1}-{year1}-{league_type1}"
        league1_key = f"{year1}-{league_type1}"
        team2_key = f"{team2}-{year2}-{league_type2}"
        league2_key = f"{year2}-{league_type2}"
        team1_list = [league_sim_stats[league1_key]['league_bins']['pct'], league_sim_stats[league1_key]['league_bins']['stats'], teams_sim_stats[team1_key]['off']['pct'], teams_sim_stats[team1_key]['off']['stats'], teams_sim_stats[team1_key]['def']['pct'], teams_sim_stats[team1_key]['def']['stats'], league_sim_stats[league1_key]['league']]
        team2_list = [league_sim_stats[league2_key]['league_bins']['pct'], league_sim_stats[league2_key]['league_bins']['stats'], teams_sim_stats[team2_key]['off']['pct'], teams_sim_stats[team2_key]['off']['stats'], teams_sim_stats[team2_key]['def']['pct'], teams_sim_stats[team2_key]['def']['stats'], league_sim_stats[league2_key]['league']]
    for _ in range(games):
        if league_sim_stats != None:
            team1_game_stats, team2_game_stats = simulate_game(team1, year1, league_type1, team2, year2, league_type2, team1_list, team2_list, True, None, None, team1_file, team2_file)
        else:
            team1_game_stats, team2_game_stats = simulate_game(team1, year1, league_type1, team2, year2, league_type2)
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

def run_sim_in_parallel(edit_bracket: dict, round_id: int, winners: list, losers: list, games_to_simulate: int, teams_sim_stats: dict, league_sin_stats: dict, playoff_stats: dict, return_dict: dict, double_elim = False, win_or_lose = None):
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
            win_year, lose_year = check_round_winner(home_key, away_key, home_team, away_team, wins_dict, edit_bracket, playoff_stats, winners, losers, round_id, game_id, win_or_lose)
            wins_key = f"{home_team[0]}'{home_team[1]}"
            playoff_stats[home_key]['record']['wins'] += wins_dict[wins_key]['wins']
            playoff_stats[home_key]['record']['losses'] += wins_dict[wins_key]['losses']
            playoff_stats[away_key]['record']['losses'] += wins_dict[wins_key]['wins']
            playoff_stats[away_key]['record']['wins'] += wins_dict[wins_key]['losses']
            if not double_elim:
                return_dict[round_id][game_id] = {'winner': winners[-1][0][0], 'winner_year': win_year, 'wins': max(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses']), 'loser': losers[-1], 'loser_year': lose_year, 'losses': min(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses'])}
            else:
                return_dict[win_or_lose][round_id][game_id] = {'winner': winners[-1][0][0], 'winner_year': win_year, 'winner_league_type': winners[-1][0][2], 'wins': max(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses']), 'loser': losers[-1], 'loser_year': lose_year, 'losses': min(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses'])}

def run_single_thread(edit_bracket: dict, round_id: str, winners: list, losers: list, games_to_simulate: int, teams_sim_stats: dict, league_sim_stats: dict, playoff_stats: dict, return_dict: dict, double_elim = False, win_or_lose = None):
    for game_id in edit_bracket[round_id]:
        game = edit_bracket[round_id][game_id]
        home_team = game[0]
        away_team = game[1]
        home_team_stats, away_team_stats, wins_dict = best_of(home_team[0], home_team[1], home_team[2], away_team[0], away_team[1], away_team[2], games_to_simulate, teams_sim_stats, league_sim_stats)
        home_key = f"{home_team[0]}-{home_team[1]}-{home_team[2]}"
        away_key = f"{away_team[0]}-{away_team[1]}-{away_team[2]}"
        two_team_update_dict(home_key, away_key, home_team, away_team, home_team_stats, away_team_stats, playoff_stats)
        win_year, lose_year = check_round_winner(home_key, away_key, home_team, away_team, wins_dict, edit_bracket, playoff_stats, winners, losers, round_id, game_id, win_or_lose)
        wins_key = f"{home_team[0]}'{home_team[1]}"
        playoff_stats[home_key]['record']['wins'] += wins_dict[wins_key]['wins']
        playoff_stats[home_key]['record']['losses'] += wins_dict[wins_key]['losses']
        playoff_stats[away_key]['record']['losses'] += wins_dict[wins_key]['wins']
        playoff_stats[away_key]['record']['wins'] += wins_dict[wins_key]['losses']
        if not double_elim:
            return_dict[round_id][game_id] = {'winner': winners[-1][0][0], 'winner_year': win_year, 'winner_league_type': winners[-1][0][2], 'wins': max(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses']), 'loser': losers[-1], 'loser_year': lose_year, 'losses': min(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses'])}
        else:
            return_dict[win_or_lose][round_id][game_id] = {'winner': winners[-1][0][0], 'winner_year': win_year, 'winner_league_type': winners[-1][0][2], 'wins': max(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses']), 'loser': losers[-1], 'loser_year': lose_year, 'losses': min(wins_dict[wins_key]['wins'], wins_dict[wins_key]['losses'])}

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
                            break
                        else:
                            edit_bracket[round_id][game_id][1] = winner[0]
                            break
                del teams_sim_stats[f"{loser[0]}-{loser[1]}-{loser[2]}"]
        winners = []
        losers = []
        simulate_games(games_to_simulate, round_id, winners, losers, edit_bracket, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
    return return_dict, playoff_stats

def simulate_double_elimination_bracket(teams: list, winners_bracket: dict, losers_bracket: dict, games_to_simulate: int):
    playoff_stats = {}
    return_dict = {'winner': {}, 'loser': {}}
    edit_winner_bracket = copy.deepcopy(winners_bracket)
    edit_loser_bracket = copy.deepcopy(losers_bracket)
    teams_sim_stats, league_sim_stats = populate_team_and_league_dict(teams)
    winner_count = 0
    losers_count = 0
    simulate_loser = False
    change_top_bracket = True
    while winner_count <= len(winners_bracket) and losers_count <= len(losers_bracket):
        if winner_count == len(winners_bracket) and losers_count == len(losers_bracket):
            return_dict['grand_finals'] = {}
            win_short_cut = return_dict['winner'][f"round{winner_count}"]
            win_team_key = list(win_short_cut.keys())[0]
            winner_team = [win_short_cut[win_team_key]['winner'], win_short_cut[win_team_key]['winner_year'], win_short_cut[win_team_key]['winner_league_type']]
            loser_short_cut = return_dict['loser'][f"round{losers_count}"]
            lose_team_key = list(loser_short_cut.keys())[0]
            loser_team = [loser_short_cut[lose_team_key]['winner'], loser_short_cut[lose_team_key]['winner_year'], loser_short_cut[lose_team_key]['winner_league_type']]
            grand_finals = {'grand_finals': {max(win_team_key, lose_team_key) + 1: [winner_team, loser_team]}}
            simulate_games(games_to_simulate, 'grand_finals', [], [], grand_finals, teams_sim_stats, league_sim_stats, playoff_stats, return_dict)
            break
        winner_key = f"round{winner_count + 1}"
        loser_key = f"round{losers_count + 1}"
        # putting the winners in the next round, and losers in the correct stop in losers bracket
        if winner_key != 'round1':
            if change_top_bracket:
                for winner, loser in zip(win_bracket_winners, win_bracket_lossers):
                    # grabing the game id
                    id_pos = winner[1]
                    # finding which game in the round to put the winning team in
                    if winner_count != len(winners_bracket):
                        for game_id in edit_winner_bracket[winner_key]:
                            if id_pos in edit_winner_bracket[winner_key][game_id]:
                                if edit_winner_bracket[winner_key][game_id][0] == id_pos:
                                    edit_winner_bracket[winner_key][game_id][0] = winner[0]
                                    break
                                else:
                                    edit_winner_bracket[winner_key][game_id][1] = winner[0]
                                    break
                    # finding which game in the round to put the losing team in the losers bracket
                    for game_id in edit_loser_bracket[loser_key]:
                        if isinstance(edit_loser_bracket[loser_key][game_id][0], str):
                            edit_loser_bracket[loser_key][game_id][0] = int(edit_loser_bracket[loser_key][game_id][0].replace("_w", ""))
                        if isinstance(edit_loser_bracket[loser_key][game_id][1], str):
                            edit_loser_bracket[loser_key][game_id][1] = int(edit_loser_bracket[loser_key][game_id][1].replace("_w", ""))
                        if id_pos in edit_loser_bracket[loser_key][game_id]:
                            if edit_loser_bracket[loser_key][game_id][0] == id_pos:
                                edit_loser_bracket[loser_key][game_id][0] = loser
                                break
                            else:
                                edit_loser_bracket[loser_key][game_id][1] = loser
                                break
            else:
                for winner, loser in zip(lose_bracket_winners, lose_bracket_lossers):
                    id_pos = winner[1]
                    for game_id in edit_loser_bracket[loser_key]:
                        if id_pos in edit_loser_bracket[loser_key][game_id]:
                            if edit_loser_bracket[loser_key][game_id][0] == id_pos:
                                edit_loser_bracket[loser_key][game_id][0] = winner[0]
                                break
                            else:
                                edit_loser_bracket[loser_key][game_id][1] = winner[0]
                                break
                    del teams_sim_stats[f"{loser[0]}-{loser[1]}-{loser[2]}"]
        win_bracket_winners = []
        win_bracket_lossers = []
        lose_bracket_winners = []
        lose_bracket_lossers = []
        if not simulate_loser:
            return_dict['winner'][winner_key] = {}
            simulate_games(games_to_simulate, winner_key, win_bracket_winners, win_bracket_lossers, edit_winner_bracket, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, True, 'winner')
            winner_count += 1
            simulate_loser = True
            change_top_bracket = True
        else:
            return_dict['loser'][loser_key] = {}
            simulate_games(games_to_simulate, loser_key, lose_bracket_winners, lose_bracket_lossers, edit_loser_bracket, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, True, 'loser')
            losers_count += 1
            if losers_count != len(losers_bracket):
                loser_key = f"round{losers_count + 1}"
                check_key = list(edit_loser_bracket[loser_key].keys())[0]
                if isinstance(edit_loser_bracket[loser_key][check_key][0], str) or isinstance(edit_loser_bracket[loser_key][check_key][1], str):
                    simulate_loser = False
                    change_top_bracket = False
                else:
                    simulate_loser = True
                    change_top_bracket = False
    return return_dict, playoff_stats

def simulate_games(games_to_simulate: int, round_id: str, winners: list, losers: list, edit_bracket: dict, teams_sim_stats: dict, league_sim_stats: dict, playoff_stats: dict, return_dict: dict, double_elim = False, win_or_lose = None):
    if games_to_simulate <= 4500:
        run_single_thread(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, double_elim, win_or_lose)
    elif games_to_simulate >= 10000:
        if len(edit_bracket[round_id]) > 1:
            run_sim_in_parallel(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, double_elim, win_or_lose)
        else:
            run_single_thread(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, double_elim, win_or_lose)
    else:
        if len(edit_bracket[round_id]) > 16: 
            run_sim_in_parallel(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, double_elim, win_or_lose)
        else:
            run_single_thread(edit_bracket, round_id, winners, losers, games_to_simulate, teams_sim_stats, league_sim_stats, playoff_stats, return_dict, double_elim, win_or_lose)

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
            team_league_bin_pct, team_league_bins = bin_games('ALL', team_stats, 'offense')
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

def check_round_winner(home_key: str, away_key: str, home_team: list, away_team: list, wins_dict: dict, edit_bracket: dict, playoff_stats: dict, winners: list, losers: list, round_id: str, game_id: int, win_or_lose = None):
    wins_key = f"{home_team[0]}'{home_team[1]}"
    if wins_dict[wins_key]['wins'] > wins_dict[wins_key]['losses']:
        winners.append([home_team, game_id])
        losers.append(away_team)
        win_year = home_team[1]
        lose_year = away_team[1]
        if round_id == 'grand_finals':
            playoff_stats[home_key]['record']['best_round'] = round_id
            playoff_stats[away_key]['record']['best_round'] = round_id
        elif int(round_id[-1]) == len(edit_bracket) - 1:
            playoff_stats[home_key]['record']['best_round'] = f"won {round_id}"
            playoff_stats[away_key]['record']['best_round'] = f"loss {round_id}"
        else:
            playoff_stats[home_key]['record']['best_round'] = round_id
            playoff_stats[away_key]['record']['best_round'] = round_id
        if win_or_lose == None:
            game_string = f"The home team: {home_team[0]}'{home_team[1]} {home_team[2]}, with {wins_dict[wins_key]['wins']} wins and the away team: {away_team[0]}'{away_team[1]} {away_team[2]}, with {wins_dict[wins_key]['losses']} in {round_id}\n"
        else:
            game_string = f"The home team: {home_team[0]}'{home_team[1]} {home_team[2]}, with {wins_dict[wins_key]['wins']} wins and the away team: {away_team[0]}'{away_team[1]} {away_team[2]}, with {wins_dict[wins_key]['losses']} in {round_id} {win_or_lose}\n"
    else:
        winners.append([away_team, game_id])
        losers.append(home_team)
        win_year = away_team[1]
        lose_year = home_team[1]
        if round_id == 'grand_finals':
            playoff_stats[home_key]['record']['best_round'] = round_id
            playoff_stats[away_key]['record']['best_round'] = round_id
        elif int(round_id[-1]) == len(edit_bracket) - 1:
            playoff_stats[home_key]['record']['best_round'] = f"loss {round_id}"
            playoff_stats[away_key]['record']['best_round'] = f"won {round_id}"
        else:
            playoff_stats[home_key]['record']['best_round'] = round_id
            playoff_stats[away_key]['record']['best_round'] = round_id
        if win_or_lose == None:
            game_string = f"The away team: {away_team[0]}'{away_team[1]} {away_team[2]}, with {wins_dict[wins_key]['losses']} wins and the home team: {home_team[0]}'{home_team[1]} {home_team[2]}, with {wins_dict[wins_key]['wins']} in {round_id}\n"
        else:
            game_string = f"The away team: {away_team[0]}'{away_team[1]} {away_team[2]}, with {wins_dict[wins_key]['losses']} wins and the home team: {home_team[0]}'{home_team[1]} {home_team[2]}, with {wins_dict[wins_key]['wins']} in {round_id} {win_or_lose}\n"
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
        ['NOP', '2023-24', '0.0'],
        ['DEN', '2023-24', '0.0']
    ]
    bracket = bracket_generator(len(teams), teams)
    games = 300_000
    for _ in range(5):
        a, b = simulate_bracket(teams, bracket, games)
    # year = '2023-24'
    # league_type = '0.0'
    # team1 = 'DEN'
    # year1 = year
    # league_type1 = league_type
    # team2 = 'NOP'
    # year2 = year
    # league_type2 = league_type
    # games = 30000
    # home_team = [team1, year1, league_type1]
    # away_team = [team2, year2, league_type2]
    # win_dict = {'home_team': 0, 'away_team': 0}
    
    # # home_team1 = [team1, year1, league_type1]
    # # home_team2 = [team2, year2, league_type2]
    # # away_team1 = [team1, year1, league_type1]
    # # away_team2 = [team2, year2, league_type2]
    
    # # file_league_type = home_team1[2].replace('.', '')
    # # with open(f"data/pickle/{home_team1[1]} NBA Team Stats {file_league_type}.pickle", "rb") as pkl:
    # #     home1_team_pickle_stats = pickle.load(pkl)
    # # home1_team_off_bin_pct, home1_team_off_bins = bin_games(home_team1[0], home1_team_pickle_stats, 'offense')
    # # home1_team_def_bin_pct, home1_team_def_bins = bin_games(home_team1[0], home1_team_pickle_stats, 'defense')
    # # home1_team_league_bin_pct, home1_team_league_bins = bin_games('ALL', home1_team_pickle_stats, 'offense')

    # # file_league_type = away_team1[2].replace('.', '')
    # # with open(f"data/pickle/{away_team1[1]} NBA Team Stats {file_league_type}.pickle", "rb") as pkl:
    # #     away1_team_pickle_stats = pickle.load(pkl)
    # # away1_team_off_bin_pct, away1_team_off_bins = bin_games(away_team1[0], away1_team_pickle_stats, 'offense')
    # # away1_team_def_bin_pct, away1_team_def_bins = bin_games(away_team1[0], away1_team_pickle_stats, 'defense')
    # # away1_team_league_bin_pct, away1_team_league_bins = bin_games('ALL', away1_team_pickle_stats, 'offense')
    # # try:
    # #     assert home1_team_off_bin_pct == away1_team_off_bin_pct
    # #     assert home1_team_def_bin_pct == away1_team_def_bin_pct
    # #     assert home1_team_league_bin_pct == away1_team_league_bin_pct
    # #     assert home1_team_off_bins == away1_team_off_bins
    # #     assert home1_team_def_bins == away1_team_def_bins
    # #     assert home1_team_league_bins == away1_team_league_bins
    # # except:
    # #     print("ur wrong")
    

    # a = 0
    # if a == 1:
    #     inter_team = home_team
    #     home_team = away_team
    #     away_team = inter_team
    
    # # ---------------------------------------------------------
    # # making the hometeam hisotrgram data
    # file_league_type = home_team[2].replace('.', '')
    # with open(f"data/pickle/{home_team[1]} NBA Team Stats {file_league_type}.pickle", "rb") as pkl:
    #     home_team_pickle_stats = pickle.load(pkl)
    # home_team_off_bin_pct, home_team_off_bins = bin_games(home_team[0], home_team_pickle_stats, 'offense')
    # home_team_def_bin_pct, home_team_def_bins = bin_games(home_team[0], home_team_pickle_stats, 'defense')
    # home_team_league_bin_pct, home_team_league_bins = bin_games('ALL', home_team_pickle_stats, 'offense')

    # file_start = "den_histo.pickle"
    # with open(file_start, "wb") as j:
        # pickle.dump(home_team_pickle_stats, j)

    
 
