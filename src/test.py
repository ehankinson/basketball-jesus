import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting

import matplotlib.pyplot as plt
import networkx as nx

def draw_bracket(teams, output_file='bracket.png'):
    G = nx.DiGraph()
    pos = {}

    # Helper function to add nodes and edges
    def add_match(G, pos, node_id, x, y, label):
        G.add_node(node_id)
        pos[node_id] = (x, y)
        nx.set_node_attributes(G, {node_id: {'label': label}})
        
    def connect_matches(G, match1, match2):
        G.add_edge(match1, match2)
    
    # Initial positions
    x = 0
    y_spacing = 2
    round_spacing = 5

    # Create winner bracket
    num_teams = len(teams)
    current_round = teams

    rounds = []
    while len(current_round) > 1:
        next_round = []
        for i in range(0, len(current_round), 2):
            match_id = f"w_{len(rounds)}_{i//2}"
            team1 = current_round[i]
            team2 = current_round[i+1] if i+1 < len(current_round) else "BYE"
            label = f"{team1} vs {team2}"
            y = i * y_spacing
            add_match(G, pos, match_id, x, y, label)
            if len(rounds) > 0:
                prev_match1 = f"w_{len(rounds)-1}_{i//2}"
                prev_match2 = f"w_{len(rounds)-1}_{i//2 + 1}"
                if prev_match1 in G.nodes:
                    connect_matches(G, prev_match1, match_id)
                if prev_match2 in G.nodes:
                    connect_matches(G, prev_match2, match_id)
            next_round.append(match_id)
        current_round = next_round
        rounds.append(next_round)
        x += round_spacing
    
    # Create loser bracket
    loser_rounds = []
    x = round_spacing * len(rounds)
    for r in range(1, len(rounds)):
        current_round = rounds[r]
        next_loser_round = []
        for i in range(0, len(current_round), 2):
            match_id = f"l_{r}_{i//2}"
            if i+1 < len(current_round):
                label = f"Loser of {current_round[i]} vs Loser of {current_round[i+1]}"
                add_match(G, pos, match_id, x, i * y_spacing, label)
                connect_matches(G, current_round[i], match_id)
                connect_matches(G, current_round[i+1], match_id)
            else:
                label = f"Loser of {current_round[i]}"
                add_match(G, pos, match_id, x, i * y_spacing, label)
                connect_matches(G, current_round[i], match_id)
            next_loser_round.append(match_id)
        loser_rounds.append(next_loser_round)
        x += round_spacing
    
    # Draw the graph
    plt.figure(figsize=(15, 8))
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color="lightblue", font_size=8, font_weight="bold", arrows=False)
    plt.title("Tournament Bracket")
    plt.savefig(output_file)  # Save the plot to a file
    plt.close()

# Example usage
teams = [
    "SEN", "CHI", "DK", "SAC", "GOW", "TCU", "JWL", "NYK",
    "MIL", "BKN", "PHI", "SAS", "LAL", "CHN", "NO", "DAL"
]

draw_bracket(teams)
