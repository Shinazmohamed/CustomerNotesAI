import json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from auth import is_authenticated, get_current_user, user_has_access
from database import DatabaseManager, Sprint
from utils import generate_unique_id, get_team_by_id, get_current_sprint

# Page config
st.set_page_config(
    page_title="Sprint Planning - IT Team Gamification",
    page_icon="🏆",
    layout="wide"
)

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Get current user
user = get_current_user()

# Check permissions
can_manage_sprints = user_has_access('create_sprints')

# Page header
st.title("🏃‍♂️ Sprint Integration")
st.write("Plan and track achievements through sprints.")

# Get user's team
user_team = get_team_by_id(user['team_id'])

# Define tabs
tab1, tab2, tab3 = st.tabs(["Current Sprint", "Sprint History", "Sprint Management"])

with tab1:
    st.subheader("Current Sprint Overview")
    
    # Get current active sprint
    current_sprint = get_current_sprint()
    
    if current_sprint:
        # Display sprint details
        st.write(f"### {current_sprint['name']}")
        
        # Calculate days remaining
        try:
            end_date = current_sprint['end_date'] if isinstance(current_sprint['end_date'], date) else datetime.strptime(current_sprint['end_date'], "%Y-%m-%d").date()
            current_date = datetime.now().date()
            days_remaining = (end_date - current_date).days
            
            if days_remaining < 0:
                status = "Completed"
                days_str = "Sprint has ended"
            else:
                status = "Active"
                days_str = f"{days_remaining} days remaining"
        except:
            status = "Unknown"
            days_str = "Unable to calculate days remaining"
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", status)
        
        with col2:
            st.metric("Timeline", f"{current_sprint.get('start_date', 'N/A')} to {current_sprint.get('end_date', 'N/A')}")
        
        with col3:
            st.metric("Remaining", days_str)
        
        with col4:
            # Count badges awarded in this sprint
            sprint_badges = [a for a in st.session_state.awards 
                            if a.get('sprint_id') == current_sprint['id']]
            st.metric("Badges Awarded", len(sprint_badges))
        
        # Sprint description
        st.subheader("Description")
        st.write(current_sprint.get('description', 'No description available.'))
        
        # Sprint goals
        st.subheader("Sprint Goals")
        goals = current_sprint.get('goals', [])
        
        if goals:
            for i, goal in enumerate(goals):
                st.write(f"{i+1}. {goal}")
        else:
            st.write("No specific goals defined for this sprint.")
        
        # Badge tracking
        st.subheader("Badge Awards in Current Sprint")
        
        if sprint_badges:
            # Create badge award data
            badge_data = []
            
            for award in sprint_badges:
                badge = st.session_state.badges.get(award['badge_id'])
                awardee = next((u for u in st.session_state.users if u['id'] == award['user_id']), None)
                awarder = next((u for u in st.session_state.users if u['id'] == award.get('awarded_by')), None)
                
                if badge and awardee:
                    badge_data.append({
                        'Date': award.get('awarded_at', 'N/A'),
                        'Badge': badge['name'],
                        'Category': badge['category'],
                        'Recipient': awardee['name'],
                        'Awarded By': awarder['name'] if awarder else 'System',
                        'Type': award.get('badge_type', 'work').capitalize()
                    })
            
            # Create DataFrame
            badge_df = pd.DataFrame(badge_data)
            
            # Sort by date
            badge_df = badge_df.sort_values('Date', ascending=False)
            
            # Display table
            st.dataframe(badge_df, use_container_width=True)
            
            # Create charts
            st.subheader("Sprint Badge Analytics")
            
            # Badge distribution by category
            category_counts = badge_df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            
            fig1 = px.pie(
                category_counts,
                values='Count',
                names='Category',
                title='Badge Distribution by Category',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            
            # Badge distribution by recipient
            recipient_counts = badge_df['Recipient'].value_counts().reset_index()
            recipient_counts.columns = ['Recipient', 'Count']
            
            fig2 = px.bar(
                recipient_counts,
                x='Recipient',
                y='Count',
                title='Badge Recipients',
                color='Count',
                color_continuous_scale='Blues'
            )
            
            # Display charts side by side
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.plotly_chart(fig2, use_container_width=True)
            
            # Work vs. Objective split
            work_badges = sum(1 for _, row in badge_df.iterrows() if row['Type'] == 'Work')
            obj_badges = sum(1 for _, row in badge_df.iterrows() if row['Type'] == 'Objective')
            
            split_data = pd.DataFrame({
                'Type': ['Regular Work (80%)', 'Objectives (20%)'],
                'Count': [work_badges, obj_badges]
            })
            
            fig3 = px.bar(
                split_data,
                x='Type',
                y='Count',
                title='Work vs. Objective Badge Distribution',
                color='Type',
                color_discrete_sequence=['#4169E1', '#32CD32']
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No badges have been awarded in this sprint yet.")
    else:
        st.warning("No active sprint found. Use the Sprint Management tab to create a new sprint.")

with tab2:
    st.subheader("Sprint History")
    
    # Get all sprints
    sprints = st.session_state.sprints
    
    # Filter completed sprints
    completed_sprints = [s for s in sprints if s.get('status') == 'completed']
    
    if completed_sprints:
        # Sort by end date (newest first)
        completed_sprints = sorted(
            completed_sprints,
            key=lambda x: x.get('end_date', '1900-01-01'),
            reverse=True
        )
        
        # Create sprint data
        sprint_data = []
        
        for sprint in completed_sprints:
            # Count badge awards in this sprint
            sprint_badges = [a for a in st.session_state.awards if a.get('sprint_id') == sprint['id']]
            
            sprint_data.append({
                'Sprint': sprint['name'],
                'Start Date': sprint.get('start_date', 'N/A'),
                'End Date': sprint.get('end_date', 'N/A'),
                'Badges Awarded': len(sprint_badges),
                'ID': sprint['id']
            })
        
        # Create DataFrame
        sprint_df = pd.DataFrame(sprint_data)
        
        # Display table
        st.dataframe(sprint_df.drop(columns=['ID']), use_container_width=True)
        
        # Sprint details
        st.subheader("Sprint Details")
        
        selected_sprint_id = st.selectbox(
            "Select Sprint to View Details",
            options=[s['id'] for s in completed_sprints],
            format_func=lambda x: next((f"{s['name']} ({s.get('start_date', 'N/A')} to {s.get('end_date', 'N/A')})" 
                                      for s in completed_sprints if s['id'] == x), x)
        )
        
        if selected_sprint_id:
            # Get sprint details
            selected_sprint = next((s for s in completed_sprints if s['id'] == selected_sprint_id), None)
            
            if selected_sprint:
                with st.expander(f"Details for {selected_sprint['name']}", expanded=True):
                    st.write(f"**Start Date:** {selected_sprint.get('start_date', 'N/A')}")
                    st.write(f"**End Date:** {selected_sprint.get('end_date', 'N/A')}")
                    st.write(f"**Description:** {selected_sprint.get('description', 'No description available.')}")
                    
                    # Sprint goals
                    st.write("**Goals:**")
                    goals = selected_sprint.get('goals', [])
                    
                    if goals:
                        for i, goal in enumerate(goals):
                            st.write(f"{i+1}. {goal}")
                    else:
                        st.write("No specific goals defined for this sprint.")
                
                # Sprint badge awards
                st.subheader("Badge Awards")
                
                # Get awards for this sprint
                sprint_badges = [a for a in st.session_state.awards if a.get('sprint_id') == selected_sprint_id]
                
                if sprint_badges:
                    # Create badge award data
                    badge_data = []
                    
                    for award in sprint_badges:
                        badge = st.session_state.badges.get(award['badge_id'])
                        awardee = next((u for u in st.session_state.users if u['id'] == award['user_id']), None)
                        awarder = next((u for u in st.session_state.users if u['id'] == award.get('awarded_by')), None)
                        
                        if badge and awardee:
                            badge_data.append({
                                'Date': award.get('awarded_at', 'N/A'),
                                'Badge': badge['name'],
                                'Category': badge['category'],
                                'Recipient': awardee['name'],
                                'Awarded By': awarder['name'] if awarder else 'System',
                                'Type': award.get('badge_type', 'work').capitalize()
                            })
                    
                    # Create DataFrame
                    badge_df = pd.DataFrame(badge_data)
                    
                    # Sort by date
                    badge_df = badge_df.sort_values('Date', ascending=False)
                    
                    # Display table
                    st.dataframe(badge_df, use_container_width=True)
                    
                    # Create chart: badge distribution by recipient
                    recipient_counts = badge_df['Recipient'].value_counts().reset_index()
                    recipient_counts.columns = ['Recipient', 'Count']
                    
                    fig = px.bar(
                        recipient_counts,
                        x='Recipient',
                        y='Count',
                        title=f'Badge Recipients - {selected_sprint["name"]}',
                        color='Count',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No badges were awarded in this sprint.")
    else:
        st.info("No completed sprints found.")

with tab3:
    st.subheader("Sprint Management")
    
    # Check if user has permission to manage sprints
    if not can_manage_sprints:
        st.warning("You don't have permission to manage sprints.")
        st.stop()
    
    # Current sprints overview
    st.write("### Active and Upcoming Sprints")
    
    # Get all sprints
    sprints = st.session_state.sprints
    
    # Filter active and upcoming sprints
    active_sprints = [s for s in sprints if s.get('status') == 'active']
    upcoming_sprints = [s for s in sprints if s.get('status') == 'upcoming']
    
    # Display active sprints
    if active_sprints:
        st.write("#### Active Sprints")
        
        for sprint in active_sprints:
            with st.expander(f"{sprint['name']} - Active", expanded=True):
                st.write(f"**Timeline:** {sprint.get('start_date', 'N/A')} to {sprint.get('end_date', 'N/A')}")
                st.write(f"**Description:** {sprint.get('description', 'No description available.')}")
                
                # Complete sprint button
                if st.button(f"Mark Sprint {sprint['name']} as Completed", key=f"complete_{sprint['id']}"):
                    # Update sprint status
                    for i, s in enumerate(sprints):
                        if s['id'] == sprint['id']:
                            sprints[i]['status'] = 'completed'
                            break
                    
                    st.session_state.sprints = sprints
                    st.success(f"Sprint {sprint['name']} marked as completed.")
                    st.rerun()
    else:
        st.info("No active sprints.")
    
    # Display upcoming sprints
    if upcoming_sprints:
        st.write("#### Upcoming Sprints")
        
        for sprint in upcoming_sprints:
            with st.expander(f"{sprint['name']} - Upcoming", expanded=False):
                st.write(f"**Timeline:** {sprint.get('start_date', 'N/A')} to {sprint.get('end_date', 'N/A')}")
                st.write(f"**Description:** {sprint.get('description', 'No description available.')}")
                
                # Start sprint button
                if st.button(f"Start Sprint {sprint['name']}", key=f"start_{sprint['id']}"):
                    # Update sprint status
                    for i, s in enumerate(sprints):
                        if s['id'] == sprint['id']:
                            sprints[i]['status'] = 'active'
                            break
                    
                    st.session_state.sprints = sprints
                    st.success(f"Sprint {sprint['name']} started.")
                    st.rerun()
    else:
        st.info("No upcoming sprints.")
    
    # Create new sprint
    st.write("### Create New Sprint")
    
    with st.form("create_sprint_form"):
        sprint_name = st.text_input("Sprint Name", placeholder="e.g., Sprint 23")
        sprint_desc = st.text_area("Description", placeholder="Sprint goals and focus areas...")
        
        # Date range
        col1, col2 = st.columns(2)
        
        with col1:
            # Default to next Monday for start date
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_monday = today + timedelta(days=days_until_monday)
            
            start_date = st.date_input("Start Date", value=next_monday)
        
        with col2:
            # Default to 2 weeks after start
            default_end = start_date + timedelta(days=13)
            end_date = st.date_input("End Date", value=default_end)
        
        # Sprint goals
        st.write("Sprint Goals (Add up to 5)")
        
        goals = []
        for i in range(5):
            goal = st.text_input(f"Goal {i+1}", key=f"goal_{i}")
            if goal:
                goals.append(goal)
        
        # Team association
        team_id = user['team_id']  # Default to user's team
        
        # If user is a manager, allow selecting any team
        if user['role'] == 'Manager':
            teams = st.session_state.teams
            team_options = [{'label': t['name'], 'value': t['id']} for t in teams]
            
            team_id = st.selectbox(
                "Team",
                options=[t['id'] for t in teams],
                index=next((i for i, t in enumerate(teams) if t['id'] == team_id), 0),
                format_func=lambda x: next((t['label'] for t in team_options if t['value'] == x), x)
            )
        
        # Submit button
        submitted = st.form_submit_button("Create Sprint")
        
        if submitted:
            # Validate form
            if not sprint_name:
                st.error("Sprint name is required.")
            elif start_date >= end_date:
                st.error("End date must be after start date.")
            else:
                # Create sprint
                new_sprint = {
                    'id': generate_unique_id('sprint_'),
                    'name': sprint_name,
                    'description': sprint_desc,
                    'start_date': start_date.strftime("%Y-%m-%d"),
                    'end_date': end_date.strftime("%Y-%m-%d"),
                    'team_id': team_id,
                    'goals': json.dumps(goals),
                    'status': 'upcoming'  # Default to upcoming
                }
                
                # Add to sprints
                DatabaseManager.create(Sprint, new_sprint)
                sprints = st.session_state.sprints
                sprints.append(new_sprint)
                st.session_state.sprints = sprints
                
                st.success(f"Sprint '{sprint_name}' created successfully!")
                st.rerun()
