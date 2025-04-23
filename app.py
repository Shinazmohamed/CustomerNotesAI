import streamlit as st
import pandas as pd
import os
from auth import authenticate_user, get_current_user, is_authenticated, initialize_auth, logout
from utils import load_data, save_data

# Page configuration
st.set_page_config(
    page_title="IT Team Gamification",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing data
if 'badges' not in st.session_state:
    st.session_state.badges = load_data('badges')
if 'users' not in st.session_state:
    st.session_state.users = load_data('users')
if 'teams' not in st.session_state:
    st.session_state.teams = load_data('teams')
if 'awards' not in st.session_state:
    st.session_state.awards = load_data('awards')
if 'sprints' not in st.session_state:
    st.session_state.sprints = load_data('sprints')

# Initialize authentication
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
        st.write(f"Team: **{user['team']}**")
        
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
    
    # Filter awards for current user
    user_awards = [a for a in st.session_state.awards if a['user_id'] == user['id']]
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Badges", len(user_awards))
    
    with col2:
        # Count badges earned in last 30 days
        # In a real app, we'd use datetime, but for simplicity:
        recent_badges = sum(1 for a in user_awards if a.get('recent', False))
        st.metric("Recent Badges", recent_badges)
    
    with col3:
        # Calculate progress percentage towards next badge
        # This is simplified - in real app would be more complex
        progress = user.get('next_badge_progress', 0)
        st.metric("Progress to Next Badge", f"{progress}%")
    
    with col4:
        # Team ranking
        team_rank = user.get('team_rank', 'N/A')
        st.metric("Team Ranking", team_rank)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if user_awards:
        recent_awards_df = pd.DataFrame([
            {
                'Badge': st.session_state.badges[a['badge_id']]['name'] if a['badge_id'] in st.session_state.badges else "Unknown",
                'Date': a.get('award_date', 'N/A'),
                'Awarded By': a.get('awarded_by', 'System')
            }
            for a in user_awards[:5]  # Show only the 5 most recent
        ])
        st.dataframe(recent_awards_df, use_container_width=True)
    else:
        st.info("No badges awarded yet. Start completing tasks to earn badges!")
