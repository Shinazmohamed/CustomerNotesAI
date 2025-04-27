import streamlit as st
import pandas as pd
import plotly.express as px
from auth import is_authenticated, get_current_user, user_has_access
from utils import get_team_by_id, generate_unique_id, get_team_members, calculate_team_stats
from models.team import Team
from models.user import User
from crud.db_manager import DatabaseManager
# Page config
st.set_page_config(
    page_title="Teams - IT Team Gamification",
    page_icon="🏆",
    layout="wide"
)

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Get current user
user = get_current_user()

# Page header
st.title("👥 Teams")
st.write("View and manage team structures and performance.")

# Define tabs
tab1, tab2 = st.tabs(["Team Overview", "Team Management"])

with tab1:
    st.subheader("Team Performance Overview")
    
    # Get teams
    teams = st.session_state.teams
    
    # Get user's team
    user_team = get_team_by_id(user['team_id'])
    
    # Allow selecting a team
    team_options = [{'label': t['name'], 'value': t['id']} for t in teams]
    
    selected_team_id = st.selectbox(
        "Select Team",
        options=[t['id'] for t in teams],
        index=teams.index(user_team) if user_team in teams else 0,
        format_func=lambda x: next((t['label'] for t in team_options if t['value'] == x), x)
    )
    
    selected_team = get_team_by_id(selected_team_id)
    
    if selected_team:
        st.write(f"### {selected_team['name']}")
        
        # Get team members
        team_members = get_team_members(selected_team['id'])
        
        # Calculate team stats
        team_stats = calculate_team_stats(selected_team['id'])
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Members", team_stats['member_count'])
        
        with col2:
            st.metric("Total Badges", team_stats['total_badges'])
        
        with col3:
            st.metric("Avg. Badges/Member", team_stats['avg_badges'])
        
        with col4:
            st.metric("Top Performer", team_stats['top_performer'])
        
        # Team members
        st.subheader("Team Members")
        
        if team_members:
            # Create member table
            member_data = []
            
            for member in team_members:
                # Count badges
                member_badges = [a for a in st.session_state.awards if a['user_id'] == member['id']]
                
                # Count different badge types
                work_badges = sum(1 for b in member_badges if b.get('badge_type') == 'work')
                obj_badges = sum(1 for b in member_badges if b.get('badge_type') == 'objective')
                
                member_data.append({
                    'Name': member['name'],
                    'Role': member['role'],
                    'Total Badges': len(member_badges),
                    'Work Badges': work_badges,
                    'Objective Badges': obj_badges,
                    'ID': member['id']
                })
            
            # Create DataFrame
            members_df = pd.DataFrame(member_data)
            
            # Sort by total badges (descending)
            members_df = members_df.sort_values('Total Badges', ascending=False)
            
            # Display table
            st.dataframe(
                members_df.drop(columns=['ID']),
                use_container_width=True
            )
            
            # Visualization: Badge distribution
            st.subheader("Badge Distribution Across Team")
            
            # Create bar chart
            fig = px.bar(
                members_df,
                x='Name',
                y=['Work Badges', 'Objective Badges'],
                title=f"Badge Distribution for {selected_team['name']}",
                labels={'value': 'Number of Badges', 'variable': 'Badge Type'},
                color_discrete_map={
                    'Work Badges': '#4169E1',
                    'Objective Badges': '#32CD32'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Role distribution
            st.subheader("Team Role Composition")
            
            # Count members by role
            role_counts = members_df['Role'].value_counts().reset_index()
            role_counts.columns = ['Role', 'Count']
            
            # Create pie chart
            fig = px.pie(
                role_counts,
                values='Count',
                names='Role',
                title=f"Role Distribution for {selected_team['name']}",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No members found for {selected_team['name']}.")
    else:
        st.error("Failed to retrieve team details.")

with tab2:
    # Check if user has permission to manage teams
    if not user_has_access('edit_teams'):
        st.info("You don't have permission to manage team structure. This view is read-only.")
        read_only = True
    else:
        read_only = False
    
    st.subheader("Team Structure Management")
    
    # Team selection
    teams = st.session_state.teams
    
    team_options = [{'label': t['name'], 'value': t['id']} for t in teams]
    
    selected_team_id = st.selectbox(
        "Select Team to View/Edit",
        options=[t['id'] for t in teams],
        format_func=lambda x: next((t['label'] for t in team_options if t['value'] == x), x),
        key="mgmt_team_select"
    )
    
    selected_team = get_team_by_id(selected_team_id)
    
    if selected_team:
        # Get team members
        team_members = get_team_members(selected_team['id'])
        
        # Team details
        with st.expander("Team Details", expanded=True):
            if read_only:
                st.write(f"**Team Name:** {selected_team['name']}")
                st.write(f"**Description:** {selected_team.get('description', 'No description available')}")
                st.write(f"**Department:** {selected_team.get('department', 'N/A')}")
                st.write(f"**Team Lead:** {next((m['name'] for m in team_members if m['role'] == 'TL'), 'Not assigned')}")
            else:
                # Editable team details form
                with st.form("edit_team_form"):
                    team_name = st.text_input("Team Name", value=selected_team['name'])
                    team_desc = st.text_area("Description", value=selected_team.get('description', ''))
                    team_dept = st.text_input("Department", value=selected_team.get('department', ''))
                    
                    # Team lead selection
                    lead_options = [m for m in team_members if m['role'] == 'TL' or m['role'] == 'Manager']
                    
                    if lead_options:
                        current_lead = next((l for l in lead_options 
                                           if l.get('is_lead', False)), lead_options[0])
                        
                        selected_lead = st.selectbox(
                            "Team Lead",
                            options=[l['id'] for l in lead_options],
                            index=lead_options.index(current_lead) if current_lead in lead_options else 0,
                            format_func=lambda x: next((l['name'] for l in lead_options if l['id'] == x), x)
                        )
                    else:
                        st.warning("No team leads or managers available in this team.")
                        selected_lead = None
                    
                    submitted = st.form_submit_button("Update Team Details")
                    
                    if submitted:
                        # Update team details
                        teams = st.session_state.teams
                        team_idx = next((i for i, t in enumerate(teams) if t['id'] == selected_team['id']), -1)

                        if team_idx >= 0:
                            teams[team_idx]['name'] = team_name
                            teams[team_idx]['description'] = team_desc
                            teams[team_idx]['department'] = team_dept
                            
                            # Update team lead if changed
                            if selected_lead:
                                # Reset lead status for all members
                                users = st.session_state.users
                                for i, user in enumerate(users):
                                    if user['team_id'] == selected_team['id'] and user.get('is_lead', False):
                                        users[i]['is_lead'] = False
                                
                                # Set new lead
                                lead_idx = next((i for i, u in enumerate(users) 
                                               if u['id'] == selected_lead), -1)
                                if lead_idx >= 0:
                                    users[lead_idx]['is_lead'] = True
                                    st.session_state.users = users

                            DatabaseManager.update(Team, teams[team_idx]['id'], teams[team_idx])
                            st.session_state.teams = teams
                            st.success("Team details updated successfully!")
                            st.rerun()
        
        # Team members
        st.subheader("Team Members")
        
        if team_members:
            # Create member table with editable role field
            member_data = []
            
            for member in team_members:
                # Count badges
                member_badges = [a for a in st.session_state.awards if a['user_id'] == member['id']]
                
                member_data.append({
                    'Name': member['name'],
                    'Role': member['role'],
                    'Badges': len(member_badges),
                    'Email': member.get('email', 'N/A'),
                    'ID': member['id']
                })
            
            # Create DataFrame
            members_df = pd.DataFrame(member_data)
            
            # Display table
            st.dataframe(
                members_df.drop(columns=['ID']),
                use_container_width=True
            )
            
            # Member editing
            if not read_only:
                st.subheader("Edit Member")
                
                # Select member to edit
                edit_member_id = st.selectbox(
                    "Select Member to Edit",
                    options=[m['id'] for m in team_members],
                    format_func=lambda x: next((m['name'] for m in team_members if m['id'] == x), x)
                )
                
                edit_member = next((m for m in team_members if m['id'] == edit_member_id), None)
                
                if edit_member:
                    with st.form("edit_member_form"):
                        member_name = st.text_input("Name", value=edit_member['name'])
                        member_email = st.text_input("Email", value=edit_member.get('email', ''))
                        
                        selected_team_id = st.selectbox(
                            "Select Team",
                            options=[t['id'] for t in teams],
                            index=teams.index(user_team) if user_team in teams else 0,
                            format_func=lambda x: next((t['label'] for t in team_options if t['value'] == x), x)
                        )   
                        # Role selection
                        roles = ['Dev', 'QA', 'RMO', 'TL', 'Manager']
                        member_role = st.selectbox(
                            "Role",
                            options=roles,
                            index=roles.index(edit_member['role']) if edit_member['role'] in roles else 0
                        )
                        
                        submitted = st.form_submit_button("Update Member")
                        
                        if submitted:
                            # Update member
                            users = st.session_state.users
                            user_idx = next((i for i, u in enumerate(users) 
                                           if u['id'] == edit_member['id']), -1)
                            
                            if user_idx >= 0:
                                users[user_idx]['name'] = member_name
                                users[user_idx]['email'] = member_email
                                users[user_idx]['role'] = member_role
                                users[user_idx]['team_id'] = selected_team_id
                                
                                DatabaseManager.update(User, users[user_idx]['id'], users[user_idx])
                                st.session_state.users = users
                                st.success(f"Member {member_name} updated successfully!")
                                st.rerun()
                
                # Add new member
                st.subheader("Add New Member")
                
                with st.form("add_member_form"):
                    new_name = st.text_input("Name")
                    new_email = st.text_input("Email")
                    new_username = st.text_input("Username")
                    new_password = st.text_input("Password", type="password")
                    
                    selected_team_id = st.selectbox(
                        "Select Team",
                        options=[t['id'] for t in teams],
                        index=teams.index(user_team) if user_team in teams else 0,
                        format_func=lambda x: next((t['label'] for t in team_options if t['value'] == x), x)
                    )

                    # Role selection
                    new_role = st.selectbox(
                        "Role",
                        options=['Dev', 'QA', 'RMO', 'TL', 'Manager']
                    )
                    
                    submitted = st.form_submit_button("Add Member")
                    
                    if submitted:
                        if not new_name or not new_username or not new_password:
                            st.error("Name, username, and password are required.")
                        else:
                            # Check if username is unique
                            users = st.session_state.users
                            if any(u['username'] == new_username for u in users):
                                st.error("Username already exists. Please choose a different one.")
                            else:
                                # Create new user
                                new_user = {
                                    'id': generate_unique_id('user_'),
                                    'name': new_name,
                                    'username': new_username,
                                    'password': new_password,  # In a real app, hash this password
                                    'email': new_email,
                                    'role': new_role,
                                    'team_id': selected_team_id,
                                    'is_lead': False
                                }
                                
                                users.append(new_user)
                                DatabaseManager.create(User, new_user)
                                st.session_state.users = users
                                st.success(f"Member {new_name} added successfully!")
                                st.rerun()
        else:
            st.info(f"No members found for {selected_team['name']}.")
        
        # Create new team (for managers only)
        if user['role'] == 'Manager' and not read_only:
            st.subheader("Create New Team")
            
            with st.form("create_team_form"):
                new_team_name = st.text_input("Team Name")
                new_team_desc = st.text_area("Description")
                new_team_dept = st.text_input("Department")
                
                submitted = st.form_submit_button("Create Team")
                
                if submitted:
                    if not new_team_name:
                        st.error("Team name is required.")
                    else:
                        # Create new team
                        new_team = {
                            'id': generate_unique_id('team_'),
                            'name': new_team_name,
                            'description': new_team_desc,
                            'department': new_team_dept
                        }
                        
                        teams.append(new_team)
                        DatabaseManager.create(Team, new_team)
                        st.session_state.teams = teams
                        st.success(f"Team {new_team_name} created successfully!")
                        st.rerun()
    else:
        st.error("Failed to retrieve team details.")
