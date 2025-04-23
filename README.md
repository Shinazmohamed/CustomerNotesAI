
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
