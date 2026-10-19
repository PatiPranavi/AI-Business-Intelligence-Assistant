import os
import logging
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import URL
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def connect_read_only_db(host, port, username, password, database):
    """Connect to PostgreSQL with read-only transactions as defense in depth."""
    uri = URL.create(
        "postgresql+psycopg2", username=username, password=password,
        host=host, port=int(port), database=database
    )
    return SQLDatabase.from_uri(
        uri,
        engine_args={
            "pool_pre_ping": True,
            "connect_args": {
                "options": "-c default_transaction_read_only=on",
                "connect_timeout": 8,
            },
        },
        sample_rows_in_table_info=2,
    )


def answer_question(db, question):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured.")
    llm = ChatGoogleGenerativeAI(
        model=MODEL, temperature=0, google_api_key=api_key,
        max_retries=2, timeout=45
    )


    agent = create_sql_agent(
        llm=llm, db=db, agent_type="zero-shot-react-description", verbose=False,
        max_iterations=10, max_execution_time=90,
        agent_executor_kwargs={"handle_parsing_errors": True},
    )

    result = agent.invoke({"input": question})
    return result.get("output", "I couldn't produce an answer.")


def main():
    st.set_page_config(page_title="AI Business Intelligence Assistant",
                       page_icon="📊", layout="wide")
    st.title("📊 AI Business Intelligence Assistant")
    st.caption("Explore PostgreSQL business data using natural-language questions.")
    st.markdown("**Tech stack:** Python · Streamlit · PostgreSQL · SQLAlchemy · LangChain · Google Gemini")

    if "db" not in st.session_state:
        st.session_state.db = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("🗄️ Database connection")
        st.caption("Use a dedicated PostgreSQL user with SELECT-only privileges.")
        with st.form("connect_form"):
            host = st.text_input("Host", value=os.getenv("DB_HOST", "localhost"))
            port = st.text_input("Port", value=os.getenv("DB_PORT", "5432"))
            database = st.text_input("Database name", value=os.getenv("DB_NAME", ""))
            username = st.text_input("Read-only username", value=os.getenv("DB_USER", ""))
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Connect database", type="primary")
            
        if submitted:
            if not os.getenv("GOOGLE_API_KEY"):
                st.error("Set GOOGLE_API_KEY in your .env file or deployment secrets.")
            elif not all([host.strip(), port.strip(), database.strip(), username.strip(), password]):
                st.warning("Please fill in every database field.")
            else:
                try:
                    db = connect_read_only_db(host.strip(), port.strip(), username.strip(),
                                              password, database.strip())
                    tables = db.get_usable_table_names()
                    st.session_state.db = db
                    st.session_state.messages = []
                    st.success(f"Connected. Found {len(tables)} usable table(s).")

                except Exception as e:
                    logger.exception("Database connection failed")
                    st.error(f"Connection failed: {e}")

        if st.session_state.db is not None and st.button("Disconnect database"):
            st.session_state.db = None
            st.session_state.messages = []
            st.rerun()

    if st.session_state.db is None:
        st.info("Connect a PostgreSQL database from the sidebar to begin.")
        st.markdown("### Example questions")
        st.markdown("- Show monthly revenue\n- List the top 10 customers by sales\n- Compare orders by region\n- Which products have the highest sales?")
        return

    with st.expander("Available database schema"):
        try:
            tables = st.session_state.db.get_usable_table_names()
            st.write(", ".join(tables) if tables else "No usable tables found.")
            for table in tables:
                with st.expander(f"Table: {table}"):
                    st.code(st.session_state.db.get_table_info([table]), language="sql")
        except Exception:
            logger.exception("Schema retrieval failed")
            st.warning("Schema information is currently unavailable.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a business question about your data…")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question…"):
                try:
                    answer = answer_question(st.session_state.db, question)
                    st.markdown(answer)
                    st.download_button("Download insight", data=answer,
                                       file_name="business_insight.txt",
                                       mime="text/plain")
                    st.session_state.messages.append({"role": "assistant", "content": answer})


                except Exception as e:
                    logger.exception("Analysis failed")
                    error_text = str(e)

                    if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
                        st.error(
                            "Gemini API quota exceeded. Please wait for the quota "
                            "to reset or check your Google AI Studio usage and billing."
                        )
                    elif "API_KEY_INVALID" in error_text or "API key not valid" in error_text:
                        st.error("Gemini API key is invalid. Check your local .env configuration.")
                    else:
                        st.error(f"Analysis failed: {error_text}")


if __name__ == "__main__":
    main()
