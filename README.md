# IT Team Gamification Platform

A Streamlit-based platform for tracking achievements, awarding badges, and motivating IT staff through gamification.

## Features
- Track personal and team achievements
- Award and receive badges based on accomplishments
- Monitor progress towards objectives
- View team and individual performance metrics
- Track sprint-based achievements
- Separate tracking for regular work (80%) and objectives (20%)

## Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- pyodbc (for SQL Server)


## Installation Steps

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-directory>
```

2. Install the required packages:
```bash
pip install pandas plotly pyodbc sqlalchemy streamlit
```

3. Start the application:
```bash
streamlit run app.py --server.port 5000
```

The application will be available at `http://0.0.0.0:5000`

## Project Structure
- `app.py`: Main application file
- `auth.py`: Authentication logic
- `database.py`: Database operations
- `utils.py`: Utility functions
- `models/`: Data models
- `pages/`: Streamlit pages for different sections
- `data/`: Sample data and data loading scripts

## Database Setup

### Option 1: SQL Server (Default)
The application is configured to use SQL Server. To set up:

1. Click the "Secrets" tool in the Tools panel
2. Add a new secret named DATABASE_URL with your SQL Server connection string:
   ```
   mssql+pyodbc://<username>:<password>@<server>/<database>?driver=ODBC+Driver+17+for+SQL+Server
   ```
3. The application will automatically use the SQL Server connection

### Option 2: PostgreSQL
To use PostgreSQL, you will need to set the `DATABASE_URL` environment variable accordingly.  Details on how to set up PostgreSQL are available in the previous documentation.  You will also need to remove pyodbc from the requirements.

Note: Make sure your SQL Server instance is accessible from Replit and has the appropriate firewall rules configured.


## Initial Setup
The application automatically initializes with sample data for:
- Teams
- Users
- Badges
- Sprints
- Badge Awards

Default login credentials:
- Username: johnsmith
- Password: password123