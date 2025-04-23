
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

## Installation Steps

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-directory>
```

2. Install the required packages:
```bash
pip install pandas plotly psycopg2-binary sqlalchemy streamlit
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

### Option 1: PostgreSQL (Default)
The application is configured to use PostgreSQL by default. To use PostgreSQL:

1. Click the "Database" tab in Replit
2. Click "Create a database" 
3. The DATABASE_URL environment variable will be automatically configured

### Option 2: SQL Server
To use SQL Server, modify the DATABASE_URL environment variable in Replit:

1. Click the "Secrets" tool in the Tools panel
2. Add a new secret named DATABASE_URL with your SQL Server connection string:
   ```
   mssql+pyodbc://<username>:<password>@<server>/<database>?driver=ODBC+Driver+17+for+SQL+Server
   ```
3. Install the required SQL Server dependencies:
   ```bash
   pip install pyodbc
   ```

Note: Make sure your SQL Server instance is accessible from Replit and has the appropriate firewall rules configured.

## Database Setup

### Option 1: PostgreSQL (Default)
The application is configured to use PostgreSQL by default. To use PostgreSQL:

1. Click the "Database" tab in Replit
2. Click "Create a database" 
3. The DATABASE_URL environment variable will be automatically configured

### Option 2: SQL Server
To use SQL Server, modify the DATABASE_URL environment variable in Replit:

1. Click the "Secrets" tool in the Tools panel
2. Add a new secret named DATABASE_URL with your SQL Server connection string:
   ```
   mssql+pyodbc://<username>:<password>@<server>/<database>?driver=ODBC+Driver+17+for+SQL+Server
   ```
3. Install the required SQL Server dependencies:
   ```bash
   pip install pyodbc
   ```

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
