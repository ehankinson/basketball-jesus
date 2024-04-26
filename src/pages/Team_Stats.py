import sys
import pandas as pd
import streamlit as st
sys.path.append('..')
from season_data import season_stats

st.set_page_config(layout="wide")

def team_stats_to_list(team: str, year: str, league_type: str, stat_type: str, end_game: int, start_game: int):
    team_stats = season_stats(team, year, league_type, stat_type, end_game, start_game)
    if team_stats == 'Did Not Make Playoffs':
        return 'Did Not Make Playoffs'
    keys = ['GP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%','2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
    team_list = [st.session_state['NBA_Teams'][team], year]
    for key in keys:
        if key == 'GP' or '%' in key:
            team_list.append(team_stats[key])
            continue
        team_list.append(round(team_stats[key] / team_stats['GP'], 1))
    team_list.append(round(team_stats['FP'] / team_stats['GP'], 2))
    team_list.append(team_stats['GmSc'])
    team_list.append(team_stats['STRS'])
    return team_list

def league_team_stats(team_list: list, season_type_opt: str, league_type: str, type: str):
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

year = st.session_state.get('season') 
st.header(f'Games Played in {year}')
teams_select, season_type, buff1, buff2, buff3 = st.columns(5)

with teams_select:
    option = st.selectbox(
        'What teams would you like to display',
        ['League', 'Eastern', 'Western', 'Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest']
    )
    teams = {
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
    team_list = teams[option]

with season_type:
    season_type_opt = st.selectbox("Games", ['Regular Season', 'Post Season', 'Regular & Post Season'])
if year == "2020-21":
    if season_type_opt == 'Regular Season':
        start_game, end_game = st.slider('Regular Season Games', 1, 72, value=(1, 72))
    elif  season_type_opt == 'Post Season':
        start_game, end_game = st.slider('Post Season Games', 1, 28, value=(1, 28))
    else:
        start_game, end_game = st.slider('Total Season Games', 1, 28, value=(1, 100))
else:
    if season_type_opt == 'Regular Season':
        start_game, end_game = st.slider('Regular Season Games', 1, 82, value=(1, 82))
    elif  season_type_opt == 'Post Season':
        start_game, end_game = st.slider('Post Season Games', 1, 28, value=(1, 28))
    else:
        start_game, end_game = st.slider('Total Season Games', 1, 28, value=(1, 110))
st.subheader(f"Games being shown are {start_game} to {end_game}, which is a total of {end_game - start_game + 1} games")

st.divider()

#----------------------------------------------------------------
# Offensive Stats Standings
if season_type_opt == 'Post Season':
    height = 598
else:
    height = 1087
st.header("Teams Offensive Statistics")
total_stats = league_team_stats(team_list, season_type_opt, st.session_state['league_type'],'offense')
columns = ['Teams', 'Year', 'GP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%','2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'Fantasy Points', 'Game Score', 'SORS']
display_columns = ['Teams', 'Year', 'GP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'Fantasy Points', 'Game Score', 'SORS']
df = pd.DataFrame(total_stats, columns=columns)
df = df[display_columns]
st.dataframe(df, hide_index=True, height=height)
st.divider()

#----------------------------------------------------------------
# Defensive Stats Standings
st.header("Teams Defensive Statistics")
total_stats = league_team_stats(team_list, season_type_opt, st.session_state['league_type'], 'defense')
columns = ['Teams', 'Year', 'GP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%','2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'Fantasy Points', 'Game Score', 'SORS']
display_columns = ['Teams', 'Year', 'GP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'Fantasy Points', 'Game Score', 'SORS']
df = pd.DataFrame(total_stats, columns=columns)
df = df[display_columns]
st.dataframe(df, hide_index=True, height=height)
st.divider()
