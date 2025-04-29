import streamlit as st
# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="IT Team Gamification",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import os
from datetime import datetime, timedelta, date
from auth import authenticate_user, get_current_user, is_authenticated, initialize_auth, logout
from utils import load_data, get_user_badges, get_team_by_id
from models.team import Team
from models.user import User
from models.badge import Badge
from models.sprint import Sprint
from models.badge_award import BadgeAward
from crud.db_manager import DatabaseManager

# Ensure database is populated with initial data in the correct order
# This will only add sample data if the tables are empty
load_data('teams')  # First, create teams
load_data('badges')  # Then badges
load_data('users')  # Then users (which have team dependencies)
load_data('sprints')  # Then sprints (which have team dependencies)
load_data('awards')  # Finally awards (which depend on badges, users, and potentially sprints)

# Store data in session state for UI rendering
if 'teams' not in st.session_state:
    st.session_state.teams = DatabaseManager.get_all(Team)
if 'badges_dict' not in st.session_state:
    all_badges = DatabaseManager.get_all(Badge)
    st.session_state.badges_dict = {badge['id']: badge for badge in all_badges}
if 'users' not in st.session_state:
    st.session_state.users = DatabaseManager.get_all(User)
if 'awards' not in st.session_state:
    st.session_state.awards = DatabaseManager.get_all(BadgeAward)
if 'sprints' not in st.session_state:
    st.session_state.sprints = DatabaseManager.get_all(Sprint)
if 'badges' not in st.session_state:
    st.session_state.badges = st.session_state.badges_dict

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Initialize authentication (for backwards compatibility)
initialize_auth()

# App title
st.title("🏆 IT Team Gamification Platform")

# Authentication check
if not is_authenticated():
    # Show login form
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            success = authenticate_user(username, password)
            if success:
                st.success("Login successful!")
                user = get_current_user()
                # Role-based navigation
                if user['role'] == 'Manager':
                    st.switch_page("pages/8_Dashboard-Manager.py")
                elif user['role'] == 'TL':
                    st.switch_page("pages/1_Dashboard.py")
                else:
                    st.switch_page("pages/1_Dashboard.py")
                st.rerun()
            else:
                st.error("Invalid username or password")
else:
    # Show the main content when authenticated
    user = get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.write(f"👤 Logged in as: **{user['name']}**")
        st.write(f"Role: **{user['role']}**")
        # Get team name from team_id
        team_name = "N/A"
        if user['team_id']:
            team = get_team_by_id(user['team_id'])
            if team:
                team_name = team['name']
        st.write(f"Team: **{team_name}**")
        
        st.divider()
        
        st.subheader("Navigation")
        st.write("Use the pages in the sidebar to navigate through different sections of the application.")
        
        st.divider()
        
        if st.button("Logout"):
            logout()
            st.rerun()
    
    # Main page content
    st.markdown("""
    ## Welcome to the IT Team Gamification Platform
    
    This platform is designed to track achievements, award badges, and motivate IT staff through gamification.
    
    ### Key Features:
    - Track personal and team achievements
    - Award and receive badges based on accomplishments
    - Monitor progress towards objectives
    - View team and individual performance metrics
    - Track sprint-based achievements
    - Separate tracking for regular work (80%) and objectives (20%)
    
    ### Get Started:
    - Navigate to the **Dashboard** to see your current badges and achievements
    - Explore **Badge Management** to view available badges and their criteria
    - Check **Badge Progress** to track your progress towards earning new badges
    - View **Teams** to see how your team is performing
    - Use **Sprint Planning** to integrate achievements with your sprint cycles
    - Access **Reports** for insights on team and individual performance
    
    Use the navigation sidebar to explore the platform's features.
    """)
    
    # Display some key metrics
    st.subheader("Your Badge Summary")
    
    # Get awards for current user from database
    # Use cached badges_dict from session state
    user_awards = get_user_badges(user['id'])
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Badges", len(user_awards))
    
    with col2:
        # Count badges earned in last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
        recent_badges = sum(1 for a in user_awards 
                          if a.get('awarded_at') and
                          isinstance(a['awarded_at'], date) and
                          a['awarded_at'] >= thirty_days_ago)
        st.metric("Recent Badges", recent_badges)
    
    with col3:
        # Calculate progress percentage towards next badge
        # This is simplified - in real app would be more complex
        progress = user.get('next_badge_progress', 0) 
        if progress == 0 and len(st.session_state.badges_dict) > len(user_awards):
            # Show some random progress if not set but user doesn't have all badges
            import random
            progress = random.randint(10, 90)
        st.metric("Progress to Next Badge", f"{progress}%")
    
    with col4:
        # Team ranking
        team_rank = user.get('team_rank', 'N/A')
        if team_rank == 'N/A' and user['team_id']:
            # If not set but user is in a team, show a placeholder ranking
            team_rank = "Top 5"
        st.metric("Team Ranking", team_rank)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if user_awards:
        # Get 5 most recent awards
        sorted_awards = sorted(user_awards, key=lambda x: x.get('awarded_at', '1900-01-01'), reverse=True)[:5]
        
        recent_awards_df = pd.DataFrame([
            {
                'Badge': award.get('name', 'Unknown'),
                'Date': award.get('awarded_at', 'N/A'),
                'Awarded By': award.get('awarded_by', 'System')
            }
            for award in sorted_awards
        ])
        st.dataframe(recent_awards_df, use_container_width=True)
    else:
        st.info("No badges awarded yet. Start completing tasks to earn badges!")
