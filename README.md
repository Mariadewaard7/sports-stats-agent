# Sports Stats Agent

A small project that pairs a basic ETL pipeline with an LLM-powered
natural-language query agent over a SQLite sports database.

I built this to get hands-on practice with the pattern of letting an
AI agent answer questions over structured data: generate SQL from a
question, run it safely, and turn the result back into a plain-English
answer.

## What it does

1. **`generate_data.py`** — creates a small sample dataset of NBA
   player season stats and team info as CSV files (`data/players.csv`,
   `data/teams.csv`).

2. **`load_db.py`** — a small ETL pipeline:
   - **Extract**: reads the CSVs
   - **Validate**: checks column names, value ranges (e.g. shooting
     percentages between 0 and 1, games played between 0 and 82,
     valid positions/conferences), and surfaces any issues before
     loading
   - **Load**: writes the data into `sports.db` (SQLite) with a
     schema that includes primary keys, foreign keys, and check
     constraints

3. **`agent.py`** — a natural-language query agent:
   - Takes a question like *"Who are the top 3 scorers by points per
     game?"*
   - Sends the question and database schema to an LLM, asking for a
     single read-only SQL query
   - Runs the query against `sports.db`, with a guardrail that rejects
     anything that isn't a `SELECT` statement
   - Sends the results back to the LLM to produce a plain-English answer

## Running it

```bash
# 1. Generate sample data
python3 generate_data.py

# 2. Load it into SQLite (validates as it goes)
python3 load_db.py

# 3. Ask questions (requires OPENAI_API_KEY)
export OPENAI_API_KEY=your-key-here
python3 agent.py
```

You can also ask a custom question directly:

```bash
python3 agent.py "Which team has the most players averaging over 25 points per game?"
```

## Why I built it this way

- **Validation before load**: bad data should fail loudly at the
  pipeline stage, not silently corrupt the database. `load_db.py`
  checks every row and aborts the load with a list of specific errors
  if anything looks wrong.

- **Schema constraints**: the SQLite schema itself enforces valid
  positions, conferences, and percentage ranges as a second layer of
  defense, not just the Python validation.

- **Guardrails on the agent**: the agent only ever runs `SELECT`
  queries, and explicitly checks for and rejects destructive keywords
  (`DROP`, `DELETE`, `UPDATE`, etc.) before executing anything the LLM
  generates.

- **Small and inspectable**: the whole thing is ~250 lines across three
  files, on purpose — easy to read end-to-end and easy to extend (e.g.
  swap the sample CSVs for a real API, or the SQLite database for
  Postgres/Snowflake).

## Possible extensions

- Pull live data from a public sports API instead of the sample CSVs
- Add a simple CLI loop for interactive Q&A
- Swap SQLite for a cloud warehouse (Snowflake/Databricks) and adjust
  the agent's schema prompt accordingly
- Add unit tests for the validation logic
# sports-stats-agent
