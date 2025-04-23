import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import csv
import io
from database import (
    get_all, get_by_id, create, update, delete, 
    get_user_by_username, get_team_members as db_get_team_members,
    get_user_badges as db_get_user_badges, get_active_sprints,
    User, Team, Badge, BadgeAward, Sprint
)

def load_data(data_type):
    """
    Load data from database.
    If no data exists, populate with sample data.
    """
    # Check if data exists
    if data_type == 'badges':
        data = get_all(Badge)
        if not data:
            # Load sample data
            from data.sample_data import sample_badges
            for badge_id, badge_data in sample_badges.items():
                badge_data['id'] = badge_id
                try:
                    create(Badge, badge_data)
                except Exception as e:
                    import streamlit as st
                    st.error(f"Error creating badge {badge_id}: {str(e)}")
            data = get_all(Badge)
        
        # Convert to dictionary format compatible with existing code
        return {badge['id']: badge for badge in data}
    
    elif data_type == 'teams':
        data = get_all(Team)
        if not data:
            # Load sample data
            from data.sample_data import sample_teams
            for team_data in sample_teams:
                try:
                    create(Team, team_data)
                except Exception as e:
                    import streamlit as st
                    st.error(f"Error creating team {team_data.get('id')}: {str(e)}")
            data = get_all(Team)
        return data
    
    elif data_type == 'users':
        # Make sure teams are loaded first
        load_data('teams')
        
        data = get_all(User)
        if not data:
            # Load sample data
            from data.sample_data import sample_users
            for user_data in sample_users:
                try:
                    create(User, user_data)
                except Exception as e:
                    import streamlit as st
                    st.error(f"Error creating user {user_data.get('id')}: {str(e)}")
            data = get_all(User)
        return data
    
    elif data_type == 'sprints':
        # Make sure teams are loaded first
        load_data('teams')
        
        data = get_all(Sprint)
        if not data:
            # Load sample data
            from data.sample_data import sample_sprints
            for sprint_data in sample_sprints:
                try:
                    create(Sprint, sprint_data)
                except Exception as e:
                    import streamlit as st
                    st.error(f"Error creating sprint {sprint_data.get('id')}: {str(e)}")
            data = get_all(Sprint)
        return data
    
    elif data_type == 'awards':
        # Make sure users and badges are loaded first
        load_data('users')
        load_data('badges')
        
        data = get_all(BadgeAward)
        if not data:
            # Load sample data
            from data.sample_data import sample_awards
            for award_data in sample_awards:
                try:
                    create(BadgeAward, award_data)
                except Exception as e:
                    import streamlit as st
                    st.error(f"Error creating award {award_data.get('id')}: {str(e)}")
            data = get_all(BadgeAward)
        return data
    
    else:
        return []

def save_data(data_type, data):
    """
    Save data to database.
    For bulk operations, this would be optimized in a production app.
    """
    if data_type == 'badges':
        # For dictionary-based badges
        if isinstance(data, dict):
            for badge_id, badge_data in data.items():
                badge_data['id'] = badge_id
                # Check if badge exists
                existing = get_by_id(Badge, badge_id)
                if existing:
                    update(Badge, badge_id, badge_data)
                else:
                    create(Badge, badge_data)
        # For list-based badges
        else:
            for badge_data in data:
                badge_id = badge_data.get('id')
                if badge_id:
                    existing = get_by_id(Badge, badge_id)
                    if existing:
                        update(Badge, badge_id, badge_data)
                    else:
                        create(Badge, badge_data)
    
    elif data_type == 'users':
        for user_data in data:
            user_id = user_data.get('id')
            if user_id:
                existing = get_by_id(User, user_id)
                if existing:
                    update(User, user_id, user_data)
                else:
                    create(User, user_data)
    
    elif data_type == 'teams':
        for team_data in data:
            team_id = team_data.get('id')
            if team_id:
                existing = get_by_id(Team, team_id)
                if existing:
                    update(Team, team_id, team_data)
                else:
                    create(Team, team_data)
    
    elif data_type == 'awards':
        for award_data in data:
            award_id = award_data.get('id')
            if award_id:
                existing = get_by_id(BadgeAward, award_id)
                if existing:
                    update(BadgeAward, award_id, award_data)
                else:
                    create(BadgeAward, award_data)
    
    elif data_type == 'sprints':
        for sprint_data in data:
            sprint_id = sprint_data.get('id')
            if sprint_id:
                existing = get_by_id(Sprint, sprint_id)
                if existing:
                    update(Sprint, sprint_id, sprint_data)
                else:
                    create(Sprint, sprint_data)

def get_user_by_id(user_id):
    """Get a user by their ID"""
    return get_by_id(User, user_id)

def get_badge_by_id(badge_id):
    """Get a badge by its ID"""
    return get_by_id(Badge, badge_id)

def get_team_by_id(team_id):
    """Get a team by its ID"""
    return get_by_id(Team, team_id)

def get_user_badges(user_id):
    """Get all badges for a specific user"""
    awards = db_get_user_badges(user_id)
    
    result = []
    for award in awards:
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
    return db_get_team_members(team_id)

def generate_unique_id(prefix=""):
    """Generate a unique ID based on timestamp"""
    import time
    return f"{prefix}{int(time.time() * 1000)}"

def format_date(date_val):
    """Format a date value for display"""
    try:
        if isinstance(date_val, (datetime, date)):
            return date_val.strftime("%b %d, %Y")
        elif isinstance(date_val, str):
            date_obj = datetime.strptime(date_val, "%Y-%m-%d")
            return date_obj.strftime("%b %d, %Y")
        return str(date_val)
    except:
        return str(date_val)

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
    active_sprints = get_active_sprints()
    if active_sprints:
        return active_sprints[0]
    
    # If no active sprint, get all sprints and find the most recent
    all_sprints = get_all(Sprint)
    if all_sprints:
        return sorted(all_sprints, key=lambda x: x.get('end_date', ''), reverse=True)[0]
    
    return None

def calculate_team_stats(team_id):
    """Calculate statistics for a team"""
    team_members = get_team_members(team_id)
    awards = get_all(BadgeAward)
    
    total_badges = 0
    badges_per_member = {}
    recent_badges = 0
    
    # Calculate 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
    
    for member in team_members:
        member_id = member['id']
        member_awards = [a for a in awards if a['user_id'] == member_id]
        
        # Count total badges
        member_badge_count = len(member_awards)
        total_badges += member_badge_count
        badges_per_member[member_id] = member_badge_count
        
        # Count recent badges
        for award in member_awards:
            award_date = award.get('award_date')
            if award_date and isinstance(award_date, date) and award_date >= thirty_days_ago:
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
