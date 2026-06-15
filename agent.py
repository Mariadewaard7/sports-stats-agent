"""
agent.py

A small natural-language-to-SQL agent for the sports stats database.

Given a question like "Who are the top 3 scorers in the West conference?",
the agent:
  1. Sends the question + database schema to an LLM, asking it to
     produce a single read-only SQL query.
  2. Runs that query against sports.db.
  3. Sends the question + query results back to the LLM and asks it
     to answer the original question in plain English.

This is a deliberately small example of an LLM-backed data agent —
the same basic pattern (schema-aware query generation + result
summarization) scales up to much larger systems, just with more
guardrails, logging, and retry logic.

Requires the OPENAI_API_KEY environment variable to be set.
"""

import os
import sqlite3
import sys

DB_PATH = "sports.db"
MODEL = "gpt-4o-mini"

SCHEMA = """
CREATE TABLE teams (
    team_code TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    conference TEXT NOT NULL CHECK (conference IN ('East', 'West'))
);

CREATE TABLE players (
    name TEXT PRIMARY KEY,
    team TEXT NOT NULL REFERENCES teams(team_code),
    position TEXT NOT NULL CHECK (position IN ('G', 'F', 'C')),
    games_played INTEGER NOT NULL,
    points_per_game REAL NOT NULL,
    rebounds_per_game REAL NOT NULL,
    assists_per_game REAL NOT NULL,
    field_goal_pct REAL NOT NULL,
    three_point_pct REAL NOT NULL,
    minutes_per_game REAL NOT NULL
);
"""

SQL_SYSTEM_PROMPT = f"""You are a SQL assistant for a small SQLite sports database.

Schema:
{SCHEMA}

Given a user's question, write a single read-only SQLite SELECT query
that answers it. Rules:
- Only output the SQL query, nothing else. No markdown, no explanation.
- Only use SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or ALTER.
- Use JOINs between players and teams when the question involves team
  cities or conferences.
- Limit results to a reasonable number of rows (e.g. LIMIT 10) unless
  the question asks for all results.
"""

ANSWER_SYSTEM_PROMPT = """You are a helpful assistant summarizing sports
database query results for a user. Given the user's original question
and the raw query results, answer in 1-3 plain-English sentences.
Do not mention SQL or databases in your answer."""


FORBIDDEN_KEYWORDS = ("insert", "update", "delete", "drop", "alter", "create", "replace")


def get_sql_query(client, question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SQL_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    sql = response.choices[0].message.content.strip()
    # Strip accidental markdown fences if the model adds them anyway
    sql = sql.strip("`").strip()
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()
    return sql


def run_query(sql):
    lowered = sql.lower()
    if not lowered.startswith("select"):
        raise ValueError("Refusing to run non-SELECT query.")
    if any(keyword in lowered for keyword in FORBIDDEN_KEYWORDS):
        raise ValueError("Query contains a forbidden keyword.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_natural_language_answer(client, question, rows):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nResults: {rows}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def ask(client, question):
    print(f"\nQ: {question}")

    sql = get_sql_query(client, question)
    print(f"  Generated SQL: {sql}")

    try:
        rows = run_query(sql)
    except (sqlite3.Error, ValueError) as e:
        print(f"  Query failed: {e}")
        return

    print(f"  Rows returned: {len(rows)}")

    answer = get_natural_language_answer(client, question, rows)
    print(f"A: {answer}")


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Set the OPENAI_API_KEY environment variable before running this script.")
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print(f"{DB_PATH} not found. Run generate_data.py and load_db.py first.")
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI()

    sample_questions = [
        "Who are the top 3 scorers by points per game?",
        "Which players on West conference teams average more than 10 rebounds per game?",
        "What is the average three point percentage for guards versus centers?",
    ]

    if len(sys.argv) > 1:
        ask(client, " ".join(sys.argv[1:]))
    else:
        for q in sample_questions:
            ask(client, q)


if __name__ == "__main__":
    main()
