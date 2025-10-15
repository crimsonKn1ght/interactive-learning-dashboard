# startup.py
import streamlit as st

st.set_page_config(
    page_title="Career Trajectory Coach",
    layout="centered",  # Changed to wide for dashboard
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.logged_in:
    pages = [
        st.Page("pages/profile.py", title="Current Role Profile", icon="👤"),
        st.Page("pages/career_coach.py", title="Career Goals", icon="✍🏻"),
        st.Page("pages/skills_dashboard.py", title="Skills Dashboard", icon="👨🏻‍💻"),
        st.Page("pages/analysis_dashboard.py", title="Analysis Dashboard", icon="📖"),
    ]
else:
    pages = [
        st.Page("pages/login.py", title="Login", icon="🔐"),
    ]

pg = st.navigation(pages)
pg.run()
