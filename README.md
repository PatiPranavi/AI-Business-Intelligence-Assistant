\# AI Business Intelligence Assistant



Ask natural-language business questions about a PostgreSQL database. The app uses a LangChain SQL agent and Google Gemini to inspect the schema, query data, and explain results in a Streamlit chat interface.



\## Features



\- Natural-language questions over PostgreSQL

\- Schema/table inspection in the UI

\- Downloadable text insights

\- Environment-based Gemini configuration

\- Read-only transaction defaults, bounded agent iterations/time, connection timeout, and user-safe error messages



\## Important security note



This is a portfolio/demo application, not a production-ready BI service. Use a \*\*dedicated PostgreSQL role with SELECT-only permissions\*\* and only grant access to the tables needed for the demo. The app also sets PostgreSQL transactions to read-only as defense in depth; database permissions are the primary security boundary. Never connect using a database owner or superuser account. Do not commit `.env` or API keys.



Example role setup (run as a database administrator and adjust database/schema/table names):



```sql

CREATE ROLE bi\_reader LOGIN PASSWORD 'replace-with-a-strong-password';

GRANT CONNECT ON DATABASE your\_database TO bi\_reader;

GRANT USAGE ON SCHEMA public TO bi\_reader;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi\_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bi\_reader;

```



\#### Setup



Requires Python 3.10+ and access to a PostgreSQL database.



\### 1. Create and activate a virtual environment



\*\*Windows PowerShell\*\*

```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



\*\*macOS/Linux\*\*

```bash

python -m venv .venv

source .venv/bin/activate

```



\### 2. Install dependencies



```bash

python -m pip install --upgrade pip

pip install -r requirements.txt

```



\### 3. Configure environment variables



Create a `.env` file in the project root and add your Gemini API key and model:



```dotenv

GOOGLE\_API\_KEY=your\_google\_api\_key\_here

GEMINI\_MODEL=gemini-3.8-flash

DB\_HOST=127.0.0.1

DB\_PORT=5432

DB\_NAME=business\_db

DB\_USER=bi\_reader

```



Use a valid Gemini model supported by your Google AI account. Never commit `.env` or expose your API key. The database password is entered in the app's sidebar and is not stored in `.env` by default.



\### 4. Run the application



```bash

streamlit run app.py

```



The app opens in your browser. Enter your PostgreSQL connection details in the sidebar and ask a business question in natural language.



\## Example questions



\- Show monthly revenue

\- Which products have the highest sales?

\- Compare orders by region

\- List the top 10 customers by purchase amount



Questions depend on the tables and columns available in the connected database. KPI cards are intentionally not hardcoded; answers are derived from database queries.



\## Limitations / next steps



\- SQL-agent answers can be incorrect; verify important results against SQL and source data.

\- The project currently has no bundled demo database or automated test suite.

\- For a stronger portfolio submission, add a small anonymized sample dataset, unit tests for connection/configuration and error paths, and a reproducible demo video/screenshots.

\- For deployment, use managed secrets, authentication, query auditing, stricter table allowlists, rate limits, and a separately provisioned read-only database account.



\## Tech stack



Python, Streamlit, PostgreSQL, SQLAlchemy, LangChain, Google Gemini.



