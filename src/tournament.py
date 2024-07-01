import math
import random


def bracket_generator(number_of_teams: int, team_list: list):
    amount_of_rounds = math.ceil(math.log2(number_of_teams))
    remainder = (2 ** amount_of_rounds) - number_of_teams
    playoff_rounds = {'round1': {}}
    if remainder > 0:
        start_idx = remainder
        key = f"round{len(playoff_rounds) + 1}"
        playoff_rounds[key] = {}
        round_ids = int((2 ** amount_of_rounds) / 2) - remainder
        sub = 1
        previous = None
        for idx in range(remainder):
            if previous is None:
                previous = (round_ids) - sub
            else:
                previous -= 1
            playoff_rounds[key][round_ids] = [team_list[idx], previous]
            round_ids += 1
            sub += 1
    else:
        start_idx = 0
    end_idx = number_of_teams - 1
    round_ids = 0
    while start_idx < end_idx:
        game_match = [team_list[start_idx], team_list[end_idx]]
        playoff_rounds['round1'][round_ids] = game_match
        start_idx += 1
        end_idx -= 1
        round_ids += 1
    idx = 1
    round_multiplier = amount_of_rounds - 1
    previous_key = None
    start_idx = None
    while round_multiplier > 0:
        key = f"round{idx + 1}"
        if previous_key is None:
            if key not in playoff_rounds:
                old_key = f"round{int(key[-1]) - 1}"
                previous_key = len(playoff_rounds[old_key])
            else:
                previous_key = list(playoff_rounds[key].keys())[-1]
        if key in playoff_rounds and len(playoff_rounds[key]) == (2 ** round_multiplier) / 2:
            idx += 1
            round_multiplier -= 1
            continue 
        if key not in playoff_rounds:
            remainder = 0
            playoff_rounds[key] = {}
        amount_of_games = int(((2 ** round_multiplier) / 2) - len(playoff_rounds[key]))
        if start_idx is None:
            start_idx = 0
            end_idx = ((2 ** round_multiplier) - 1) - remainder * 2
        for _ in range(amount_of_games):
            game_match = [start_idx, end_idx]
            playoff_rounds[key][previous_key + 1] = game_match
            previous_key += 1
            start_idx += 1
            end_idx -= 1
        idx += 1
        round_multiplier -= 1
        start_idx = min(list(playoff_rounds[key].keys()))
        end_idx = previous_key
    return playoff_rounds

def double_bracket_generator(team_list: list):
    number_of_teams = len(team_list)
    winner_bracket = bracket_generator(number_of_teams, team_list)
    losers_bracket = {}
    amount_of_rounds = math.ceil(math.log2(number_of_teams))
    remainder = 2 ** amount_of_rounds - number_of_teams
    games = {}
    for round_id in winner_bracket:
        games[round_id] = []
        for game in winner_bracket[round_id]:
            games[round_id].append(game)
    round_count = 0
    count = 1
    previous_round = None
    grab_winners = False
    while round_count < amount_of_rounds:
        loser_keys = list(losers_bracket.keys())
        round_id = f"round{count}"
        if round_id not in losers_bracket:
            losers_bracket[round_id] = {}
        if round_id == 'round1':
            if remainder > 0:
                key = f"round{len(losers_bracket) + 1}"
                losers_bracket[key] = {}
                round_ids = int((len(winner_bracket[round_id]) - remainder) / 2)
                sub = 1
                previous = None
                winner_keys = list(winner_bracket[key].keys())
                for idx in range(remainder):
                    if previous is None:
                        previous = (round_ids) - sub
                    else:
                        previous -= 1
                    losers_bracket[key][round_ids] = [f"{winner_keys[idx]}_w", previous]
                    round_ids += 1
                    sub += 1
            start_idx = 0
            end_idx = len(games[round_id]) - remainder - 1
            while start_idx < end_idx:
                key = len(losers_bracket[round_id])
                losers_bracket[round_id][key] = [start_idx, end_idx]
                end_idx -= 1
                start_idx += 1
            previous_round = 2
            round_count += 1
            count += 1
        elif int(math.log2(len(losers_bracket[loser_keys[-previous_round]]))) == math.log2(len(losers_bracket[loser_keys[-previous_round]])):
            loser_round_keys = list(losers_bracket.keys())
            keys = list(losers_bracket[loser_round_keys[-2]].keys())
            if grab_winners:
                winner_keys = list(winner_bracket[loser_round_keys[round_count]].keys())
            key = keys[-1] + 1
            start_idx = 0
            if not grab_winners:
                end_idx = len(keys) - 1
            else:
                end_idx = len(keys)
            while start_idx < end_idx:
                if not grab_winners:
                    losers_bracket[round_id][key] = [keys[start_idx], keys[end_idx]]
                    end_idx -=1
                else:
                    if len(keys) == 1:
                        losers_bracket[round_id][key] = [f"{winner_keys[0]}_w", keys[0]]
                    elif start_idx % 2 == 0:
                        losers_bracket[round_id][key] = [f"{winner_keys[start_idx]}_w", keys[-(start_idx + 2)]]
                    else:
                        losers_bracket[round_id][key] = [f"{winner_keys[start_idx]}_w", keys[-start_idx]]
                start_idx += 1
                key += 1
            if grab_winners:
                grab_winners = False
                count += 1
                round_count += 1
            else:
                grab_winners = True
                count += 1
        else:
            add_count = 0
            previous_keys = list(losers_bracket[loser_keys[-previous_round]].keys())
            remainder = len(list(losers_bracket[round_id].keys()))
            key = list(losers_bracket[round_id].keys())[-1] + 1
            loop_count = len(winner_bracket[round_id]) - len(losers_bracket[round_id])
            while add_count < loop_count:
                if add_count % 2 == 0:
                    losers_bracket[round_id][key] = [f"{winner_keys[add_count + remainder]}_w", previous_keys[add_count + 1]]
                else:
                    losers_bracket[round_id][key] = [f"{winner_keys[add_count + remainder]}_w", previous_keys[add_count - 1]]
                add_count += 1
                key += 1
            count += 1
            round_count += 1
            previous_round = 1
    return winner_bracket, losers_bracket

def season_generator(teams: list, conf_games: int, div_games: int, non_conf_games: int):
    schedule_list = []
    for team in teams:
        team_abr = f"{team['name']}-{team['year']} {team['league_type']}"
        team_conf = team['conf']
        team_div = team['div']
        teams.pop(0)
        for team in teams:
            opp_abr = f"{team['name']}-{team['year']} {team['league_type']}"
            opp_conf = team['conf']
            opp_div = team['div']
            if team_div == opp_div:
                for _ in range(div_games):
                    schedule_list.append([team_abr, 'vs', opp_abr])
            elif team_conf == opp_conf:
                for _ in range(conf_games):
                    schedule_list.append([team_abr, 'vs', opp_abr])
            else:
                for _ in range(non_conf_games):
                    schedule_list.append([team_abr, 'vs', opp_abr])
    random.shuffle(schedule_list)
    return schedule_list

if __name__ == '__main__':
    # Example usage
    year = '2023-24'
    league_type = '0.0'
    teams = [
        {'name': 'BOS', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Atlantic'},
        {'name': 'OKC', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Atlantic'},
        {'name': 'DEN', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Atlantic'},
        {'name': 'NYK', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Atlantic'},
        {'name': 'MIL', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Atlantic'},
        {'name': 'MIN', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Central'},
        {'name': 'LAC', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Central'},
        {'name': 'CLE', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Central'},
        {'name': 'ORL', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Central'},
        {'name': 'DAL', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Central'},
        {'name': 'PHO', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Southeast'},
        {'name': 'IND', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Southeast'},
        {'name': 'PHI', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Southeast'},
        {'name': 'NOP', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Southeast'},
        {'name': 'LAL', 'year': year, 'league_type': league_type, 'conf': 'East', 'div': 'Southeast'},
        {'name': 'MIA', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Northwest'},
        {'name': 'CHI', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Northwest'},
        {'name': 'SAC', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Northwest'},
        {'name': 'GSW', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Northwest'},
        {'name': 'ATL', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Northwest'},
        {'name': 'BRK', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Pacific'},
        {'name': 'HOU', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Pacific'},
        {'name': 'UTA', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Pacific'},
        {'name': 'TOR', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Pacific'},
        {'name': 'CHO', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Pacific'},
        {'name': 'MEM', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Southwest'},
        {'name': 'SAS', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Southwest'},
        {'name': 'WAS', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Southwest'},
        {'name': 'DET', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Southwest'},
        {'name': 'POR', 'year': year, 'league_type': league_type, 'conf': 'West', 'div': 'Southwest'}
    ]

    # season_generator(teams, 4, 4, 2)
    num_teams = len(teams)
    winners, losers = double_bracket_generator(teams)

    # Print the bracket structure (you can modify this to visualize the bracket)
    # print(f"Bracket for {num_teams} teams:")
    # for key in bracket:
    #     print(bracket[key])