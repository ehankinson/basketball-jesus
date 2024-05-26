import sys
import json
import pandas as pd
import streamlit as st
sys.path.append('..')
from simulations import simulate_game
from season_data import calculate_pct, team_record


st.title("Simulate Some of the Craziest Matchups in History")

with open(f"data/json/teams.json", "r") as j:
    nba_teams = json.load(j)

with open(f"data/json/team_to_photo.json", "r") as p:
    photos = json.load(p)

def year_list(team: str) -> list[str]:
    start_year: str = nba_teams[team]['start_year']
    end_year: str = nba_teams[team]['end_year']
    years: list[str] = []
    start_year: int = int(start_year[:4])
    end_year: int = int(end_year[:4])
    for year in range(start_year, end_year + 1):
        back_end = str(year + 1)[-2:]
        years.append(f"{year}-{back_end}")
    return years

away_team, home_team = st.columns(2)
with away_team:
    st.header("Away Team")
    away_team: str = st.selectbox("Choose the Away Team", nba_teams.keys())
    st.image(photos[away_team], caption=f"The {away_team} Logo")
    years, league_type = st.columns(2)
    with years:
        team_years = year_list(away_team)
        away_year = st.selectbox("Choose the away teams Year", team_years, index=len(team_years) - 1)
    with league_type:
        away_type = st.selectbox("Select the away Team Version", ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1', '3.0', '3.1', '4.0'])
    away_record = team_record(nba_teams[away_team]['abr'], away_year, away_type, 82)
    wins, losses, pct, buff, buff, buff = st.columns(6)
    with wins:
        st.metric("Team Wins", away_record['Wins'])
    with losses:
        st.metric("Team Losses", away_record['Loses'])
    with pct:
        st.metric("Team Win %", round(away_record['Wins'] / (away_record['Wins'] + away_record['Loses']), 3))
with home_team:
    st.header("Home Team")
    home_team: str = st.selectbox("Choose the Home Team", nba_teams.keys())
    st.image(photos[home_team], caption=f"The {home_team} Logo")
    years, league_type = st.columns(2)
    with years:
        team_years = year_list(home_team)
        home_year = st.selectbox("Choose the home teams Year", team_years, index=len(team_years) - 1)
    with league_type:
        home_type = st.selectbox("Select the home Team Version", ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1', '3.0', '3.1', '4.0'])
    home_record = team_record(nba_teams[home_team]['abr'], home_year, home_type, 82)
    wins, losses, pct, buff, buff, buff = st.columns(6)
    with wins:
        st.metric("Team Wins", home_record['Wins'])
    with losses:
        st.metric("Team Losses", home_record['Loses'])
    with pct:
        st.metric("Team Win %", round(home_record['Wins'] / (home_record['Wins'] + home_record['Loses']), 3))

if st.button("Simulate Game"):

    away_stats, home_stats = simulate_game(nba_teams[away_team]['abr'], away_year, away_type, nba_teams[home_team]['abr'], home_year, home_type)
    if away_stats['PTS'] > home_stats['PTS']:
        text = f"The {away_team}'{away_year} has beeten the {home_team}'{home_year}: {away_stats['PTS']} to {home_stats['PTS']}"
    else:
        text = f"The {home_team}'{home_year} has beeten the {away_team}'{away_year}: {home_stats['PTS']} to {away_stats['PTS']}"
    st.header(text)
    st.markdown(
    """
    <style>
    .css-1v3fvcr > div > p { 
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    away1, abr1, home1 = st.columns(3)
    with away1:
        st.metric("", away_stats['PTS'])
        st.metric("", f"{away_stats['FGM']} / {away_stats['FGA']}")
        st.metric("", f"{calculate_pct(away_stats['FGM'], away_stats['FGA'])}")
        st.metric("", f"{away_stats['3PM']} / {away_stats['3PA']}")
        st.metric("", f"{calculate_pct(away_stats['3PM'], away_stats['3PA'])}")
        st.metric("", f"{away_stats['FTM']} / {away_stats['FTA']}")
        st.metric("", f"{calculate_pct(away_stats['FTM'], away_stats['FTA'])}")
        st.divider()
        st.metric("", f"{away_stats['TRB']}")
        st.metric("", f"{away_stats['ORB']}")
        st.metric("", f"{away_stats['DRB']}")
        st.metric("", f"{away_stats['AST']}")
        st.metric("", f"{away_stats['BLK']}")
        st.metric("", f"{away_stats['STL']}")
        st.metric("", f"{away_stats['TOV']}")
        st.metric("", f"{away_stats['PF']}")
    with abr1:
        st.metric("", "Points")
        st.metric("", "Field Goals")
        st.metric("", "Field Goal %")
        st.metric("", "3 Pointers")
        st.metric("", "Three Point %")
        st.metric("", "Free Throw")
        st.metric("", "Free Throw %")
        st.divider()
        st.metric("", "Total Rebounds")
        st.metric("", "Offensive Rebounds")
        st.metric("", "Defensive Rebounds")
        st.metric("", "Assists")
        st.metric("", "Blocks")
        st.metric("", "Steals")
        st.metric("", "Turnovers")
        st.metric("", "Fouls - Personal")
    with home1:
        st.metric("", home_stats['PTS'])
        st.metric("", f"{home_stats['FGM']} / {home_stats['FGA']}")
        st.metric("", f"{calculate_pct(home_stats['FGM'], home_stats['FGA'])}")
        st.metric("", f"{home_stats['3PM']} / {home_stats['3PA']}")
        st.metric("", f"{calculate_pct(home_stats['3PM'], home_stats['3PA'])}")
        st.metric("", f"{home_stats['FTM']} / {home_stats['FTA']}")
        st.metric("", f"{calculate_pct(home_stats['FTM'], home_stats['FTA'])}")
        st.divider()
        st.metric("", f"{home_stats['TRB']}")
        st.metric("", f"{home_stats['ORB']}")
        st.metric("", f"{home_stats['DRB']}")
        st.metric("", f"{home_stats['AST']}")
        st.metric("", f"{home_stats['BLK']}")
        st.metric("", f"{home_stats['STL']}")
        st.metric("", f"{home_stats['TOV']}")
        st.metric("", f"{home_stats['PF']}")