import math


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



if __name__ == '__main__':
    # Example usage
    teams = [
        ['BOS', '2023-24', '0.0'], 
        ['OKC', '2023-24', '0.0'], 
        ['DEN', '2023-24', '0.0'], 
        ['NYK', '2023-24', '0.0'], 
        ['MIL', '2023-24', '0.0'], 
        ['MIN', '2023-24', '0.0'], 
        ['LAC', '2023-24', '0.0'], 
        ['CLE', '2023-24', '0.0'], 
        ['ORL', '2023-24', '0.0'], 
        ['DAL', '2023-24', '0.0'], 
        ['PHO', '2023-24', '0.0'], 
        ['IND', '2023-24', '0.0'], 
        ['PHI', '2023-24', '0.0'], 
        ['NOP', '2023-24', '0.0'], 
        ['LAL', '2023-24', '0.0'], 
        ['MIA', '2023-24', '0.0'], 
        ['CHI', '2023-24', '0.0'], 
        ['SAC', '2023-24', '0.0'], 
        ['GSW', '2023-24', '0.0'], 
        ['ATL', '2023-24', '0.0'], 
        ['BRK', '2023-24', '0.0'], 
        ['HOU', '2023-24', '0.0'], 
        ['UTA', '2023-24', '0.0'], 
        ['TOR', '2023-24', '0.0'], 
        ['CHO', '2023-24', '0.0'], 
        ['MEM', '2023-24', '0.0'], 
        ['SAS', '2023-24', '0.0'], 
        ['WAS', '2023-24', '0.0'], 
        ['DET', '2023-24', '0.0'], 
        ['POR', '2023-24', '0.0']
             ]
    num_teams = len(teams)
    bracket = bracket_generator(num_teams, teams)

    # Print the bracket structure (you can modify this to visualize the bracket)
    print(f"Bracket for {num_teams} teams:")
    for key in bracket:
        print(bracket[key])