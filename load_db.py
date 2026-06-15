"""
load_db.py

Small ETL pipeline: reads raw CSVs from data/, validates them,
and loads them into a SQLite database (sports.db) with a clean schema.

This mirrors the basic shape of a production pipeline at much smaller
scale: extract (read CSV) -> validate (schema + range checks) ->
load (write to relational store).
"""

import csv
import sqlite3
import sys
from pathlib import Path

DB_PATH = "sports.db"

PLAYER_COLUMNS = [
    "name", "team", "position", "games_played", "points_per_game",
    "rebounds_per_game", "assists_per_game", "field_goal_pct",
    "three_point_pct", "minutes_per_game"
]

TEAM_COLUMNS = ["team_code", "city", "conference"]


def validate_players(rows):
    """Basic data quality checks before loading."""
    errors = []
    for i, row in enumerate(rows, start=2):  # start=2 to account for header row
        if not row["name"].strip():
            errors.append(f"Row {i}: missing player name")
        if row["position"] not in ("G", "F", "C"):
            errors.append(f"Row {i}: unexpected position '{row['position']}' for {row['name']}")
        for pct_field in ("field_goal_pct", "three_point_pct"):
            try:
                val = float(row[pct_field])
                if not (0.0 <= val <= 1.0):
                    errors.append(f"Row {i}: {pct_field}={val} out of expected range [0,1] for {row['name']}")
            except ValueError:
                errors.append(f"Row {i}: {pct_field} is not numeric for {row['name']}")
        try:
            gp = int(row["games_played"])
            if not (0 <= gp <= 82):
                errors.append(f"Row {i}: games_played={gp} out of valid season range [0,82] for {row['name']}")
        except ValueError:
            errors.append(f"Row {i}: games_played is not an integer for {row['name']}")
    return errors


def validate_teams(rows):
    errors = []
    for i, row in enumerate(rows, start=2):
        if not row["team_code"].strip():
            errors.append(f"Row {i}: missing team_code")
        if row["conference"] not in ("East", "West"):
            errors.append(f"Row {i}: unexpected conference '{row['conference']}' for {row['team_code']}")
    return errors


def read_csv(path, expected_columns):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != expected_columns:
            raise ValueError(
                f"{path}: expected columns {expected_columns}, got {reader.fieldnames}"
            )
        return list(reader)


def main():
    data_dir = Path("data")
    players_path = data_dir / "players.csv"
    teams_path = data_dir / "teams.csv"

    if not players_path.exists() or not teams_path.exists():
        print("Source CSVs not found. Run generate_data.py first.")
        sys.exit(1)

    print("Reading source files...")
    players = read_csv(players_path, PLAYER_COLUMNS)
    teams = read_csv(teams_path, TEAM_COLUMNS)
    print(f"  players.csv: {len(players)} rows")
    print(f"  teams.csv:   {len(teams)} rows")

    print("\nValidating...")
    player_errors = validate_players(players)
    team_errors = validate_teams(teams)
    all_errors = player_errors + team_errors

    if all_errors:
        print(f"Found {len(all_errors)} validation error(s):")
        for err in all_errors:
            print(f"  - {err}")
        print("\nAborting load. Fix source data and re-run.")
        sys.exit(1)

    print("  All checks passed.")

    print(f"\nLoading into {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS players;
        DROP TABLE IF EXISTS teams;

        CREATE TABLE teams (
            team_code TEXT PRIMARY KEY,
            city TEXT NOT NULL,
            conference TEXT NOT NULL CHECK (conference IN ('East', 'West'))
        );

        CREATE TABLE players (
            name TEXT PRIMARY KEY,
            team TEXT NOT NULL REFERENCES teams(team_code),
            position TEXT NOT NULL CHECK (position IN ('G', 'F', 'C')),
            games_played INTEGER NOT NULL CHECK (games_played BETWEEN 0 AND 82),
            points_per_game REAL NOT NULL,
            rebounds_per_game REAL NOT NULL,
            assists_per_game REAL NOT NULL,
            field_goal_pct REAL NOT NULL CHECK (field_goal_pct BETWEEN 0 AND 1),
            three_point_pct REAL NOT NULL CHECK (three_point_pct BETWEEN 0 AND 1),
            minutes_per_game REAL NOT NULL
        );
    """)

    cur.executemany(
        "INSERT INTO teams (team_code, city, conference) VALUES (?, ?, ?)",
        [(r["team_code"], r["city"], r["conference"]) for r in teams]
    )

    cur.executemany(
        """INSERT INTO players (
            name, team, position, games_played, points_per_game,
            rebounds_per_game, assists_per_game, field_goal_pct,
            three_point_pct, minutes_per_game
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(
            r["name"], r["team"], r["position"], int(r["games_played"]),
            float(r["points_per_game"]), float(r["rebounds_per_game"]),
            float(r["assists_per_game"]), float(r["field_goal_pct"]),
            float(r["three_point_pct"]), float(r["minutes_per_game"])
        ) for r in players]
    )

    conn.commit()

    # Sanity check: row counts match
    cur.execute("SELECT COUNT(*) FROM players")
    player_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM teams")
    team_count = cur.fetchone()[0]

    conn.close()

    print(f"  Loaded {player_count} players, {team_count} teams.")
    print("Done.")


if __name__ == "__main__":
    main()
