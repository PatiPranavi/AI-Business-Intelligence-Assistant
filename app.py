import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent

# ---------------- Load Environment Variables ---------------- #

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# ---------------- Gemini + SQL Agent ---------------- #

async def get_answer_by_sql_query(db, user_input):

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        temperature=0
    )

    agent_executor = create_sql_agent(
        llm,
        db=db,
        verbose=True
    )

    response = agent_executor.invoke(
        {"input": user_input}
    )

    return response


# ---------------- Main App ---------------- #

def main():

    st.set_page_config(
        page_title="AI Business Intelligence Assistant",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 AI Business Intelligence Assistant")

    st.markdown(
        "**Tech Stack:** Python | Streamlit | PostgreSQL | LangChain | Google Gemini | SQL"
    )

    # ---------------- KPI Cards ---------------- #

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Revenue", "$125,400", "+8.2%")

    with col2:
        st.metric("🛒 Orders", "2,145", "+5.4%")

    with col3:
        st.metric("👥 Customers", "842", "+3.1%")

    with col4:
        st.metric("📈 Profit", "$38,600", "+9.7%")

    st.markdown(
        "Analyze business databases using natural language powered by **Google Gemini**, **LangChain**, and **PostgreSQL**."
    )

    st.info("""
### 💡 Example Business Questions

• Show monthly revenue

• Top 10 customers

• Which category generated highest sales?

• Which products are underperforming?

• Show region-wise sales

• Compare sales between Q1 and Q2
""")

    # ---------------- Session State ---------------- #

    if "activate_chat" not in st.session_state:
        st.session_state.activate_chat = False

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---------------- Display Chat History ---------------- #

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"],
            avatar=message["avatar"]
        ):
            st.markdown(message["content"])

    # ---------------- Sidebar ---------------- #

    with st.sidebar:

        st.header("🗄️ Database Connection")

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        hostname = st.text_input(
            "Host",
            value="localhost"
        )

        port = st.text_input(
            "Port",
            value="5432"
        )

        db_name = st.text_input("Database Name")

        if st.button("Connect Database"):

            if not GOOGLE_API_KEY:
                st.error("GOOGLE_API_KEY not found in .env file.")

            elif not all([username, password, hostname, port, db_name]):
                st.warning("Please fill all database details.")

            else:

                postgres_uri = (
                    f"postgresql+psycopg2://"
                    f"{username}:{password}@"
                    f"{hostname}:{port}/{db_name}"
                )

                try:

                    db = SQLDatabase.from_uri(postgres_uri)

                    st.session_state.db = db
                    st.session_state.activate_chat = True

                    st.success("✅ Database Connected Successfully!")

                    with st.expander("Connection Details"):
                        st.code(postgres_uri)

                except Exception as e:

                    st.error(f"❌ Database Connection Failed\n\n{e}")

    # ---------------- Chat Section ---------------- #

    if st.session_state.activate_chat:

        prompt = st.chat_input(
            "Ask a business question (e.g., Show monthly revenue)"
        )

        if prompt:

            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            st.session_state.messages.append(
                {
                    "role": "user",
                    "avatar": "👤",
                    "content": prompt
                }
            )

            try:

                with st.spinner("🤖 Analyzing database..."):

                    response = asyncio.run(
                        get_answer_by_sql_query(
                            st.session_state.db,
                            prompt
                        )
                    )

                cleaned_response = response["output"]

                with st.chat_message("assistant", avatar="📊"):

                    st.subheader("AI Business Insight")

                    st.success("Analysis Complete!")

                    st.markdown(cleaned_response)

                    st.download_button(
                        label="📥 Download Business Insight",
                        data=cleaned_response,
                        file_name="business_insight.txt",
                        mime="text/plain"
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "avatar": "📊",
                        "content": cleaned_response
                    }
                )

            except Exception as e:

                st.error(f"❌ {e}")

    else:

        st.warning("👈 Connect your PostgreSQL database to begin.")

    # ---------------- Footer ---------------- #

    st.divider()

    st.caption(
        "Built with ❤️ using Streamlit • LangChain • Google Gemini • PostgreSQL"
    )

    st.caption(
        "AI-generated insights depend on the connected database."
    )


if __name__ == "__main__":
    main()