import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from auth import is_authenticated, get_current_user
from queries.gamification_queries import GamificationQueries
from utils import  get_user_badges, get_team_by_id, calculate_team_stats

def calculate_next_badge_progress(user_badges):
    """
    Calculate the user's progress towards the next badge.
    The logic here is just a placeholder for actual business logic.
    """
    total_badges = len(user_badges)
    badges_needed_for_next = 10  # Placeholder: this would be dynamic based on the system's rules
    
    if total_badges >= badges_needed_for_next:
        return 100  # Already reached the next badge
    
    progress = (total_badges / badges_needed_for_next) * 100
    return round(progress)

def calculate_recent_badges(user_badges):
    """
    Calculate the number of badges earned by the user in the last 30 days.
    """
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
    recent_badges = sum(1 for badge in user_badges if isinstance(badge['awarded_at'], date) and badge['awarded_at'] >= thirty_days_ago)
    return recent_badges

# Page config
st.set_page_config(page_title="Dashboard - IT Team Gamification", page_icon="🏆", layout="wide")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Get current user
user = get_current_user()
user_badges = get_user_badges(user['id'])
team = get_team_by_id(user['team_id'])

# Dashboard Header
st.title("🏆 Achievement Dashboard")
st.write(f"Welcome back, **{user['name']}**! Here's a summary of your achievements.")

# Create columns for main content
col1, col2 = st.columns([2, 1])

with col1:
    # Badge Summary
    st.subheader("Your Badge Collection")
    if user_badges:
        badges_df = pd.DataFrame([
            {
                'Badge': badge['name'],
                'Category': badge['category'],
                'Date Earned': badge['awarded_at'].strftime('%Y-%m-%d') if isinstance(badge['awarded_at'], (datetime, date)) else 'N/A',
                'Awarded By': badge.get('awarded_by', 'System'),
                'Description': badge['description']
            } for badge in user_badges
        ])
        st.dataframe(badges_df, use_container_width=True)

        # Badge Category Pie Chart
        category_counts = badges_df['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        fig = px.pie(category_counts, values='Count', names='Category', title='Badges by Category', color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("You haven't earned any badges yet. Complete tasks to earn your first badge!")

with col2:
    # Personal Stats
    st.subheader("Personal Statistics")
    badge_counts = {category: sum(1 for b in user_badges if b['category'] == category) for category in ['Technical', 'Leadership', 'Teamwork', 'Innovation', 'Other']}
    for category, count in badge_counts.items():
        st.metric(f"{category} Badges", count)
    st.metric("Total Badges", len(user_badges))

    # Next Badge Progress
    progress = calculate_next_badge_progress(user_badges)  # Replace with actual logic
    st.subheader("Next Badge Progress")
    st.progress(progress/100)
    st.write(f"{progress}% complete")

# Team Performance
st.subheader(f"Team Performance: {team['name']}")
team_stats = calculate_team_stats(team['id'])

# Show team stats in columns
tm1, tm2, tm3, tm4 = st.columns(4)
with tm1: st.metric("Total Team Badges", team_stats['total_badges'])
with tm2: st.metric("Average Badges/Member", team_stats['avg_badges'])
with tm3: st.metric("Badges in Last 30 Days", calculate_recent_badges(user_badges))
with tm4: st.metric("Team Top Performer", team_stats['top_performer'])

# Leaderboard
st.subheader("Team Leaderboard")
team_members = GamificationQueries.get_team_members(team['id'])  # Use GamificationQueries instead of DatabaseManager

# Show leaderboard
leaderboard_data = []
for member in team_members:
    try:
        member_badges = get_user_badges(member['id'])
        leaderboard_data.append({
            "Name": member['name'],
            "Badges": len(member_badges) if member_badges else 0
        })
    except Exception as e:
        st.error(f"Error loading badges for {member['name']}: {str(e)}")
        continue

if leaderboard_data:
    leaderboard_df = pd.DataFrame(leaderboard_data).sort_values('Badges', ascending=False)
    fig = px.bar(leaderboard_df, x='Name', y='Badges', color='Badges', title='Team Leaderboard')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No team member data available for the leaderboard.")
