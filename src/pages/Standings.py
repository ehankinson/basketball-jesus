import sys
import streamlit as st

sys.path.append('..')
from season_data import rank_teams
st.set_page_config(layout="wide")

def standings_table(ranked_teams: list[list], type: str):
    data_string = ""
    for index, line in enumerate(ranked_teams):
        for data in line:
            if type == 'conf':
                if index < 6:
                    data_string += f"|***{data}***"
                    continue
                if index < 10:
                    data_string += f"|*{data}*"
                    continue
            if type == 'div':
                if index < 1:
                   data_string += f"|***{data}***"
                   continue 
            data_string += f"| {data}"
        data_string += "|\n"
    
    table = f"""| Rank | Team | Season  | Games | Wins | Losses | Win Percentage |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{data_string}
"""
    return table

year = st.session_state.get('season')
st.header(f'Games Played in {year}')
if year == '2020-21':
    start_game, end_game = st.slider('', 1, 72, value=(1, 72))
else:
    start_game, end_game = st.slider('', 1, 82, value=(1, 82))
st.subheader(f"Games being shown are {start_game} to {end_game}, which is a total of {end_game - start_game + 1} games")
st.divider()
#----------------------------------------------------------------
# Conference Standings
st.title('Conference Results')
eastern, western = st.columns(2)
with eastern:
    st.header("Eastern Conference")
    teams = ["ATL", "BOS", "BRK", "CHI", "CHO", "CLE", "DET", "IND", "MIA", "MIL", "NYK", "ORL", "PHI", "TOR", "WAS"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'conf')
    st.markdown(table)

with western:
    st.header("Western Conference")
    teams = ["DAL", "DEN", "GSW", "HOU", "LAC", "LAL", "MEM", "MIN", "NOP", "OKC", "PHO", "POR", "SAC", "SAS", "UTA"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'conf')
    st.markdown(table)

st.divider()
#----------------------------------------------------------------
# Division Standings
st.title('Division Results')
eastern, western = st.columns(2)
with eastern:
    st.header("Atlantic")
    teams = ["BOS", "BRK", "NYK", "PHI", "TOR"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'div')
    st.markdown(table)

    st.header("Central")
    teams = ["CHI", "CLE", "DET", "IND", "MIL"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'div')
    st.markdown(table)

    st.header("Southeast")
    teams = ["ATL", "CHO", "MIA", "ORL", "WAS"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'div')
    st.markdown(table)

with western:
    st.header("Northwest")
    teams = ["DEN", "MIN", "OKC", "POR", "UTA"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'div')
    st.markdown(table)

    st.header("Pacific")
    teams = ["GSW", "LAC", "LAL", "PHO", "SAC"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'div')
    st.markdown(table)

    st.header("Southwest")
    teams = ["DAL", "HOU", "MEM", "NOP", "SAS"]
    ranked_teams = rank_teams(teams, year, st.session_state['league_type'], end_game, start_game)
    table = standings_table(ranked_teams, 'div')
    st.markdown(table)







