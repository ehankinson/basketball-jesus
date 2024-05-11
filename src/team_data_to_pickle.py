import csv
import time
import pickle
import numpy as np


index_map = {'offense': [9, 24, 25, 27, 28, 30, 31, 48, 49, 10, 16, 17, 13, 14],
           'defense': [9, 37, 38, 40, 41, 43, 44, 51, 52, 15, 11, 12, 18, 19]}

teams_dict = {
    'League': ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'],
    'Eastern': ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DET', 'IND', 'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS'],
    'Western': ['DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN', 'NOP', 'OKC', 'PHO', 'POR', 'SAC', 'SAS', 'UTA'],
    'Atlantic': ['BOS', 'BRK', 'NYK', 'PHI', 'TOR'],
    'Central': ['CHI', 'CLE', 'DET', 'IND', 'MIL'],
    'Southeast': ['ATL', 'CHO', 'MIA', 'ORL', 'WAS'],
    'Northwest': ['DEN', 'MIN', 'OKC', 'POR', 'UTA'],
    'Pacific': ['GSW', 'LAC', 'LAL', 'PHO', 'SAC'],
    'Southwest': ['DAL', 'HOU', 'MEM', 'NOP', 'SAS']
    }

nba_teams = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BRK": "Brooklyn Nets",
    "CHI": "Chicago Bulls",
    "CHO": "Charlotte Hornets",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards"
}

def game_score(pts: float, fgm: float, fga: float, fta: float, ftm: float, orb: float, drb: float, stl: float, ast: float, blk: float, pf: float, tov: float):
    return round(pts + 0.4 * fgm - 0.7 * fga - 0.4 * (fta- ftm) + 0.7 * orb + 0.3 * drb + stl + 0.7 *ast + 0.7 * blk -0.4 * pf - tov, 1)

def fantasy_points(pm3: float, pm2: float, ftm: float, orb: float, drb: float, ast: float, blk: float, stl: float, tov: float):
    return round(pm3 * 3 + pm2 * 2 + ftm + orb * 0.9 + drb * 0.3 + ast * 1.5 + blk * -2 + stl * -2 + tov * -1, 1)

def stat_per_game(stat: int, game_path: str, stats_dict: dict):
    return stats_dict[stat] / stats_dict[game_path]

def calculate_pct(above: int, below: int):
    if below == 0:
        return 0.000
    return round(above / below, 3)

def putting_stats_in_dict(path: dict, indexes: list, line: list):
    keys = ['MP', '2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
    for key, index in zip(keys, indexes):
        path[key] = int(line[index])
    advanced_stats(path)

def advanced_stats(path: dict):
    path['PTS'] = path['2PM'] * 2 + path['3PM'] * 3 + path['FTM']
    path['2P%'] = calculate_pct(path['2PM'], path['2PA'])
    path['3P%'] = calculate_pct(path['3PM'], path['3PA'])
    path['FT%'] = calculate_pct(path['FTM'], path['FTA'])
    path['TRB'] = path['ORB'] + path['DRB']
    path['FGM'] = path['2PM'] + path['3PM']
    path['FGA'] = path['2PA'] + path['3PA']
    path['FG%'] = calculate_pct(path['FGM'], path['FGA'])
    path['eFG%'] = calculate_pct((path['FGM'] + 0.5 * path['3PM']), path['FGA'])
    path['FP'] = fantasy_points(path['3PM'], path['2PM'], path['FTM'], path['ORB'], path['DRB'], path['AST'], path['BLK'], path['STL'], path['TOV'])
    path['GmSc'] = game_score(path['PTS'], path['FGM'], path['FGA'], path['FTA'], path['FTM'], path['ORB'], path['DRB'], path['STL'], path['AST'], path['BLK'], path['PF'], path['TOV'])
    path['STRS'] = round((path['PTS'] + path['FP'] + path['GmSc']) / 3, 3)
    
def process_team_data(reading_file: list, team_stats: dict):
    playoff_round = ['round1', 'conf_semi', 'conf_final', 'finals']
    playoff_teams = {}
    for line in reading_file:
        if line[1] == 'Team':
            continue
        team = line[1]
        if team not in team_stats:
            team_stats[team] = {}
        if len(team_stats[team]) > 82:
            a = 5
        game = len(team_stats[team]) + 1
        if game not in team_stats[team]:
            team_stats[team][game] = {}
        #offense
        team_stats[team][game]['offense'] = {}
        putting_stats_in_dict(team_stats[team][game]['offense'], index_map['offense'], line)
        #defense
        team_stats[team][game]['defense'] = {}
        putting_stats_in_dict(team_stats[team][game]['defense'], index_map['defense'], line)
        #opponant
        team_stats[team][game]['opp'] = line[7]
        if len(team_stats[team]) <= 82:
            team_stats[team][game]['game_type'] = 'regular_season'
        else:
            if team == 'CLE':
                a = 5
            if team not in playoff_teams:
                playoff_teams[team] = {'wins': 0, 'losses': 0, 'round_count': 0}
            if playoff_teams[team]['wins'] == 4 or playoff_teams[team]['losses'] == 4:
                playoff_teams[team]['round_count'] += 1
                playoff_teams[team]['wins'] = 0
                playoff_teams[team]['losses'] = 0
            team_stats[team][game]['game_type'] = {'playoffs': playoff_round[playoff_teams[team]['round_count']]}
            if line[8][0] == 'W':
                playoff_teams[team]['wins'] += 1
            else:
                playoff_teams[team]['losses'] += 1

def greater_than(off_stats: dict, def_stats: dict):
    stats = ['2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
    new_off = {}
    new_def = {}
    for stat in stats:
        if stat != 'PF' and stat[2] == 'A':
            if min(off_stats[stat], def_stats[stat]) >= new_off[stat.replace('A', 'M')]:
                new_off[stat] = min(off_stats[stat], def_stats[stat])
                new_def[stat] = max(off_stats[stat], def_stats[stat])
            else:
                new_off[stat] = max(off_stats[stat], def_stats[stat])
                new_def[stat] = min(off_stats[stat], def_stats[stat])
        else:
            new_off[stat] = max(off_stats[stat], def_stats[stat])
            new_def[stat] = min(off_stats[stat], def_stats[stat])
    advanced_stats(new_off)
    advanced_stats(new_def)
    return new_off, new_def

def lower_than(off_stats: dict, def_stats: dict):
    stats = ['2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
    new_off = {}
    new_def = {}
    for stat in stats:
        if stat != 'PF' and stat[2] == 'A':
            if min(off_stats[stat], def_stats[stat]) >= new_def[stat.replace('A', 'M')]:
                new_off[stat] = max(off_stats[stat], def_stats[stat])
                new_def[stat] = min(off_stats[stat], def_stats[stat])
            else:
                new_off[stat] = min(off_stats[stat], def_stats[stat])
                new_def[stat] = max(off_stats[stat], def_stats[stat])
        else:
            new_off[stat] = min(off_stats[stat], def_stats[stat])
            new_def[stat] = max(off_stats[stat], def_stats[stat])
    advanced_stats(new_off)
    advanced_stats(new_def)
    return new_off, new_def

def make_00_pickle(year: int):
    with open(f"{year}-{int(str(year)[2:]) + 1} NBA Team Stats.pickle", "rb") as pk:
        league_stats = pickle.load(pk)
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 00.pickle", "wb") as pk:
        pickle.dump(league_stats, pk)

def make_01_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 00.pickle", "rb") as f:
        league_data = pickle.load(f)
    if year != 2020:
        end_game = 82
        start_game = 1
    else:
        end_game = 72
        start_game = 1
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Standings.pickle", "rb") as f:
        standings = pickle.load(f)
    eastern_ranks = standings['East']
    western_ranks = standings['West']
    new_league_data = {}
    for team in league_data:
        if team in eastern_ranks:
            teams = eastern_ranks
        else:
            teams = western_ranks
        seed = (15 - teams.index(team))
        new_team = teams[seed - 1]
        new_league_data[team] = {}
        if year == '2020-21':
            start_game = 73
            end_game = 100
        else:
            start_game = 83
            end_game = 110
        if start_game not in league_data[new_team]:
            for game in range(1, start_game):
                new_league_data[team][game] = {'offense': None, 'defense': None, 'opp': None}
                new_league_data[team][game]['offense'] = league_data[team][game]['defense']
                new_league_data[team][game]['defense'] = league_data[team][game]['offense']
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
                new_league_data[team][game]['game_type'] = league_data[team][game]['game_type']
        else:
            for game in range(1, end_game):
                if game not in league_data[new_team]:
                    break
                new_league_data[team][game] = {'offense': None, 'defense': None, 'opp': None}
                if game >= start_game:
                    new_league_data[team][game]['offense'] = league_data[new_team][game]['offense']
                    new_league_data[team][game]['defense'] = league_data[new_team][game]['defense']
                    opp = league_data[new_team][game]['opp']
                    if opp not in teams:
                        if opp in western_ranks:
                            teams = western_ranks
                        else:
                            teams = eastern_ranks
                    seed = (15 - teams.index(opp))
                    new_opp = teams[seed - 1]
                    new_league_data[team][game]['opp'] = new_opp
                    new_league_data[team][game]['game_type'] = league_data[new_team][game]['game_type']
                else:
                    new_league_data[team][game]['offense'] = league_data[team][game]['defense']
                    new_league_data[team][game]['defense'] = league_data[team][game]['offense']
                    new_league_data[team][game]['opp'] = league_data[team][game]['opp']
                    new_league_data[team][game]['game_type'] = league_data[team][game]['game_type']
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 01.pickle", "wb") as pk:
        pickle.dump(new_league_data, pk)

def make_10_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 00.pickle", "rb") as f:
        league_data = pickle.load(f)
    new_league_data = {}
    for team in league_data:
        new_league_data[team] = {}
        for game in league_data[team]:
            new_league_data[team][game] = {'offense': None, 'defense': None}
            if league_data[team][game]['offense']['PTS'] > league_data[team][game]['defense']['PTS']:
                new_off, new_def = greater_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
            else:
                new_off, new_def = lower_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
            new_league_data[team][game]['opp'] = league_data[team][game]['opp']
            new_league_data[team][game]['game_type'] = league_data[team][game]['game_type']
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 10.pickle", "wb") as pk:
        pickle.dump(new_league_data, pk)

def make_11_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 01.pickle", "rb") as f:
        league_data = pickle.load(f)
    new_league_data = {}
    for team in league_data:
        new_league_data[team] = {}
        for game in league_data[team]:
            new_league_data[team][game] = {'offense': None, 'defense': None}
            if league_data[team][game]['offense']['PTS'] > league_data[team][game]['defense']['PTS']:
                new_off, new_def = greater_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
            else:
                new_off, new_def = lower_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
            new_league_data[team][game]['opp'] = league_data[team][game]['opp']
            new_league_data[team][game]['game_type'] = league_data[team][game]['game_type']
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 11.pickle", "wb") as pk:
        pickle.dump(new_league_data, pk)

def make_20_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 10.pickle", "rb") as f:
        league_data = pickle.load(f)
    ranked_teams = srs_ranking(teams_dict['League'], league_data, 82, 1)
    ranked_teams = [team[0] for team in ranked_teams]
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Standings.pickle", "rb") as f:
        standings = pickle.load(f)
    east_rank = standings['East']
    west_rank = standings['West']
    new_league_data = {}
    if year == 2020:
        end_game = 72
    else:
        end_game = 82
    for team in league_data:
        new_league_data[team] = {}
        tm_index = ranked_teams.index(team)
        for game in range(1, end_game + 1):
            opp_index = ranked_teams.index(league_data[team][game]['opp'])
            new_league_data[team][game] = {'offense': None, 'defense': None}
            if tm_index < opp_index:
                new_off, new_def = greater_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
            else:
                new_off, new_def = lower_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
    new_east_rank = rank_teams(teams_dict['Eastern'], 'conf', new_league_data, end_game, 1)
    new_west_rank = rank_teams(teams_dict['Western'], 'conf', new_league_data, end_game, 1)
    playoff_games = {}
    for team in league_data:
        if len(league_data[team]) < end_game + 1:
            continue
        if team in east_rank:
            team_conf = 'East'
            conf_to_comapare = east_rank
        else:
            team_conf = 'West'
            conf_to_comapare = west_rank
        did_conf_count = False
        did_final_count = False
        game_count = 1
        for game in range(end_game + 1, end_game + 28):
            if game not in league_data[team]:
                break
            if league_data[team][game]['game_type']['playoffs'] == 'round1':
                continue
            if team_conf not in playoff_games:
                playoff_games[team_conf] = {}
            if league_data[team][game]['game_type']['playoffs'] == 'conf_semi':
                team_seed = conf_to_comapare.index(team)
                opp_seed = conf_to_comapare.index(league_data[team][game]['opp'])
                if team_seed == 3 or opp_seed == 3 or team_seed == 4 or opp_seed == 4:
                    if 'Up Semi' not in playoff_games[team_conf]:
                        playoff_games[team_conf]['Up Semi'] = {}
                    if game_count not in playoff_games[team_conf]['Up Semi']:
                        playoff_games[team_conf]['Up Semi'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [conf_to_comapare[0], conf_to_comapare[3]]}
                else:
                    if 'Down Semi' not in playoff_games[team_conf]:
                        playoff_games[team_conf]['Down Semi'] = {}
                    if game_count not in playoff_games[team_conf]['Down Semi']:
                        playoff_games[team_conf]['Down Semi'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [conf_to_comapare[1], conf_to_comapare[2]]}
            elif league_data[team][game]['game_type']['playoffs'] == 'conf_final':
                if not did_conf_count:
                    game_count = 1
                    did_conf_count = True
                if 'conf_final' not in playoff_games[team_conf]:
                    playoff_games[team_conf]['conf_final'] = {}
                if game_count not in playoff_games[team_conf]['conf_final']:
                    playoff_games[team_conf]['conf_final'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [conf_to_comapare[0], conf_to_comapare[1]]}
            else:
                if not did_final_count:
                    game_count = 1
                    did_final_count = True
                if 'finals' not in playoff_games[team_conf]:
                    playoff_games[team_conf]['finals'] = {}
                if game_count not in playoff_games[team_conf]['finals']:
                    playoff_games[team_conf]['finals'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [new_east_rank[0], new_west_rank[0]]}   
            game_count += 1
    playoff_games_to_add = {
        0: ['round1', 'Up Semi', 'conf_final', 'finals'],
        1: ['round1', 'Down Semi', 'conf_final'],
        2: ['round1', 'Down Semi'],
        3: ['round1', 'Up Semi'],
        4: ['round1'],
        5: ['round1'],
        6: ['round1'],
        7: ['round1']
    }
    conferences = [east_rank, west_rank]
    for conf_id, conf in enumerate(conferences):
        if conf_id == 0:
            team_conf = 'East'
        else:
            team_conf = 'West'
        for team_index in range(8):
            team = conf[team_index]
            games_to_add = playoff_games_to_add[team_index]
            idx = 0
            previous_round = None
            for game in range(end_game + 1, end_game + 28):
                if game not in league_data[team]:
                    if len(games_to_add) > 1 and idx != len(games_to_add):
                        if games_to_add[idx] == 'Up Semi' or games_to_add[idx] == 'Down Semi':
                            add_round = 'conf_semi'
                        else:
                            add_round = games_to_add[idx]
                        for games in playoff_games[team_conf][games_to_add[idx]]:
                            if playoff_games[team_conf][games_to_add[idx]][games]['offense']['STRS'] > playoff_games[team_conf][games_to_add[idx]][games]['defense']['STRS']:
                                league_data[team][game + games - 1] = {
                                    'offense': playoff_games[team_conf][games_to_add[idx]][games]['offense'],
                                    'defense': playoff_games[team_conf][games_to_add[idx]][games]['defense'],
                                    'opp': playoff_games[team_conf][games_to_add[idx]][games]['teams'][0] if team == playoff_games[team_conf][games_to_add[idx]][games]['teams'][1] else playoff_games[team_conf][games_to_add[idx]][games]['teams'][1],
                                    'game_type': {'playoffs': add_round}
                                }
                            else:
                                league_data[team][game + games - 1] = {
                                    'offense': playoff_games[team_conf][games_to_add[idx]][games]['defense'],
                                    'defense': playoff_games[team_conf][games_to_add[idx]][games]['offense'],
                                    'opp': playoff_games[team_conf][games_to_add[idx]][games]['teams'][0] if team == playoff_games[team_conf][games_to_add[idx]][games]['teams'][1] else playoff_games[team_conf][games_to_add[idx]][games]['teams'][1],
                                    'game_type': {'playoffs': add_round}
                                }
                    else:
                        break
                elif league_data[team][game]['game_type']['playoffs'] not in games_to_add:
                    if league_data[team][game]['game_type']['playoffs'] == 'conf_semi' and len(games_to_add) >= 2:
                        if league_data[team][game]['game_type']['playoffs'] != previous_round:
                            previous_round = league_data[team][game]['game_type']['playoffs']
                            idx += 1
                    else:
                        del league_data[team][game]
                if game in league_data[team] and league_data[team][game]['game_type']['playoffs'] != previous_round:
                    previous_round = league_data[team][game]['game_type']['playoffs']
                    idx += 1
                if game in league_data[team] and league_data[team][game]['game_type']['playoffs'] == 'round1':
                    continue
                if game in league_data[team]:
                    opp = league_data[team][game]['opp']
                    expected_opps = playoff_games[team_conf][games_to_add[idx - 1]][1]['teams']
                    if opp not in expected_opps:
                        if team == expected_opps[0]:
                            league_data[team][game]['opp'] = expected_opps[1]
                        else:
                            league_data[team][game]['opp'] = expected_opps[0]
    teams = teams_dict['League']
    for team in teams:
        if team in east_rank:
            compare = east_rank
            new_compare = new_east_rank
        else:
            compare = west_rank
            new_compare = new_west_rank
        if len(league_data[team]) < end_game:
            continue
        game_dict = {
            'round1': {},
            'conf_semi': {},
            'conf_final': {},
            'finals': {},
        }
        for game in range(end_game + 1, end_game + 28):
            if game not in league_data[team]:
                break
            diff = max(league_data[team][game]['offense']['STRS'], league_data[team][game]['defense']['STRS']) - min(league_data[team][game]['offense']['STRS'], league_data[team][game]['defense']['STRS'])
            game_dict[league_data[team][game]['game_type']['playoffs']][diff] = game
        team_index = compare.index(team)
        new_team = new_compare[team_index]
        sorted_game_dict = {
            'round1': None,
            'conf_semi': None,
            'conf_final': None,
            'finals': None,
        }
        for key in game_dict:
            if len(game_dict[key].keys()) == 0:
                break
            round_list = list(game_dict[key].keys())
            round_list = sorted(round_list, reverse=True)
            sorted_game_dict[key] = round_list
        for key in sorted_game_dict:
            if sorted_game_dict[key] == None:
                break
            count = 0
            while count < 4:
                game_to_add = game_dict[key][sorted_game_dict[key][count]]
                game = league_data[team][game_to_add]
                team_league_idx = ranked_teams.index(team)
                opp_league_idx = ranked_teams.index(league_data[team][game_to_add]['opp'])
                if team_league_idx < opp_league_idx:
                    # give better
                    if league_data[team][game_to_add]['offense']['STRS'] > league_data[team][game_to_add]['defense']['STRS']:
                        offense = league_data[team][game_to_add]['offense']
                        defense = league_data[team][game_to_add]['defense']
                    else:
                        offense = league_data[team][game_to_add]['defense']
                        defense = league_data[team][game_to_add]['offense']
                else:
                    #give worse
                    if league_data[team][game_to_add]['offense']['STRS'] > league_data[team][game_to_add]['defense']['STRS']:
                        offense = league_data[team][game_to_add]['defense']
                        defense = league_data[team][game_to_add]['offense']
                    else:
                        offense = league_data[team][game_to_add]['offense']
                        defense = league_data[team][game_to_add]['defense']
                if league_data[team][game_to_add]['opp'] not in compare:
                    if team in teams_dict['Eastern']:
                        new_opp = new_west_rank[0]
                    else:
                        new_opp = new_east_rank[0]
                else:
                    new_opp = new_compare[compare.index(league_data[team][game_to_add]['opp'])]
                new_league_data[new_team][len(new_league_data[new_team]) + 1] = {
                    'offense': offense,
                    'defense': defense,
                    'opp': new_opp,
                    'game_type': league_data[team][game_to_add]['game_type']
                }
                count += 1            
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 20.pickle", "wb") as pk:
        pickle.dump(new_league_data, pk)

def make_21_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 11.pickle", "rb") as f:
        league_data = pickle.load(f)
    if year == 2020:
        end_game = 72
    else:
        end_game = 82
    ranked_teams = srs_ranking(teams_dict['League'], league_data, end_game, 1)
    ranked_teams = [team[0] for team in ranked_teams]
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Standings.pickle", "rb") as f:
        standings = pickle.load(f)
    east_rank = standings['East'][::-1]
    west_rank = standings['West'][::-1]
    new_league_data = {}
    for team in league_data:
        new_league_data[team] = {}
        tm_index = ranked_teams.index(team)
        for game in range(1, end_game + 1):
            opp_index = ranked_teams.index(league_data[team][game]['opp'])
            new_league_data[team][game] = {'offense': None, 'defense': None}
            if tm_index < opp_index:
                new_off, new_def = greater_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
            else:
                new_off, new_def = lower_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
    new_east_rank = rank_teams(teams_dict['Eastern'], 'conf', new_league_data, end_game, 1)
    new_west_rank = rank_teams(teams_dict['Western'], 'conf', new_league_data, end_game, 1)
    playoff_games = {}
    for team in league_data:
        if team == 'NYK':
            a = 5
        if len(league_data[team]) < end_game + 1:
            continue
        if team in east_rank:
            team_conf = 'East'
            conf_to_comapare = east_rank
        else:
            team_conf = 'West'
            conf_to_comapare = west_rank
        did_conf_count = False
        did_final_count = False
        game_count = 1
        for game in range(end_game + 1, end_game + 28):
            if game not in league_data[team]:
                break
            if league_data[team][game]['game_type']['playoffs'] == 'round1':
                continue
            if team_conf not in playoff_games:
                playoff_games[team_conf] = {}
            if league_data[team][game]['game_type']['playoffs'] == 'conf_semi':
                team_seed = conf_to_comapare.index(team)
                opp_seed = conf_to_comapare.index(league_data[team][game]['opp'])
                if team_seed == 3 or opp_seed == 3 or team_seed == 4 or opp_seed == 4:
                    if 'Up Semi' not in playoff_games[team_conf]:
                        playoff_games[team_conf]['Up Semi'] = {}
                    if game_count not in playoff_games[team_conf]['Up Semi']:
                        playoff_games[team_conf]['Up Semi'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [conf_to_comapare[0], conf_to_comapare[3]]}
                else:
                    if 'Down Semi' not in playoff_games[team_conf]:
                        playoff_games[team_conf]['Down Semi'] = {}
                    if game_count not in playoff_games[team_conf]['Down Semi']:
                        playoff_games[team_conf]['Down Semi'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [conf_to_comapare[1], conf_to_comapare[2]]}
            elif league_data[team][game]['game_type']['playoffs'] == 'conf_final':
                if not did_conf_count:
                    game_count = 1
                    did_conf_count = True
                if 'conf_final' not in playoff_games[team_conf]:
                    playoff_games[team_conf]['conf_final'] = {}
                if game_count not in playoff_games[team_conf]['conf_final']:
                    playoff_games[team_conf]['conf_final'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [conf_to_comapare[0], conf_to_comapare[1]]}
            else:
                if not did_final_count:
                    game_count = 1
                    did_final_count = True
                if 'finals' not in playoff_games[team_conf]:
                    playoff_games[team_conf]['finals'] = {}
                if game_count not in playoff_games[team_conf]['finals']:
                    playoff_games[team_conf]['finals'][game_count] = {'offense': league_data[team][game]['offense'], 'defense': league_data[team][game]['defense'], 'teams': [new_east_rank[0], new_west_rank[0]]}   
            game_count += 1
    playoff_games_to_add = {
        0: ['round1', 'Up Semi', 'conf_final', 'finals'],
        1: ['round1', 'Down Semi', 'conf_final'],
        2: ['round1', 'Down Semi'],
        3: ['round1', 'Up Semi'],
        4: ['round1'],
        5: ['round1'],
        6: ['round1'],
        7: ['round1']
    }
    conferences = [east_rank, west_rank]
    for conf_id, conf in enumerate(conferences):
        if conf_id == 0:
            team_conf = 'East'
        else:
            team_conf = 'West'
        for team_index in range(8):
            team = conf[team_index]
            games_to_add = playoff_games_to_add[team_index]
            idx = 0
            previous_round = None
            for game in range(end_game + 1, end_game + 28):
                if game not in league_data[team]:
                    if len(games_to_add) > 1 and idx != len(games_to_add):
                        if games_to_add[idx] == 'Up Semi' or games_to_add[idx] == 'Down Semi':
                            add_round = 'conf_semi'
                        else:
                            add_round = games_to_add[idx]
                        for games in playoff_games[team_conf][games_to_add[idx]]:
                            if playoff_games[team_conf][games_to_add[idx]][games]['offense']['STRS'] > playoff_games[team_conf][games_to_add[idx]][games]['defense']['STRS']:
                                league_data[team][game + games - 1] = {
                                    'offense': playoff_games[team_conf][games_to_add[idx]][games]['offense'],
                                    'defense': playoff_games[team_conf][games_to_add[idx]][games]['defense'],
                                    'opp': playoff_games[team_conf][games_to_add[idx]][games]['teams'][0] if team == playoff_games[team_conf][games_to_add[idx]][games]['teams'][1] else playoff_games[team_conf][games_to_add[idx]][games]['teams'][1],
                                    'game_type': {'playoffs': add_round}
                                }
                            else:
                                league_data[team][game + games - 1] = {
                                    'offense': playoff_games[team_conf][games_to_add[idx]][games]['defense'],
                                    'defense': playoff_games[team_conf][games_to_add[idx]][games]['offense'],
                                    'opp': playoff_games[team_conf][games_to_add[idx]][games]['teams'][0] if team == playoff_games[team_conf][games_to_add[idx]][games]['teams'][1] else playoff_games[team_conf][games_to_add[idx]][games]['teams'][1],
                                    'game_type': {'playoffs': add_round}
                                }
                    else:
                        break
                elif league_data[team][game]['game_type']['playoffs'] not in games_to_add:
                    if league_data[team][game]['game_type']['playoffs'] == 'conf_semi' and len(games_to_add) >= 2:
                        if league_data[team][game]['game_type']['playoffs'] != previous_round:
                            previous_round = league_data[team][game]['game_type']['playoffs']
                            idx += 1
                    else:
                        del league_data[team][game]
                if game in league_data[team] and league_data[team][game]['game_type']['playoffs'] != previous_round:
                    previous_round = league_data[team][game]['game_type']['playoffs']
                    idx += 1
                if game in league_data[team] and league_data[team][game]['game_type']['playoffs'] == 'round1':
                    continue
                if game in league_data[team]:
                    opp = league_data[team][game]['opp']
                    expected_opps = playoff_games[team_conf][games_to_add[idx - 1]][1]['teams']
                    if opp not in expected_opps:
                        if team == expected_opps[0]:
                            league_data[team][game]['opp'] = expected_opps[1]
                        else:
                            league_data[team][game]['opp'] = expected_opps[0]
    teams = teams_dict['League']
    for team in teams:
        if team in east_rank:
            compare = east_rank
            new_compare = new_east_rank
        else:
            compare = west_rank
            new_compare = new_west_rank
        if len(league_data[team]) < 83:
            continue
        game_dict = {
            'round1': {},
            'conf_semi': {},
            'conf_final': {},
            'finals': {},
        }
        for game in range(end_game + 1, end_game + 28):
            if game not in league_data[team]:
                break
            diff = max(league_data[team][game]['offense']['STRS'], league_data[team][game]['defense']['STRS']) - min(league_data[team][game]['offense']['STRS'], league_data[team][game]['defense']['STRS'])
            game_dict[league_data[team][game]['game_type']['playoffs']][diff] = game
        team_index = compare.index(team)
        new_team = new_compare[team_index]
        sorted_game_dict = {
            'round1': None,
            'conf_semi': None,
            'conf_final': None,
            'finals': None,
        }
        for key in game_dict:
            if len(game_dict[key].keys()) == 0:
                break
            round_list = list(game_dict[key].keys())
            round_list = sorted(round_list, reverse=True)
            sorted_game_dict[key] = round_list
        for key in sorted_game_dict:
            if sorted_game_dict[key] == None:
                break
            count = 0
            while count < 4:
                game_to_add = game_dict[key][sorted_game_dict[key][count]]
                game = league_data[team][game_to_add]
                team_league_idx = ranked_teams.index(team)
                opp_league_idx = ranked_teams.index(league_data[team][game_to_add]['opp'])
                if team_league_idx < opp_league_idx:
                    # give better
                    if league_data[team][game_to_add]['offense']['STRS'] > league_data[team][game_to_add]['defense']['STRS']:
                        offense = league_data[team][game_to_add]['offense']
                        defense = league_data[team][game_to_add]['defense']
                    else:
                        offense = league_data[team][game_to_add]['defense']
                        defense = league_data[team][game_to_add]['offense']
                else:
                    #give worse
                    if league_data[team][game_to_add]['offense']['STRS'] > league_data[team][game_to_add]['defense']['STRS']:
                        offense = league_data[team][game_to_add]['defense']
                        defense = league_data[team][game_to_add]['offense']
                    else:
                        offense = league_data[team][game_to_add]['offense']
                        defense = league_data[team][game_to_add]['defense']
                if league_data[team][game_to_add]['opp'] not in compare:
                    if team in teams_dict['Eastern']:
                        new_opp = new_west_rank[0]
                    else:
                        new_opp = new_east_rank[0]
                else:
                    new_opp = new_compare[compare.index(league_data[team][game_to_add]['opp'])]
                new_league_data[new_team][len(new_league_data[new_team]) + 1] = {
                    'offense': offense,
                    'defense': defense,
                    'opp': new_opp,
                    'game_type': league_data[team][game_to_add]['game_type']
                }
                count += 1            
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 21.pickle", "wb") as pk:
        pickle.dump(new_league_data, pk)

def srs_ranking(teams: list, league_data: dict, end_game: int, start_game: int):
    start_time = time.time()
    ranked_teams = []
    for team in teams:
        record = {'wins':0, 'losses': 0, 'pf': 0, 'pa': 0}
        for game in range(start_game, end_game + 1):
            if league_data[team][game]['offense']['PTS'] > league_data[team][game]['defense']['PTS']:
                record['wins'] += 1
            else:
                record['losses'] += 1
            record['pf'] += league_data[team][game]['offense']['PTS']
            record['pa'] += league_data[team][game]['defense']['PTS']
        record['gp'] = record['wins'] + record['losses']
        record['win%'] = record['wins'] / record['gp']
        record['diff'] = round((record['pf'] - record['pa']) / record['gp'], 3)
        ranked_teams.append([team, record['gp'], record['wins'], record['losses'], round(record['win%'], 3), round(record['pf'] / record['gp'], 1), round(record['pa'] / record['gp'], 1), record['diff']])
    sorted_teams = sorted(ranked_teams, key=lambda x: x[4], reverse=True)
    old_srs_dict = {}
    for team in sorted_teams:
        old_srs_dict[team[0]] = {'og': team[7], 'strs': team[7], 'total': 0, 'gp': 0, 'new_pg': 0}
    for _ in range(3500):
        for team in old_srs_dict:
            old_srs_dict[team]['total'] = np.sum([old_srs_dict[league_data[team][game]['opp']]['strs'] for game in range(start_game, end_game + 1)])
            old_srs_dict[team]['gp'] = end_game - start_game + 1
        for team in old_srs_dict:
            old_srs_dict[team]['new_pg'] = old_srs_dict[team]['total'] / old_srs_dict[team]['gp']
            old_srs_dict[team]['strs'] = old_srs_dict[team]['og'] + old_srs_dict[team]['new_pg']
            old_srs_dict[team]['total'] = 0
            old_srs_dict[team]['gp'] = 0
    for team in sorted_teams:
        team[7] = old_srs_dict[team[0]]['strs']
    sorted_teams = sorted(ranked_teams, key=custom_sort, reverse=True)
    end_time = time.time()
    print(f"Total time it took was {end_time - start_time} seconds")
    return sorted_teams

def custom_sort(item):
    return (item[4], item[7])

def rank_teams(teams: list, rank_type: str, league_data: dict, end_game: int, start_game: int):
    ranked_teams = []
    for team in teams:
        record = {'wins':0, 'losses': 0, 'pf': 0, 'pa': 0}
        for game in range(start_game, end_game + 1):
            if league_data[team][game]['offense']['PTS'] > league_data[team][game]['defense']['PTS']:
                record['wins'] += 1
            else:
                record['losses'] += 1
            record['pf'] += league_data[team][game]['offense']['PTS']
            record['pa'] += league_data[team][game]['defense']['PTS']
        record['gp'] = record['wins'] + record['losses']
        record['win%'] = record['wins'] / record['gp']
        record['diff'] = round((record['pf'] - record['pa']) / record['gp'], 3)
        ranked_teams.append([team, record['gp'], record['wins'], record['losses'], round(record['win%'], 3), round(record['pf'] / record['gp'], 1), round(record['pa'] / record['gp'], 1), record['diff']])
    sorted_teams = sorted(ranked_teams, key=lambda x: x[4], reverse=True)
    # ranked_teams = ranking_teams(sorted_teams, rank_type, league_data, end_game, start_game)
    return_list = [team[0] for team in sorted_teams]
    return return_list

def ranking_teams(teams: list, rank_type: str, league_data: dict, end_game: int, start_game = 1) -> list:
    ranked_list = []
    if rank_type == 'Div':
        max_tm = 2
    elif rank_type == 'Conf':
        max_tm = 12
    else:
        max_tm = 27
    for count, team in enumerate(teams):
        if count + 1 == len(teams):
            ranked_list.append(team)
            break
        compare_team = teams[count + 1]
        if team[4] > compare_team[4]:
            ranked_list.append(team)
            continue
        else:
            if count <= max_tm and team[4] == teams[count + 2][4]:
                multi_teams = []
                for seed in range(count, len(teams) + 1):
                    if teams[seed][4] == team[4]:
                        multi_teams.append(teams[seed])
                    else:
                        break
                multi_div_winners = multi_div_winner(multi_teams, league_data, end_game, start_game, teams)
                if len(multi_div_winners) == 2:
                    rank_two_teams(multi_div_winners[0], multi_div_winners[1], league_data, end_game, start_game, ranked_list, teams, count)
                elif multi_div_winners != 'continue':
                    ranked_list.append(multi_div_winners[0])
                    for idx in range(len(multi_div_winners)):
                        teams[count + idx] = multi_div_winners[idx]
            else:
                rank_two_teams(team, compare_team, league_data, end_game, start_game, ranked_list, teams, count)            
    return ranked_list

def rank_two_teams(team: list, compare_team: list, league_data: dict, end_game: int, start_game: int, ranked_list: list, teams: list, count: int):
    # checking for 2 teams
    team1 = team[0]
    team2 = compare_team[0]
    h2h = head2head(league_data[team[0]], compare_team[0], end_game, start_game)
    if h2h == 0:
        ranked_list.append(team)
    elif h2h == 1:
        move = compare_team
        ranked_list.append(teams[count + 1])
        teams[count + 1] = team
        teams[count] = move
    else:
        div_winner = check_if_div_winner(team1, team2, league_data, end_game, start_game, teams)
        if div_winner == 0:
            ranked_list.append(team)
        elif div_winner == 1:
            move = compare_team
            ranked_list.append(teams[count + 1])
            teams[count + 1] = team
            teams[count] = move
        else:
            if div_winner[0] == div_winner[1]:
                #check division record
                div_pct = div_win_pct(team1, team2, div_winner[0], league_data, end_game, start_game)
                if div_pct == 0:
                    ranked_list.append(team)
                    return
                elif div_pct == 1:
                    ranked_list.append(teams[count + 1])
                    teams[count + 1] = team
                    return
            conf_check = conf_win_pct(team1, team2, league_data, end_game, start_game)
            if conf_check == 0:
                ranked_list.append(team)
            elif conf_check == 1:
                ranked_list.append(teams[count + 1])
                teams[count + 1] = team
            else:
                conf_play_check = conf_playoff_win_pct(team1, team2, teams, league_data, end_game, start_game)
                if conf_play_check == 0:
                    ranked_list.append(team)
                elif conf_play_check == 1:
                    ranked_list.append(teams[count + 1])
                    teams[count + 1] = team
                else:
                    non_conf_play_check = conf_playoff_win_pct(team1, team2, league_data, end_game, start_game)
                    if non_conf_play_check == 0:
                        ranked_list.append(team)
                    elif non_conf_play_check == 1:
                        ranked_list.append(teams[count + 1])
                        teams[count + 1] = team
                    else:
                        net_points = net_point_diff(team1, team2, league_data, end_game, start_game)
                        if net_points == 0:
                            ranked_list.append(team)
                        else:
                            ranked_list.append(teams[count + 1])
                            teams[count + 1] = team  

def net_point_diff(team1: str, team2: str, league_data: str, end_game: int, start_game: int):
    team1_points = [0, 0]
    team2_points = [0, 0]
    for game in range(start_game, end_game + 1):
        team1_points[0] += league_data[team1][game]['offense']['PTS']
        team1_points[1] += league_data[team1][game]['defense']['PTS']
        team2_points[0] += league_data[team2][game]['offense']['PTS']
        team2_points[1] += league_data[team2][game]['defense']['PTS']
    team1_points.append(team1_points[0] - team1_points[1])
    team1_points.append(team1_points[0] - team1_points[1])
    if team1_points[2] > team1_points[2]:
        return 0
    elif team1_points[2] < team1_points[2]:
        return 1

def non_conf_playoff_win_pct(team1: str, team2: str, league_data: str, end_game: int, start_game: int):
    team1_record = [0, 0]
    team2_record = [0, 0]
    if team1 in teams_dict['Eastern']:
        teams = teams_dict['Western']
    else:
        teams = teams_dict['Eastern']
    if year >= 2020:
        min_rank = 10
    else:
        min_rank = 8
    conf_rank = ranking_teams(teams, league_data, 82, 1)
    for game in range(start_game, end_game + 1):
        #check for team 1
        if conf_rank.index(league_data[team1][game]['opp']) >= min_rank and league_data[team1][game]['opp'] in conf_rank:
            if league_data[team1][game]['offense']['PTS'] > league_data[team1][game]['defense']['PTS']:
                team1_record[0] += 1
            else:
                team1_record[1] += 1
        #check for team 2
        if conf_rank.index(league_data[team1][game]['opp']) >= min_rank and league_data[team1][game]['opp'] in conf_rank:
            if league_data[team2][game]['offense']['PTS'] > league_data[team2][game]['defense']['PTS']:
                team2_record[0] += 1
            else:
                team2_record[1] += 1
    team1_record.append(team1_record[0] / (team1_record[0] + team1_record[1]))
    team2_record.append(team2_record[0] / (team2_record[0] + team2_record[1]))
    if team1_record[2] > team2_record[2]:
        return 0
    elif team1_record[2] < team2_record[2]:
        return 1
    else:
        'continue'

def conf_playoff_win_pct(team1: str, team2: str, teams: list, league_data: str, end_game: int, start_game: int):
    team1_record = [0, 0]
    team2_record = [0, 0]
    if team1 in teams_dict['Eastern']:
        conf_teams = teams_dict['Eastern']
    else:
        conf_teams = teams_dict['Western']
    if year >= 2020:
        min_rank = 10
    else:
        min_rank = 8
    conf_rank = [team[0] for team in teams]
    for game in range(start_game, end_game + 1):
        #check for team 1
        if league_data[team1][game]['opp'] in conf_rank and conf_rank.index(league_data[team1][game]['opp']) >= min_rank:
            if league_data[team1][game]['offense']['PTS'] > league_data[team1][game]['defense']['PTS']:
                team1_record[0] += 1
            else:
                team1_record[1] += 1
        #check for team 2
        if league_data[team2][game]['opp'] in conf_rank and conf_rank.index(league_data[team2][game]['opp']) >= min_rank :
            if league_data[team2][game]['offense']['PTS'] > league_data[team2][game]['defense']['PTS']:
                team2_record[0] += 1
            else:
                team2_record[1] += 1
    team1_record.append(team1_record[0] / (team1_record[0] + team1_record[1]))
    team2_record.append(team2_record[0] / (team2_record[0] + team2_record[1]))
    if team1_record[2] > team2_record[2]:
        return 0
    elif team1_record[2] < team2_record[2]:
        return 1
    else:
        'continue'

def conf_win_pct(team1: str, team2: str, league_data: dict, end_game: int, start_game: int):
    team1_record = [0, 0]
    team2_record = [0, 0]
    if team1 in teams_dict['Eastern']:
        teams = teams_dict['Eastern']
    else:
        teams = teams_dict['Western']
    for game in range(start_game, end_game + 1):
        # checking for team1
        if league_data[team1][game]['opp'] in teams:
            if league_data[team1][game]['offense']['PTS'] > league_data[team1][game]['defense']['PTS']:
                team1_record[0] += 1
            else:
                team1_record[1] += 1
        #checking for team2
        if league_data[team2][game]['opp'] in teams:
            if league_data[team2][game]['offense']['PTS'] > league_data[team2][game]['defense']['PTS']:
                team2_record[0] += 1
            else:
                team2_record[1] += 1
    team1_record.append(team1_record[0] / (team1_record[0] + team1_record[1]))
    team2_record.append(team2_record[0] / (team2_record[0] + team2_record[1]))
    if team1_record[2] > team2_record[2]:
        return 0
    elif team1_record[2] < team2_record[2]:
        return 1
    else:
        'continue'

def div_win_pct(team1: str, team2: str, division: str, league_data: dict, end_game: int, start_game: int):
    team1_record = [0, 0]
    team2_record = [0, 0]
    teams = teams_dict[division]
    for game in range(start_game, end_game + 1):
        # checking for team1
        if league_data[team1][game]['opp'] in teams:
            if league_data[team1][game]['offense']['PTS'] > league_data[team1][game]['defense']['PTS']:
                team1_record[0] += 1
            else:
                team1_record[1] += 1
        #checking for team2
        if league_data[team2][game]['opp'] in teams:
            if league_data[team2][game]['offense']['PTS'] > league_data[team2][game]['defense']['PTS']:
                team2_record[0] += 1
            else:
                team2_record[1] += 1
    team1_record.append(team1_record[0] / (team1_record[0] + team1_record[1]))
    team2_record.append(team2_record[0] / (team2_record[0] + team2_record[1]))
    if team1_record[2] > team2_record[2]:
        return 0
    elif team1_record[2] < team2_record[2]:
        return 1
    else:
        'continue'

def check_if_div_winner(team1: str, team2: str, league_data: dict, end_game: int, start_game: int, teams: list):
    divisions = ['Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest']
    team1_done = False
    team2_done = False
    for division in divisions:
        if team1 in teams_dict[division] and team2 in teams_dict[division]:
            div_teams = []
            for team in teams:
                if len(div_teams) == 5:
                    break
                if team[0] in teams_dict[division]:
                    div_teams.append(team)
            if (div_teams[0][0] == team1 and div_teams[1][0] == team2 and div_teams[0][4] == div_teams[1][4]) or (div_teams[0][0] == team2 and div_teams[1][0] == team1 and div_teams[0][4] == div_teams[1][4]):
                return 'continue'
            if div_teams[0][0] == team1:
                return 0
            elif div_teams[0][0] == team2:
                return 1
            else:
                return [division, division]
        if team1 in teams_dict[division]:
            team1_rank_team_list = []
            for team in teams:
                if team[0] in teams_dict[division]:
                    team1_rank_team_list.append(team) 
            team1_div_rank = ranking_teams(team1_rank_team_list, 'Div', league_data, end_game, start_game)
            team1_div = division
            team1_done = True
        if team2 in teams_dict[division]:
            team2_rank_team_list = []
            for team in teams:
                if team[0] in teams_dict[division]:
                    team2_rank_team_list.append(team) 
            team2_div_rank = ranking_teams(team2_rank_team_list, 'Div', league_data, end_game, start_game)
            team2_div = division
            team2_done = True
        if team1_done and team2_done:
            break
    new_team1 = []
    new_team2 = []
    for team1_team, team2_team in zip(team1_div_rank, team2_div_rank):
        new_team1.append(team1_team[0])
        new_team2.append(team2_team[0])
    team1_seed = new_team1.index(team1)
    team2_seed = new_team2.index(team2)
    if team1_seed == 0 and team2_seed != 0:
        return 0
    elif team1_seed != 0 and team2_seed == 0:
        return 1
    else:
        return [team1_div, team2_div]

def head2head(team1_stats: dict, team2: str, end_game: int, start_game = 1):
    record = {'wins': 0, 'losses': 0}
    for game in range(start_game, end_game + 1):
        if team1_stats[game]['opp'] == team2:
            if team1_stats[game]['offense']['PTS'] > team1_stats[game]['defense']['PTS']:
                record['wins'] += 1
            else:
                record['losses'] += 1
    if record['wins'] > record['losses']:
        return 0
    elif record['wins'] == record['losses']:
        return 'continue'
    else:
        return 1

def multi_div_winner(teams_to_check: list, league_data: dict, end_game: int, start_game: int, teams: list):
    divisions = ['Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest']
    teams_divisions_rank = []
    for tm in teams_to_check:
        teams_divisions_rank.append(None)
    for div in divisions:
        for idx, team in enumerate(teams_to_check):
            if team[0] in teams_dict[div]:
                team_rank = []
                for tm in teams:
                    if len(team_rank) == 5:
                        break
                    if tm[0] in teams_dict[div]:
                        team_rank.append(tm)
                final_team_rank = ranking_teams(team_rank, 'Div', league_data, end_game, start_game)
                tm_abrs = []
                for tm in final_team_rank:
                    tm_abrs.append(tm[0])
                teams_divisions_rank[idx] = tm_abrs
    index_list = []
    for idx, team in enumerate(teams_to_check):
        index_list.append(teams_divisions_rank[idx].index(team[0]))
    div_leaders = 0
    div_leaders_idx = []
    for idx, seed in enumerate(index_list):
        if seed == 0:
            div_leaders += 1
            div_leaders_idx.append(idx)
    if div_leaders == 0:
        return 'continue'
    elif div_leaders == 1:
        winner_index = div_leaders_idx[0]
        move = teams_to_check[0]
        teams_to_check[0] = teams_to_check[winner_index]
        teams_to_check[winner_index] = move
        return teams_to_check
    elif div_leaders > 1:
        return_list = []
        for idx, div_rank in enumerate(index_list):
            if div_rank == 0:
                return_list.append(teams_to_check[idx])
        return return_list

function_map = {
    '0.0': make_00_pickle,
    '0.1': make_01_pickle,
    '1.0': make_10_pickle,
    '1.1': make_11_pickle,
    '2.0': make_20_pickle,
    '2.1': make_21_pickle
}

year = 2014
league_types = ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1']#, '3.0', '3.1', '4.0']
start = time.time()
for year in range(year, year + 1):
    team_stats = {}
    team_file = f"./data/csv/{year}-{int(str(year)[2:]) + 1} NBA Team Stats.csv"
    with open(team_file, 'r') as team_file:
        reading_file = csv.reader(team_file)
        process_team_data(reading_file, team_stats)
    with open(f"{year}-{int(str(year)[2:]) + 1} NBA Team Stats.pickle", "wb") as pk:
        pickle.dump(team_stats, pk)
    for league_type in league_types:
        function_map[league_type](year)

print(f"Total Run Time: {time.time() - start}")
# year = 2016
# start_time = time.time()
# with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 10.pickle", "rb") as f:
#     league_data = pickle.load(f)
# print(f"file load time was {time.time() - start_time}")
# a = srs_ranking(teams_dict['League'], league_data, 82, 1)
# print(a)