import sys
import json
import pandas as pd
import streamlit as st
from PIL import Image
sys.path.append('..')
from simulations import simulate_game, best_of
from season_data import calculate_pct, team_record

def resize_image(image_path, width):
    # Open the image
    image = Image.open(image_path)
    
    # Calculate aspect ratio and new height
    aspect_ratio = image.height / image.width
    new_height = int(aspect_ratio * width)
    
    # Handle different Pillow versions for resampling attribute
    try:
        resample_method = Image.Resampling.BILINEAR
    except AttributeError:
        resample_method = Image.BILINEAR

    # Resize the image
    resized_image = image.resize((width, new_height), resample=resample_method)
    return resized_image

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
        reversed_years = team_years[::-1]
        away_year = st.selectbox("Choose the away teams Year", reversed_years)
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
        team_years = year_list(away_team)
        reversed_years = team_years[::-1]
        if away_team == home_team:
            idx_remove = reversed_years.index(away_year)
            reversed_years.pop(idx_remove)
        home_year = st.selectbox("Choose the home teams Year", reversed_years)
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

# Initial state setup
if 'multi_game' not in st.session_state:
    st.session_state['multi_game'] = False
if 'games' not in st.session_state:
    st.session_state['games'] = ''

games_played = False
what_game_version = None

# Layout columns
game_sim, multi_game_sim, buff, buff, buff, buff, buff, buff = st.columns(8)

# Simulate Game button
with game_sim:
    if st.button("Simulate Game"):
        what_game_version = 1
        away_stats, home_stats = simulate_game(
            nba_teams[away_team]['abr'], away_year, away_type, 
            nba_teams[home_team]['abr'], home_year, home_type
        )
        games_played = True

# Multiple Games button and input
with multi_game_sim:
    if st.button("Best_of"):
        st.session_state['multi_game'] = True
        what_game_version = 2

# Text input for number of games
if st.session_state['multi_game']:
    st.session_state['games'] = st.text_input("Please Insert the amount of games you want them to play")

# Processing multiple games simulation
if st.session_state['multi_game'] and st.session_state['games'].isdigit():
    num_games = int(st.session_state['games'])
    away_stats, home_stats, records = best_of(
        nba_teams[away_team]['abr'], away_year, away_type, 
        nba_teams[home_team]['abr'], home_year, home_type, num_games, {}, {}
    )
    st.session_state['multi_game'] = False
    games_played = True



st.divider()
if games_played:
    # game header:
    away_logo, away_pts, middle, home_pts, home_logo = st.columns(5)
    with away_logo:
        resized_image = resize_image(photos[away_team], 200)
        st.image(resized_image, caption=f"{away_team}-{away_year}")
    with away_pts:
        if what_game_version == 1:
            add = away_stats['PTS']
        else:
            add = records[f"{nba_teams[away_team]['abr']}'{away_year}"]['wins']
        st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                <div>
                    <p>&nbsp;</p>  <!-- Empty paragraph to create vertical space -->
                    <p style="font-size: 55px;">{add}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with middle:
        st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                <div>
                    <p>&nbsp;</p>  <!-- Empty paragraph to create vertical space -->
                    <p style="font-size: 55px;">-</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with home_pts:
        if what_game_version == 1:
            add = home_stats['PTS']
        else:
            add = records[f"{nba_teams[home_team]['abr']}'{home_year}"]['wins']
        st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                <div>
                    <p>&nbsp;</p>  <!-- Empty paragraph to create vertical space -->
                    <p style="font-size: 55px;">{add}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with home_logo:
        resized_image = resize_image(photos[home_team], 200)
        st.image(resized_image, caption=f"{home_team}-{home_year}")

    # away1, abr1, home1 = st.columns(3)
    # with away1:
    #     resized_image = resize_image(photos[away_team], 100)
    #     st.image(resized_image)
    #     st.write(away_stats['PTS'] / games)
    #     st.metric("", f"{away_stats['FGM'] / games} / {away_stats['FGA'] / games}")
    #     st.metric("", f"{calculate_pct(away_stats['FGM'] / games, away_stats['FGA'] / games)}")
    #     st.metric("", f"{away_stats['3PM'] / games} / {away_stats['3PA'] / games}")
    #     st.metric("", f"{calculate_pct(away_stats['3PM'] / games, away_stats['3PA']) / games}")
    #     st.metric("", f"{away_stats['FTM'] / games} / {away_stats['FTA'] / games}")
    #     st.metric("", f"{calculate_pct(away_stats['FTM'] / games, away_stats['FTA']) / games}")
    #     st.divider()
    #     st.metric("", f"{away_stats['TRB'] / games}")
    #     st.metric("", f"{away_stats['ORB'] / games}")
    #     st.metric("", f"{away_stats['DRB'] / games}")
    #     st.metric("", f"{away_stats['AST'] / games}")
    #     st.metric("", f"{away_stats['BLK'] / games}")
    #     st.metric("", f"{away_stats['STL'] / games}")
    #     st.metric("", f"{away_stats['TOV'] / games}")
    #     st.metric("", f"{away_stats['PF'] / games}")
    # with abr1:
    #     st.write("Points")
    #     st.metric("", "Field Goals")
    #     st.metric("", "Field Goal %")
    #     st.metric("", "3 Pointers")
    #     st.metric("", "Three Point %")
    #     st.metric("", "Free Throw")
    #     st.metric("", "Free Throw %")
    #     st.divider()
    #     st.metric("", "Total Rebounds")
    #     st.metric("", "Offensive Rebounds")
    #     st.metric("", "Defensive Rebounds")
    #     st.metric("", "Assists")
    #     st.metric("", "Blocks")
    #     st.metric("", "Steals")
    #     st.metric("", "Turnovers")
    #     st.metric("", "Fouls - Personal")
    # with home1:
    #     st.write(home_stats['PTS'])
    #     st.metric("", f"{home_stats['FGM'] / games} / {home_stats['FGA'] / games}")
    #     st.metric("", f"{calculate_pct(home_stats['FGM'] / games, home_stats['FGA'] / games)}")
    #     st.metric("", f"{home_stats['3PM'] / games} / {home_stats['3PA'] / games}")
    #     st.metric("", f"{calculate_pct(home_stats['3PM'] / games, home_stats['3PA'] / games)}")
    #     st.metric("", f"{home_stats['FTM'] / games} / {home_stats['FTA'] / games}")
    #     st.metric("", f"{calculate_pct(home_stats['FTM'] / games, home_stats['FTA'] / games)}")
    #     st.divider()
    #     st.metric("", f"{home_stats['TRB'] / games}")
    #     st.metric("", f"{home_stats['ORB'] / games}")
    #     st.metric("", f"{home_stats['DRB'] / games}")
    #     st.metric("", f"{home_stats['AST'] / games}")
    #     st.metric("", f"{home_stats['BLK'] / games}")
    #     st.metric("", f"{home_stats['STL'] / games}")
    #     st.metric("", f"{home_stats['TOV'] / games}")
    #     st.metric("", f"{home_stats['PF']/ games}")

# with multi_game:
#     if st.button("Multiple Games"):
#         games = st.text_input("Please Insert the amount of games you want them to play")
#         if games != '':
#             away_stats, home_stats = multi_game_sim(nba_teams[away_team]['abr'], away_year, away_type, nba_teams[home_team]['abr'], home_year, home_type, int(games))
#             if away_stats['PTS'] > home_stats['PTS']:
#                 text = f"The {away_team}'{away_year} has beeten the {home_team}'{home_year}: {away_stats['PTS']} to {home_stats['PTS']}"
#             else:
#                 text = f"The {home_team}'{home_year} has beeten the {away_team}'{away_year}: {home_stats['PTS']} to {away_stats['PTS']}"
#             st.header(text)

            