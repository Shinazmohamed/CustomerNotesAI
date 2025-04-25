import streamlit as st
from models.team import Team
from models.user import User
from models.badge import Badge
from models.sprint import Sprint
from models.badge_award import BadgeAward
from crud.db_manager import DatabaseManager

def initialize_app_data():
    if 'teams' not in st.session_state:
        st.session_state.teams = DatabaseManager.get_all(Team)
    if 'badges_dict' not in st.session_state:
        badges = DatabaseManager.get_all(Badge)
        st.session_state.badges_dict = {b['id']: b for b in badges}
    if 'users' not in st.session_state:
        st.session_state.users = DatabaseManager.get_all(User)
    if 'awards' not in st.session_state:
        st.session_state.awards = DatabaseManager.get_all(BadgeAward)
    if 'sprints' not in st.session_state:
        st.session_state.sprints = DatabaseManager.get_all(Sprint)
    if 'badges' not in st.session_state:
        st.session_state.badges = st.session_state.badges_dict

def initialize_auth_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
