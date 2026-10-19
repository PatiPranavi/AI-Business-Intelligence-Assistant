# AI Business Intelligence Assistant

Ask natural-language business questions about a PostgreSQL database. The app uses a LangChain SQL agent and Google Gemini to inspect the schema, query data, and explain results in a Streamlit chat interface.

## Features

- Natural-language questions over PostgreSQL
- Schema/table inspection in the UI
- Downloadable text insights
- Environment-based Gemini configuration
- Read-only transaction defaults, bounded agent iterations/time, connection timeout, and user-safe error messages

## Important security note

This is a portfolio/demo application, not a production-ready BI service. Use a **dedicated PostgreSQL role with SELECT-only permissions** and only grant access to the tables needed for the demo. The app also sets PostgreSQL transactions to read-only as defense in depth; database permissions are the primary security boundary. Never connect using a database owner or superuser account. Do not commit `.env` or API keys.

Example role setup (run as a database administrator and adjust database/schema/table names):

```sql
CREATE ROLE bi_reader LOGIN PASSWORD 'replace-with-a-strong-password';
GRANT CONNECT ON DATABASE your_database TO bi_reader;
GRANT USAGE ON SCHEMA public TO bi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bi_reader;
```

## Setup

Requires Python 3.10+ and PostgreSQL access.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.sample` to `.env` and set your Gemini API key:

```dotenv
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
# Optional defaults for the sidebar:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=bi_reader
```

The database password is entered in the app's sidebar and is not stored in `.env` by default.

Run:

```bash
streamlit run app.py
```

## Example questions

- Show monthly revenue
- Which products have the highest sales?
- Compare orders by region
- List the top 10 customers by purchase amount

Questions depend on the tables and columns available in the connected database. KPI cards are intentionally not hardcoded; answers are derived from database queries.

## Limitations / next steps

- SQL-agent answers can be incorrect; verify important results against SQL and source data.
- The project currently has no bundled demo database or automated test suite.
- For a stronger portfolio submission, add a small anonymized sample dataset, unit tests for connection/configuration and error paths, and a reproducible demo video/screenshots.
- For deployment, use managed secrets, authentication, query auditing, stricter table allowlists, rate limits, and a separately provisioned read-only database account.

## Tech stack

Python, Streamlit, PostgreSQL, SQLAlchemy, LangChain, Google Gemini.
