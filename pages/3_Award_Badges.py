import json
import streamlit as st
import pandas as pd
from datetime import datetime

from crud.db_manager import DatabaseManager
from models.badge import Badge
from models.badge_award import BadgeAward
from auth import is_authenticated, get_current_user, user_has_access
from utils import generate_unique_id, get_user_by_id, get_badge_by_id, get_team_by_id, get_team_members

# Page config
st.set_page_config(
    page_title="Award Badges - IT Team Gamification",
    page_icon="🏆",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'badges' not in st.session_state:
    st.session_state.badges = DatabaseManager.get_all(Badge)
if 'awards' not in st.session_state:
    st.session_state.awards = []
if 'sprints' not in st.session_state:
    st.session_state.sprints = []

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Check user access
user = get_current_user()
if not user_has_access('award_badges'):
    st.warning("You don't have permission to award badges.")
    st.stop()

# Page title
st.title("🎖️ Award Badges")
st.write("Recognize achievements by awarding badges to team members.")

# Get user's team
user_team = get_team_by_id(user['team_id'])

# Define tabs
tab1, tab2 = st.tabs(["Award Badge", "Award History"])

with tab1:
    st.subheader("Award a New Badge")
    
    # Select team member
    team_members = [m for m in get_team_members(user['team_id']) if m['id'] != user['id']]
    team_members_options = [{'label': m['name'], 'value': m['id']} for m in team_members]
    
    selected_member_id = st.selectbox(
        "Select Team Member",
        options=[m['id'] for m in team_members],
        format_func=lambda x: next((m['label'] for m in team_members_options if m['value'] == x), x)
    )
    
    selected_member = get_user_by_id(selected_member_id)
    
    if selected_member:
        st.write(f"Selected: **{selected_member['name']}** ({selected_member['role']})")
        
        # Select badge
        badges = st.session_state.badges
        eligible_badges = []
        for badge_id, badge in badges.items():
            try:
                roles = json.loads(badge['eligible_roles']) if isinstance(badge['eligible_roles'], str) else badge['eligible_roles']
                if selected_member['role'] in roles:
                    badge_dict = badge.copy()
                    badge_dict['id'] = badge_id
                    eligible_badges.append(badge_dict)
            except (json.JSONDecodeError, AttributeError, KeyError):
                continue
        
        if eligible_badges:
            badge_options = [{'label': f"{b['name']} ({b['category']})", 'value': b['id']} for b in eligible_badges]
            
            selected_badge_id = st.selectbox(
                "Select Badge to Award",
                options=[b['id'] for b in eligible_badges],
                format_func=lambda x: next((b['label'] for b in badge_options if b['value'] == x), x)
            )
            
            selected_badge = get_badge_by_id(selected_badge_id)
            
            if selected_badge:
                with st.expander("Badge Details", expanded=True):
                    st.write(f"**Name:** {selected_badge['name']}")
                    st.write(f"**Category:** {selected_badge['category']}")
                    st.write(f"**Description:** {selected_badge['description']}")
                    st.write(f"**How to Achieve:** {selected_badge.get('how_to_achieve', 'Not specified')}")
                
                # Check if already awarded
                filtered_awards = DatabaseManager.filter_by(
                    BadgeAward,
                    user_id=selected_member_id,
                    badge_id=selected_badge_id
                )
                if filtered_awards:
                    st.warning(f"Note: {selected_member['name']} already has this badge (awarded on {filtered_awards[0].get('awarded_at', 'unknown date')})")
                    st.stop()
                
                # Reason
                reason = st.text_area("Reason for Awarding", placeholder="Explain why you're awarding this badge...")
                awarded_at = st.date_input("Award Date", datetime.now())
                
                # Sprint selection
                sprints = st.session_state.sprints
                sprint_options = [{'label': f"{s['name']} ({s['start_date']} to {s['end_date']})", 'value': s['id']} for s in sprints]
                current_sprint = next((s for s in sprints if s.get('status') == 'active'), None)
                
                selected_sprint_id = st.selectbox(
                    "Associate with Sprint",
                    options=[None] + [s['id'] for s in sprints],
                    format_func=lambda x: "None" if x is None else next(
                        (s['label'] for s in sprint_options if s['value'] == x), x),
                    index=0 if current_sprint is None else sprint_options.index(
                        next((s for s in sprint_options if s['value'] == current_sprint['id']), {'value': None})
                    ) + 1
                )
                
                # Award button
                if st.button("Award Badge"):
                    if not reason:
                        st.error("Please provide a reason for awarding this badge.")
                    else:
                        award = {
                            'id': generate_unique_id('award_'),
                            'user_id': selected_member_id,
                            'badge_id': selected_badge_id,
                            'awarded_by': user['id'],
                            'awarded_at': awarded_at.strftime("%Y-%m-%d"),
                            'reason': reason,
                            'sprint_id': selected_sprint_id
                        }
                        DatabaseManager.create(BadgeAward, award)
                        st.session_state.awards.append(award)
                        st.success(f"Badge '{selected_badge['name']}' successfully awarded to {selected_member['name']}!")
                        st.rerun()
            else:
                st.error("Failed to retrieve badge details.")
        else:
            st.warning(f"No eligible badges found for role: {selected_member['role']}")
    else:
        st.error("Failed to retrieve team member details.")

with tab2:
    st.subheader("Award History")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        member_filter = st.selectbox(
            "Filter by Team Member",
            options=["All"] + [m['id'] for m in team_members],
            format_func=lambda x: "All" if x == "All" else next(
                (m['name'] for m in team_members if m['id'] == x), x)
        )
    with col2:
        time_filter = st.selectbox(
            "Filter by Time Period",
            options=["All Time", "This Month", "Last Month", "This Quarter"]
        )
    
    # Fetch awards
    awards = st.session_state.awards
    team_member_ids = [m['id'] for m in team_members]
    team_awards = [a for a in awards if a['awarded_by'] in team_member_ids or (a['user_id'] in team_member_ids and user_has_access('view_reports'))]
    
    # Apply filters
    if member_filter != "All":
        team_awards = [a for a in team_awards if a['user_id'] == member_filter]
    
    current_date = datetime.now()
    if time_filter == "This Month":
        start_date = current_date.replace(day=1).strftime("%Y-%m-%d")
        team_awards = [a for a in team_awards if a.get('awarded_at', '') >= start_date]
    elif time_filter == "Last Month":
        last_month = current_date.month - 1 if current_date.month > 1 else 12
        last_month_year = current_date.year if current_date.month > 1 else current_date.year - 1
        start_date = datetime(last_month_year, last_month, 1).strftime("%Y-%m-%d")
        end_date = current_date.replace(day=1).strftime("%Y-%m-%d")
        team_awards = [a for a in team_awards if start_date <= a.get('awarded_at', '') < end_date]
    elif time_filter == "This Quarter":
        quarter_start_month = ((current_date.month - 1) // 3) * 3 + 1
        start_date = datetime(current_date.year, quarter_start_month, 1).strftime("%Y-%m-%d")
        team_awards = [a for a in team_awards if a.get('awarded_at', '') >= start_date]
    
    # Display awards
    if team_awards:
        award_data = []
        for award in team_awards:
            badge = get_badge_by_id(award['badge_id'])
            recipient = get_user_by_id(award['user_id'])
            awarder = get_user_by_id(award['awarded_by'])
            
            if badge and recipient and awarder:
                award_data.append({
                    'Date': award.get('awarded_at', 'N/A'),
                    'Recipient': recipient['name'],
                    'Badge': badge['name'],
                    'Category': badge['category'],
                    'Awarded By': awarder['name'],
                    'ID': award['id']
                })
        
        award_df = pd.DataFrame(award_data)
        
        if not award_df.empty:
            award_df['Date'] = pd.to_datetime(award_df['Date'], errors='coerce')
            award_df = award_df.sort_values('Date', ascending=False)
            st.dataframe(
                award_df.drop(columns=['ID']),
                use_container_width=True
            )
            
            st.subheader("Award Details")
            award_id = st.selectbox(
                "Select an award to view details",
                options=[a['id'] for a in team_awards],
                format_func=lambda x: next((
                    f"{a.get('awarded_at', 'N/A')} - {get_badge_by_id(a['badge_id'])['name']} to {get_user_by_id(a['user_id'])['name']}"
                    for a in team_awards if a['id'] == x
                ), x)
            )
            
            if award_id:
                selected_award = next((a for a in team_awards if a['id'] == award_id), None)
                if selected_award:
                    badge = get_badge_by_id(selected_award['badge_id'])
                    recipient = get_user_by_id(selected_award['user_id'])
                    awarder = get_user_by_id(selected_award['awarded_by'])
                    
                    with st.expander("Award Details", expanded=True):
                        st.write(f"**Date:** {selected_award.get('awarded_at', 'N/A')}")
                        st.write(f"**Badge:** {badge['name']} ({badge['category']})")
                        st.write(f"**Awarded to:** {recipient['name']} ({recipient['role']})")
                        st.write(f"**Awarded by:** {awarder['name']}")
                        st.write(f"**Reason:** {selected_award.get('reason', 'No reason provided')}")
                        if selected_award.get('sprint_id'):
                            sprint = next((s for s in st.session_state.sprints if s['id'] == selected_award['sprint_id']), None)
                            if sprint:
                                st.write(f"**Sprint:** {sprint['name']}")
    else:
        st.info("No awards found matching the selected criteria.")
