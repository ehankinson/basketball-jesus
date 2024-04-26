import csv
import time
import pickle


index_map = {'offense': [24, 25, 27, 28, 30, 31, 48, 49, 10, 16, 17, 13, 14],
           'defense': [37, 38, 40, 41, 43, 44, 51, 52, 15, 11, 12, 18, 19]}
def game_score(pts: float, fgm: float, fga: float, fta: float, ftm: float, orb: float, drb: float, stl: float, ast: float, blk: float, pf: float, tov: float):
    return round(pts + 0.4 * fgm - 0.7 * fga - 0.4 * (fta- ftm) + 0.7 * orb + 0.3 * drb + stl + 0.7 *ast + 0.7 * blk -0.4 * pf - tov, 1)

def stat_per_game(stat: int, game_path: str, stats_dict: dict):
    return stats_dict[stat] / stats_dict[game_path]

def calculate_pct(above: int, below: int):
    if below == 0:
        return 0.000
    return round(above / below, 3)

def putting_stats_in_dict(path: dict, indexes: list, line: list):
    keys = ['2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
    for key, index in zip(keys, indexes):
        path[key] = int(line[index])
    path['PTS'] = path['2PM'] * 2 + path['3PM'] * 3 + path['FTM']
    path['2P%'] = calculate_pct(path['2PM'], path['2PA'])
    path['3P%'] = calculate_pct(path['3PM'], path['3PA'])
    path['FT%'] = calculate_pct(path['FTM'], path['FTA'])
    path['TRB'] = path['ORB'] + path['DRB']
    path['FGM'] = path['2PM'] + path['3PM'] + path['FTM']
    path['FGA'] = path['2PA'] + path['3PA'] + path['FTA']
    path['FG%'] = calculate_pct(path['FGM'], path['FGA'])
    path['eFG%'] = calculate_pct((path['FGM'] + 0.5 * path['3PM']), path['FGA'])
    path['FP'] = round(path['3PM'] * 3 + path['2PM'] * 2 + path['FTM'] + path['ORB'] * 0.9 + path['DRB'] * 0.3 + path['AST'] * 1.5 + path['BLK'] * -2 + path['STL'] * -2 + path['TOV'] * -1, 1)
    path['GmSc'] = game_score(path['PTS'], path['FGM'], path['FGA'], path['FTA'], path['FTM'], path['ORB'], path['DRB'], path['STL'], path['AST'], path['BLK'], path['PF'], path['TOV'])
    path['STRS'] = round((path['PTS'] + path['FP'] + path['GmSc']) / 3, 3)
    

def process_team_data(reading_file: list, team_stats: dict, year: str):
    for line in reading_file:
        if line[1] == 'Team':
            continue
        team = line[1]
        if team not in team_stats:
            team_stats[team] = {}
        if year not in team_stats[team]:
            team_stats[team][year] = {}
        game = len(team_stats[team][year]) + 1
        if game not in team_stats[team][year]:
            team_stats[team][year][game] = {}
        #offense
        team_stats[team][year][game]['offense'] = {}
        putting_stats_in_dict(team_stats[team][year][game]['offense'], index_map['offense'], line)
        #defense
        team_stats[team][year][game]['defense'] = {}
        putting_stats_in_dict(team_stats[team][year][game]['defense'], index_map['defense'], line)



year = 2014
start = time.time()
team_stats = {}
while year < 2024:
    team_file = f"./data/{year}-{int(str(year)[2:]) + 1} NBA Team Stats.csv"
    with open(team_file, 'r') as team_file:
        reading_file = csv.reader(team_file)
        process_team_data(reading_file, team_stats, f"{year}-{int(str(year)[2:]) + 1}")
    year += 1
    


with open('team_stats.pickle', 'wb') as f:
    pickle.dump(team_stats, f)

print(f"Total Run Time: {time.time() - start}")


