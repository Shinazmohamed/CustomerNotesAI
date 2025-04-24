import json
import streamlit as st
from database import Badge, DatabaseManager
# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Badge Management - IT Team Gamification",
    page_icon="🏆",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'badges' not in st.session_state:
    st.session_state.badges = {}
if 'badge_to_edit' not in st.session_state:
    st.session_state.badge_to_edit = None

import pandas as pd
from auth import is_authenticated, get_current_user, user_has_access
from utils import generate_unique_id

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

user = get_current_user()

# Page header
st.title("📝 Badge Management")
st.write("Create, edit, and manage badges for your team.")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'badges' not in st.session_state:
    st.session_state.badges = {}
if 'badge_to_edit' not in st.session_state:
    st.session_state.badge_to_edit = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "View Badges"

# Tab layout
tabs = ["View Badges", "Create/Edit Badge"]
current_tab_index = tabs.index(st.session_state.active_tab)
tab_selection = st.radio("Select a tab", tabs, index=current_tab_index, key="tab_selector", horizontal=True)

# Sync session state
if tab_selection != st.session_state.active_tab:
    st.session_state.active_tab = tab_selection
    st.rerun()

# Content rendering
if st.session_state.active_tab == "View Badges":
    st.subheader("Available Badges")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filter by category
        categories = ['All']
        for badge in st.session_state.badges.values():
            if badge['category'] not in categories:
                categories.append(badge['category'])
        
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        # Filter by role
        roles = ['All', 'Dev', 'QA', 'RMO', 'TL']
        selected_role = st.selectbox("Filter by Role", roles)
    
    with col3:
        # Filter by badge type
        badge_types = ['All', 'Work', 'Objective']
        selected_type = st.selectbox("Filter by Type", badge_types)
    
    # Get badges and apply filters
    badges = st.session_state.badges
    
    # Convert badge dictionary to list for filtering
    badge_list = list(badges.values())
    
    # Apply category filter
    if selected_category != 'All':
        badge_list = [b for b in badge_list if b['category'] == selected_category]
    
    # Apply role filter
    if selected_role != 'All':
        badge_list = [b for b in badge_list if selected_role in b.get('valid_roles', [])]
    
    # Apply type filter
    if selected_type != 'All':
        type_key = selected_type.lower()
        badge_list = [b for b in badge_list if b.get('criteria', '').lower() == type_key]
    
    # Display badges
    if badge_list:
        # Convert to DataFrame for display
        badge_df = pd.DataFrame([
            {
                'Name': badge['name'],
                'Category': badge['category'],
                'Description': badge['description'],
                'Eligible Roles': ', '.join(json.loads(badge.get('valid_roles', '[]')) if isinstance(badge.get('valid_roles'), str) else badge.get('valid_roles', [])),
                'Expected Time (days)': badge.get('validity_days', 'N/A'),
                'Type': badge.get('criteria', 'N/A').capitalize(),
                'ID': badge['id']
            }
            for badge in badge_list
        ])
        
        # Display as interactive table
        selected_rows = st.dataframe(
            badge_df.drop(columns=['ID']), 
            use_container_width=True,
            column_config={
                'Description': st.column_config.TextColumn(width="large")
            }
        )
        
        # Badge details expander
        st.subheader("Badge Details")
        badge_id = st.selectbox("Select a badge to view details", 
                              options=[b['id'] for b in badge_list],
                              format_func=lambda x: next((b['name'] for b in badge_list if b['id'] == x), x))
        
        if badge_id:
            selected_badge = next((b for b in badge_list if b['id'] == badge_id), None)
            if selected_badge:
                with st.expander(f"Details for {selected_badge['name']}", expanded=True):
                    st.write(f"**Name:** {selected_badge['name']}")
                    st.write(f"**Category:** {selected_badge['category']}")
                    st.write(f"**Description:** {selected_badge['description']}")
                    st.write(f"**How to Achieve:** {selected_badge.get('how_to_achieve', 'Not specified')}")
                    roles = selected_badge.get('valid_roles', [])
                    if isinstance(roles, str):
                        try:
                            roles = json.loads(roles)
                        except json.JSONDecodeError:
                            roles = []
                    st.write(f"**Eligible Roles:** {', '.join(roles)}")
                    st.write(f"**Expected Time:** {selected_badge.get('validity_days', 'N/A')} days")
                    st.write(f"**Expiry Date:** {selected_badge.get('expired_at', 'Permanent')}")
                    st.write(f"**Type:** {selected_badge.get('criteria', 'N/A').capitalize()}")
                    
                    # Edit button
                    if user_has_access('create_badges'):
                        if st.button("Edit this Badge", key="edit_badge_button"):
                            st.session_state.badge_to_edit = selected_badge
                            st.session_state.active_tab = "Create/Edit Badge"
                            st.rerun()
    else:
        st.info("No badges found matching the selected filters.")

elif st.session_state.active_tab == "Create/Edit Badge":
    # Check if user has permission to create/edit badges
    if not user_has_access('create_badges'):
        st.warning("You don't have permission to create or edit badges.")
        st.stop()
    
    st.subheader("Create/Edit Badge")
    
    # Initialize edited badge
    editing = False
    if 'badge_to_edit' in st.session_state and st.session_state.badge_to_edit:
        editing = True
        badge = st.session_state.badge_to_edit
        st.info(f"Editing badge: {badge['name']}")
    else:
        badge = {
            'id': generate_unique_id('badge_'),
            'name': '',
            'description': '',
            'category': '',
            'how_to_achieve': '',
            'valid_roles': [],
            'validity_days': 30,
            'expired_at': 'Permanent',
            'criteria': 'work'
        }
    
    # Badge form
    with st.form("badge_form"):
        name = st.text_input("Badge Name", value=badge['name'])
        description = st.text_area("Description", value=badge['description'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "Category", 
                ['Technical', 'Leadership', 'Teamwork', 'Innovation', 'Process', 'Other'],
                index=['Technical', 'Leadership', 'Teamwork', 'Innovation', 'Process', 'Other'].index(badge['category']) if badge['category'] in ['Technical', 'Leadership', 'Teamwork', 'Innovation', 'Process', 'Other'] else 0
            )
            
            valid_roles = st.multiselect(
                "Eligible Roles",
                ['Dev', 'QA', 'RMO', 'TL'],
                default=badge.get('valid_roles', [])
            )
        
        with col2:
            how_to_achieve = st.text_area("How to Achieve", value=badge.get('how_to_achieve', ''))
            
            validity_time = st.number_input(
                "Validity Time (days)",
                min_value=1,
                max_value=365,
                value=badge.get('validity_days', 30)
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            expired_at = st.selectbox(
                "Expiry Date",
                ['Permanent', '1 Month', '3 Months', '6 Months', '1 Year'],
                index=['Permanent', '1 Month', '3 Months', '6 Months', '1 Year'].index(badge.get('expired_at', 'Permanent')) if badge.get('expired_at', 'Permanent') in ['Permanent', '1 Month', '3 Months', '6 Months', '1 Year'] else 0
            )
        
        with col4:
            criteria = st.selectbox(
                "Badge Type",
                ['Work', 'Objective'],
                index=['Work', 'Objective'].index(badge.get('criteria', 'work').capitalize()) if badge.get('criteria', 'work').capitalize() in ['Work', 'Objective'] else 0
            )
        
        # Submit button
        if editing:
            submit_label = "Update Badge"
        else:
            submit_label = "Create Badge"
        
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            # Validate form
            if not name:
                st.error("Badge name is required")
            elif not description:
                st.error("Description is required")
            elif not category:
                st.error("Category is required")
            elif not valid_roles:
                st.error("At least one eligible role is required")
            else:
                # Prepare badge data
                badge_data = {
                    'id': badge['id'],
                    'name': name,
                    'description': description,
                    'category': category,
                    'how_to_achieve': how_to_achieve,
                    'valid_roles': json.dumps(valid_roles),
                    'validity_days': validity_time,
                    'expired_at': expired_at,
                    'criteria': criteria.lower()
                }
                
                # Save to session state
                badges = st.session_state.badges
                badges[badge_data['id']] = badge_data
                st.session_state.badges = badges
                
                # Reset form if creating new badge
                if not editing:
                    DatabaseManager.create(Badge, badge_data)
                    st.success("Badge created successfully!")
                else:
                    DatabaseManager.update(Badge, badge['id'], badge_data)
                    st.success("Badge updated successfully!")
                    # Clear edit state
                    st.session_state.badge_to_edit = None
                
                # Rerun app to refresh
                st.rerun()
    
    # Cancel edit button
    if editing:
        if st.button("Cancel Edit"):
            st.session_state.badge_to_edit = None
            st.rerun()
