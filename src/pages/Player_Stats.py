import sys
import json
import pickle
import pandas as pd
import streamlit as st
sys.path.append('..')
from season_data import player_rankings
st.set_page_config(layout="wide")
year = st.session_state.get('season')

with open("data/json/teams.json", "r") as j:
    NBA_TEAMS = json.load(j)

st.title("Select League Information")
multi_season = st.toggle("Do you want multiple seasons")
teams_select, season_type, season, league_type = st.columns(4)
with teams_select:
    option = st.selectbox(
        'What teams would you like to display',
        ['League']
    )
    league_teams = [team for team in NBA_TEAMS if len(team) == 3]
    teams = {
    'League': league_teams,
    }
    
    team_list = teams[option]

with season_type:
    season_type_opt = st.selectbox("Games", ['Regular Season', 'Post Season', 'Regular & Post Season'])
with season:
    seasons = {'2023-24': 0, '2022-23': 1, '2021-22': 2, '2020-21': 3, '2019-20': 4, '2018-19': 5, '2017-18': 6, '2016-17': 7, '2015-16': 8,
    '2014-15': 9, '2013-14': 10, '2012-13': 11, '2011-12': 12, '2010-11': 13, '2009-10': 14, '2008-09': 15, '2007-08': 16, '2006-07': 17,
    '2005-06': 18, '2004-05': 19, '2003-04': 20, '2002-03': 21, '2001-02': 22, '2000-01': 23, '1999-00': 24, '1998-99': 25, '1997-98': 26,
    '1996-97': 27, '1995-96': 28, '1994-95': 29, '1993-94': 30, '1992-93': 31, '1991-92': 32}
    if not multi_season:
        season = st.selectbox('Select season', list(seasons.keys()), index=0, placeholder='Select Season', key='season')
    else:
        seasons = st.multiselect('Select season', list(seasons.keys()),  placeholder='Select Season', key='season')
with league_type:
    versions = ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1', '3.0', '3.1', '4.0']
    league_type = st.selectbox("Select League Type", versions, index=0, placeholder='Select League Type', key='league_type')

st.divider()

#-------------------------------------------------------------------------------
# Player Stats Display
st.header("Select Player Information Information")
conference, division, team, positions = st.columns(4)

with conference:
    conferences = ['Both', 'Eastern', 'Western']
    conf = st.selectbox("Pick a Conference", conferences, index=0, placeholder="Choose a Conference")

with division:
    if conf == 'Western':
        divisions = ['ALL', "Northwest", "Pacific", "Southwest"]
    elif conf == 'Eastern':
        divisions = ['ALL', "Atlantic", "Central", "Southeast"]
    else:
        divisions = ["ALL", "Northwest", "Pacific", "Southwest", "Atlantic", "Central", "Southeast"]
    division = st.selectbox("Pick Division", divisions)
    
with team:
    teams_abr = []
    team_full_name = []
    for team in NBA_TEAMS:
        if len(team) > 3:
            team_full_name.append(team)
        else:
            teams_abr.append(team)
    teams_abr.insert(0, "ALL")
    team = st.selectbox("Picke A Team", teams_abr, index=0)

with positions:
    positions = ['ALL', 'G', 'F', 'C', 'G-F', 'F-C', 'F-G']
    position = st.selectbox("Pick Position", positions, index=0, placeholder="Choose a Position")

st.divider()

year = st.session_state.get('season')
if multi_season:
    st.header(f"Games Played in the years you've choosen")
else:
    st.header(f'Games Played in {year}')
if year == "2020-21" or year == '2019-20':
    if season_type_opt == 'Regular Season':
        start_game, end_game = st.slider('Regular Season Games', 1, 72, value=(1, 72))
    elif  season_type_opt == 'Post Season':
        start_game, end_game = st.slider('Post Season Games', 1, 28, value=(1, 28))
    else:
        start_game, end_game = st.slider('Total Season Games', 1, 100, value=(1, 100))
else:
    if season_type_opt == 'Regular Season':
        start_game, end_game = st.slider('Regular Season Games', 1, 82, value=(1, 82))
    elif  season_type_opt == 'Post Season':
        start_game, end_game = st.slider('Post Season Games', 1, 28, value=(1, 28))
    else:
        start_game, end_game = st.slider('Total Season Games', 1, 110, value=(1, 110))
st.subheader(f"Games being shown are {start_game} to {end_game}, which is a total of {end_game - start_game + 1} games")

st.divider()

st.title("Player Rankings")
if season_type_opt == "Post Season":
    ranked_players = player_rankings(team_full_name, year, league_type, conf, division, team, position, end_game + 82, start_game + 82)
else:
    ranked_players = player_rankings(team_full_name, year, league_type, conf, division, team, position, end_game, start_game)
columns = ['Name', 'Year', 'Pos', 'GP', 'MP', 'PTS', 'FGM', 'FGA', 'FG%', 'eFG%','2PM', '2PA', '2P%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'FP', 'GmSc', 'SPRS']
df = pd.DataFrame(ranked_players, columns=columns)
st.dataframe(df, hide_index=True, height=1015)
st.divider()

