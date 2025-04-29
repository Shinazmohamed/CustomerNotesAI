import streamlit as st
import pandas as pd
import plotly.express as px
from auth import is_authenticated, get_current_user, user_has_access
from utils import get_team_members, get_user_badges, calculate_team_stats

# Page config
st.set_page_config(page_title="Manager Dashboard - IT Team Gamification", page_icon="🏆", layout="wide")

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

user = get_current_user()

if user['role'] != 'Manager':
    st.error("You do not have permission to view this page.")
    st.stop()

st.title("🏆 Manager Dashboard")
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