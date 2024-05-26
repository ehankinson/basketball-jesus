import json
import time
import random
import pickle

with open(f"data/json/teams.json", "r") as j:
    teams = json.load(j)

def find_game(team: str, season_data: dict, side_of_ball: str):
    games_played = len(season_data[team])
    game = random.randint(1, games_played)
    return season_data[team][game][side_of_ball]

def avg_stats(off_stats: dict, def_stats: dict):
    return_stats = {}
    off_pct = off_stats['STRS'] / (off_stats['STRS'] + def_stats['STRS'])
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

def simulate_game(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, opened = False, team1_stats = None, team2_stats = None):
    if not opened:
        file_league1_type = league_type1.replace('.', '')
        file_league2_type = league_type2.replace('.', '')
        with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
            team1_stats = pickle.load(pkl)
        with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
            team2_stats = pickle.load(pkl)
    team1_off = find_game(team1, team1_stats, 'offense')
    team1_def = find_game(team1, team1_stats, 'defense')
    team2_off = find_game(team2, team2_stats, 'offense')
    team2_def = find_game(team2, team2_stats, 'defense')
    new_team1_stats = avg_stats(team1_off, team2_def)
    new_team2_stats = avg_stats(team2_off, team1_def)
    return new_team1_stats, new_team2_stats

def multi_game_sim(team1: str, year1: str, league_type1: str, team2: str, year2: str, league_type2: str, games: int):
    return_dict = {team1: {'wins': 0, 'losses': 0}, team2: {'wins': 0, 'losses': 0}}
    file_league1_type = league_type1.replace('.', '')
    file_league2_type = league_type2.replace('.', '')
    start_time = time.time()
    with open(f"data/pickle/{year1} NBA Team Stats {file_league1_type}.pickle", "rb") as pkl:
        league1_season_stats = pickle.load(pkl)
    end_time = time.time()
    print(f"{end_time - start_time} seconds") 
    with open(f"data/pickle/{year2} NBA Team Stats {file_league2_type}.pickle", "rb") as pkl:
        league2_season_stats = pickle.load(pkl)
    for _ in range(games):
        team1_stats, team2_stats = simulate_game(team1, year1, league_type1, team2, year2, league_type2, True, league1_season_stats, league2_season_stats)
        if team1_stats['PTS'] > team2_stats['PTS']:
            return_dict[team1]['wins'] += 1
            return_dict[team2]['losses'] += 1
        else:
            return_dict[team2]['wins'] += 1
            return_dict[team1]['losses'] += 1
    return return_dict

if __name__ == '__main__':
    team1 = 'GSW'
    team2 = 'MIA'
    year1 = '2016-17'
    year2 = '2012-13'
    league_type1 = '2.0'
    league_type2 = '2.0'
    start_time = time.time()
    a = multi_game_sim(team1=team1, year1=year1, league_type1=league_type1, team2=team2, year2=year2, league_type2=league_type2, games=100_000)
    end_time = time.time()
    print(f"{end_time - start_time} seconds")
    print(a)

    
    