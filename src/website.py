import streamlit as st
st.set_page_config(layout="wide")

# st.session_state['NBA_Teams'] = {
#     "ATL": "Atlanta Hawks",
#     "BOS": "Boston Celtics",
#     "BRK": "Brooklyn Nets",
#     "CHI": "Chicago Bulls",
#     "CHO": "Charlotte Hornets",
#     "CLE": "Cleveland Cavaliers",
#     "DAL": "Dallas Mavericks",
#     "DEN": "Denver Nuggets",
#     "DET": "Detroit Pistons",
#     "GSW": "Golden State Warriors",
#     "HOU": "Houston Rockets",
#     "IND": "Indiana Pacers",
#     "LAC": "Los Angeles Clippers",
#     "LAL": "Los Angeles Lakers",
#     "MEM": "Memphis Grizzlies",
#     "MIA": "Miami Heat",
#     "MIL": "Milwaukee Bucks",
#     "MIN": "Minnesota Timberwolves",
#     "NOP": "New Orleans Pelicans",
#     "NYK": "New York Knicks",
#     "OKC": "Oklahoma City Thunder",
#     "ORL": "Orlando Magic",
#     "PHI": "Philadelphia 76ers",
#     "PHO": "Phoenix Suns",
#     "POR": "Portland Trail Blazers",
#     "SAC": "Sacramento Kings",
#     "SAS": "San Antonio Spurs",
#     "TOR": "Toronto Raptors",
#     "UTA": "Utah Jazz",
#     "WAS": "Washington Wizards"
# }

st.title("Hello, world!")
seasons = {'2023-24': 0, '2022-23': 1, '2021-22': 2, '2020-21': 3, '2019-20': 4, '2018-19': 5, '2017-18': 6, '2016-17': 7, '2015-16': 8,
    '2014-15': 9, '2013-14': 10, '2012-13': 11, '2011-12': 12, '2010-11': 13, '2009-10': 14, '2008-09': 15, '2007-08': 16, '2006-07': 17,
    '2005-06': 18, '2004-05': 19, '2003-04': 20, '2002-03': 21, '2001-02': 22, '2000-01': 23, '1999-00': 24, '1998-99': 25, '1997-98': 26,
    '1996-97': 27, '1995-96': 28, '1994-95': 29, '1993-94': 30, '1992-93': 31, '1991-92': 32}

# st.session_state['seasons'] = seasons


season_list = list(seasons.keys())
if 'season' in st.session_state:
    season = st.selectbox('Which Season', season_list, index=seasons[st.session_state['season']])
else:
    season = st.selectbox('Which Season', list(seasons.keys()), index=None, placeholder="Please pick a year")

if season != None:
    st.session_state['season'] = season
    st.header(f"The current season is {st.session_state['season']}")
else:
    st.header("Please Select a Season")

st.subheader('Select the league type')

versions = ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1', '3.0', '3.1', '4.0']
if 'league_type' in st.session_state:
    index = versions.index(st.session_state['league_type'])
    league_type = st.radio("", versions, index=index, horizontal=True)
else:
    league_type = st.radio("", versions, horizontal=True)

if league_type != None:
    st.session_state['league_type'] = league_type