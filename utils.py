import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import csv
import io

def load_data(data_type):
    """
    Load data from persistence layer.
    In a production app, this would use a database.
    For this sample, we're using session state to simulate persistence.
    """
    # Initialize with sample data if not already loaded
    from data.sample_data import (
        sample_badges, 
        sample_users, 
        sample_teams, 
        sample_awards,
        sample_sprints
    )
    
    if data_type == 'badges':
        return sample_badges
    elif data_type == 'users':
        return sample_users
    elif data_type == 'teams':
        return sample_teams
    elif data_type == 'awards':
        return sample_awards
    elif data_type == 'sprints':
        return sample_sprints
    else:
        return []

def save_data(data_type, data):
    """
    Save data to persistence layer.
    In a production app, this would use a database.
    For this sample, we're storing in session state.
    """
    if data_type == 'badges':
        st.session_state.badges = data
    elif data_type == 'users':
        st.session_state.users = data
    elif data_type == 'teams':
        st.session_state.teams = data
    elif data_type == 'awards':
        st.session_state.awards = data
    elif data_type == 'sprints':
        st.session_state.sprints = data

def get_user_by_id(user_id):
    """Get a user by their ID"""
    users = st.session_state.users
    return next((u for u in users if u['id'] == user_id), None)

def get_badge_by_id(badge_id):
    """Get a badge by its ID"""
    badges = st.session_state.badges
    return badges.get(badge_id, None)

def get_team_by_id(team_id):
    """Get a team by its ID"""
    teams = st.session_state.teams
    return next((t for t in teams if t['id'] == team_id), None)

def get_user_badges(user_id):
    """Get all badges for a specific user"""
    awards = st.session_state.awards
    user_awards = [a for a in awards if a['user_id'] == user_id]
    
    result = []
    for award in user_awards:
        badge = get_badge_by_id(award['badge_id'])
        if badge:
            badge_data = badge.copy()
            badge_data.update({
                'award_date': award.get('award_date', 'N/A'),
                'awarded_by': award.get('awarded_by', 'System'),
                'award_id': award.get('id', 'N/A')
            })
            result.append(badge_data)
    
    return result

def get_team_members(team_id):
    """Get all members of a specific team"""
    users = st.session_state.users
    return [u for u in users if u['team_id'] == team_id]

def generate_unique_id(prefix=""):
    """Generate a unique ID based on timestamp"""
    import time
    return f"{prefix}{int(time.time() * 1000)}"

def format_date(date_str):
    """Format a date string for display"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%b %d, %Y")
    except:
        return date_str

def calculate_badge_progress(user_id, badge_id):
    """
    Calculate a user's progress towards earning a specific badge
    This would be more complex in a real application
    """
    badge = get_badge_by_id(badge_id)
    if not badge:
        return 0
    
    # Check if user already has this badge
    user_badges = get_user_badges(user_id)
    if any(b['id'] == badge_id for b in user_badges):
        return 100
    
    # In a real app, you would check specific criteria
    # For this sample, we'll return a random percentage
    import random
    return random.randint(0, 99)

def export_to_csv(data, filename="export.csv"):
    """Export data to a CSV file for download"""
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    # Create a download button
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

def filter_badges_by_role(badges, role):
    """Filter badges by role requirement"""
    if role == 'All':
        return badges
    
    # Convert badges dict to list if needed
    if isinstance(badges, dict):
        badges_list = list(badges.values())
    else:
        badges_list = badges
    
    return [b for b in badges_list if role in b.get('eligible_roles', [])]

def get_current_sprint():
    """Get the current active sprint"""
    sprints = st.session_state.sprints
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for sprint in sprints:
        start_date = sprint.get('start_date')
        end_date = sprint.get('end_date')
        
        if start_date and end_date:
            if start_date <= current_date <= end_date:
                return sprint
    
    # Return the most recent sprint if no active sprint is found
    if sprints:
        return sorted(sprints, key=lambda x: x.get('end_date', ''), reverse=True)[0]
    
    return None

def calculate_team_stats(team_id):
    """Calculate statistics for a team"""
    team_members = get_team_members(team_id)
    awards = st.session_state.awards
    
    total_badges = 0
    badges_per_member = {}
    recent_badges = 0
    
    # Calculate 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    for member in team_members:
        member_id = member['id']
        member_awards = [a for a in awards if a['user_id'] == member_id]
        
        # Count total badges
        member_badge_count = len(member_awards)
        total_badges += member_badge_count
        badges_per_member[member_id] = member_badge_count
        
        # Count recent badges
        for award in member_awards:
            award_date = award.get('award_date', '1900-01-01')
            if award_date >= thirty_days_ago:
                recent_badges += 1
    
    # Calculate average badges per member
    avg_badges = total_badges / len(team_members) if team_members else 0
    
    # Find top performer
    top_performer_id = max(badges_per_member.items(), key=lambda x: x[1])[0] if badges_per_member else None
    top_performer = next((m for m in team_members if m['id'] == top_performer_id), None)
    
    return {
        'total_badges': total_badges,
        'recent_badges': recent_badges,
        'avg_badges': round(avg_badges, 2),
        'top_performer': top_performer['name'] if top_performer else 'N/A',
        'member_count': len(team_members)
    }
