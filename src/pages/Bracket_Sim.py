import sys
import json
import math
import pandas as pd
import streamlit as st
from PIL import Image
sys.path.append('..')
from simulations import simulate_bracket, multi_bracket_sim, simulate_double_elimination_bracket
from season_data import rank_custon_teams, rank_bracket_team
from tournament import bracket_generator, double_bracket_generator
from website import NBA_TEAMS

LEAGUE_TYPES = ["0.0", "0.1", "1.0", "1.1", "2.0", "2.1", "3.0", "3.1", "4.0"]

with open(f"data/json/team_to_photo.json", "r") as p:
    photos = json.load(p)

st.title("Simulate the Playoff Bracket of your dreams")
st.divider()

def reset_teams():
    for key in st.session_state.keys():
        del st.session_state[key]

def reverse_teams():
    team_keys = []
    for key in st.session_state.keys():
        if 'team' in key and 'list' not in key:
            team_keys.append(key)
    team_keys = sorted(team_keys, key=lambda x: int(x[4:]))
    start_idx = 1
    end_idx = len(team_keys) - 1
    while start_idx < end_idx:
        start_key = team_keys[start_idx]
        end_key = team_keys[end_idx]
        new_bottom = st.session_state[start_key]
        new_top = st.session_state[end_key]
        st.session_state[start_key] = new_top
        st.session_state[end_key] = new_bottom
        start_idx += 1
        end_idx -= 1

def rank_teams():
    teams_to_rank = []
    keys_to_replace = []
    for key in st.session_state.keys():
        if 'team' in key and 'list' not in key and key != "team0":
            if st.session_state[key]['team'] == None:
                continue
            teams_to_rank.append([st.session_state[key]])
            keys_to_replace.append(key)
    sorted_keys = sorted(keys_to_replace, key=lambda x: int(x[4:]))
    ranked_teams = rank_custon_teams(teams_to_rank)
    for key, team in zip(sorted_keys, ranked_teams):
        st.session_state[key]['team'] = NBA_TEAMS[team[0]]['team']
        st.session_state[key]['year'] = team[1]
        st.session_state[key]['league_type'] = team[2]

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

st.subheader("Input the size of the bracket you wish to simulate")
n_teams = st.text_input("Number of teams")
series_max = st.text_input("What is the max games in the series. Ex: 7 for best of 7 (4 wins to move on)")
reset, reverse, rank, buff, buff, buff, buff, buff = st.columns(8)

with reset:
    if st.button("Reset Teams"):
        reset_teams()
        st.session_state['team_list'] = {}

with reverse:
    if st.button("Revese Teams"):
        reverse_teams()

with rank:
    if st.button("Rank Teams"):
        rank_teams()

st.divider()

full_team_name = [team for team in NBA_TEAMS.keys() if len(team) > 3]
if n_teams != "":
    view_teams = st.toggle("View Teams", value=True)
    if view_teams:
        if 'team_list' not in st.session_state:
            st.session_state['team_list'] = {}
        for team_seed, _ in enumerate(range(int(n_teams) + 1)):
            
            if f"team{team_seed}" not in st.session_state:
                st.session_state[f"team{team_seed}"] = {'team': None, 'year': None, 'league_type': None}
            seed, team_name, team_year, league_type = st.columns(4)
            
            with seed:
                if team_seed == 0:
                    st.header("Seedings")
                    st.divider()
                else:
                    match team_seed:
                        case 1:
                            st.divider()
                            seed_str = "1st"
                        case 2:
                            seed_str = "2nd"
                        case 3:
                            seed_str = "3rd"
                        case _ if team_seed > 3:
                            seed_str = f"{team_seed}th"
                    st.subheader(seed_str)

            with team_name:
                if team_seed == 0:
                    st.header("Team Selection")
                    st.divider()
                else:
                    if st.session_state[f"team{team_seed}"]['team'] != None:
                        team = st.session_state[f"team{team_seed}"]['team']
                        team_idx = full_team_name.index(team)
                    else:
                        team_idx = None
                    if team_seed == 1:
                        st.divider()
                    team = st.selectbox(f"Select the Team {team_seed}", full_team_name, index=team_idx, placeholder="Please select a team")
                    st.session_state[f"team{team_seed}"]["team"] = team

            with team_year:
                if team_seed == 0:
                    st.header("Select Year")
                    st.divider()
                    same_year = st.toggle("Every team has the same year")
                    if same_year:
                        all_years_list = []
                        for year in range(1980, 2024):
                            next_year = year + 1
                            if next_year % 100 < 10:
                                all_years_list.append(f"{year}-0{next_year % 100}")
                            else:
                                all_years_list.append(f"{year}-{next_year % 100}")
                        all_years_list.reverse()
                        all_year = st.selectbox("Select the Year", all_years_list, index=0)
                else:
                    year = None
                    if team != None:
                        start_year = NBA_TEAMS[team]['start_year']
                        end_year = NBA_TEAMS[team]['end_year']
                        start_year = int(start_year[:4])
                        end_year = int(end_year[:4])
                        years_list = []
                        for year in range(start_year, end_year + 1):
                            next_year = year + 1
                            if next_year % 100 < 10:
                                years_list.append(f"{year}-0{next_year % 100}")
                            else:
                                years_list.append(f"{year}-{next_year % 100}")
                        years_list.reverse()
                        if st.session_state[f"team{team_seed}"]['year'] != None:
                            year = st.session_state[f"team{team_seed}"]['year']
                            year_idx = years_list.index(year)
                        else:
                            year_idx = None
                        if team_seed == 1:
                            st.divider()
                        if same_year:
                            year_idx = all_years_list.index(all_year)
                            year = st.selectbox(f"Select the {team_seed} seed's year", years_list, index=year_idx, placeholder="Please select the year")
                        else:
                            year = st.selectbox(f"Select the {team_seed} seed's year", years_list, index=year_idx, placeholder="Please select the year")
                        st.session_state[f"team{team_seed}"]["year"] = year

            with league_type:
                if team_seed == 0:
                    st.header("Select League Type")
                    st.divider()
                    same_league_type = st.toggle("Every team has the same type")
                    if same_league_type:
                        all_league_type = st.selectbox("Select the league type", ["0.0", "0.1", "1.0", "1.1", "2.0", "2.1", "3.0", "3.1", "4.0"], index=0)
                else:
                    if year != None:
                        if st.session_state[f"team{team_seed}"]['league_type'] != None:
                            league_type = st.session_state[f"team{team_seed}"]['league_type']
                            league_type_idx = LEAGUE_TYPES.index(league_type)
                        else:
                            league_type_idx = None
                        if team_seed == 1:
                            st.divider()
                        if same_league_type:
                            league_idx = LEAGUE_TYPES.index(all_league_type)
                            league_type = st.selectbox(f"Select the {team_seed} seed's league _type", LEAGUE_TYPES, index=league_idx)
                        else:
                            league_type = st.selectbox(f"Select the {team_seed} seed's league _type", LEAGUE_TYPES, index=league_type_idx, placeholder="Please select the leaguetype")
                        st.session_state[f"team{team_seed}"]["league_type"] = league_type
    keys_to_sort = []
    for key in list(st.session_state.keys()):
        if 'team' not in key or 'list' in key:
            continue
        keys_to_sort.append(key)
    sorted_keys = sorted(keys_to_sort, key=lambda x: int(x[4:]))
    for key in sorted_keys:
        if 'team' not in key:
            continue
        if st.session_state[key]['year'] != None and st.session_state[key]['league_type'] != None:
            st.session_state['team_list'][key] = [NBA_TEAMS[st.session_state[key]['team']]['abr'], st.session_state[key]['year'], st.session_state[key]['league_type']]
    st.divider()

    single_bracket, double_elimination, bracket_statistics, buff, buff, buff  = st.columns(6)

    simulated_type = None
    with single_bracket:
        if st.button("Simulate the Bracket"):
            simulated_type = 'single'
            with st.spinner("The Games Are Being Simulated"):
                bracket = bracket_generator(int(n_teams), list(st.session_state['team_list'].values()))
                game_strings, playoff_stats = simulate_bracket(st.session_state['team_list'], bracket, int(series_max))
    with double_elimination:
        if st.button("Simulate with Losers Bracket"):
            simulated_type = 'double'
            with st.spinner("The Games Are Being Simulated"):
                winner, loser = double_bracket_generator(list(st.session_state['team_list'].values()))
                game_strings, playoff_stats = simulate_double_elimination_bracket(st.session_state['team_list'], winner, loser, int(series_max))
    with bracket_statistics:
        if 'run_multi_braacket' not in st.session_state:
            st.session_state['run_multi_braacket'] = False
        if st.button("Run Bracket Multiple Times Statistics") or st.session_state['run_multi_braacket']:
            st.session_state['run_multi_braacket'] = True
            amount_of_bracket_simulations = st.text_input("Amount of Times to Simulate the Bracket")
            bracket_stats = None
            if amount_of_bracket_simulations != "":
                with st.spinner("The Games Are Being Simulated"):
                    simulated_type = 'single_stats'
                    bracket_stats = multi_bracket_sim(list(st.session_state['team_list'].values()), int(amount_of_bracket_simulations), int(series_max))
                    st.session_state['run_multi_braacket'] = False

    
    match simulated_type:
        case None:
            a = None
        case "single":
            if len(game_strings) > 1:
                sorted_keys = sorted(list(game_strings.keys()), key=lambda x: int(x[5:]))
            else:
                sorted_keys = list(game_strings.keys())
            x = len(sorted_keys)
            new_keys = []
            while x > 0:
                new_keys.append(sorted_keys[x - 1])
                x -= 1
            for idx, round_id in enumerate(new_keys):
                games_in_round = len(game_strings[round_id])
                match games_in_round:
                    case 1:
                        st.header(f"Finals")
                    case 2:
                        st.header(f"Conference Finals")
                    case 4:
                        st.header(f"Conference Semi-Finals")
                    case _ if games_in_round > 4:
                        st.header(f"Round - {idx}")
                for game in game_strings[round_id]:
                    home_team = game_strings[round_id][game]['loser'][0]
                    home_year = game_strings[round_id][game]['loser_year']
                    away_team = game_strings[round_id][game]['winner']
                    away_year = game_strings[round_id][game]['winner_year']
                    away_logo, away_pts, middle, home_pts, home_logo = st.columns(5)
                    photo_size = 135
                    with away_logo:
                        resized_image = resize_image(photos[NBA_TEAMS[away_team]['team']], photo_size)
                        st.image(resized_image, caption=f"{away_team}-{away_year}")
                    with away_pts:
                        add = game_strings[round_id][game]['wins']
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
                        add = game_strings[round_id][game]['losses']
                        st.markdown(f"""
                            <div style="display: flex; justify-content: center;">
                                <div>
                                    <p>&nbsp;</p>  <!-- Empty paragraph to create vertical space -->
                                    <p style="font-size: 55px;">{add}</p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with home_logo:
                        resized_image = resize_image(photos[NBA_TEAMS[home_team]['team']], photo_size)
                        st.image(resized_image, caption=f"{home_team}-{home_year}")
                st.divider()
            st.header("Team Stats")
            ranked_playoff_teams = rank_bracket_team(playoff_stats)
            columns = ['Rank', 'Teams', 'Year', 'GP', 'Wins', 'Losses', 'Pct', 'STRS', 'SORS','SDRS', 'PF', 'PA', 'DIFF', 'FP For', 'FP Againts', 'Diff', 'Off GmSc', 'Def GmSc', 'Game Score Diff']
            df = pd.DataFrame(ranked_playoff_teams, columns=columns)
            st.dataframe(df, hide_index=True, height=1015)
            st.divider()
        case 'double':
            if len(game_strings['winner']) > 1:
                sorted_winner_keys = sorted(list(game_strings['winner'].keys()), key=lambda x: int(x[5:]))
                sorted_winner_keys = sorted_winner_keys[::-1]
            else:
                sorted_winner_keys = list(game_strings['winner'].keys())
            if len(game_strings['loser']) > 1:
                sorted_loser_keys = sorted(list(game_strings['loser'].keys()), key=lambda x: int(x[5:]))
                sorted_loser_keys = sorted_loser_keys[::-1]
            else:
                sorted_loser_keys = list(game_strings['loser'].keys())
            
            winner_count, loser_count, total_count = 0, 0, 0
            use_losers = True
            while winner_count < len(sorted_winner_keys) or loser_count < len(sorted_loser_keys):
                if total_count == 0:
                    st.header('Grand Finals')
                    bracket_version = 'grand_finals'
                    games_to_check = game_strings[bracket_version]
                else:
                    if use_losers:
                        round_id = sorted_loser_keys[loser_count]
                        games_in_round = len(game_strings['loser'][round_id])
                        if games_in_round == 1:
                            if loser_count == 0:
                                st.header("Losers Grand Finals")
                            elif loser_count >= 1:
                                st.header("Losers Finals")
                        else:
                            st.header(f"Losers Round {round_id[-1]}")
                        games_to_check = game_strings['loser'][round_id]
                        loser_count += 1
                        if loser_count > 1 and len(sorted_loser_keys) > 2:
                            if loser_count % 2 == 0 and loser_count != len(sorted_loser_keys):
                                use_losers = True
                            else:
                                use_losers = False
                        else:
                            use_losers = False
                    else:
                        round_id = sorted_winner_keys[winner_count]
                        games_in_round = len(game_strings['winner'][round_id])
                        match games_in_round:
                            case 1:
                                st.header("Winners Finals")
                            case 2:
                                st.header("Winners Semi-Finals")
                            case 4:
                                st.header(f"Winners Quarter Semi-Finals")
                            case _ if games_in_round > 4:
                                st.header(f"Winners Round {round_id[-1]}")
                        games_to_check = game_strings['winner'][round_id]
                        winner_count += 1
                        use_losers = True
                for game in games_to_check:
                    home_team = games_to_check[game]['loser'][0]
                    home_year = games_to_check[game]['loser_year']
                    away_team = games_to_check[game]['winner']
                    away_year = games_to_check[game]['winner_year']
                    away_logo, away_pts, middle, home_pts, home_logo = st.columns(5)
                    photo_size = 135
                    with away_logo:
                        resized_image = resize_image(photos[NBA_TEAMS[away_team]['team']], photo_size)
                        st.image(resized_image, caption=f"{away_team}-{away_year}")
                    with away_pts:
                        add = games_to_check[game]['wins']
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
                        add = games_to_check[game]['losses']
                        st.markdown(f"""
                            <div style="display: flex; justify-content: center;">
                                <div>
                                    <p>&nbsp;</p>  <!-- Empty paragraph to create vertical space -->
                                    <p style="font-size: 55px;">{add}</p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with home_logo:
                        resized_image = resize_image(photos[NBA_TEAMS[home_team]['team']], photo_size)
                        st.image(resized_image, caption=f"{home_team}-{home_year}")
                total_count += 1
            st.divider()
            st.header("Team Stats")
            ranked_playoff_teams = rank_bracket_team(playoff_stats)
            columns = ['Rank', 'Teams', 'Year', 'GP', 'Wins', 'Losses', 'Pct', 'STRS', 'SORS','SDRS', 'PF', 'PA', 'DIFF', 'FP For', 'FP Againts', 'Diff', 'Off GmSc', 'Def GmSc', 'Game Score Diff']
            df = pd.DataFrame(ranked_playoff_teams, columns=columns)
            st.dataframe(df, hide_index=True, height=1015)
            st.divider()

        case "single_stats":
            header = ['Team', 'Year', 'League_Type']
            power_list = []
            amount_of_rounds = math.ceil(math.log2(len(st.session_state['team_list'])))
            rounds = [i + 1 for i in range(amount_of_rounds + 1)]
            rounds.sort(reverse=True)
            for round_id in rounds:
                header.append(str(round_id))
            for team in bracket_stats:
                add_list = [NBA_TEAMS[team['name']]['team'], team['year'], team['league_type']]
                for round_id in rounds:
                    if round_id not in team:
                        add_list.append("0.0%")
                    else:
                        add_list.append(f"{round((team[round_id] / int(amount_of_bracket_simulations) * 100), 3)}%")
                power_list.append(add_list)
            sorted_power_list = sorted(power_list, key=lambda x: (float(x[3].replace("%", "")), float(x[4].replace("%", "")), float(x[5].replace("%", ""))), reverse=True)
            df = pd.DataFrame(sorted_power_list, columns=header)
            st.title("Table of round percentages")
            st.dataframe(df, hide_index=True, height=1015)
            st.divider()
