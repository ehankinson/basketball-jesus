import csv
import time
import pickle


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
    for line in reading_file:
        if line[1] == 'Team':
            continue
        team = line[1]
        if team not in team_stats:
            team_stats[team] = {}
        game = len(team_stats[team]) + 1
        if game not in team_stats[team]:
            team_stats[team][game] = {}
        #offense
        team_stats[team][game]['offense'] = {}
        putting_stats_in_dict(team_stats[team][game]['offense'], index_map['offense'], line)
        #defense
        team_stats[team][game]['defense'] = {}
        putting_stats_in_dict(team_stats[team][game]['defense'], index_map['defense'], line)
        team_stats[team][game]['opp'] = line[7]

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
    with open("2023-24 NBA Team Stats.pickle", "rb") as pk:
        league_stats = pickle.load(pk)
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 00.pickle", "wb") as pk:
        pickle.dump(league_stats, pk)

def make_01_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 00.pickle", "rb") as f:
        league_data = pickle.load(f)
    if year != 2021:
        end_game = 82
        start_game = 1
    eastern_teams = teams_dict['Eastern']
    western_teams = teams_dict['Western']
    eastern_ranks = rank_teams(eastern_teams, league_data, end_game, start_game)
    western_ranks = rank_teams(western_teams, league_data, end_game, start_game)
    new_league_data = {}
    for team in league_data:
        if team in western_teams:
            teams = western_ranks
        else:
            teams = eastern_ranks
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
                else:
                    new_league_data[team][game]['offense'] = league_data[team][game]['defense']
                    new_league_data[team][game]['defense'] = league_data[team][game]['offense']
                    new_league_data[team][game]['opp'] = league_data[team][game]['opp']
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
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
            else:
                new_off, new_def = lower_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
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
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
            else:
                new_off, new_def = lower_than(league_data[team][game]['offense'], league_data[team][game]['defense'])
                new_league_data[team][game]['offense'] = new_off
                new_league_data[team][game]['defense'] = new_def
                new_league_data[team][game]['opp'] = league_data[team][game]['opp']
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 11.pickle", "wb") as pk:
        pickle.dump(new_league_data, pk)

def make_20_pickle(year: int):
    with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Team Stats 10.pickle", "rb") as f:
        league_data = pickle.load(f)
    ranked_teams = rank_teams(teams_dict['League'], league_data, 82, 1)
    new_league_data = {}
    if year == 2021:
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
    new_ranked_teams = rank_teams(teams_dict['League'], new_league_data, 82, 1)
    a = 5

def rank_teams(teams: list, league_data: dict, end_game: int, start_game: int):
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
    ranked_teams = sorted(ranked_teams, key=lambda x: x[4], reverse=True)
    return_list = [team[0] for team in ranked_teams]
    return return_list




function_map = {
    '0.0': make_00_pickle,
    '0.1': make_01_pickle,
    '1.0': make_10_pickle,
    '1.1': make_11_pickle,
    '2.0': make_20_pickle,
}

year = 2022
league_types = ['0.0', '0.1', '1.0', '1.1', '2.0']#, '2.1', '3.0', '3.1', '4.0']
start = time.time()
team_stats = {}
for year in range(year, 2023):
    team_file = f"./data/csv/{year}-{int(str(year)[2:]) + 1} NBA Team Stats.csv"
    with open(team_file, 'r') as team_file:
        reading_file = csv.reader(team_file)
        process_team_data(reading_file, team_stats)
    with open("2023-24 NBA Team Stats.pickle", "wb") as pk:
        pickle.dump(team_stats, pk)
    for league_type in league_types:
        function_map[league_type](year)

print(f"Total Run Time: {time.time() - start}")






