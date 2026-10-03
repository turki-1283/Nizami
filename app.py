import streamlit as st

from nizami import ask_nizami_with_sources


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="نظامي",
    page_icon="⚖️",
    layout="centered",
)


# --------------------------------------------------
# RTL styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {
        direction: rtl !important;
    }

    [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    [data-testid="stChatMessage"] {
        direction: rtl !important;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    [data-testid="stChatMessage"] h1 {
        direction: rtl !important;
        text-align: right !important;
        font-size: 28px !important;
        line-height: 1.5 !important;
        margin-top: 18px !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatMessage"] h2 {
        direction: rtl !important;
        text-align: right !important;
        font-size: 22px !important;
        line-height: 1.6 !important;
        margin-top: 18px !important;
        margin-bottom: 10px !important;
    }

    [data-testid="stChatMessage"] h3 {
        direction: rtl !important;
        text-align: right !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
        margin-top: 14px !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stChatMessage"] p {
        direction: rtl !important;
        text-align: right !important;
        font-size: 16px !important;
        line-height: 1.9 !important;
    }

    [data-testid="stChatMessage"] ul,
    [data-testid="stChatMessage"] ol {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 28px !important;
        padding-left: 0 !important;
    }

    [data-testid="stChatMessage"] li {
        direction: rtl !important;
        text-align: right !important;
        font-size: 16px !important;
        line-height: 1.9 !important;
        margin-bottom: 5px !important;
    }

    [data-testid="stChatMessage"] blockquote {
        direction: rtl !important;
        text-align: right !important;
        border-right: 3px solid #555 !important;
        border-left: none !important;
        padding-right: 15px !important;
        padding-left: 0 !important;
        margin-right: 0 !important;
        margin-left: 0 !important;
    }

    [data-testid="stChatMessage"] blockquote p {
        text-align: right !important;
    }

    [data-testid="stChatInput"] {
        direction: rtl !important;
    }

    [data-testid="stChatInput"] textarea {
        direction: rtl !important;
        text-align: right !important;
    }

    h1,
    .stCaption {
        text-align: right !important;
    }

    [data-testid="stExpander"],
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    div.stButton {
        direction: rtl !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def display_sources(sources):
    """Display retrieved Saudi Labor Law articles."""
    if not sources:
        return

    with st.expander("📚 عرض المواد المسترجعة"):
        for source in sources:
            st.markdown(f"### {source['title']}")
            st.write(source["text"])
            st.divider()


def initialize_chat():
    """Initialize the chat history."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """
مرحبًا بك في **نظامي** ⚖️

اسألني عن حقوق وواجبات العامل وصاحب العمل وفق **نظام العمل السعودي**.

> **تنبيه:** نظامي مساعد معلوماتي ولا تغني إجاباته عن الاستشارة القانونية المتخصصة.
""",
            }
        ]


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("⚖️ نظامي")

st.caption(
    "مساعد ذكي للإجابة عن أسئلتك وفق نظام العمل السعودي"
)


# --------------------------------------------------
# New conversation
# --------------------------------------------------

if st.button("＋ محادثة جديدة"):
    st.session_state.pop("messages", None)
    st.rerun()


# --------------------------------------------------
# Chat history
# --------------------------------------------------

initialize_chat()

for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="⚖️"):
            st.markdown(message["content"])
            display_sources(message.get("sources", []))

    else:
        with st.chat_message("user"):
            st.markdown(message["content"])


# --------------------------------------------------
# User input
# --------------------------------------------------

question = st.chat_input("اسأل عن نظام العمل السعودي...")


# --------------------------------------------------
# Generate response
# --------------------------------------------------

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="⚖️"):
        try:
            with st.spinner("أراجع مواد نظام العمل..."):
                answer, sources = ask_nizami_with_sources(question)

            st.markdown(answer)
            display_sources(sources)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except Exception:
            error_message = (
                "حدث خطأ أثناء معالجة السؤال. "
                "يرجى المحاولة مرة أخرى."
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )