import streamlit as st
import pandas as pd
import plotly.express as px
from auth import is_authenticated, get_current_user
from utils import calculate_badge_progress, filter_badges_by_role

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

# Get all badges
badges = st.session_state.badges

# Get user's earned badges
user_awards = [a for a in st.session_state.awards if a['user_id'] == user['id']]
earned_badge_ids = [a['badge_id'] for a in user_awards]

# Filter badges by user's role
eligible_badges = filter_badges_by_role(badges, user['role'])

# Separate earned and unearned badges
earned_badges = [b for b in eligible_badges if b['id'] in earned_badge_ids]
unearned_badges = [b for b in eligible_badges if b['id'] not in earned_badge_ids]

# Create tabs
tab1, tab2 = st.tabs(["Available Badges", "Earned Badges"])

with tab1:
    st.subheader("Badges Available to Earn")

    if unearned_badges:
        # Filter controls
        col1, col2 = st.columns(2)

        with col1:
            # Filter by category
            categories = ['All']
            for badge in unearned_badges:
                if badge['category'] not in categories:
                    categories.append(badge['category'])

            selected_category = st.selectbox("Filter by Category", categories, key="unearned_category")

        with col2:
            # Filter by badge type
            badge_types = ['All', 'Work', 'Objective']
            selected_type = st.selectbox("Filter by Type", badge_types, key="unearned_type")

        # Apply filters
        filtered_badges = unearned_badges

        if selected_category != 'All':
            filtered_badges = [b for b in filtered_badges if b['category'] == selected_category]

        if selected_type != 'All':
            type_key = selected_type.lower()
            filtered_badges = [b for b in filtered_badges if b.get('badge_type', '').lower() == type_key]

        if filtered_badges:
            # Create progress data
            progress_data = []

            for badge in filtered_badges:
                # Calculate progress
                progress = calculate_badge_progress(user['id'], badge['id'])

                progress_data.append({
                    'Badge': badge['name'],
                    'Category': badge['category'],
                    'Description': badge['description'],
                    'Progress': progress,
                    'Expected Time': f"{badge.get('expected_time_days', 'N/A')} days",
                    'Type': badge.get('badge_type', 'work').capitalize(),
                    'ID': badge['id']
                })

            # Create DataFrame
            progress_df = pd.DataFrame(progress_data)

            # Sort by progress (highest first)
            progress_df = progress_df.sort_values('Progress', ascending=False)

            # Display as table
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

            # Badge details
            st.subheader("Badge Details")
            badge_id = st.selectbox("Select a badge to view details", 
                                   options=[b['id'] for b in filtered_badges],
                                   format_func=lambda x: next((b['name'] for b in filtered_badges if b['id'] == x), x))

            if badge_id:
                selected_badge = next((b for b in filtered_badges if b['id'] == badge_id), None)
                if selected_badge:
                    progress = calculate_badge_progress(user['id'], selected_badge['id'])

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Progress circle
                        st.subheader("Your Progress")
                        st.progress(progress / 100)
                        st.write(f"**{progress}%** complete")

                        estimated_days = selected_badge.get('expected_time_days', 0)
                        remaining_days = int(estimated_days * (1 - progress / 100))

                        if remaining_days > 0:
                            st.write(f"Estimated time to completion: **{remaining_days}** days")
                        else:
                            st.write("**Almost there!** Complete the remaining requirements to earn this badge.")

                    with col2:
                        # Badge info
                        st.subheader(selected_badge['name'])
                        st.write(f"**Category:** {selected_badge['category']}")
                        st.write(f"**Description:** {selected_badge['description']}")
                        st.write(f"**How to Achieve:** {selected_badge.get('how_to_achieve', 'Not specified')}")
                        st.write(f"**Expected Time:** {selected_badge.get('expected_time_days', 'N/A')} days")
                        st.write(f"**Type:** {selected_badge.get('badge_type', 'work').capitalize()}")
        else:
            st.info("No badges found matching the selected filters.")
    else:
        st.info("You've earned all available badges for your role! Congratulations!")

with tab2:
    st.subheader("Your Earned Badges")

    if earned_badges:
        # Filter controls
        col1, col2 = st.columns(2)

        with col1:
            # Filter by category
            earned_categories = ['All']
            for badge in earned_badges:
                if badge['category'] not in earned_categories:
                    earned_categories.append(badge['category'])

            selected_earned_category = st.selectbox("Filter by Category", earned_categories, key="earned_category")

        with col2:
            # Filter by badge type
            earned_badge_types = ['All', 'Work', 'Objective']
            selected_earned_type = st.selectbox("Filter by Type", earned_badge_types, key="earned_type")

        # Apply filters
        filtered_earned_badges = earned_badges

        if selected_earned_category != 'All':
            filtered_earned_badges = [b for b in filtered_earned_badges 
                                     if b['category'] == selected_earned_category]

        if selected_earned_type != 'All':
            type_key = selected_earned_type.lower()
            filtered_earned_badges = [b for b in filtered_earned_badges 
                                     if b.get('badge_type', '').lower() == type_key]

        if filtered_earned_badges:
            # Get award details for each badge
            earned_data = []

            for badge in filtered_earned_badges:
                # Find award record
                award = next((a for a in user_awards if a['badge_id'] == badge['id']), None)

                if award:
                    earned_data.append({
                        'Badge': badge['name'],
                        'Category': badge['category'],
                        'Date Earned': award.get('awarded_at', 'N/A'),
                        'Awarded By': next((u['name'] for u in st.session_state.users 
                                          if u['id'] == award.get('awarded_by')), 'System'),
                        'Type': badge.get('badge_type', 'work').capitalize(),
                        'ID': badge['id']
                    })

            # Create DataFrame
            earned_df = pd.DataFrame(earned_data)

            # Sort by date (newest first)
            earned_df = earned_df.sort_values('Date Earned', ascending=False)

            # Display table
            st.dataframe(earned_df.drop(columns=['ID']), use_container_width=True)

            # Chart: Badges by category
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

            # Chart: Badges over time
            if 'Date Earned' in earned_df.columns:
                # Convert to datetime for charting
                #earned_df['Date'] = pd.to_datetime([d if isinstance(d, str) else d.strftime('%Y-%m-%d') for d in earned_df['Date Earned']], errors='coerce')
                earned_df['Date'] = pd.to_datetime(
                    [d if isinstance(d, str) else d.strftime('%Y-%m-%d') for d in earned_df['Date Earned']],
                    format='%Y-%m-%d',
                    errors='coerce'
                )

                # Sort by date
                earned_df = earned_df.sort_values('Date')

                # Create cumulative count
                earned_df['Cumulative'] = range(1, len(earned_df) + 1)

                # Create line chart
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

# Work/Objective split
st.subheader("Regular Work vs. Objectives Split")

# Count badges by type
work_badges = len([b for b in earned_badges if b.get('badge_type', 'work') == 'work'])
objective_badges = len([b for b in earned_badges if b.get('badge_type', 'objective') == 'objective'])

# Create data for chart
split_data = pd.DataFrame({
    'Type': ['Regular Work (80%)', 'Objectives (20%)'],
    'Count': [work_badges, objective_badges]
})

if work_badges > 0 or objective_badges > 0:
    # Create chart
    fig = px.bar(
        split_data,
        x='Type',
        y='Count',
        title='Badges by Work Type',
        color='Type',
        color_discrete_sequence=['#4169E1', '#32CD32']
    )
    st.plotly_chart(fig, use_container_width=True)

    # Calculate percentages
    total = work_badges + objective_badges
    work_pct = (work_badges / total * 100) if total > 0 else 0
    obj_pct = (objective_badges / total * 100) if total > 0 else 0

    # Display metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Regular Work Badges", f"{work_badges} ({work_pct:.1f}%)")

    with col2:
        st.metric("Objective Badges", f"{objective_badges} ({obj_pct:.1f}%)")

    # Suggestion based on split
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