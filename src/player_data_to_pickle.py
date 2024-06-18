import csv
import time
import json
import pickle


def process_csv_file(player_file: str, player_pos: dict, player_data: dict, ):
    with open(player_file, 'r', encoding="utf-8") as f:
        reading_file = csv.reader(f)
        date = ""
        tm = ""
        for line in reading_file:
            if line[1] == 'Player':
                continue
            pos = line[36]
            if pos not in player_pos:
                player_pos[pos] = []
            player = line[1]
            if player not in player_data:
                player_data[player] = {}
            if player not in player_pos[pos]:
                player_pos[pos].append(player)
            team = line[5]
            if team not in player_data[player]:
                player_data[player][team] = {}
            if date == "":
                date = line[3]
                tm = line[5]
                game = 1
            else:
                if line[5] != tm:
                    tm = line[5]
                    date = line[3]
                    game = 1
                elif line[3] != date:
                    game += 1
                    date = line[3]
            if game not in player_data[player][team]:
                player_data[player][team][game] = {}
            indexes = [10, 11, 12, 14, 15, 17, 18, 20, 21, 24, 25, 27, 28, 29, 30, 31, 32]
            keys = ['MP', 'FGM', 'FGA', '2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
            for index, key in zip(indexes, keys):
                player_data[player][team][game][key] = int(line[index])
        
def update_player_stats(new_player_dict: dict, player_stats: dict, og_game_stats: dict, needed_game_stats: dict):
    for key in player_stats:
        if key == 'BLK' or key == 'STL':
            side_of_ball = 'defense'
        else:
            side_of_ball = 'offense'
        if og_game_stats[side_of_ball][key] == 0:
            new_player_dict[key] = 0
        else:
            new_player_dict[key] = int(round((player_stats[key] / og_game_stats[side_of_ball][key]) * needed_game_stats[side_of_ball][key], 0))


def make_00_pickle(year: int):
    player_data = {}
    player_pos = {}
    player_file = f"data/csv/{year}-{int(str(year)[2:]) + 1} NBA Player Stats.csv"
    str_year = f"{year}-{int(str(year)[2:]) + 1}"
    process_csv_file(player_file, player_pos, player_data)
    pickle_dump = {'data': player_data, 'pos': player_pos}
    with open(f"data/pickle/{str_year} NBA Player Stats 00.pickle", "wb") as p:
        pickle.dump(pickle_dump, p)

def make_01_pickle(year: int):
    player_data = {}
    team_inverse = {}
    with open(f"data/json/standings/2023-24.json", "r") as j:
        year_standings = json.load(j)
    str_year = f"{year}-{int(str(year)[2:]) + 1}"
    with open(f"data/pickle/{str_year} NBA Player Stats 00.pickle", "rb") as p:
        og_player_stats = pickle.load(p)
    with open(f"data/pickle/{str_year} NBA Team Stats 00.pickle", "rb") as p:
        og_team_stats = pickle.load(p)
    with open(f"data/pickle/{str_year} NBA Team Stats 01.pickle", "rb") as p:
        version_team_stats = pickle.load(p)
    for player in og_player_stats['data']:
        if player == 'Miles Bridges':
            a = 5
        player_data[player] = {}
        for team in og_player_stats['data'][player]:
            player_data[player][team] = {}
            for game in og_player_stats['data'][player][team]:
                if game not in version_team_stats[team] or game not in og_team_stats[team]:
                    break
                player_data[player][team][game] = {}
                new_player_dict = player_data[player][team][game] 
                player_stats = og_player_stats['data'][player][team][game]
                og_game_stats = og_team_stats[team][game]
                needed_game_stats = version_team_stats[team][game]
                update_player_stats(new_player_dict, player_stats, og_game_stats, needed_game_stats)
            if len(version_team_stats[team]) > len(og_team_stats[team]):
                if team not in team_inverse:
                    if team in year_standings['East']:
                        conf = 'East'
                    else:
                        conf = 'West'
                    idx = year_standings[conf].index(team)
                    new_idx = (len(year_standings[conf]) - idx) - 1
                    inverse_team = year_standings[conf][new_idx]
                    team_inverse[team] = inverse_team
                inverse_team = team_inverse[team]
                game_diff = len(version_team_stats[team]) - len(og_team_stats[team])
                game_inverse = 0
                while game_inverse < game_diff:
                    if (82 - game_inverse) not in player_data[player][team]:
                        game_inverse += 1
                        continue
                    player_data[player][team][82 + game_inverse] = {}
                    new_player_dict = player_data[player][team][82 + game_inverse]
                    player_stats = og_player_stats['data'][player][team][82 - game_inverse]
                    og_game_stats = og_team_stats[team][82 - game_inverse]
                    needed_game_stats = version_team_stats[team][82 + game_inverse]
                    update_player_stats(new_player_dict, player_stats, og_game_stats, needed_game_stats)
                    game_inverse += 1                
    player_data['pos'] = og_player_stats['pos']
    with open(f"data/pickle/{str_year} NBA Player Stats 01.pickle", "wb") as p:
        pickle.dump(player_data, p)
            



def make_pickles():
    year = 2023
    end_year = year + 1
    cases = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    while year < end_year:
        for case in cases:
            match case:
                case 0:
                    make_00_pickle(year)
                case 1:
                    make_01_pickle(year)
        year += 1

if __name__ == '__main__':
    make_pickles()