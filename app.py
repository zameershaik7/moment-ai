import streamlit as st
from groq import Groq

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Moment AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE
# =====================================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "chats" not in st.session_state:
    st.session_state.chats = []

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None


def on_theme_change():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


# =====================================================
# THEME COLORS (CHATGPT-LIKE)
# =====================================================
if st.session_state.theme == "dark":
    BG = "#0f0f0f"
    SIDEBAR = "#171717"
    CARD = "#1f1f1f"
    BORDER = "#2a2a2a"
    TEXT = "#ffffff"
    MUTED = "#b3b3b3"
    PRIMARY_BG = "#ffffff"
    PRIMARY_TEXT = "#000000"
else:
    BG = "#ffffff"
    SIDEBAR = "#f7f7f8"
    CARD = "#ffffff"
    BORDER = "#e5e5e5"
    TEXT = "#000000"
    MUTED = "#555555"
    PRIMARY_BG = "#000000"
    PRIMARY_TEXT = "#ffffff"

# =====================================================
# GLOBAL CSS (STABLE + CLEAR)
# =====================================================
st.markdown(
    f"""
    <style>
    html, body, .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    header, footer {{
        display: none;
    }}

    .block-container {{
        max-width: 900px;
        padding-top: 0.6rem;
        padding-bottom: 2rem;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR};
        border-right: 1px solid {BORDER};
    }}

    section[data-testid="stSidebar"] * {{
        color: {TEXT} !important;
    }}

    /* PRIMARY SIDEBAR BUTTON (NEW CHAT) */
    .primary-btn button {{
        background-color: {PRIMARY_BG} !important;
        color: {PRIMARY_TEXT} !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
    }}

    /* NORMAL BUTTONS */
    button {{
        border-radius: 10px !important;
        font-weight: 500 !important;
    }}

    .card {{
        background-color: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 0.75rem;
    }}

    textarea, input {{
        background-color: {CARD} !important;
        color: {TEXT} !important;
        border-radius: 8px !important;
    }}

    h1 {{
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }}

    p {{
        color: {MUTED};
        margin-top: 0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# CLIENT
# =====================================================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown(
        """
        <div style="font-size:1.3rem;font-weight:700;">
            ◉ Moment <span style="font-size:0.75rem;opacity:0.6;">1.0</span>
        </div>
        <p>Decide the best next action — right now.</p>
        """,
        unsafe_allow_html=True
    )

    # PRIMARY BUTTON
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("New chat", use_container_width=True):
        st.session_state.active_chat = None
    st.markdown('</div>', unsafe_allow_html=True)

    st.text_input("Search chats")

    st.markdown("### Recent")
    if not st.session_state.chats:
        st.caption("No chats yet")
    else:
        for i, chat in enumerate(st.session_state.chats):
            title = chat.get("title", "Untitled decision")
            if st.button(title, key=f"chat_{i}", use_container_width=True):
                st.session_state.active_chat = i

    st.markdown("---")

    st.toggle(
        "Dark mode",
        value=(st.session_state.theme == "dark"),
        on_change=on_theme_change
    )

# =====================================================
# MAIN
# =====================================================
st.markdown(
    """
    <h1>Moment AI</h1>
    <p>A human-like decision engine for the current moment.</p>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="card">', unsafe_allow_html=True)

current_time = st.text_input("Current time", placeholder="e.g. 7:45 PM")
energy = st.radio("Energy level", ["Low", "Medium", "High"], horizontal=True)
mental = st.radio("Mental state", ["Stressed", "Neutral", "Motivated"], horizontal=True)
goal = st.text_area("Your goal", placeholder="Clearly state the one thing that matters right now…", height=90)

run = st.button("Make the decision", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# AI RESPONSE
# =====================================================
if run and goal and current_time:
    system_prompt = """
You are Moment AI — a human-like decision engine.
Make ONE decisive judgment call.
Explain using Productivity, Structure, Growth, Well-being.
"""

    user_prompt = f"""
Time: {current_time}
Energy: {energy}
Mental state: {mental}
Goal: {goal}
"""

    with st.spinner("Thinking…"):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=350
        )

    response = completion.choices[0].message.content

    st.session_state.chats.append({
        "title": goal[:50],
        "messages": [{"role": "assistant", "content": response}]
    })
    st.session_state.active_chat = len(st.session_state.chats) - 1

if st.session_state.active_chat is not None:
    chat = st.session_state.chats[st.session_state.active_chat]
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Do this now")
    st.markdown(chat["messages"][0]["content"])
    st.markdown('</div>', unsafe_allow_html=True)
