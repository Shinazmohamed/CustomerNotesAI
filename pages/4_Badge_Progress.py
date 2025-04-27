import streamlit as st
import pandas as pd
import plotly.express as px
from auth import is_authenticated, get_current_user
from utils import calculate_badge_progress, filter_badges_by_role
from crud.db_manager import DatabaseManager
from models.badge import Badge
from models.badge_award import BadgeAward

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'badges' not in st.session_state:
    st.session_state.badges = DatabaseManager.get_all(Badge)
if 'awards' not in st.session_state:
    st.session_state.awards = DatabaseManager.get_all(BadgeAward)

# Page config
st.set_page_config(
    page_title="Badge Progress - IT Team Gamification",
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
st.title("📊 Badge Progress Tracker")
st.write("Track your progress towards earning new badges.")

# Badge type filtering helper
def normalize_criteria(value):
    return value.lower().strip() if isinstance(value, str) else "work"

# Prepare badges
badges = st.session_state.badges
user_awards = [a for a in st.session_state.awards if a['user_id'] == user['id']]
earned_ids = [a['id'] for a in user_awards]
eligible_badges = filter_badges_by_role(badges, user['role'])

# Normalize criteria for consistency
for badge in eligible_badges:
    badge['criteria'] = normalize_criteria(badge.get('criteria', 'work'))

earned_badges = [b for b in eligible_badges if b['id'] in earned_ids]
unearned_badges = [b for b in eligible_badges if b['id'] not in earned_ids]

# Create tabs
tab1, tab2 = st.tabs(["Available Badges", "Earned Badges"])

with tab1:
    st.subheader("Badges Available to Earn")

    if unearned_badges:
        col1, col2 = st.columns(2)

        with col1:
            categories = ['All'] + sorted(set(b['category'] for b in unearned_badges))
            selected_category = st.selectbox("Filter by Category", categories, key="unearned_category")

        with col2:
            badge_types = ['All', 'Work', 'Objective']
            selected_type = st.selectbox("Filter by Type", badge_types, key="unearned_type")

        filtered_badges = unearned_badges

        if selected_category != 'All':
            filtered_badges = [b for b in filtered_badges if b['category'] == selected_category]

        if selected_type != 'All':
            type_key = normalize_criteria(selected_type)
            filtered_badges = [b for b in filtered_badges if b['criteria'] == type_key]

        if filtered_badges:
            progress_data = []
            for badge in filtered_badges:
                progress = calculate_badge_progress(user['id'], badge['id'])
                progress_data.append({
                    'Badge': badge['name'],
                    'Category': badge['category'],
                    'Description': badge['description'],
                    'Progress': progress,
                    'Expected Time': f"{badge.get('validity_days', 'N/A')} days",
                    'Type': badge['criteria'].capitalize(),
                    'ID': badge['id']
                })

            progress_df = pd.DataFrame(progress_data).sort_values('Progress', ascending=False)

            st.dataframe(
                progress_df.drop(columns=['ID']),
                use_container_width=True,
                column_config={
                    'Progress': st.column_config.ProgressColumn(
                        "Progress",
                        help="Progress towards earning this badge",
                        format="%d%%",
                        min_value=0,
                        max_value=100
                    ),
                    'Description': st.column_config.TextColumn(width="large")
                }
            )

            st.subheader("Badge Details")
            id = st.selectbox("Select a badge to view details", 
                options=[b['id'] for b in filtered_badges],
                format_func=lambda x: next((b['name'] for b in filtered_badges if b['id'] == x), x)
            )

            selected_badge = next((b for b in filtered_badges if b['id'] == id), None)

            if selected_badge:
                progress = calculate_badge_progress(user['id'], selected_badge['id'])
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader("Your Progress")
                    st.progress(progress / 100)
                    st.write(f"**{progress}%** complete")
                    estimated_days = selected_badge.get('validity_days', 0)
                    remaining_days = int(estimated_days * (1 - progress / 100))
                    if remaining_days > 0:
                        st.write(f"Estimated time to completion: **{remaining_days}** days")
                    else:
                        st.write("**Almost there!** Complete the remaining requirements to earn this badge.")

                with col2:
                    st.subheader(selected_badge['name'])
                    st.write(f"**Category:** {selected_badge['category']}")
                    st.write(f"**Description:** {selected_badge['description']}")
                    st.write(f"**How to Achieve:** {selected_badge.get('how_to_achieve', 'Not specified')}")
                    st.write(f"**Expected Time:** {selected_badge.get('validity_days', 'N/A')} days")
                    st.write(f"**Type:** {selected_badge['criteria'].capitalize()}")
        else:
            st.info("No badges found matching the selected filters.")
    else:
        st.info("You've earned all available badges for your role! Congratulations!")

with tab2:
    st.subheader("Your Earned Badges")

    if earned_badges:
        col1, col2 = st.columns(2)

        with col1:
            earned_categories = ['All'] + sorted(set(b['category'] for b in earned_badges))
            selected_earned_category = st.selectbox("Filter by Category", earned_categories, key="earned_category")

        with col2:
            earned_badge_types = ['All', 'Work', 'Objective']
            selected_earned_type = st.selectbox("Filter by Type", earned_badge_types, key="earned_type")

        filtered_earned_badges = earned_badges

        if selected_earned_category != 'All':
            filtered_earned_badges = [b for b in filtered_earned_badges if b['category'] == selected_earned_category]

        if selected_earned_type != 'All':
            type_key = normalize_criteria(selected_earned_type)
            filtered_earned_badges = [b for b in filtered_earned_badges if b['criteria'] == type_key]

        if filtered_earned_badges:
            earned_data = []
            for badge in filtered_earned_badges:
                award = next((a for a in user_awards if a['id'] == badge['id']), None)
                if award:
                    earned_data.append({
                        'Badge': badge['name'],
                        'Category': badge['category'],
                        'Date Earned': award.get('awarded_at', 'N/A'),
                        'Awarded By': next((u['name'] for u in st.session_state.users if u['id'] == award.get('awarded_by')), 'System'),
                        'Type': badge['criteria'].capitalize(),
                        'ID': badge['id']
                    })

            earned_df = pd.DataFrame(earned_data).sort_values('Date Earned', ascending=False)

            st.dataframe(earned_df.drop(columns=['ID']), use_container_width=True)

            # Chart: Category Pie
            category_counts = earned_df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']

            fig = px.pie(
                category_counts,
                values='Count',
                names='Category',
                title='Earned Badges by Category',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # Chart: Accumulation Over Time
            earned_df['Date'] = pd.to_datetime(earned_df['Date Earned'], errors='coerce')
            earned_df = earned_df.sort_values('Date')
            earned_df['Cumulative'] = range(1, len(earned_df) + 1)

            fig = px.line(
                earned_df,
                x='Date',
                y='Cumulative',
                title='Badge Accumulation Over Time',
                labels={'Cumulative': 'Total Badges', 'Date': 'Date Earned'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No earned badges match the selected filters.")
    else:
        st.info("You haven't earned any badges yet. Start completing tasks to earn your first badge!")

# Work/Objective Split Analysis
st.subheader("Regular Work vs. Objectives Split")

work_badges = len([b for b in earned_badges if b['criteria'] == 'work'])
objective_badges = len([b for b in earned_badges if b['criteria'] == 'objective'])

total = work_badges + objective_badges
work_pct = (work_badges / total * 100) if total else 0
obj_pct = (objective_badges / total * 100) if total else 0

if total > 0:
    split_data = pd.DataFrame({
        'Type': [f'Regular Work ({work_pct:.1f}%)', f'Objectives ({obj_pct:.1f}%)'],
        'Count': [work_badges, objective_badges]
    })

    fig = px.bar(
        split_data,
        x='Type',
        y='Count',
        title='Badges by Work Type',
        color='Type',
        color_discrete_sequence=['#4169E1', '#32CD32']
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Regular Work Badges", f"{work_badges} ({work_pct:.1f}%)")
    with col2:
        st.metric("Objective Badges", f"{objective_badges} ({obj_pct:.1f}%)")

    st.subheader("Balance Analysis")
    if total < 3:
        st.info("Earn more badges to see a meaningful analysis of your work/objective balance.")
    elif work_pct > 90:
        st.warning("Your badge distribution is heavily focused on regular work. Consider pursuing more objective-related achievements to balance your development.")
    elif obj_pct > 50:
        st.warning("You have an unusually high proportion of objective badges. While personal development is important, ensure you're also focusing on your core responsibilities.")
    elif 70 <= work_pct <= 90 and 10 <= obj_pct <= 30:
        st.success("You have a good balance between regular work and objectives, close to the ideal 80/20 split!")
    else:
        st.info("Your badge distribution shows a reasonable balance, but could be optimized further.")
else:
    st.info("Earn badges to see your work/objective distribution.")
