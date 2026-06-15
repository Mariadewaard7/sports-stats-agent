"""
generate_data.py

Creates a small sample dataset of NBA player season stats for the
sports-stats-agent project. In a real version of this project you'd
pull this from a public API (balldontlie.io, NBA stats API, etc.) —
this script generates a representative sample so the pipeline and
agent are runnable end-to-end without external API keys.
"""

import csv
import os

PLAYERS = [
    # name, team, position, games_played, points_per_game, rebounds_per_game,
    # assists_per_game, field_goal_pct, three_point_pct, minutes_per_game
    ("Luka Doncic", "LAL", "G", 70, 28.4, 8.6, 7.8, 0.487, 0.382, 35.1),
    ("Jayson Tatum", "BOS", "F", 74, 26.9, 8.1, 4.9, 0.471, 0.376, 35.7),
    ("Shai Gilgeous-Alexander", "OKC", "G", 76, 30.1, 5.5, 6.2, 0.535, 0.353, 34.0),
    ("Nikola Jokic", "DEN", "C", 79, 29.6, 13.7, 9.8, 0.583, 0.359, 36.7),
    ("Giannis Antetokounmpo", "MIL", "F", 73, 30.4, 11.5, 6.5, 0.611, 0.274, 35.2),
    ("Anthony Edwards", "MIN", "G", 79, 25.9, 5.4, 5.1, 0.461, 0.395, 35.1),
    ("Devin Booker", "PHX", "G", 75, 27.1, 4.5, 6.9, 0.466, 0.361, 36.0),
    ("Donovan Mitchell", "CLE", "G", 77, 26.6, 5.1, 6.1, 0.460, 0.367, 35.4),
    ("Kevin Durant", "PHX", "F", 70, 27.1, 6.6, 4.2, 0.527, 0.413, 36.6),
    ("Tyrese Haliburton", "IND", "G", 69, 18.6, 3.9, 9.2, 0.477, 0.402, 32.4),
    ("Jalen Brunson", "NYK", "G", 77, 28.7, 3.6, 7.3, 0.479, 0.401, 35.4),
    ("Trae Young", "ATL", "G", 76, 25.7, 2.8, 11.6, 0.433, 0.371, 36.0),
    ("Domantas Sabonis", "SAC", "C", 71, 19.4, 13.7, 7.3, 0.594, 0.372, 34.6),
    ("LeBron James", "LAL", "F", 71, 23.5, 7.8, 8.2, 0.510, 0.410, 35.0),
    ("Pascal Siakam", "IND", "F", 80, 21.3, 7.2, 3.7, 0.540, 0.358, 33.6),
    ("De'Aaron Fox", "SAC", "G", 74, 25.2, 4.1, 5.6, 0.461, 0.337, 35.0),
    ("Paolo Banchero", "ORL", "F", 80, 22.6, 6.9, 5.4, 0.456, 0.337, 33.6),
    ("Cade Cunningham", "DET", "G", 62, 22.7, 4.3, 7.5, 0.452, 0.354, 34.0),
    ("Victor Wembanyama", "SAS", "C", 71, 21.4, 10.6, 3.9, 0.469, 0.324, 29.7),
    ("Jaylen Brown", "BOS", "F", 70, 23.0, 5.5, 3.6, 0.490, 0.354, 33.5),
]

TEAMS = [
    # team_code, city, conference
    ("LAL", "Los Angeles", "West"),
    ("BOS", "Boston", "East"),
    ("OKC", "Oklahoma City", "West"),
    ("DEN", "Denver", "West"),
    ("MIL", "Milwaukee", "East"),
    ("MIN", "Minneapolis", "West"),
    ("PHX", "Phoenix", "West"),
    ("CLE", "Cleveland", "East"),
    ("IND", "Indianapolis", "East"),
    ("NYK", "New York", "East"),
    ("ATL", "Atlanta", "East"),
    ("SAC", "Sacramento", "West"),
    ("ORL", "Orlando", "East"),
    ("DET", "Detroit", "East"),
    ("SAS", "San Antonio", "West"),
]

os.makedirs("data", exist_ok=True)

with open("data/players.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "name", "team", "position", "games_played", "points_per_game",
        "rebounds_per_game", "assists_per_game", "field_goal_pct",
        "three_point_pct", "minutes_per_game"
    ])
    writer.writerows(PLAYERS)

with open("data/teams.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["team_code", "city", "conference"])
    writer.writerows(TEAMS)

print(f"Wrote {len(PLAYERS)} player rows to data/players.csv")
print(f"Wrote {len(TEAMS)} team rows to data/teams.csv")
