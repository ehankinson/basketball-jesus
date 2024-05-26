import sys
import pandas as pd
import streamlit as st

sys.path.append('..')
from season_data import power_rankings
st.set_page_config(layout="wide")
year = st.session_state.get('season')

teams_select, season_type, season, league_type = st.columns(4)
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
    
    if year != None and int(year[:4]) < 2014:
        teams['League'][3] = 'CHA'
        teams['Eastern'][3] = 'CHA'
        teams['Southeast'][1] = 'CHA'
    if year != None and int(year[:4]) < 2014:
        teams['League'][18] = 'NOH'
        teams['Western'][8] = 'NOH'
        teams['Southwest'][3] = 'NOH'
    if year != None and int(year[:4]) < 2011:
        teams['League'][2] = 'NJN'
        teams['Eastern'][2] = 'NJN'
        teams['Atlantic'][1] = 'NJN'
    if year != None and int(year[:4]) < 2008:
        teams['League'][20] = 'SEA'
        teams['Western'][9] = 'SEA'
        teams['Northwest'][2] = 'SEA'
    team_list = teams[option]

with season_type:
    season_type_opt = st.selectbox("Games", ['Regular Season', 'Post Season', 'Regular & Post Season'])
with season:
    seasons = {'2023-24': 0, '2022-23': 1, '2021-22': 2, '2020-21': 3, '2019-20': 4, '2018-19': 5, '2017-18': 6, '2016-17': 7, '2015-16': 8,
    '2014-15': 9, '2013-14': 10, '2012-13': 11, '2011-12': 12, '2010-11': 13, '2009-10': 14, '2008-09': 15, '2007-08': 16, '2006-07': 17,
    '2005-06': 18, '2004-05': 19, '2003-04': 20, '2002-03': 21, '2001-02': 22, '2000-01': 23, '1999-00': 24, '1998-99': 25, '1997-98': 26,
    '1996-97': 27, '1995-96': 28, '1994-95': 29, '1993-94': 30, '1992-93': 31, '1991-92': 32}
    season = st.selectbox('Select season', list(seasons.keys()), index=None, placeholder='Select Season', key='season')
with league_type:
    versions = ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1', '3.0', '3.1', '4.0']
    league_type = st.selectbox("", versions, index=None, placeholder='Select League Type', key='league_type')

year = st.session_state.get('season')
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


#----------------------------------------------------------------
# Power Rankings
st.title("Power Rankings")
if season_type_opt == 'Post Season':
    if year == '2020-21' or year == '2019-20':
        ranked_teams = power_rankings(team_list, year, st.session_state['league_type'], end_game + 72, start_game + 72)
    else:
        ranked_teams = power_rankings(team_list, year, st.session_state['league_type'], end_game + 82, start_game + 82)
else:
    ranked_teams = power_rankings(team_list, year, st.session_state['league_type'], end_game, start_game)
columns = ['Rank', 'Teams', 'Year', 'GP', 'Wins', 'Losses', 'Pct', 'SRS', 'STRS', 'SORS','SDRS', 'PF', 'PA', 'DIFF', 'FP For', 'FP Againts', 'Diff', 'Off GmSc', 'Def GmSc', 'Game Score Diff']
display_columns = ['Teams', 'Year', 'GP', 'Wins', 'Losses', 'Pct', 'SRS', 'STRS', 'SORS','SDRS', 'PF', 'PA', 'DIFF', 'Fantasy Poitns For', 'Fantasy Points Againts', 'Diff', 'Off Game Score', 'Def Game Score', 'Game Score Diff']
df = pd.DataFrame(ranked_teams, columns=columns)
# df = df[display_columns]
st.dataframe(df, hide_index=True, height=1015)
st.divider()

def upper_everthing(elements: list[str]) -> list[str]:
    return [element.upper() for element in elements]


thing: list[int] = [1, 2, 3, 4, 5]
word_list: list[int] = upper_everthing(thing)