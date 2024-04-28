import time
import pickle
from advanced_stats import calculate_player_advanced_stats

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

nba_teams_swapped = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BRK",
    "Chicago Bulls": "CHI",
    "Charlotte Hornets": "CHO",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHO",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}

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

def game_score(pts: float, fgm: float, fga: float, fta: float, ftm: float, orb: float, drb: float, stl: float, ast: float, blk: float, pf: float, tov: float):
    return round(pts + 0.4 * fgm - 0.7 * fga - 0.4 * (fta- ftm) + 0.7 * orb + 0.3 * drb + stl + 0.7 *ast + 0.7 * blk -0.4 * pf - tov, 3)

def fantasy_points(pm3: float, pm2: float, ftm: float, orb: float, drb: float, ast: float, blk: float, stl: float, tov: float):
    return round(pm3 * 3 + pm2 * 2 + ftm + orb * 0.9 + drb * 0.3 + ast * 1.5 + blk * -2 + stl * -2 + tov * -1, 1)

def stat_per_game(stat: int, game_path: str, stats_dict: dict):
    return stats_dict[stat] / stats_dict[game_path]

def calculate_pct(above: int, below: int):
    if below == 0:
        return 0.000
    return round(above / below, 3)

def calculating_record(league_type: str, team_stats: dict, year: str, game: int, record: dict, team: str):
    if league_type == '0.0':
        points_for = team_stats[game]['offense']['PTS']
        points_againts = team_stats[game]['defense']['PTS']
        if points_for > points_againts:
            record['Wins'] += 1
            return
        record['Loses'] += 1
    elif league_type == '0.1':
        points_for = team_stats[game]['offense']['PTS']
        points_againts = team_stats[game]['defense']['PTS']
        if points_for < points_againts:
            record['Wins'] += 1
            return
        record['Loses'] += 1

def team_record(team: str, year: str, league_type: str, end_game: int, start_game = 1, opened = None, team_stats = None) -> dict[str, int]:
    record = {'Wins': 0, 'Loses': 0}
    if not opened:
        with open("team_stats.pickle", "rb") as f:
            league_stats = pickle.load(f)
            team_stats = league_stats[team][year]
    for game in range(start_game, end_game + 1):
        if start_game not in team_stats:
            return "Did not make the playoffs"
        if game not in team_stats:
            continue
        calculating_record(league_type, team_stats, year, game, record, team)
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

def calculating_regular_stats(year_stats: dict, game: int, side_of_ball: str, season_stats: dict):
    for stat in year_stats[game][side_of_ball]:
        if stat == 'OPP':
            continue
        if stat not in season_stats:
            season_stats[stat] = year_stats[game][side_of_ball][stat]
            continue
        season_stats[stat] += year_stats[game][side_of_ball][stat]

def stats_per_league_type(league_type, year_stats, game, side_of_ball, season_stats):
    if league_type == '0.0':
        calculating_regular_stats(year_stats, game, side_of_ball, season_stats)
    elif league_type == '0.1':
        if type == 'offense':
            new_type = 'defense'
        else:
            new_type = 'offense'
        calculating_regular_stats(year_stats, game, new_type, season_stats)

def season_stats(team: str, year: str, league_type: str, side_of_ball: str, end_game: int, start_game = 1):
    season_stats = {}
    season_stats['GP'] = 0
    with open("team_stats.pickle", "rb") as f:
        team_stats = pickle.load(f)
        year_stats = team_stats[team][year]
        if start_game not in year_stats:
            return "Did Not Make Playoffs"
        for game in range(start_game, end_game + 1):
            if game not in year_stats:
                continue
            season_stats['GP'] += 1
            stats_per_league_type(league_type, year_stats, game, side_of_ball, season_stats)
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

#----------------------------------------------------------------
# Power Ranking Calculations
def power_rankings(teams: list, year: str, league_type: str, end_game: int, start_game = 1):
    with open("team_stats.pickle", "rb") as f:
        opened = True
        league_stats = pickle.load(f)
        if league_type == '0.0':
            power_list = power_rankigns_00(teams, year, league_type, end_game, start_game, league_stats)
        elif league_type == '0.1':
            power_list = power_rankings_01(teams, year, league_type, end_game, start_game, opened, league_stats)
        elif league_type == '1.0':
            power_list = power_rankings_10(teams, year, league_type, end_game, start_game, league_stats)
    return_list = sorted(power_list, key=lambda x: x[6], reverse=True)
    for rank, team in enumerate(return_list):
        team.insert(0, rank + 1)
        team[1] = nba_teams[team[1]]
    return return_list

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
            if league_type == '0.0':
                if key == 'PTS':
                    if team_stats[game]['offense'][key] > team_stats[game]['defense'][key]:
                        record['wins'] += 1
                    else:
                        record['losses'] += 1
                offense[key] += team_stats[game]['offense'][key]
                defense[key] += team_stats[game]['defense'][key]
            else:
                if key == 'PTS':
                    if team_stats[game]['defense'][key] > team_stats[game]['offense'][key]:
                        record['wins'] += 1
                    else:
                        record['losses'] += 1
                offense[key] += team_stats[game]['defense'][key]
                defense[key] += team_stats[game]['offense'][key]
    off_gmsc = game_score(offense['PTS'] / offense['GP'], offense['FGM'] / offense['GP'], offense['FGA'] / offense['GP'], offense['FTA'] / offense['GP'], offense['FTM'] / offense['GP'], offense['ORB'] / offense['GP'], offense['DRB'] / offense['GP'], offense['STL'] / offense['GP'], offense['AST'] / offense['GP'], offense['BLK'] / offense['GP'], offense['PF'] / offense['GP'], offense['TOV'] / offense['GP'])
    def_gmsc = game_score(defense['PTS'] / defense['GP'], defense['FGM'] / defense['GP'], defense['FGA'] / defense['GP'], defense['FTA'] / defense['GP'], defense['FTM'] / defense['GP'], defense['ORB'] / defense['GP'], defense['DRB'] / defense['GP'], defense['STL'] / defense['GP'], defense['AST'] / defense['GP'], defense['BLK'] / defense['GP'], defense['PF'] / defense['GP'], defense['TOV'] / defense['GP'])
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

def calculating_power_ranking_10(team: str, year: str, team_stats: dict, league_type: str, end_game: int, start_game = 1):
    record = {'wins': 0, 'losses': 0}
    offense = {'2PM': 0, '2PA': 0, '3PM': 0, '3PA': 0, 'FTM': 0, 'FTA': 0, 'ORB': 0, 'DRB': 0, 'AST': 0, 'STL': 0, 'BLK': 0, 'TOV': 0, 'PF': 0}
    defense = {'2PM': 0, '2PA': 0, '3PM': 0, '3PA': 0, 'FTM': 0, 'FTA': 0, 'ORB': 0, 'DRB': 0, 'AST': 0, 'STL': 0, 'BLK': 0, 'TOV': 0, 'PF': 0}
    if start_game not in team_stats:
        return "Did not make Playoffs"
    for game in range(start_game, end_game + 1):
        if game not in team_stats:
            break
        if team_stats[game]['offense']['PTS'] > team_stats[game]['defense']["PTS"]:
            record['wins'] += 1
        else:
            record['losses'] += 1
        for index, key in enumerate(offense.keys()):
            if team_stats[game]['offense']['PTS'] > team_stats[game]['defense']['PTS']:
                if index >= 9:
                    offense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    defense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    continue
                if key[2] == "A":
                    if min(team_stats[game]['offense'][key], team_stats[game]['defense'][key]) >= offense[key.replace('A', 'M')]:
                        offense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                        defense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    else:
                        offense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                        defense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    continue
                offense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                defense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
            else:
                if index >= 9:
                    offense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    defense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    continue
                if key[2] == "A":
                    if min(team_stats[game]['offense'][key], team_stats[game]['defense'][key]) >= defense[key.replace('A', 'M')]:
                        offense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                        defense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    else:
                        offense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                        defense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                    continue
                offense[key] += min(team_stats[game]['offense'][key], team_stats[game]['defense'][key])
                defense[key] += max(team_stats[game]['offense'][key], team_stats[game]['defense'][key])

    offense['PTS'] = offense['2PM'] * 2 + offense['3PM'] * 3 + offense['FTM']
    defense['PTS'] = defense['2PM'] * 2 + defense['3PM'] * 3 + defense['FTM']
    offense['FGM'] = offense['2PM'] + offense['3PM'] + offense['FTM']
    offense['FGA'] = offense['2PA'] + offense['3PA'] + offense['FTA']
    defense['FGM'] = defense['2PM'] + defense['3PM'] + defense['FTM']
    defense['FGA'] = defense['2PA'] + defense['3PA'] + defense['FTA']
    offense['GP'] = record['wins'] + record['losses']
    defense['GP'] = offense['GP']
    off_gmsc = game_score(offense['PTS'] / offense['GP'], offense['FGM'] / offense['GP'], offense['FGA'] / offense['GP'], offense['FTA'] / offense['GP'], offense['FTM'] / offense['GP'], offense['ORB'] / offense['GP'], offense['DRB'] / offense['GP'], offense['STL'] / offense['GP'], offense['AST'] / offense['GP'], offense['BLK'] / offense['GP'], offense['PF'] / offense['GP'], offense['TOV'] / offense['GP'])
    def_gmsc = game_score(defense['PTS'] / defense['GP'], defense['FGM'] / defense['GP'], defense['FGA'] / defense['GP'], defense['FTA'] / defense['GP'], defense['FTM'] / defense['GP'], defense['ORB'] / defense['GP'], defense['DRB'] / defense['GP'], defense['STL'] / defense['GP'], defense['AST'] / defense['GP'], defense['BLK'] / defense['GP'], defense['PF'] / defense['GP'], defense['TOV'] / defense['GP'])
    diff_gmsc = round(off_gmsc - def_gmsc, 1)
    offense['FP'] = round(offense['3PM'] * 3 + offense['2PM'] * 2 + offense['FTM'] + offense['ORB'] * 0.9 + offense['DRB'] * 0.3 + offense['AST'] * 1.5 + offense['BLK'] * -2 + offense['STL'] * -2 + offense['TOV'] * -1, 1)
    defense['FP'] = round(defense['3PM'] * 3 + defense['2PM'] * 2 + defense['FTM'] + defense['ORB'] * 0.9 + defense['DRB'] * 0.3 + defense['AST'] * 1.5 + defense['BLK'] * -2 + defense['STL'] * -2 + defense['TOV'] * -1, 1)
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

def power_rankigns_00(teams: list, year: str, league_type: str, end_game: int, start_game = 1, league_stats = None):
    power_list = []
    for team in teams:
        team_stats = league_stats[team][year]
        stats = calculating_power_ranking(team, year, team_stats, league_type, end_game, start_game)
        if stats == "Did not make Playoffs":
            continue
        power_list.append(stats)
    return power_list

def power_rankings_01(teams: list, year: str, league_type: str, end_game: int, start_game = 1, opened = None, league_stats = None):
    power_list = []
    old_league = league_type.replace('.1', '.0')
    if year == '2020-21':
        rank_end_game = 72
    else:
        rank_end_game = 82
    standings = rank_teams(teams, year, old_league, rank_end_game, 1, opened, league_stats)
    eastern_conf = []
    western_conf = []
    for team_rank in standings:
        tm_abr = nba_teams_swapped[team_rank[1]]
        if tm_abr in teams_list['Eastern']:
            eastern_conf.append(tm_abr)
        else:
            western_conf.append(tm_abr)
    for team in teams:
        team_stats = league_stats[team][year]
        if team in teams_list['Eastern']:
            standings = eastern_conf
        else:
            standings = western_conf
        new_team_stats = adding_playoff_games_for_point_ones(team, year, league_stats, team_stats, standings, end_game, start_game)
        stats = calculating_power_ranking(team, year, new_team_stats, league_type, end_game, start_game)
        if stats == "Did not make Playoffs":
            continue
        power_list.append(stats)
    return power_list

def power_rankings_10(teams: list, year: str, league_type: str, end_game:int, start_game = 1, league_stats = None):
    power_list = []
    for team in teams:
        team_stats = league_stats[team][year]
        stats = calculating_power_ranking_10(team, year, team_stats, league_type, end_game, start_game)
        if stats == "Did not make Playoffs":
            continue
        power_list.append(stats)
    return power_list

#----------------------------------------------------------------
# Player Ranking Calculations
def player_rankings(teams: list, year: str, league_type: str, end_game: int, start_game = 1):
    start_time = time.time()
    player_list = []
    with open("player_data.pickle", "rb") as f:
        league_data = pickle.load(f)
    with open("player_pos.pickle", "rb") as f:
        pos_data = pickle.load(f)
        pos_data = pos_data[year]
    for player in league_data:
        player_list.append(player_season_stats(player, year, league_type, end_game, start_game, teams, league_data, pos_data))
    sorted_list = sorted(player_list, key=lambda x: x[32], reverse=True)
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

def player_season_stats(player: str, year: str, league_type: str, end_game: int, start_game = 1, teams = None, league_data = None, pos_data = None):
    if league_data == None:
        with open("player_data.pickle", "rb") as f:
            league_data = pickle.load(f)
        with open("player_pos.pickle", "rb") as f:
            pos_data = pickle.load(f)
            pos_data = pos_data[year]
    player_dict = {}
    league_player_data = league_data[player][year]
    if teams == None:
        teams = league_player_data.keys()
    for team in league_player_data:
        if team in teams:
            player_stats = league_player_data[team]
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
        break
    fg_pct = calculate_pct(player_dict['FGM'], player_dict['FGA'])
    pct_2p = calculate_pct(player_dict['2PM'], player_dict['2PA'])
    pct_3p = calculate_pct(player_dict['3PM'], player_dict['3PA'])
    ft_pct = calculate_pct(player_dict['FTM'], player_dict['FTA'])
    eFG = calculate_pct((player_dict['FGM'] + 0.5 * player_dict['3PM']), player_dict['FGA'])
    trb = (player_dict['ORB'] + player_dict['DRB']) / player_dict['GP']
    player_dict_per_game = {}
    for stat in player_dict:
        if stat == 'GP':
            continue
        player_dict_per_game[stat] = player_dict[stat] / player_dict['GP']
    off_stats = season_stats(team, year, league_type, 'offense', end_game, start_game)
    def_stats = season_stats(team, year, league_type, 'defense', end_game, start_game)
    advanced_stats = calculate_player_advanced_stats(player_dict, off_stats, def_stats)
    for stat in advanced_stats:
        player_dict_per_game[stat] = advanced_stats[stat]
    for pos in pos_data:
        if player in pos_data[pos]:
            break
    fp = fantasy_points(player_dict_per_game['3PM'], player_dict_per_game['2PM'], player_dict_per_game['FTM'], player_dict_per_game['ORB'], player_dict_per_game['DRB'], player_dict_per_game['AST'], player_dict_per_game['BLK'], player_dict_per_game['STL'], player_dict_per_game['TOV'])
    gmsc = game_score(player_dict_per_game['PTS'], player_dict_per_game['FGM'], player_dict_per_game['FGA'], player_dict_per_game['FTA'], player_dict_per_game['FTM'], player_dict_per_game['ORB'], player_dict_per_game['DRB'], player_dict_per_game['STL'], player_dict_per_game['AST'], player_dict_per_game['BLK'], player_dict_per_game['PF'], player_dict_per_game['TOV'])
    spr = round((fp * 0.15 + gmsc * 0.45 + player_dict_per_game['nRtg'] * 0.4), 3)
    return [player, year, pos, player_dict['GP'], round(player_dict_per_game['MP'], 1), round(player_dict_per_game['PTS'], 1), round(player_dict_per_game['FGM'], 1), round(player_dict_per_game['FGA'], 1), round(fg_pct, 3), round(eFG, 3), round(player_dict_per_game['2PM'], 1), round(player_dict_per_game['2PA'], 1), round(pct_2p, 3), round(player_dict_per_game['3PM'], 1), round(player_dict_per_game['3PA'], 1), round(pct_3p, 3), round(player_dict_per_game['FTM'], 1), round(player_dict_per_game['FTA'], 1), round(ft_pct, 3), round(player_dict_per_game['ORB'], 1), round(player_dict_per_game['DRB'], 1), round(trb, 1), round(player_dict_per_game['AST'], 1), round(player_dict_per_game['STL'], 1), round(player_dict_per_game['BLK'], 1), round(player_dict_per_game['TOV'], 1), round(player_dict_per_game['PF'], 1), round(player_dict_per_game['oRtg'], 1), round(player_dict_per_game['dRtg'], 1), round(player_dict_per_game['nRtg'], 1), fp, gmsc, spr]


teams = ['GSW', 'ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
# # # for team in teams: 
a = player_rankings(teams, '2023-24', '0.0', 82)
# a = player_season_stats('Trae Young', '2023-24', '0.0', 82)
# # a = rank_teams(teams, '2020-21', '0.0', 73, 1)
print(a)