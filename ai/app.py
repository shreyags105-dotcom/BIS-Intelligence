import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_DIR = PROJECT_ROOT / "ai"

if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))

try:
    from rag import ask_bis
except ImportError:
    from ai.rag import ask_bis


# ============================================================
# PAGE
# ============================================================

st.set_page_config(

    page_title="BIS Intelligent Assistant",

    page_icon="🇮🇳",

    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🇮🇳 BIS Intelligent Assistant"
)

st.write(
    "AI-powered Indian Standards and "
    "BIS Services Assistant"
)


st.info(
    "Ask about products, Indian Standards, "
    "requirements, safety, testing and certification."
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.subheader("Try asking")


examples = [

    "I manufacture domestic pressure cookers. Which standard applies?",

    "What are the safety requirements for helmets?",

    "What tests are required for cement?",

    "How do I get BIS certification for my product?",

    "What standard applies to LED lamps?"

]


for example in examples:

    st.write(
        "• " + example
    )


# ============================================================
# CHAT
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# INPUT
# ============================================================

question = st.chat_input(
    "Ask your BIS question..."
)


if question:

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    st.session_state.messages.append({

        "role": "user",

        "content": question

    })


    with st.chat_message("user"):

        st.markdown(question)


    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching verified BIS information..."
        ):

            try:

                response = ask_bis(
                    question
                )


                # Answer
                st.markdown(
                    response["answer"]
                )


                # ------------------------------------------------
                # SOURCES
                # ------------------------------------------------

                if response["results"]:

                    st.markdown(
                        "### 📚 BIS Sources"
                    )


                    shown = set()


                    for result in response["results"]:

                        source = result["source"]

                        if source not in shown:

                            st.write(
                                f"**{result['standard']}** — "
                                f"{result['product']}"
                            )

                            if result["url"]:

                                st.write(
                                    result["url"]
                                )

                            shown.add(source)


                st.session_state.messages.append({

                    "role": "assistant",

                    "content": response["answer"]

                })


            except Exception as e:

                st.error(
                    f"Error: {e}"
                )