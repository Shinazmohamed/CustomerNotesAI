import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from models.team import Team
from models.user import User
from models.badge import Badge
from models.sprint import Sprint
from models.badge_award import BadgeAward
from crud.db_manager import DatabaseManager
from queries.gamification_queries import GamificationQueries
import json

def load_data(data_type):
    if data_type == 'badges':
        return {badge['id']: badge for badge in DatabaseManager.get_all(Badge)}
    
    elif data_type == 'teams':
        return DatabaseManager.get_all(Team)
    
    elif data_type == 'users':
        return DatabaseManager.get_all(User)
    
    elif data_type == 'sprints':
        return DatabaseManager.get_all(Sprint)
    
    elif data_type == 'awards':
        return DatabaseManager.get_all(BadgeAward)
    
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
                existing = DatabaseManager.get_by_id(Badge, badge_id)
                if existing:
                    DatabaseManager.update(Badge, badge_id, badge_data)
                else:
                    DatabaseManager.create(Badge, badge_data)
        # For list-based badges
        else:
            for badge_data in data:
                badge_id = badge_data.get('id')
                if badge_id:
                    existing = DatabaseManager.get_by_id(Badge, badge_id)
                    if existing:
                        DatabaseManager.update(Badge, badge_id, badge_data)
                    else:
                        DatabaseManager.create(Badge, badge_data)
    
    elif data_type == 'users':
        for user_data in data:
            user_id = user_data.get('id')
            if user_id:
                existing = DatabaseManager.get_by_id(User, user_id)
                if existing:
                    DatabaseManager.update(User, user_id, user_data)
                else:
                    DatabaseManager.create(User, user_data)
    
    elif data_type == 'teams':
        for team_data in data:
            team_id = team_data.get('id')
            if team_id:
                existing = DatabaseManager.get_by_id(Team, team_id)
                if existing:
                    DatabaseManager.update(Team, team_id, team_data)
                else:
                    DatabaseManager.create(Team, team_data)
    
    elif data_type == 'awards':
        for award_data in data:
            award_id = award_data.get('id')
            if award_id:
                existing = DatabaseManager.get_by_id(BadgeAward, award_id)
                if existing:
                    DatabaseManager.update(BadgeAward, award_id, award_data)
                else:
                    DatabaseManager.create(BadgeAward, award_data)
    
    elif data_type == 'sprints':
        for sprint_data in data:
            sprint_id = sprint_data.get('id')
            if sprint_id:
                existing = DatabaseManager.get_by_id(Sprint, sprint_id)
                if existing:
                    DatabaseManager.update(Sprint, sprint_id, sprint_data)
                else:
                    DatabaseManager.create(Sprint, sprint_data)

def get_user_by_id(user_id):
    """Get a user by their ID"""
    return DatabaseManager.get_by_id(User, user_id)

def get_badge_by_id(badge_id):
    """Get a badge by its ID"""
    return DatabaseManager.get_by_id(Badge, badge_id)

def get_team_by_id(team_id):
    """Get a team by its ID"""
    return DatabaseManager.get_by_id(Team, team_id)

def get_user_badges(user_id):
    """Get all badges for a specific user"""
    awards = GamificationQueries.get_user_badges(user_id)
    
    result = []
    for award in awards:
        badge = get_badge_by_id(award['badge_id'])
        if badge:
            badge_data = badge.copy()
            badge_data.update({
                'awarded_at': award.get('awarded_at', 'N/A'),
                'awarded_by': award.get('awarded_by', 'System'),
                'award_id': award.get('id', 'N/A')
            })
            result.append(badge_data)
    
    return result

def get_team_members(team_id):
    """Get all members of a specific team"""
    return GamificationQueries.get_team_members(team_id)

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
    active_sprints = GamificationQueries.get_active_sprints()
    if active_sprints:
        return active_sprints[0]
    
    # If no active sprint, get all sprints and find the most recent
    all_sprints = DatabaseManager.get_all(Sprint)
    if all_sprints:
        return sorted(all_sprints, key=lambda x: x.get('end_date', ''), reverse=True)[0]
    
    return None

def calculate_team_stats(team_id):
    """Calculate statistics for a team"""
    team_members = get_team_members(team_id)
    awards = DatabaseManager.get_all(BadgeAward)
    
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
            awarded_at = award.get('awarded_at')
            if awarded_at and isinstance(awarded_at, date) and awarded_at >= thirty_days_ago:
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

def safe_load_badge(badge):
    if isinstance(badge, str):
        try:
            return json.loads(badge)
        except json.JSONDecodeError:
            return None
    return badge
