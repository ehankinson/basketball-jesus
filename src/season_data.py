import json
import time
import pickle
import numpy as np
from advanced_stats import calculate_player_advanced_stats

with open("data/json/teams.json", "r") as j:
    NBA_TEAMS = json.load(j)

teams_list = {
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

def game_score(stats_dict: dict):
    return round(stats_dict['PTS'] + (0.4 * stats_dict['FGM']) - (0.7 * stats_dict['FGA']) - (0.4 * (stats_dict['FTA'] - stats_dict['FTM'])) + (0.7 * stats_dict['ORB']) + (0.3 * stats_dict['DRB']) + stats_dict['STL'] + (0.7 * stats_dict['AST']) + (0.7 * stats_dict['BLK']) - (0.4 * stats_dict['PF']) - stats_dict['TOV'], 3)

def fantasy_points(stats_dict: dict, player_or_team: str):
    if player_or_team == "T":
        return round(stats_dict['3PM'] * 3 + stats_dict['2PM'] * 2 + stats_dict['FTM'] + stats_dict['ORB'] * 1.675 + stats_dict['DRB'] * 1.075 + stats_dict['AST'] * 1.5 + stats_dict['BLK'] * -2 + stats_dict['STL'] * -2 + stats_dict['TOV'] * -1, 1)
    else:
        return round(stats_dict['3PM'] * 3 + stats_dict['2PM'] * 2 + stats_dict['FTM'] + stats_dict['ORB'] * 1.675  + stats_dict['DRB'] * 1.075 + stats_dict['AST'] * 1.5 + stats_dict['BLK'] * 2 + stats_dict['STL'] * 2 + stats_dict['TOV'] * -1, 1)

def stat_per_game(stat: int, game_path: str, stats_dict: dict):
    return stats_dict[stat] / stats_dict[game_path]

def calculate_pct(above: int, below: int):
    if below == 0:
        return 0.000
    return round(above / below, 3)

def calculating_record(team_stats: dict, game: int, record: dict, team: str):
    points_for = team_stats[game]['offense']['PTS']
    points_againts = team_stats[game]['defense']['PTS']
    if points_for > points_againts:
        record['Wins'] += 1
        return
    record['Loses'] += 1

def team_record(team: str, year: str, league_type: str, end_game: int, start_game = 1, opened = None, team_stats = None) -> dict[str, int]:
    record = {'Wins': 0, 'Loses': 0}
    if not opened:
        file_league_type = league_type.replace(".", "")
        with open(f"data/pickle/{year} NBA Team Stats {file_league_type}.pickle", "rb") as f:
            team_stats = pickle.load(f)
            team_stats = team_stats[team]
    for game in range(start_game, end_game + 1):
        if start_game not in team_stats:
            return "Did not make the playoffs"
        if game not in team_stats:
            continue
        calculating_record(team_stats, game, record, team)
    return record

def season_ranking(year: str, end_game: int, start_game = 1):
    season_records = {}
    with open("team_stats.pickle", "rb") as f:
        team_stats = pickle.load(f)
        for team in team_stats:
            season_records[team] = team_record(team, year, end_game, start_game)
    return season_records

def rank_teams(teams: list, year: str, league_type: str, end_game: int, start_game = 1, opened = None, league_stats = None):
    records = []
    for team in teams:
        if league_stats != None:
            team_stats = league_stats[team][year]
        else:
            team_stats = None
        record = team_record(team, year, league_type, end_game, start_game, opened, team_stats)
        if record == "Did not make the playoffs":
            continue
        team = [nba_teams[team], year, record['Wins'] + record['Loses'], record['Wins'], record['Loses'], float(round(record['Wins'] / (record['Wins'] + record['Loses']), 3))]
        records.append(team)
    sorted_records = sorted(records, key=lambda x: x[5], reverse=True)
    for seed, team in enumerate(sorted_records):
        team.insert(0, seed + 1)
    return sorted_records

def stats_per_league_type(year_stats, game, side_of_ball, season_stats):
    for stat in year_stats[game][side_of_ball]:
        if stat == 'OPP':
            continue
        if stat not in season_stats:
            season_stats[stat] = year_stats[game][side_of_ball][stat]
            continue
        season_stats[stat] += year_stats[game][side_of_ball][stat]

def season_stats(team: str, year: str, league_type: str, side_of_ball: str, end_game: int, start_game = 1):
    season_stats = {}
    season_stats['GP'] = 0
    file_league_type = league_type.replace(".", "")
    with open(f"data/pickle/{year} NBA Team Stats {file_league_type}.pickle", "rb") as f:
        team_stats = pickle.load(f)
        year_stats = team_stats[team]
        if start_game not in year_stats:
            return "Did Not Make Playoffs"
        for game in range(start_game, end_game + 1):
            if game not in year_stats:
                continue
            season_stats['GP'] += 1
            stats_per_league_type(year_stats, game, side_of_ball, season_stats)
    season_stats['2P%'] = round(season_stats['2PM'] / season_stats['2PA'], 3)
    season_stats['3P%'] = round(season_stats['3PM'] / season_stats['3PA'], 3)
    season_stats['FT%'] = round(season_stats['FTM'] / season_stats['FTA'], 3)
    season_stats['TRB'] = season_stats['ORB'] + season_stats['DRB']
    season_stats['FGM'] = season_stats['2PM'] + season_stats['3PM']
    season_stats['FGA'] = season_stats['2PA'] + season_stats['3PA']
    season_stats['FG%'] = round(season_stats['FGM'] / season_stats['FGA'], 3)
    season_stats['eFG%'] = round((season_stats['FGM'] + 0.5 * season_stats['3PM']) / season_stats['FGA'], 3)
    season_stats['FP'] = round(season_stats['3PM'] * 3 + season_stats['2PM'] * 2 + season_stats['FTM'] + season_stats['ORB'] * 0.9 + season_stats['DRB'] * 0.3 + season_stats['AST'] * 1.5 + season_stats['BLK'] * -2 + season_stats['STL'] * -2 + season_stats['TOV'] * -1, 1)
    season_stats['GmSc'] = game_score(stat_per_game('PTS', 'GP', season_stats), stat_per_game('FGM', 'GP', season_stats), stat_per_game('FGA', 'GP', season_stats), stat_per_game('FTA', 'GP', season_stats), stat_per_game('FTM', 'GP', season_stats), stat_per_game('ORB', 'GP', season_stats), stat_per_game('DRB', 'GP', season_stats), stat_per_game('STL', 'GP', season_stats), stat_per_game('AST', 'GP', season_stats), stat_per_game('BLK', 'GP', season_stats), stat_per_game('PF', 'GP', season_stats), stat_per_game('TOV', 'GP', season_stats))
    season_stats['STRS'] = round((stat_per_game('PTS', 'GP', season_stats) + stat_per_game('FP', 'GP', season_stats) + season_stats['GmSc']) / 3, 3)
    return season_stats

def team_stats_to_list(team: str, year: str, league_type: str, stat_type: str, end_game: int, start_game: int):
    team_stats = season_stats(team, year, league_type, stat_type, end_game, start_game)
    if team_stats == 'Did Not Make Playoffs':
        return 'Did Not Make Playoffs'
    keys = ['GP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%','2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
    team_list = [nba_teams[team], year]
    for key in keys:
        if key == 'GP' or '%' in key:
            team_list.append(team_stats[key])
            continue
        team_list.append(round(team_stats[key] / team_stats['GP'], 1))
    team_list.append(round(team_stats['FP'] / team_stats['GP'], 2))
    team_list.append(team_stats['GmSc'])
    team_list.append(team_stats['STRS'])
    return team_list

def league_team_stats(team_list: list, year: str, season_type_opt: str, league_type: str, type: str, end_game: int, start_game: int):
    total_stats = []
    for team in team_list:
        if season_type_opt == 'Post Season':
            if year == '2020-21':
                team_stats = team_stats_to_list(team, year, league_type, type, end_game + 72, start_game + 72)
            else:
                team_stats = team_stats_to_list(team, year, league_type, type, end_game + 82, start_game + 82)
        else:
            team_stats = team_stats_to_list(team, year, league_type, type, end_game, start_game)
        if team_stats == 'Did Not Make Playoffs':
            continue
        total_stats.append(team_stats)
    if type == 'offense':
        sorted_team = sorted(total_stats, key=lambda x: x[27], reverse=True)
    else:
        sorted_team = sorted(total_stats, key=lambda x: x[27])
    return sorted_team

#----------------------------------------------------------------
# Power Ranking Calculations
def power_rankings(teams: list, year: str, league_type: str, end_game: int, start_game = 1):
    if not isinstance(year, list):
        year = [year]
    league_dict = {}
    for year_key in year:
        file_league_type = league_type.replace(".", "")
        with open(f"data/pickle/{year_key} NBA Team Stats {file_league_type}.pickle", "rb") as f:
            league_dict[year_key] = pickle.load(f)
        
    power_list = []
    for key in league_dict:
        intermidiate_list = []
        for team in league_dict[key]:
            if team not in league_dict[key]:
                continue
            team_stats = league_dict[key][team]
            stats = calculating_power_ranking(team, key, team_stats, league_type, end_game, start_game)
            if stats == "Did not make Playoffs":
                continue
            intermidiate_list.append(stats)
        new_teams = srs_ranking(intermidiate_list, league_dict[key], end_game, start_game)
        for team in new_teams:
            power_list.append(team)

    return_list = sorted(power_list, key=lambda x: x[6], reverse=True)
    for rank, team in enumerate(return_list):
        team.insert(0, rank + 1)
        team[1] = NBA_TEAMS[team[1]]['team']
    return return_list

def rank_custon_teams(teams: list):
    league_dict = {}
    teams_rank = []
    for team in teams:
        year = team[0]['year']
        league_type = team[0]['league_type']
        team_name = NBA_TEAMS[team[0]['team']]['abr']
        league_key = f"{year}-{league_type}"
        if league_key not in league_dict:
            file_type = league_type.replace(".", "")
            with open(f"data/pickle/{year} NBA Team Stats {file_type}.pickle", "rb") as pkl:
                league_data = pickle.load(pkl)
                league_dict[league_key] = league_data
        team_stats = {'offense': {}, 'defense': {}, 'record': {'wins': 0, 'losses': 0}}
        for game in league_dict[league_key][team_name]:
            if league_dict[league_key][team_name][game]['offense']['PTS'] > league_dict[league_key][team_name][game]['defense']['PTS']:
                team_stats['record']['wins'] += 1
            else:
                team_stats['record']['losses'] += 1
            for off_key, def_key in zip(league_dict[league_key][team_name][game]['offense'], league_dict[league_key][team_name][game]['defense']):
                if "%" in off_key or off_key == 'GmSc' or off_key == 'STRS':
                    continue
                if off_key not in team_stats['offense']:
                    team_stats['offense'][off_key] = league_dict[league_key][team_name][game]['offense'][off_key]
                    team_stats['defense'][def_key] = league_dict[league_key][team_name][game]['defense'][def_key]
                    continue
                team_stats['offense'][off_key] += league_dict[league_key][team_name][game]['offense'][off_key]
                team_stats['defense'][def_key] += league_dict[league_key][team_name][game]['defense'][def_key]
        offense = team_stats['offense']
        defense = team_stats['defense']
        offense['GP'] = game
        defense['GP'] = game
        off_gmsc = game_score(offense)
        def_gmsc = game_score(defense)
        off_fanpts = round(offense['FP'] / offense['GP'], 2)
        def_fanpts = round(defense['FP'] / defense['GP'], 2)
        sors = round((off_gmsc + off_fanpts + (offense['PTS'] / offense['GP'])) / 3, 3)
        sdrs = round((def_gmsc + def_fanpts + (defense['PTS'] / defense['GP'])) / 3, 3)
        strs = round(sors - sdrs, 3)
        team_list = [team_name, year, league_type, game, team_stats['record']['wins'], team_stats['record']['losses'], team_stats['record']['wins'] / game, strs]
        teams_rank.append(team_list)
    ranked_teams = sorted(teams_rank, key=lambda x: (x[6], x[7]), reverse=True)
    return ranked_teams
    
def rank_bracket_team(bracket_stats: dict):
    power_list = []
    for team in bracket_stats:
        offense_stats = bracket_stats[team]['offense']
        defense_stats = bracket_stats[team]['defense']
        record = bracket_stats[team]['record']
        info = bracket_stats[team]['info']
        games_played = record['wins'] + record['losses']
        pf = calculate_pct(offense_stats['PTS'], games_played)
        pa = calculate_pct(defense_stats['PTS'], games_played)
        diff = pf - pa
        off_fanpts = round(fantasy_points(offense_stats, "T") / games_played, 2)
        def_fanpts = round(fantasy_points(defense_stats, "T") / games_played, 2)
        fp_diff = off_fanpts - def_fanpts
        off_gmsc = round(game_score(offense_stats) / games_played, 3)
        def_gmsc = round(game_score(defense_stats) / games_played, 3)
        diff_gmsc = off_gmsc - def_gmsc
        sors = round((off_gmsc + off_fanpts + pf) / 3, 3)
        sdrs = round((def_gmsc + def_fanpts + pa) / 3, 3)
        strs = round(sors - sdrs, 3)
        power_list.append([NBA_TEAMS[team[:3]]['team'], info['year'], games_played, record['wins'], record['losses'], calculate_pct(record['wins'], games_played), strs, sors, sdrs, pf, pa, diff, off_fanpts, def_fanpts, fp_diff, off_gmsc, def_gmsc, diff_gmsc])
    sorted_list = sorted(power_list, key=lambda x: (x[3], x[5], x[6]), reverse=True)
    for idx, team in enumerate(sorted_list):
        team.insert(0, idx + 1)
    return sorted_list

def adding_playoff_games_for_point_ones(team: str, year: str, league_stats: dict, team_stats: dict, standings: list, end_game: str, start_game = 1):
    seed = (15 - standings.index(team))
    new_team = standings[seed - 1]
    if year == '2020-21':
        start_game = 73
        end_game = 100
    else:
        start_game = 83
        end_game = 110
    new_team_stats = {}
    if start_game not in league_stats[new_team][year]:
        for game in team_stats:
            if game >= start_game:
                return new_team_stats
            new_team_stats[game] = team_stats[game]
        return new_team_stats
    else:
        for game in range(1, end_game):
            if game >= start_game:
                if game in league_stats[new_team][year]:
                    if game not in new_team_stats:
                        new_team_stats[game] = {'offense': None, 'defense': None}
                    new_team_stats[game]['offense'] = league_stats[new_team][year][game]['defense']
                    new_team_stats[game]['defense'] = league_stats[new_team][year][game]['offense']
                    continue
                break
            new_team_stats[game] = team_stats[game]
        return new_team_stats
           
def calculating_power_ranking(team: str, year: str, team_stats: dict, league_type: str, end_game: int, start_game = 1):
    record = {'wins': 0, 'losses': 0}
    offense = {'GP': 0, 'PTS': 0, 'FP': 0, 'FGM': 0, 'FGA': 0, 'FTA': 0, 'FTM': 0, 'ORB': 0, 'DRB': 0, 'STL': 0, 'AST': 0, 'BLK': 0, 'PF': 0, 'TOV': 0}
    defense = {'GP': 0, 'PTS': 0, 'FP': 0, 'FGM': 0, 'FGA': 0, 'FTA': 0, 'FTM': 0, 'ORB': 0, 'DRB': 0, 'STL': 0, 'AST': 0, 'BLK': 0, 'PF': 0, 'TOV': 0}
    if start_game not in team_stats:
        return "Did not make Playoffs"
    for game in range(start_game, end_game + 1):
        if game not in team_stats:
            continue
        for key in offense.keys():
            if key == 'GP':
                offense[key] += 1
                defense[key] += 1
                continue
            if key == 'PTS':
                if team_stats[game]['offense'][key] > team_stats[game]['defense'][key]:
                    record['wins'] += 1
                else:
                    record['losses'] += 1
            offense[key] += team_stats[game]['offense'][key]
            defense[key] += team_stats[game]['defense'][key]
    off_gmsc = round(game_score(offense) / offense['GP'], 2)
    def_gmsc = round(game_score(defense) / defense['GP'], 2)
    diff_gmsc = round(off_gmsc - def_gmsc, 1)
    off_fanpts = round(offense['FP'] / offense['GP'], 2)
    def_fanpts = round(defense['FP'] / defense['GP'], 2)
    fp_diff = round(offense['FP'] / offense['GP'] - defense['FP'] / defense['GP'], 2)
    pf = round(offense['PTS'] / offense['GP'], 1)
    pa = round(defense['PTS'] / defense['GP'], 1)
    diff = round(offense['PTS'] / offense['GP'] - defense['PTS'] / defense['GP'], 1)
    sors = round((off_gmsc + off_fanpts + pf) / 3, 3)
    sdrs = round((def_gmsc + def_fanpts + pa) / 3, 3)
    strs = round(sors - sdrs, 3)
    return [team, year, offense['GP'], record['wins'], record['losses'], calculate_pct(record['wins'], offense['GP']), strs, sors, sdrs, pf, pa, diff, off_fanpts, def_fanpts, fp_diff, off_gmsc, def_gmsc, diff_gmsc]

def srs_ranking(teams: list, league_data: dict, end_game: int, start_game: int):
    start_time = time.time()
    srs_dict = {team[0]: team[6] for team in teams}
    team_opps = {}
    for team in teams:
        team_name = team[0]
        team_opps[team_name] = []
        for game in range(start_game, end_game + 1):
            if game > len(league_data[team_name]):
                break
            team_opps[team_name].append(league_data[team_name][game]['opp'])
    terms = []
    solutions = []
    for team in srs_dict:
        row = []
        opps = team_opps[team]
        for opp in srs_dict:
            if opp == team:
                row.append(1)
            elif opp in opps:
                row.append(-1 / len(opps))
            else:
                row.append(0)
        terms.append(row)
        solutions.append(srs_dict[team])
    solutions = list(np.linalg.solve(np.array(terms), np.array(solutions)))
    for idx, team in enumerate(srs_dict):
        srs_dict[team] = solutions[idx]
    for team in teams:
        team.insert(6, round(srs_dict[team[0]], 3))
    sorted_teams = sorted(teams, key=custom_sort, reverse=True)
    end_time = time.time()
    print(f"Total time it took was {end_time - start_time} seconds")
    return sorted_teams

def custom_sort(item):
    return (item[6], item[5])

#----------------------------------------------------------------
# Player Ranking Calculations
def player_rankings(teams: list, year: str, league_type: str, conf: str, divison: str, team: str, positions: str, end_game: int, start_game = 1):
    start_time = time.time()
    player_list = []
    file_league_type = league_type.replace(".", "")
    with open(f"data/pickle/{year} NBA Player Stats {file_league_type}.pickle", "rb") as p:
        league_data = pickle.load(p)
    if positions != "ALL":
        positions = [positions]
    else:
        positions = list(league_data['pos'].keys())
    for pos in positions:
        for player in league_data['pos'][pos]:
            season_stats = player_season_stats(player, pos, year, league_type, league_data['data'], team, end_game, start_game)
            if season_stats == "Did not make Playoffs":
                continue
            player_list.append(season_stats)
    sorted_list = sorted(player_list, key=lambda x: x[29], reverse=True)
    game_min = len(range(start_game, end_game + 1)) * 0.4
    min_minute = game_min * 15
    final_list = []
    for player in sorted_list:
        if player[3] >= game_min:
            if player[4] * game_min > min_minute:
                final_list.append(player)
    end_time = time.time()
    print(f"it took {end_time - start_time} seconds to run")
    return final_list

def player_season_stats(player: str, pos: str, year: str, league_type: str, league_data: dict, team: str, end_game: int, start_game = 1):
    player_dict = {}
    league_player_data = league_data[player]
    if team == "ALL":
        teams = list(league_player_data.keys())
    for team in teams:
        player_stats = league_player_data[team]
        if start_game not in player_stats:
            return "Did not make Playoffs"
        for game in range(start_game, end_game + 1):
            if game not in player_stats:
                continue
            for stat in player_stats[game]:
                if stat not in player_dict:
                    player_dict[stat] = player_stats[game][stat]
                    continue
                player_dict[stat] += player_stats[game][stat]
            if 'GP' not in player_dict:
                player_dict['GP'] = 1
                continue
            player_dict['GP'] += 1
    if player == "Victor Wembanyama":
        a = 5
    player_dict['FG%'] = calculate_pct(player_dict['FGM'], player_dict['FGA'])
    player_dict['2P%'] = calculate_pct(player_dict['2PM'], player_dict['2PA'])
    player_dict['3P%'] = calculate_pct(player_dict['3PM'], player_dict['3PA'])
    player_dict['FT%'] = calculate_pct(player_dict['FTM'], player_dict['FTA'])
    player_dict['eFG%'] = calculate_pct((player_dict['FGM'] + 0.5 * player_dict['3PM']), player_dict['FGA'])
    player_dict['TRB'] = player_dict['ORB'] + player_dict['DRB']
    player_dict_per_game = {}
    for stat in player_dict:
        if stat == 'GP' or "%" in stat:
            continue
        player_dict_per_game[stat] = player_dict[stat] / player_dict['GP']
    # off_stats = season_stats(team, year, league_type, 'offense', end_game, start_game)
    # def_stats = season_stats(team, year, league_type, 'defense', end_game, start_game)
    # advanced_stats = calculate_player_advanced_stats(player_dict, off_stats, def_stats)
    fp = fantasy_points(player_dict_per_game, "P")
    gmsc = game_score(player_dict_per_game)
    spr = round((fp * 0.25 + gmsc * 0.75), 3)
    return [player, year, pos, player_dict['GP'], round(player_dict_per_game['MP'], 1), round(player_dict_per_game['PTS'], 1), round(player_dict_per_game['FGM'], 1), round(player_dict_per_game['FGA'], 1), round(player_dict['FG%'], 3), round(player_dict['eFG%'], 3), round(player_dict_per_game['2PM'], 1), round(player_dict_per_game['2PA'], 1), round(player_dict['2P%'], 3), round(player_dict_per_game['3PM'], 1), round(player_dict_per_game['3PA'], 1), round(player_dict['3P%'], 3), round(player_dict_per_game['FTM'], 1), round(player_dict_per_game['FTA'], 1), round(player_dict['FT%'], 3), round(player_dict_per_game['ORB'], 1), round(player_dict_per_game['DRB'], 1), round(player_dict_per_game['TRB'], 1), round(player_dict_per_game['AST'], 1), round(player_dict_per_game['STL'], 1), round(player_dict_per_game['BLK'], 1), round(player_dict_per_game['TOV'], 1), round(player_dict_per_game['PF'], 1), fp, gmsc, spr]


if __name__ == '__main__':
    teams = []
    for team in NBA_TEAMS:
        if len(team) > 3:
            continue
        teams.append(team)
    year = "2023-24"
    league_type = "0.0"
    conf = "ALL"
    division = "ALL"
    team = "ALL"
    position = "ALL"
    player_rankings(NBA_TEAMS, year, league_type, conf, division, team, position, 82, 1)