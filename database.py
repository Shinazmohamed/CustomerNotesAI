# database.py
import os
import pyodbc  # Ensure pyodbc is imported if using raw DB connections elsewhere
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_base import Base  # Import Base from db_base module
from models.team import Team
from models.user import User
from models.badge import Badge
from models.sprint import Sprint
from models.badge_award import BadgeAward
# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = (
        "mssql+pyodbc://@DXBSHINAZ/dbGamification?"
        "driver=ODBC+Driver+17+for+SQL+Server&"
        "trusted_connection=yes"
    )
    print("Using SQL Server with Windows Authentication")

ENGINE_CONFIG = {
    "pool_pre_ping": True,
    "connect_args": {
        "connect_timeout": 10,
        "autocommit": False
    },
    "echo_pool": "debug" if os.getenv('DEBUG') else False
}

def get_engine():
    for attempt in range(3):
        try:
            return create_engine(DATABASE_URL, **ENGINE_CONFIG)
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {str(e)}")
    raise ConnectionError("Failed to connect to database after 3 attempts.")
    
def get_database_connection():
    """
    Establishes a connection to the MS SQL Server and returns the connection object.
    """
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=DXBSHINAZ;"
        "Database=dbGamification;"
        "Trusted_Connection=yes;"
    )
    return conn

engine = get_engine()
Session = sessionmaker(bind=engine)

# Initialization
def initialize_database():
    try:
        Base.metadata.create_all(engine)
        print("Database schema initialized")
    except Exception as e:
        print(f"Failed to create tables: {e}")

initialize_database()
