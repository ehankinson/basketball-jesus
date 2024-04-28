import csv
import time
import pickle

player_data = {}
player_pos = {}
year = 2023
while year < 2024:
    player_file = f"./data/{year}-{int(str(year)[2:]) + 1} NBA Player Stats.csv"
    str_year = f"{year}-{int(str(year)[2:]) + 1}"
    with open(player_file, 'r', encoding="utf-8") as f:
        reading_file = csv.reader(f)
        start_time = time.time()
        date = ""
        tm = ""
        for line in reading_file:
            if line[1] == 'Player':
                continue
            if str_year not in player_pos:
                player_pos[str_year] = {}
            pos = line[36]
            if pos not in player_pos[str_year]:
                player_pos[str_year][pos] = []
            player = line[1]
            if player not in player_data:
                player_data[player] = {}
            if player not in player_pos[str_year][pos]:
                player_pos[str_year][pos].append(player)
            if str_year not in player_data[player]:
                player_data[player][str_year] = {}
            team = line[5]
            if team not in player_data[player][str_year]:
                player_data[player][str_year][team] = {}
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
            if game not in player_data[player][str_year][team]:
                player_data[player][str_year][team][game] = {}
            indexes = [10, 11, 12, 14, 15, 17, 18, 20, 21, 24, 25, 27, 28, 29, 30, 31, 32]
            keys = ['MP', 'FGM', 'FGA', '2PM', '2PA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
            for index, key in zip(indexes, keys):
                player_data[player][str_year][team][game][key] = int(line[index])
        year += 1
end_time = time.time()
print(f"It took {end_time - start_time} seconds")

with open('player_data.pickle', 'wb') as f:
    pickle.dump(player_data, f)

with open('player_pos.pickle', 'wb') as f:
    pickle.dump(player_pos, f)       