import streamlit as st
import pandas as pd
import plotly.express as px
from auth import is_authenticated, get_current_user
from utils import get_team_members, get_user_badges, calculate_team_stats

# Page config
st.set_page_config(page_title="Dashboard - IT Team Gamification", page_icon="🏆", layout="wide")

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

user = get_current_user()

if user['role'] != 'Manager':
    st.error("You do not have permission to view this page.")
    st.stop()

st.title("🏆 Dashboard")
st.write(f"Welcome, **{user['name']}**! Here is an overview of all teams and members.")

# Get all teams from session state
teams = st.session_state.teams if 'teams' in st.session_state else []

if not teams:
    st.info("No teams found in the system.")
    st.stop()

# Team selection
team_options = [{'label': t['name'], 'value': t['id']} for t in teams]
selected_team_id = st.selectbox(
    "Select a Team to View",
    options=[t['id'] for t in teams],
    format_func=lambda x: next((t['name'] for t in teams if t['id'] == x), x)
)

selected_team = next((t for t in teams if t['id'] == selected_team_id), None)

if selected_team:
    st.header(f"Team: {selected_team['name']}")
    team_stats = calculate_team_stats(selected_team['id'])
    st.write(f"**Total Badges:** {team_stats['total_badges']} &nbsp;&nbsp; **Avg Badges/Member:** {team_stats['avg_badges']} &nbsp;&nbsp; **Top Performer:** {team_stats['top_performer']}")

    # Team members and their badges
    members = get_team_members(selected_team['id'])
    if not members:
        st.info("No members found in this team.")
    else:
        member_data = []
        for m in members:
            badges = get_user_badges(m['id'])
            member_data.append({
                "Name": m['name'],
                "Role": m['role'],
                "Badges": len(badges)
            })
        df = pd.DataFrame(member_data)
        st.dataframe(df, use_container_width=True)

        # Team leaderboard
        if not df.empty:
            fig = px.bar(df, x='Name', y='Badges', color='Badges', title=f"{selected_team['name']} Leaderboard")
            st.plotly_chart(fig, use_container_width=True)

# Organization-wide stats
st.header("Organization Overview")
org_stats = {
    "Total Teams": len(teams),
    "Total Members": sum(len(get_team_members(t['id'])) for t in teams),
    "Total Badges Awarded": sum(calculate_team_stats(t['id'])['total_badges'] for t in teams)
}
col1, col2, col3 = st.columns(3)
col1.metric("Total Teams", org_stats["Total Teams"])
col2.metric("Total Members", org_stats["Total Members"])
col3.metric("Total Badges Awarded", org_stats["Total Badges Awarded"])

st.info("For more analytics, visit the Reports page or use the Award Badges and Badge Management pages.")


# --- Team Comparison Table and Visualization ---
st.header("Team Comparison Overview")

# Gather stats for all teams
comparison_data = []
for t in teams:
    stats = calculate_team_stats(t['id'])
    comparison_data.append({
        "Team": t['name'],
        "Total Badges": stats['total_badges'],
        "Avg Badges/Member": stats['avg_badges'],
        "Recent Badges (30d)": stats.get('recent_badges', 0),
        "Members": stats['member_count'],
        "Top Performer": stats['top_performer']
    })
comparison_df = pd.DataFrame(comparison_data)

# Show comparison table
st.dataframe(comparison_df, use_container_width=True)

# Visualization: Grouped Bar Chart for Key Metrics
if not comparison_df.empty:
    metrics_to_plot = ["Total Badges", "Avg Badges/Member", "Recent Badges (30d)"]
    fig = px.bar(
        comparison_df.melt(id_vars=["Team"], value_vars=metrics_to_plot),
        x="Team",
        y="value",
        color="variable",
        barmode="group",
        title="Team Metrics Comparison",
        labels={"value": "Metric Value", "variable": "Metric"}
    )
    st.plotly_chart(fig, use_container_width=True)


# --- Sprint/Year/Category Filters ---
st.header("Sprint & Year Badge Analysis")

# Collect all badge awards for all teams
all_badge_awards = []
for t in teams:
    members = get_team_members(t['id'])
    for m in members:
        badges = get_user_badges(m['id'])
        for b in badges:
            all_badge_awards.append({
                "Team": t['name'],
                "TeamID": t['id'],
                "Member": m['name'],
                "Badge": b['name'],
                "Category": b.get('category', 'Other'),
                "Awarded At": b.get('awarded_at'),
                "Sprint": b.get('sprint', None)  # If you have sprint info
            })

awards_df = pd.DataFrame(all_badge_awards)
if not awards_df.empty:
    # Extract year and sprint if available
    awards_df['Year'] = pd.to_datetime(awards_df['Awarded At']).dt.year
    if 'Sprint' not in awards_df or awards_df['Sprint'].isnull().all():
        # If no sprint info, create a placeholder (e.g., by month)
        awards_df['Sprint'] = pd.to_datetime(awards_df['Awarded At']).dt.strftime('M%Y-%m')
    
    years = sorted(awards_df['Year'].dropna().unique())
    sprints = ['All'] + sorted(awards_df['Sprint'].dropna().unique())
    categories = ['All'] + sorted(awards_df['Category'].dropna().unique())

    # Filters
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        selected_year = st.selectbox("Select Year", years, index=len(years)-1 if years else 0)
    with colf2:
        selected_sprint = st.selectbox("Select Sprint", sprints)
    with colf3:
        selected_category = st.selectbox("Select Category", categories)

    # Filter data
    filtered_df = awards_df[awards_df['Year'] == selected_year]
    if selected_sprint != 'All':
        filtered_df = filtered_df[filtered_df['Sprint'] == selected_sprint]
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]

    # Group by team and show badge counts
    team_sprint_counts = filtered_df.groupby('Team').size().reset_index(name='Badge Count')
    st.subheader(f"Badges Awarded per Team (Sprint: {selected_sprint}, Year: {selected_year})")
    st.dataframe(team_sprint_counts, use_container_width=True)

    # Chart: Stacked bar for all teams across sprints in the year
    pivot = awards_df[awards_df['Year'] == selected_year]
    if selected_category != 'All':
        pivot = pivot[pivot['Category'] == selected_category]
    if selected_sprint != 'All':
        pivot = pivot[pivot['Sprint'] == selected_sprint]
    fig = px.bar(
        pivot.groupby(['Sprint', 'Team']).size().reset_index(name='Badge Count'),
        x='Sprint',
        y='Badge Count',
        color='Team',
        barmode='group',
        title=f"Team Badges per Sprint ({selected_year})"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No badge award data available for the selected filters.")