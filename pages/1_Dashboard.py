import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from auth import is_authenticated, get_current_user
from utils import get_user_badges, get_team_by_id, calculate_team_stats

# Page config
st.set_page_config(
    page_title="Dashboard - IT Team Gamification",
    page_icon="🏆",
    layout="wide"
)

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

# Create two columns for the main content
col1, col2 = st.columns([2, 1])

with col1:
    # Badge Summary
    st.subheader("Your Badge Collection")
    
    if user_badges:
        # Create a DataFrame for the badges
        badges_df = pd.DataFrame([
            {
                'Badge': badge['name'],
                'Category': badge['category'],
                'Date Earned': badge.get('award_date', 'N/A'),
                'Awarded By': badge.get('awarded_by', 'System'),
                'Description': badge['description']
            } 
            for badge in user_badges
        ])
        
        # Display as a table
        st.dataframe(badges_df, use_container_width=True)
        
        # Create a pie chart for badge categories
        category_counts = badges_df['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        fig = px.pie(
            category_counts, 
            values='Count', 
            names='Category',
            title='Badges by Category',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("You haven't earned any badges yet. Complete tasks to earn your first badge!")

with col2:
    # Personal Stats
    st.subheader("Personal Statistics")
    
    # Count badges by type
    badge_counts = {
        'Technical': sum(1 for b in user_badges if b['category'] == 'Technical'),
        'Leadership': sum(1 for b in user_badges if b['category'] == 'Leadership'),
        'Teamwork': sum(1 for b in user_badges if b['category'] == 'Teamwork'),
        'Innovation': sum(1 for b in user_badges if b['category'] == 'Innovation'),
        'Other': sum(1 for b in user_badges if b['category'] not in ['Technical', 'Leadership', 'Teamwork', 'Innovation'])
    }
    
    # Display badge counts
    for category, count in badge_counts.items():
        st.metric(f"{category} Badges", count)
    
    # Total badges
    st.metric("Total Badges", len(user_badges))
    
    # Next Badge Progress
    # In a real app, this would calculate actual progress
    import random
    progress = random.randint(0, 100) if user_badges else 0
    
    st.subheader("Next Badge Progress")
    st.progress(progress/100)
    st.write(f"{progress}% complete")

# Team Performance
st.subheader(f"Team Performance: {team['name']}")

# Calculate team stats
team_stats = calculate_team_stats(team['id'])

# Create columns for team metrics
tm1, tm2, tm3, tm4 = st.columns(4)

with tm1:
    st.metric("Total Team Badges", team_stats['total_badges'])

with tm2:
    st.metric("Average Badges/Member", team_stats['avg_badges'])

with tm3:
    st.metric("Badges in Last 30 Days", team_stats['recent_badges'])

with tm4:
    st.metric("Team Top Performer", team_stats['top_performer'])

# Recent Activity Timeline
st.subheader("Recent Activity Timeline")

if user_badges:
    # Sort badges by award date
    sorted_badges = sorted(
        user_badges, 
        key=lambda x: x.get('award_date', '1900-01-01'),
        reverse=True
    )[:5]  # Get 5 most recent
    
    # Create timeline
    for badge in sorted_badges:
        with st.expander(f"{badge['name']} - {badge.get('award_date', 'N/A')}"):
            st.write(f"**Category:** {badge['category']}")
            st.write(f"**Description:** {badge['description']}")
            st.write(f"**Awarded by:** {badge.get('awarded_by', 'System')}")
else:
    st.info("No recent activity to display.")

# Work vs. Objectives Split
st.subheader("Work (80%) vs. Objectives (20%) Split")

# Create sample data for the split
work_obj_data = {
    'Category': ['Regular Work', 'Objectives'],
    'Badges': [
        sum(1 for b in user_badges if b.get('badge_type') == 'work'), 
        sum(1 for b in user_badges if b.get('badge_type') == 'objective')
    ]
}

if sum(work_obj_data['Badges']) > 0:
    work_obj_df = pd.DataFrame(work_obj_data)
    
    fig = px.bar(
        work_obj_df,
        x='Category',
        y='Badges',
        color='Category',
        title='Badges by Work Type',
        color_discrete_sequence=['#4169E1', '#32CD32']
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No work/objective data available yet.")

# Leaderboard
st.subheader("Team Leaderboard")

# Get all team members
from database import get_all, User, BadgeAward
team_members = get_team_members(team['id'])

# Calculate badge counts for each member
leaderboard_data = []
all_awards = get_all(BadgeAward)
for member in team_members:
    member_badges = [a for a in all_awards if a['user_id'] == member['id']]
    leaderboard_data.append({
        'Name': member['name'],
        'Role': member['role'],
        'Badges': len(member_badges)
    })

# Sort by badge count
leaderboard_df = pd.DataFrame(leaderboard_data).sort_values('Badges', ascending=False)

# Show leaderboard
if not leaderboard_df.empty:
    # Highlight current user
    leaderboard_df['Current User'] = leaderboard_df['Name'] == user['name']
    
    # Create a bar chart
    fig = px.bar(
        leaderboard_df,
        x='Name',
        y='Badges',
        color='Current User',
        title='Team Leaderboard',
        color_discrete_map={True: '#4169E1', False: '#A9A9A9'},
        hover_data=['Role']
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No leaderboard data available.")
