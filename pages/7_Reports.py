import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import io
from auth import is_authenticated, get_current_user, user_has_access
from utils import get_team_by_id, export_to_csv, calculate_team_stats, get_badge_by_id



def safe_date(d):
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(d, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


# Page config
st.set_page_config(
    page_title="Reports - IT Team Gamification",
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
st.title("📊 Reports & Analytics")
st.write("Access performance reports and analytics across teams and individuals.")

# Check if user has access to reports
if not user_has_access('view_reports'):
    st.warning("You don't have sufficient permissions to view detailed reports.")

    # Show limited personal reports
    st.subheader("Your Achievement Summary")

    # Get user badges
    user_awards = [a for a in st.session_state.awards if a['user_id'] == user['id']]

    if user_awards:
        badge_data = []
        for award in user_awards:
            badge = get_badge_by_id(award['badge_id'])
            if badge:
                badge_data.append({
                    'Badge': badge['name'],
                    'Category': badge['category'],
                    'Date Earned': award.get('award_date', 'N/A'),
                    'Type': award.get('badge_type', 'work').capitalize()
                })

        badge_df = pd.DataFrame(badge_data)
        st.dataframe(badge_df, use_container_width=True)

        # Simple chart
        if len(badge_df) > 0:
            # Badge count by category
            category_counts = badge_df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']

            fig = px.pie(
                category_counts,
                values='Count',
                names='Category',
                title='Your Badges by Category',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("You haven't earned any badges yet.")

    st.stop()

# Define report types
report_type = st.selectbox(
    "Report Type",
    ["Team Performance Overview", "Badge Distribution Analysis", 
     "Work-Objective Balance", "Sprint Achievement Analysis", 
     "Leaderboard", "Custom Report"]
)

# Get teams for filtering
teams = st.session_state.teams
team_options = [{'label': t['name'], 'value': t['id']} for t in teams]

# Time period filter
time_period = st.selectbox(
    "Time Period",
    ["All Time", "This Month", "Last Month", "Last 3 Months", "Last 6 Months", "This Year", "Custom Range"]
)

# Handle custom date range
if time_period == "Custom Range":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
else:
    # Calculate date range based on selection
    today = datetime.now()

    if time_period == "This Month":
        start_date_str = today.replace(day=1).strftime("%Y-%m-%d")
        end_date_str = today.strftime("%Y-%m-%d")
    elif time_period == "Last Month":
        last_month = today.month - 1 if today.month > 1 else 12
        last_month_year = today.year if today.month > 1 else today.year - 1
        start_date_str = datetime(last_month_year, last_month, 1).strftime("%Y-%m-%d")
        end_date_str = today.replace(day=1).strftime("%Y-%m-%d")
    elif time_period == "Last 3 Months":
        start_date_str = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date_str = today.strftime("%Y-%m-%d")
    elif time_period == "Last 6 Months":
        start_date_str = (today - timedelta(days=180)).strftime("%Y-%m-%d")
        end_date_str = today.strftime("%Y-%m-%d")
    elif time_period == "This Year":
        start_date_str = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        end_date_str = today.strftime("%Y-%m-%d")
    else:  # All Time
        start_date_str = "1900-01-01"
        end_date_str = "2100-12-31"

# Get all awards
all_awards = st.session_state.awards

# Filter awards by date
start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

filtered_awards = [
    a for a in all_awards
    if safe_date(a.get('award_date')) and start_date <= safe_date(a['award_date']) <= end_date
]


# Specific report generation based on selection
if report_type == "Team Performance Overview":
    st.subheader("Team Performance Overview")

    # Select team(s) to include
    selected_teams = st.multiselect(
        "Select Teams",
        options=[t['id'] for t in teams],
        default=[user['team_id']],  # Default to user's team
        format_func=lambda x: next((t['label'] for t in team_options if t['value'] == x), x)
    )

    if not selected_teams:
        st.warning("Please select at least one team to generate the report.")
    else:
        # Calculate stats for each selected team
        team_stats_data = []

        for team_id in selected_teams:
            team = get_team_by_id(team_id)
            if team:
                stats = calculate_team_stats(team_id)

                # Filter awards for this team's members
                team_members = [u['id'] for u in st.session_state.users if u['team_id'] == team_id]
                team_awards = [a for a in filtered_awards if a['user_id'] in team_members]

                # Count different badge types
                work_badges = sum(1 for a in team_awards if a.get('badge_type') == 'work')
                obj_badges = sum(1 for a in team_awards if a.get('badge_type') == 'objective')

                thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
                recent_badges = sum(
                    1 for a in team_awards
                    if safe_date(a.get('award_date')) and safe_date(a['award_date']) >= thirty_days_ago
                )

                team_stats_data.append({
                    'Team': team['name'],
                    'Members': stats['member_count'],
                    'Total Badges': len(team_awards),
                    'Avg Badges/Member': round(len(team_awards) / stats['member_count'], 2) if stats['member_count'] > 0 else 0,
                    'Work Badges': work_badges,
                    'Objective Badges': obj_badges,
                    'Team ID': team_id
                })

        # Create DataFrame
        team_stats_df = pd.DataFrame(team_stats_data)

        # Display team stats table
        st.dataframe(team_stats_df.drop(columns=['Team ID']), use_container_width=True)

        # Create visualizations
        st.subheader("Team Comparisons")

        # Total badges by team
        fig1 = px.bar(
            team_stats_df,
            x='Team',
            y='Total Badges',
            title='Total Badges by Team',
            color='Team',
            labels={'Total Badges': 'Number of Badges'}
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Average badges per member
        fig2 = px.bar(
            team_stats_df,
            x='Team',
            y='Avg Badges/Member',
            title='Average Badges per Team Member',
            color='Team',
            labels={'Avg Badges/Member': 'Average Badges'}
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Work-Objective split
        fig3 = px.bar(
            team_stats_df,
            x='Team',
            y=['Work Badges', 'Objective Badges'],
            title='Work vs. Objective Badge Distribution',
            barmode='group',
            labels={'value': 'Number of Badges', 'variable': 'Badge Type'}
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Export option
        if st.button("Export Team Performance Data"):
            export_to_csv(team_stats_df.drop(columns=['Team ID']), "team_performance_report.csv")

elif report_type == "Badge Distribution Analysis":
    st.subheader("Badge Distribution Analysis")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        # Team filter
        selected_team_id = st.selectbox(
            "Select Team",
            options=["All Teams"] + [t['id'] for t in teams],
            format_func=lambda x: "All Teams" if x == "All Teams" else next(
                (t['label'] for t in team_options if t['value'] == x), x)
        )

    with col2:
        # Badge category filter
        categories = ["All Categories"]
        for badge in st.session_state.badges.values():
            if badge['category'] not in categories:
                categories.append(badge['category'])

        selected_category = st.selectbox("Badge Category", categories)

    # Apply filters to awards
    # Team filter
    selected_team_id = st.selectbox(
        "Select Team",
        options=["All Teams"] + [t['id'] for t in teams],
        format_func=lambda x: "All Teams" if x == "All Teams" else next(
            (t['label'] for t in team_options if t['value'] == x), x),
        key="bd_team" 
    )


    if selected_team_id != "All Teams":
        team_members = [u['id'] for u in st.session_state.users if u['team_id'] == selected_team_id]
        badge_awards = [a for a in filtered_awards if a['user_id'] in team_members]
    else:
        badge_awards = filtered_awards

    # Prepare badge data
    badge_data = []

    for award in badge_awards:
        badge = get_badge_by_id(award['badge_id'])
        user = next((u for u in st.session_state.users if u['id'] == award['user_id']), None)
        team = get_team_by_id(user['team_id']) if user else None

        if badge and user and team:
            if selected_category == "All Categories" or badge['category'] == selected_category:
                badge_data.append({
                    'Badge': badge['name'],
                    'Category': badge['category'],
                    'Recipient': user['name'],
                    'Team': team['name'],
                    'Role': user['role'],
                    'Date': award.get('award_date', 'N/A'),
                    'Type': award.get('badge_type', 'work').capitalize()
                })

    # Create DataFrame
    badge_df = pd.DataFrame(badge_data)

    if not badge_df.empty:
        # Show badge distribution
        st.write(f"Total badges awarded: **{len(badge_df)}**")

        # Display table
        st.dataframe(badge_df, use_container_width=True)

        # Visualizations
        st.subheader("Badge Distribution Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Categories distribution
            category_counts = badge_df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']

            fig1 = px.pie(
                category_counts,
                values='Count',
                names='Category',
                title='Badge Distribution by Category',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Role distribution
            role_counts = badge_df['Role'].value_counts().reset_index()
            role_counts.columns = ['Role', 'Count']

            fig2 = px.pie(
                role_counts,
                values='Count',
                names='Role',
                title='Badge Distribution by Role',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Badges over time
        if 'Date' in badge_df.columns:
            try:
                # Convert to datetime for charting
                badge_df['DateObj'] = pd.to_datetime(badge_df['Date'], errors='coerce')
                badge_df = badge_df.sort_values('DateObj')

                # Group by date
                date_counts = badge_df.groupby(badge_df['DateObj'].dt.strftime('%Y-%m-%d')).size().reset_index()
                date_counts.columns = ['Date', 'Count']
                date_counts['DateObj'] = pd.to_datetime(date_counts['Date'])
                date_counts = date_counts.sort_values('DateObj')

                # Calculate cumulative sum
                date_counts['Cumulative'] = date_counts['Count'].cumsum()

                # Create time series chart
                fig3 = px.line(
                    date_counts,
                    x='DateObj',
                    y=['Count', 'Cumulative'],
                    title='Badge Awards Over Time',
                    labels={'value': 'Number of Badges', 'variable': 'Metric', 'DateObj': 'Date'}
                )
                st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("Could not create time series chart due to date format issues.")

        # Export option
        if st.button("Export Badge Distribution Data"):
            export_to_csv(badge_df, "badge_distribution_report.csv")
    else:
        st.info("No badges found matching the selected filters.")

elif report_type == "Work-Objective Balance":
    st.subheader("Work-Objective Balance Analysis")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        # Team filter
        selected_team_id = st.selectbox(
            "Select Team",
            options=["All Teams"] + [t['id'] for t in teams],
            format_func=lambda x: "All Teams" if x == "All Teams" else next(
                (t['label'] for t in team_options if t['value'] == x), x),
            key="wo_team"
        )

    with col2:
        # Role filter
        roles = ["All Roles", "Dev", "QA", "RMO", "TL", "Manager"]
        selected_role = st.selectbox("Role", roles)

    # Filter team members
    if selected_team_id == "All Teams":
        team_members = st.session_state.users
    else:
        team_members = [u for u in st.session_state.users if u['team_id'] == selected_team_id]

    # Apply role filter
    if selected_role != "All Roles":
        team_members = [m for m in team_members if m['role'] == selected_role]

    if team_members:
        # Calculate work-objective balance for each member
        balance_data = []

        for member in team_members:
            # Get member's awards
            member_awards = [a for a in filtered_awards if a['user_id'] == member['id']]

            # Count work and objective badges
            work_badges = sum(1 for a in member_awards if a.get('badge_type') == 'work')
            obj_badges = sum(1 for a in member_awards if a.get('badge_type') == 'objective')
            total_badges = work_badges + obj_badges

            # Calculate percentages
            work_pct = (work_badges / total_badges * 100) if total_badges > 0 else 0
            obj_pct = (obj_badges / total_badges * 100) if total_badges > 0 else 0

            # Determine balance status
            if total_badges < 3:
                balance_status = "Insufficient Data"
            elif 75 <= work_pct <= 85 and 15 <= obj_pct <= 25:
                balance_status = "Optimal Balance"
            elif work_pct > 90:
                balance_status = "Work Heavy"
            elif obj_pct > 30:
                balance_status = "Objective Heavy"
            else:
                balance_status = "Reasonable Balance"

            balance_data.append({
                'Name': member['name'],
                'Role': member['role'],
                'Team': next((t['name'] for t in teams if t['id'] == member['team_id']), 'Unknown'),
                'Work Badges': work_badges,
                'Objective Badges': obj_badges,
                'Total Badges': total_badges,
                'Work %': round(work_pct, 1),
                'Objective %': round(obj_pct, 1),
                'Balance Status': balance_status
            })

        # Create DataFrame
        balance_df = pd.DataFrame(balance_data)

        # Sort by total badges (descending)
        balance_df = balance_df.sort_values('Total Badges', ascending=False)

        # Display table
        st.dataframe(balance_df, use_container_width=True)

        # Analytics
        st.subheader("Balance Analytics")

        if not balance_df.empty and any(balance_df['Total Badges'] > 0):
            # Stacked bar chart for individuals
            top_members = balance_df[balance_df['Total Badges'] > 0].head(10)

            if not top_members.empty:
                fig1 = px.bar(
                    top_members,
                    x='Name',
                    y=['Work %', 'Objective %'],
                    title='Work-Objective Balance by Individual (Top 10)',
                    labels={'value': 'Percentage', 'variable': 'Type'},
                    color_discrete_map={'Work %': '#4169E1', 'Objective %': '#32CD32'}
                )
                st.plotly_chart(fig1, use_container_width=True)

            # Balance distribution
            status_counts = balance_df['Balance Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']

            fig2 = px.pie(
                status_counts,
                values='Count',
                names='Status',
                title='Balance Status Distribution',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Team averages (if multiple teams)
            if selected_team_id == "All Teams" and len(teams) > 1:
                team_avgs = balance_df.groupby('Team').agg({
                    'Work %': 'mean',
                    'Objective %': 'mean',
                    'Total Badges': 'sum'
                }).reset_index()

                fig3 = px.bar(
                    team_avgs,
                    x='Team',
                    y=['Work %', 'Objective %'],
                    title='Work-Objective Balance by Team',
                    barmode='stack',
                    labels={'value': 'Percentage', 'variable': 'Type'},
                    color_discrete_map={'Work %': '#4169E1', 'Objective %': '#32CD32'}
                )

                # Add ideal balance reference line
                fig3.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(team_avgs)-0.5,
                    y0=80,
                    y1=80,
                    line=dict(color='red', width=2, dash='dash'),
                    name='Ideal Work %'
                )

                st.plotly_chart(fig3, use_container_width=True)

            # Export option
            if st.button("Export Work-Objective Balance Data"):
                export_to_csv(balance_df, "work_objective_balance_report.csv")
        else:
            st.info("No badge data available for the selected filters.")
    else:
        st.warning("No team members found matching the selected criteria.")

elif report_type == "Sprint Achievement Analysis":
    st.subheader("Sprint Achievement Analysis")

    # Get sprints
    sprints = st.session_state.sprints

    # Filter completed sprints within the date range
    filtered_sprints = [
        s for s in sprints 
        if s.get('status') == 'completed' and
        isinstance(s.get('end_date'), date) and
        start_date_str <= s.get('end_date').strftime('%Y-%m-%d') <= end_date_str
    ]

    if filtered_sprints:
        # Sort by end date (newest first)
        filtered_sprints = sorted(
            filtered_sprints,
            key=lambda x: x.get('end_date', '1900-01-01'),
            reverse=True
        )

        # Sprint selection
        sprint_options = [
            {'label': f"{s['name']} ({s.get('start_date', 'N/A')} to {s.get('end_date', 'N/A')})", 
             'value': s['id']} for s in filtered_sprints
        ]

        selected_sprints = st.multiselect(
            "Select Sprints to Analyze",
            options=[s['id'] for s in filtered_sprints],
            default=[filtered_sprints[0]['id']] if filtered_sprints else [],
            format_func=lambda x: next((s['label'] for s in sprint_options if s['value'] == x), x)
        )

        if selected_sprints:
            # Analyze each selected sprint
            sprint_data = []

            for sprint_id in selected_sprints:
                sprint = next((s for s in filtered_sprints if s['id'] == sprint_id), None)

                if sprint:
                    # Get awards for this sprint
                    sprint_awards = [a for a in all_awards if a.get('sprint_id') == sprint_id]

                    # Count different badge types
                    work_badges = sum(1 for a in sprint_awards if a.get('badge_type') == 'work')
                    obj_badges = sum(1 for a in sprint_awards if a.get('badge_type') == 'objective')

                    # Get unique recipients
                    unique_recipients = len(set(a['user_id'] for a in sprint_awards))

                    # Calculate sprint duration
                    try:
                        start_date = datetime.strptime(sprint.get('start_date', '2100-01-01'), "%Y-%m-%d")
                        end_date = datetime.strptime(sprint.get('end_date', '2100-01-01'), "%Y-%m-%d")
                        duration = (end_date - start_date).days + 1
                    except:
                        duration = 0

                    sprint_data.append({
                        'Sprint': sprint['name'],
                        'Start Date': sprint.get('start_date', 'N/A'),
                        'End Date': sprint.get('end_date', 'N/A'),
                        'Duration (days)': duration,
                        'Total Badges': len(sprint_awards),
                        'Work Badges': work_badges,
                        'Objective Badges': obj_badges,
                        'Unique Recipients': unique_recipients,
                        'ID': sprint_id
                    })

            # Create DataFrame
            sprint_df = pd.DataFrame(sprint_data)

            # Sort by start date
            sprint_df = sprint_df.sort_values('Start Date')

            # Display table
            st.dataframe(sprint_df.drop(columns=['ID']), use_container_width=True)

            # Visualizations
            st.subheader("Sprint Analytics")

            # Badges by sprint
            fig1 = px.bar(
                sprint_df,
                x='Sprint',
                y=['Work Badges', 'Objective Badges'],
                title='Badges Awarded by Sprint',
                barmode='stack',
                labels={'value': 'Number of Badges', 'variable': 'Badge Type'}
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Recipients vs badges
            fig2 = px.scatter(
                sprint_df,
                x='Total Badges',
                y='Unique Recipients',
                size='Duration (days)',
                color='Sprint',
                title='Recipients vs. Total Badges by Sprint',
                labels={'Total Badges': 'Total Badges Awarded', 
                        'Unique Recipients': 'Unique Badge Recipients'}
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Badges per day trend
            sprint_df['Badges per Day'] = sprint_df['Total Badges'] / sprint_df['Duration (days)'].replace(0, 1)

            fig3 = px.line(
                sprint_df,
                x='Sprint',
                y='Badges per Day',
                markers=True,
                title='Badge Award Rate Trend',
                labels={'Badges per Day': 'Average Badges per Day'}
            )
            st.plotly_chart(fig3, use_container_width=True)

            # Detailed sprint analysis
            st.subheader("Detailed Sprint Analysis")
            selected_detail_sprint = st.selectbox(
                "Select Sprint for Detailed Analysis",
                options=selected_sprints,
                format_func=lambda x: next((s['label'] for s in sprint_options if s['value'] == x), x)
            )

            if selected_detail_sprint:
                # Get detailed awards for this sprint
                detail_awards = [a for a in all_awards if a.get('sprint_id') == selected_detail_sprint]

                if detail_awards:
                    # Get sprint details
                    sprint = next((s for s in filtered_sprints if s['id'] == selected_detail_sprint), None)

                    if sprint:
                        st.write(f"### Detailed Analysis: {sprint['name']}")
                        st.write(f"**Duration:** {sprint.get('start_date', 'N/A')} to {sprint.get('end_date', 'N/A')}")

                        # Create award details
                        award_details = []

                        for award in detail_awards:
                            badge = get_badge_by_id(award['badge_id'])
                            user = next((u for u in st.session_state.users if u['id'] == award['user_id']), None)
                            awarder = next((u for u in st.session_state.users if u['id'] == award.get('awarded_by')), None)

                            if badge and user:
                                award_details.append({
                                    'Date': award.get('award_date', 'N/A'),
                                    'Badge': badge['name'],
                                    'Category': badge['category'],
                                    'Recipient': user['name'],
                                    'Role': user['role'],
                                    'Team': next((t['name'] for t in teams if t['id'] == user['team_id']), 'Unknown'),
                                    'Awarded By': awarder['name'] if awarder else 'System',
                                    'Type': award.get('badge_type', 'work').capitalize()
                                })

                        # Create DataFrame
                        award_df = pd.DataFrame(award_details)

                        # Sort by date
                        award_df = award_df.sort_values('Date', ascending=False)

                        # Display table
                        st.dataframe(award_df, use_container_width=True)

                        # Badge distribution by category
                        category_counts = award_df['Category'].value_counts().reset_index()
                        category_counts.columns = ['Category', 'Count']

                        fig4 = px.pie(
                            category_counts,
                            values='Count',
                            names='Category',
                            title=f'Badge Distribution by Category - {sprint["name"]}',
                            color_discrete_sequence=px.colors.qualitative.Safe
                        )
                        st.plotly_chart(fig4, use_container_width=True)

                        # Distribution by recipient
                        recipient_counts = award_df['Recipient'].value_counts().reset_index()
                        recipient_counts.columns = ['Recipient', 'Count']

                        fig5 = px.bar(
                            recipient_counts.head(10),  # Top 10 recipients
                            x='Recipient',
                            y='Count',
                            title=f'Top Badge Recipients - {sprint["name"]}',
                            color='Count',
                            color_continuous_scale='Blues',
                            labels={'Count': 'Number of Badges', 'Recipient': 'Team Member'}
                        )
                        st.plotly_chart(fig5, use_container_width=True)
                else:
                    st.info(f"No badges were awarded in the selected sprint.")

            # Export option
            if st.button("Export Sprint Analysis Data"):
                export_to_csv(sprint_df.drop(columns=['ID']), "sprint_analysis_report.csv")
        else:
            st.warning("Please select at least one sprint to analyze.")
    else:
        st.info("No completed sprints found in the selected date range.")

elif report_type == "Leaderboard":
    st.subheader("Leaderboard")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Team filter
        selected_team_id = st.selectbox(
            "Team",
            options=["All Teams"] + [t['id'] for t in teams],
            format_func=lambda x: "All Teams" if x == "All Teams" else next(
                (t['label'] for t in team_options if t['value'] == x), x),
            key="lb_team"
        )

    with col2:
        # Role filter
        roles = ["All Roles", "Dev", "QA", "RMO", "TL", "Manager"]
        selected_role = st.selectbox("Role", roles, key="lb_role")

    with col3:
        # Badge type filter
        badge_types = ["All Badges", "Work Badges", "Objective Badges"]
        selected_badge_type = st.selectbox("Badge Type", badge_types)

    # Filter users
    if selected_team_id == "All Teams":
        users = st.session_state.users
    else:
        users = [u for u in st.session_state.users if u['team_id'] == selected_team_id]

    if selected_role != "All Roles":
        users = [u for u in users if u['role'] == selected_role]

    if users:
        # Create leaderboard data
        leaderboard_data = []

        for user in users:
            # Get user's awards
            user_awards = [a for a in filtered_awards if a['user_id'] == user['id']]

            # Apply badge type filter
            if selected_badge_type == "Work Badges":
                user_awards = [a for a in user_awards if a.get('badge_type') == 'work']
            elif selected_badge_type == "Objective Badges":
                user_awards = [a for a in user_awards if a.get('badge_type') == 'objective']

            # Count badges by category
            technical_badges = sum(1 for a in user_awards if 
                                  get_badge_by_id(a['badge_id']).get('category') == 'Technical')
            leadership_badges = sum(1 for a in user_awards if 
                                   get_badge_by_id(a['badge_id']).get('category') == 'Leadership')
            teamwork_badges = sum(1 for a in user_awards if 
                                 get_badge_by_id(a['badge_id']).get('category') == 'Teamwork')
            innovation_badges = sum(1 for a in user_awards if 
                                   get_badge_by_id(a['badge_id']).get('category') == 'Innovation')

            leaderboard_data.append({
                'Name': user['name'],
                'Role': user['role'],
                'Team': next((t['name'] for t in teams if t['id'] == user['team_id']), 'Unknown'),
                'Total Badges': len(user_awards),
                'Technical': technical_badges,
                'Leadership': leadership_badges,
                'Teamwork': teamwork_badges,
                'Innovation': innovation_badges,
                'ID': user['id']
            })

        # Create DataFrame
        leaderboard_df = pd.DataFrame(leaderboard_data)

        # Sort by total badges (descending)
        leaderboard_df = leaderboard_df.sort_values('Total Badges', ascending=False)

        # Display leaderboard
        st.write(f"### Top Performers ({selected_badge_type})")

        # Highlight current user
        leaderboard_df['Current User'] = leaderboard_df['ID'] == user['id']

        # Display table
        st.dataframe(
            leaderboard_df.drop(columns=['ID', 'Current User']),
            use_container_width=True
        )

        #Visualizations
        st.subheader("Leaderboard Visualizations")

        # Top performers chart
        top_users = leaderboard_df.head(10)

        if not top_users.empty and any(top_users['Total Badges'] > 0):
            fig1 = px.bar(
                top_users,
                x='Name',
                y='Total Badges',
                color='Team',
                title='Top 10 Badge Earners',
                labels={'Total Badges': 'Number of Badges'}
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Category distribution for top performers
            fig2 = px.bar(
                top_users,
                x='Name',
                y=['Technical', 'Leadership', 'Teamwork', 'Innovation'],
                title='Badge Categories for Top Performers',
                barmode='stack',
                labels={'value': 'Number of Badges', 'variable': 'Category'}
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Show current user's position
            if user['id'] in leaderboard_df['ID'].values:
                user_position = leaderboard_df.index[leaderboard_df['ID'] == user['id']].tolist()[0] + 1
                user_row = leaderboard_df[leaderboard_df['ID'] == user['id']]

                st.info(f"Your current position: **#{user_position}** with **{user_row['Total Badges'].values[0]}** badges")

            # Export option
            if st.button("Export Leaderboard Data"):
                export_to_csv(leaderboard_df.drop(columns=['ID', 'Current User']), "leaderboard_report.csv")
        else:
            st.info("No badge data available for the selected filters.")
    else:
        st.warning("No users found matching the selected criteria.")

elif report_type == "Custom Report":
    st.subheader("Custom Report Builder")

    # Report configuration
    st.write("### Configure Report")

    # Data selection
    data_source = st.selectbox(
        "Data Source",
        ["Badges", "Users", "Teams", "Sprints"]
    )

    # Define dimensions and metrics based on data source
    if data_source == "Badges":
        dimensions = ["Category", "Badge Name", "Recipient", "Team", "Role", "Date Awarded", "Badge Type"]
        metrics = ["Count", "Unique Recipients", "Team Distribution"]
    elif data_source == "Users":
        dimensions = ["Name", "Team", "Role"]
        metrics = ["Total Badges", "Work Badges", "Objective Badges", "Technical Badges", "Leadership Badges", 
                  "Teamwork Badges", "Innovation Badges"]
    elif data_source == "Teams":
        dimensions = ["Team Name", "Department"]
        metrics = ["Member Count", "Total Badges", "Avg Badges/Member", "Work Badges", "Objective Badges"]
    else:  # Sprints
        dimensions = ["Sprint Name", "Start Date", "End Date", "Duration"]
        metrics = ["Total Badges", "Work Badges", "Objective Badges", "Unique Recipients"]

    # Select dimensions and metrics
    selected_dimensions = st.multiselect("Dimensions", dimensions, default=[dimensions[0]])
    selected_metrics = st.multiselect("Metrics", metrics, default=[metrics[0]])

    if not selected_dimensions or not selected_metrics:
        st.warning("Please select at least one dimension and one metric.")
    else:
        # Generate report
        st.write("### Custom Report Results")

        # Prepare data based on selection
        if data_source == "Badges":
            report_data = []

            for award in filtered_awards:
                badge = get_badge_by_id(award['badge_id'])
                user = next((u for u in st.session_state.users if u['id'] == award['user_id']), None)
                team = get_team_by_id(user['team_id']) if user else None

                if badge and user and team:
                    item = {}

                    # Add selected dimensions
                    if "Category" in selected_dimensions:
                        item["Category"] = badge['category']
                    if "Badge Name" in selected_dimensions:
                        item["Badge Name"] = badge['name']
                    if "Recipient" in selected_dimensions:
                        item["Recipient"] = user['name']
                    if "Team" in selected_dimensions:
                        item["Team"] = team['name']
                    if "Role" in selected_dimensions:
                        item["Role"] = user['role']
                    if "Date Awarded" in selected_dimensions:
                        item["Date Awarded"] = award.get('award_date', 'N/A')
                    if "Badge Type" in selected_dimensions:
                        item["Badge Type"] = award.get('badge_type', 'work').capitalize()

                    report_data.append(item)

            if report_data:
                # Create DataFrame
                df = pd.DataFrame(report_data)

                # Add metrics (aggregates)
                result_df = df.groupby(selected_dimensions).size().reset_index(name='Count')

                if "Unique Recipients" in selected_metrics and "Recipient" in df.columns:
                    recipient_counts = df.groupby(selected_dimensions)['Recipient'].nunique().reset_index(name='Unique Recipients')
                    result_df = pd.merge(result_df, recipient_counts, on=selected_dimensions)

                if "Team Distribution" in selected_metrics and "Team" in df.columns:
                    # This is more complex - we'll just add team counts as new columns
                    team_names = df['Team'].unique()
                    for team_name in team_names:
                        team_counts = df[df['Team'] == team_name].groupby(selected_dimensions).size().reset_index(name=f"Team: {team_name}")
                        result_df = pd.merge(result_df, team_counts, on=selected_dimensions, how='left')
                        result_df[f"Team: {team_name}"] = result_df[f"Team: {team_name}"].fillna(0)

                # Display results
                st.dataframe(result_df, use_container_width=True)

                # Create visualization
                if len(selected_dimensions) == 1:
                    # Create bar chart for single dimension
                    fig = px.bar(
                        result_df.sort_values('Count', ascending=False),
                        x=selected_dimensions[0],
                        y='Count',
                        title=f'Badge Count by {selected_dimensions[0]}',
                        color=selected_dimensions[0] if len(result_df) <= 10 else None
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif len(selected_dimensions) == 2:
                    # Create heatmap for two dimensions
                    pivot_table = df.pivot_table(
                        index=selected_dimensions[0], 
                        columns=selected_dimensions[1], 
                        aggfunc='size', 
                        fill_value=0
                    )

                    fig = px.imshow(
                        pivot_table,
                        labels=dict(x=selected_dimensions[1], y=selected_dimensions[0], color="Count"),
                        title=f'Badge Distribution: {selected_dimensions[0]} vs {selected_dimensions[1]}'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Export option
                if st.button("Export Custom Report"):
                    export_to_csv(result_df, "custom_badge_report.csv")
            else:
                st.info("No badge data available for the selected filters.")

        elif data_source == "Users":
            report_data = []

            for user_item in st.session_state.users:
                # Filter by team if applicable
                if selected_team_id != "All Teams" and user_item['team_id'] != selected_team_id:
                    continue

                # Get user's awards
                user_awards = [a for a in filtered_awards if a['user_id'] == user_item['id']]

                item = {}

                # Add selected dimensions
                if "Name" in selected_dimensions:
                    item["Name"] = user_item['name']
                if "Team" in selected_dimensions:
                    item["Team"] = next((t['name'] for t in teams if t['id'] == user_item['team_id']), 'Unknown')
                if "Role" in selected_dimensions:
                    item["Role"] = user_item['role']

                # Add selected metrics
                if "Total Badges" in selected_metrics:
                    item["Total Badges"] = len(user_awards)
                if "Work Badges" in selected_metrics:
                    item["Work Badges"] = sum(1 for a in user_awards if a.get('badge_type') == 'work')
                if "Objective Badges" in selected_metrics:
                    item["Objective Badges"] = sum(1 for a in user_awards if a.get('badge_type') == 'objective')

                # Badge categories
                if "Technical Badges" in selected_metrics:
                    item["Technical Badges"] = sum(1 for a in user_awards if 
                                               get_badge_by_id(a['badge_id']).get('category') == 'Technical')
                if "Leadership Badges" in selected_metrics:
                    item["Leadership Badges"] = sum(1 for a in user_awards if 
                                               get_badge_by_id(a['badge_id']).get('category') == 'Leadership')
                if "Teamwork Badges" in selected_metrics:
                    item["Teamwork Badges"] = sum(1 for a in user_awards if 
                                              get_badge_by_id(a['badge_id']).get('category') == 'Teamwork')
                if "Innovation Badges" in selected_metrics:
                    item["Innovation Badges"] = sum(1 for a in user_awards if 
                                               get_badge_by_id(a['badge_id']).get('category') == 'Innovation')

                report_data.append(item)

            if report_data:
                # Create DataFrame
                df = pd.DataFrame(report_data)

                # Display results
                st.dataframe(df, use_container_width=True)

                # Create visualization
                if len(selected_metrics) == 1 and len(selected_dimensions) == 1:
                    # Simple bar chart
                    fig = px.bar(
                        df.sort_values(selected_metrics[0], ascending=False),
                        x=selected_dimensions[0],
                        y=selected_metrics[0],
                        title=f'{selected_metrics[0]} by {selected_dimensions[0]}',
                        color=selected_dimensions[0] if len(df) <= 10 else None
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif len(selected_metrics) > 1 and "Name" in selected_dimensions:
                    # Multi-metric comparison for users
                    top_users = df.sort_values("Total Badges" if "Total Badges" in df.columns else selected_metrics[0], 
                                             ascending=False).head(10)

                    fig = px.bar(
                        top_users,
                        x='Name',
                        y=selected_metrics,
                        title='Badge Metrics for Top Users',
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Export option
                if st.button("Export User Report"):
                    export_to_csv(df, "custom_user_report.csv")
            else:
                st.info("No user data available for the selected filters.")

        elif data_source == "Teams":
            report_data = []

            for team in teams:
                # Get team members
                team_members = [u['id'] for u in st.session_state.users if u['team_id'] == team['id']]

                # Get team awards
                team_awards = [a for a in filtered_awards if a['user_id'] in team_members]

                item = {}

                # Add selected dimensions
                if "Team Name" in selected_dimensions:
                    item["Team Name"] = team['name']
                if "Department" in selected_dimensions:
                    item["Department"] = team.get('department', 'N/A')

                # Add selected metrics
                if "Member Count" in selected_metrics:
                    item["Member Count"] = len(team_members)
                if "Total Badges" in selected_metrics:
                    item["Total Badges"] = len(team_awards)
                if "Avg Badges/Member" in selected_metrics:
                    item["Avg Badges/Member"] = round(len(team_awards) / len(team_members), 2) if team_members else 0
                if "Work Badges" in selected_metrics:
                    item["Work Badges"] = sum(1 for a in team_awards if a.get('badge_type') == 'work')
                if "Objective Badges" in selected_metrics:
                    item["Objective Badges"] = sum(1 for a in team_awards if a.get('badge_type') == 'objective')

                report_data.append(item)

            if report_data:
                # Create DataFrame
                df = pd.DataFrame(report_data)

                # Display results
                st.dataframe(df, use_container_width=True)

                # Create visualization
                if "Total Badges" in selected_metrics:
                    # Bar chart for total badges by team
                    fig = px.bar(
                        df.sort_values("Total Badges", ascending=False),
                        x="Team Name",
                        y="Total Badges",
                        title='Total Badges by Team',
                        color="Team Name" if len(df) <= 10 else None
                    )
                    st.plotly_chart(fig, use_container_width=True)

                if "Work Badges" in selected_metrics and "Objective Badges" in selected_metrics:
                    # Stacked bar for work vs objective
                    fig = px.bar(
                        df,
                        x="Team Name",
                        y=["Work Badges", "Objective Badges"],
                        title='Work vs Objective Badges by Team',
                        barmode='stack'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Export option
                if st.button("Export Team Report"):
                    export_to_csv(df, "custom_team_report.csv")
            else:
                st.info("No team data available for the selected filters.")

        else:  # Sprints
            report_data = []

            for sprint in st.session_state.sprints:
                # Filter by date range
                if not (start_date_str <= sprint.get('end_date', '2100-01-01') <= end_date_str):
                    continue

                # Get awards for this sprint
                sprint_awards = [a for a in all_awards if a.get('sprint_id') == sprint['id']]

                item = {}

                # Add selected dimensions
                if "Sprint Name" in selected_dimensions:
                    item["Sprint Name"] = sprint['name']
                if "Start Date" in selected_dimensions:
                    item["Start Date"] = sprint.get('start_date', 'N/A')
                if "End Date" in selected_dimensions:
                    item["End Date"] = sprint.get('end_date', 'N/A')
                if "Duration" in selected_dimensions:
                    try:
                        start_date = datetime.strptime(sprint.get('start_date', '2100-01-01'), "%Y-%m-%d")
                        end_date = datetime.strptime(sprint.get('end_date', '2100-01-01'), "%Y-%m-%d")
                        item["Duration"] = f"{(end_date - start_date).days + 1} days"
                    except:
                        item["Duration"] = "N/A"

                # Add selected metrics
                if "Total Badges" in selected_metrics:
                    item["Total Badges"] = len(sprint_awards)
                if "Work Badges" in selected_metrics:
                    item["Work Badges"] = sum(1 for a in sprint_awards if a.get('badge_type') == 'work')
                if "Objective Badges" in selected_metrics:
                    item["Objective Badges"] = sum(1 for a in sprint_awards if a.get('badge_type') == 'objective')
                if "Unique Recipients" in selected_metrics:
                    item["Unique Recipients"] = len(set(a['user_id'] for a in sprint_awards))

                report_data.append(item)

            if report_data:
                # Create DataFrame
                df = pd.DataFrame(report_data)

                # Sort by start date
                if "Start Date" in df.columns:
                    df["Start Date Obj"] = pd.to_datetime(df["Start Date"], errors='coerce')
                    df = df.sort_values("Start Date Obj")
                    df = df.drop(columns=["Start Date Obj"])

                # Display results
                st.dataframe(df, use_container_width=True)

                # Create visualization
                if "Total Badges" in selected_metrics:
                    # Line chart for badges over sprints
                    fig = px.line(
                        df,
                        x="Sprint Name",
                        y="Total Badges",
                        title='Total Badges by Sprint',
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)

                if "Work Badges" in selected_metrics and "Objective Badges" in selected_metrics:
                    # Stacked bar for work vs objective
                    fig = px.bar(
                        df,
                        x="Sprint Name",
                        y=["Work Badges", "Objective Badges"],
                        title='Work vs Objective Badges by Sprint',
                        barmode='stack'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Export option
                if st.button("Export Sprint Report"):
                    export_to_csv(df, "custom_sprint_report.csv")
            else:
                st.info("No sprint data available for the selected filters.")

