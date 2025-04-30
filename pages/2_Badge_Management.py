import json
import streamlit as st
import pandas as pd
from crud.db_manager import DatabaseManager
from models.badge import Badge
from auth import is_authenticated, get_current_user, user_has_access
from utils import generate_unique_id

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Badge Management - IT Team Gamification",
    page_icon="🏆",
    layout="wide"
)

# ---- SESSION STATE INIT ----
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

# ---- AUTHENTICATION ----
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

user = get_current_user()

# ---- PAGE HEADER ----
st.title("📝 Badge Management")
st.write("Create, edit, and manage badges for your team.")

# ---- TAB NAVIGATION ----
tabs = ["View Badges", "Create/Edit Badge"]
current_tab_index = tabs.index(st.session_state.active_tab)
tab_selection = st.radio("Select a tab", tabs, index=current_tab_index, key="tab_selector", horizontal=True)

if tab_selection != st.session_state.active_tab:
    st.session_state.active_tab = tab_selection
    st.rerun()

# ---- VIEW BADGES TAB ----
if st.session_state.active_tab == "View Badges":
    if not user_has_access('view_badges'):
        st.warning("You don't have permission to create or edit badges.")
        st.stop()

    st.subheader("Available Badges")

    # Filters
    col1, col2, col3 = st.columns(3)
    badges = st.session_state.badges
    badge_list = list(badges.values()) if isinstance(badges, dict) else badges

    with col1:
        categories = list({badge['category'] for badge in badge_list})
        categories.sort()
        categories.insert(0, "All")
        selected_category = st.selectbox("Filter by Category", categories)

    with col2:
        roles = ['All', 'Dev', 'QA', 'RMO', 'TL']
        selected_role = st.selectbox("Filter by Role", roles)

    with col3:
        badge_types = ['All', 'Work', 'Objective']
        selected_type = st.selectbox("Filter by Type", badge_types)

    # Apply filters
    if selected_category != 'All':
        badge_list = [b for b in badge_list if b['category'] == selected_category]
    if selected_role != 'All':
        badge_list = [b for b in badge_list if selected_role in (b.get('eligible_roles', []) if isinstance(b.get('eligible_roles', []), list) else json.loads(b.get('eligible_roles', '[]')))]
    if selected_type != 'All':
        badge_list = [b for b in badge_list if b.get('badge_type', '').lower() == selected_type.lower()]

    # Display Badges
    if badge_list:
        badge_df = pd.DataFrame([
            {
                'Name': badge['name'],
                'Category': badge['category'],
                'Description': badge['description'],
                'Eligible Roles': ', '.join(json.loads(badge.get('eligible_roles', '[]')) if isinstance(badge.get('eligible_roles'), str) else badge.get('eligible_roles', [])),
                'Expected Time (days)': badge.get('expected_time_days', 'N/A'),
                'Type': badge.get('badge_type', 'N/A').capitalize(),
                'ID': badge['id']
            }
            for badge in badge_list
        ])
        
        st.dataframe(badge_df.drop(columns=['ID']), use_container_width=True)

        # Badge Details
        st.subheader("Badge Details")
        badge_id = st.selectbox(
            "Select a badge to view details",
            options=[b['id'] for b in badge_list],
            format_func=lambda x: next((b['name'] for b in badge_list if b['id'] == x), x)
        )

        if badge_id:
            selected_badge = next((b for b in badge_list if b['id'] == badge_id), None)
            if selected_badge:
                with st.expander(f"Details for {selected_badge['name']}", expanded=True):
                    st.write(f"**Name:** {selected_badge['name']}")
                    st.write(f"**Category:** {selected_badge['category']}")
                    st.write(f"**Description:** {selected_badge['description']}")
                    st.write(f"**How to Achieve:** {selected_badge.get('how_to_achieve', 'Not specified')}")
                    roles = selected_badge.get('eligible_roles', [])
                    if isinstance(roles, str):
                        roles = json.loads(roles)
                    st.write(f"**Eligible Roles:** {', '.join(roles)}")
                    st.write(f"**Expected Time:** {selected_badge.get('expected_time_days', 'N/A')} days")
                    st.write(f"**Expiry Date:** {selected_badge.get('validity', 'Permanent')}")
                    st.write(f"**Type:** {selected_badge.get('badge_type', 'N/A').capitalize()}")

                    if user_has_access('create_badges'):
                        if st.button("Edit this Badge", key="edit_badge_button"):
                            st.session_state.badge_to_edit = selected_badge
                            st.session_state.active_tab = "Create/Edit Badge"
                            st.rerun()
    else:
        st.info("No badges found matching the selected filters.")

# ---- CREATE/EDIT BADGE TAB ----
elif st.session_state.active_tab == "Create/Edit Badge":
    if not user_has_access('create_badges'):
        st.warning("You don't have permission to create or edit badges.")
        st.stop()
    
    st.subheader("Create/Edit Badge")

    editing = False
    if st.session_state.badge_to_edit:
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
            'eligible_roles': [],
            'expected_time_days': 30,
            'validity': 'Permanent',
            'badge_type': 'work'
        }

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
            eligible_roles = st.multiselect(
                "Eligible Roles",
                ['Dev', 'QA', 'RMO', 'TL'],
                default=badge.get('eligible_roles', [])
            )
        with col2:
            how_to_achieve = st.text_area("How to Achieve", value=badge.get('how_to_achieve', ''))
            expected_time_days = st.number_input(
                "Validity Time (days)",
                min_value=1,
                max_value=365,
                value=badge.get('expected_time_days', 30)
            )

        col3, col4 = st.columns(2)
        with col3:
            validity = st.selectbox(
                "Expiry Date",
                ['Permanent', '1 Month', '3 Months', '6 Months', '1 Year'],
                index=['Permanent', '1 Month', '3 Months', '6 Months', '1 Year'].index(badge.get('validity', 'Permanent')) if badge.get('validity', 'Permanent') in ['Permanent', '1 Month', '3 Months', '6 Months', '1 Year'] else 0
            )
        with col4:
            badge_type = st.selectbox(
                "Badge Type",
                ['Work', 'Objective'],
                index=['Work', 'Objective'].index(badge.get('badge_type', 'work').capitalize()) if badge.get('badge_type', 'work').capitalize() in ['Work', 'Objective'] else 0
            )

        # Submit
        submit_label = "Update Badge" if editing else "Create Badge"
        submitted = st.form_submit_button(submit_label)

        if submitted:
            if not name:
                st.error("Badge name is required")
            elif not description:
                st.error("Description is required")
            elif not category:
                st.error("Category is required")
            elif not eligible_roles:
                st.error("At least one eligible role is required")
            else:
                badge_data = {
                    'id': badge['id'],
                    'name': name,
                    'description': description,
                    'category': category,
                    'how_to_achieve': how_to_achieve,
                    'eligible_roles': eligible_roles,
                    'expected_time_days': expected_time_days,
                    'validity': validity,
                    'badge_type': badge_type.lower()
                }

                if editing:
                    DatabaseManager.update(Badge, badge['id'], badge_data)
                    st.success(f"Badge '{name}' updated successfully!")
                else:
                    DatabaseManager.create(Badge, badge_data)
                    st.success(f"Badge '{name}' created successfully!")

                # Refresh badges
                badges = DatabaseManager.get_all(Badge)
                st.session_state.badges = badges if badges else []

                st.session_state.badge_to_edit = None
                st.session_state.active_tab = "View Badges"
                st.rerun()

    if editing:
        if st.button("Cancel Edit"):
            st.session_state.badge_to_edit = None
            st.rerun()
