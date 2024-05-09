import pickle

year = 2021
# with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Standings.pickle", "wb") as pk:
#     standings = {
#         'East': ['MIA', 'BOS', 'MIL', 'PHI', 'TOR', 'CHI', 'BRK', 'CLE', 'ATL', 'CHO', 'NYK', 'WAS', 'IND', 'DET', 'ORL'],
#         'West': ['PHO', 'MEM', 'GSW', 'DAL', 'UTA', 'DEN', 'MIN', 'LAC', 'NOR', 'SAN', 'LAL', 'SAC', 'POR', 'OKC', 'HOU']
#     }
#     pickle.dump(standings, pk)
with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Standings.pickle", "rb") as pk:
    standings = pickle.load(pk)
standings['West'][9] = 'SAS'
with open(f"./data/pickle/{year}-{int(str(year)[2:]) + 1} NBA Standings.pickle", "wb") as pk:
    pickle.dump(standings, pk)
