import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Default configuration for Windows Authentication
    DATABASE_URL = (
        "mssql+pyodbc://@DXBSHINAZ/dbGamification?"
        "driver=ODBC+Driver+17+for+SQL+Server&"
        "trusted_connection=yes"
    )
    print("Using SQL Server with Windows Authentication")

# SQL Server specific settings
ENGINE_CONFIG = {
    "pool_pre_ping": True,
    "connect_args": {
        "connect_timeout": 10,
        "autocommit": False
    },
    "echo_pool": "debug" if os.getenv('DEBUG') else False
}

def get_engine():
    """Create database engine with retry logic"""
    for attempt in range(3):
        try:
            return create_engine(DATABASE_URL, **ENGINE_CONFIG)
        except Exception as e:
            print(f"Connection attempt {attempt+1} failed: {str(e)}")

# Create engine and base class
engine = get_engine()
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Database Models
class User(Base):
    """User model with team association"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)  # Using UUID strings
    name = Column(String(255), nullable=False) 
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100))
    role = Column(String(50), nullable=False, default='Developer')
    team_id = Column(String(36), ForeignKey('teams.id'))
    is_lead = Column(Boolean, default=False)
    
    # Relationships
    team = relationship('Team', back_populates='members')
    badges = relationship('BadgeAward', back_populates='user', foreign_keys='BadgeAward.user_id')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Team(Base):
    """Team structure model"""
    __tablename__ = 'teams'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    department = Column(String(50))
    
    members = relationship('User', back_populates='team')
    sprints = relationship('Sprint', back_populates='team')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Badge(Base):
    """Badge definition model"""
    __tablename__ = 'badges'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    criteria = Column(Text)
    valid_roles = Column(Text)  # JSON stored as string
    validity_days = Column(Integer)
    
    awards = relationship('BadgeAward', back_populates='badge')

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['valid_roles'] = json.loads(self.valid_roles) if self.valid_roles else []
        return data

class BadgeAward(Base):
    """Badge award tracking model"""
    __tablename__ = 'badge_awards'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    badge_id = Column(String(36), ForeignKey('badges.id'), nullable=False)
    awarded_at = Column(Date, default=datetime.utcnow)
    awarded_by = Column(String(36), ForeignKey('users.id'))
    
    # Explicit foreign key specifications
    user = relationship('User', 
                       back_populates='badges',
                       foreign_keys=[user_id])
    badge = relationship('Badge', back_populates='awards')
    awarded_by_user = relationship('User', 
                                  foreign_keys=[awarded_by])

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Sprint(Base):
    """Sprint management model"""
    __tablename__ = 'sprints'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    team_id = Column(String(36), ForeignKey('teams.id'))
    goals = Column(Text)  # JSON stored as string
    
    team = relationship('Team', back_populates='sprints')

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['goals'] = json.loads(self.goals) if self.goals else []
        return data

# Database Operations
class DatabaseManager:
    """Handles database operations with retry logic"""
    
    def __init__(self):
        self.session = Session()
        
    def __enter__(self):
        return self.session
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        except Exception as e:
            print(f"Commit failed: {str(e)}")
            self.session.rollback()
        finally:
            self.session.close()

    @staticmethod
    def get_all(model):
        """Retrieve all records of a model"""
        with DatabaseManager() as session:
            return [item.to_dict() for item in session.query(model).all()]
    
    @staticmethod
    def get_by_id(model, item_id):
        """Get single record by ID"""
        with DatabaseManager() as session:
            item = session.query(model).get(item_id)
            return item.to_dict() if item else None
    
    @staticmethod
    def create(model, data):
        """Create new record"""
        with DatabaseManager() as session:
            item = model(**data)
            session.add(item)
            session.flush()
            return item.to_dict()
    
    @staticmethod
    def update(model, item_id, update_data):
        """Update existing record"""
        with DatabaseManager() as session:
            item = session.query(model).get(item_id)
            if not item:
                return None
            for key, value in update_data.items():
                setattr(item, key, value)
            return item.to_dict()
    
    @staticmethod
    def delete(model, item_id):
        """Delete record"""
        with DatabaseManager() as session:
            item = session.query(model).get(item_id)
            if item:
                session.delete(item)
                return True
            return False
        
    @staticmethod
    def get_user_by_username(username):
        """Get user by username with proper session handling"""
        try:
            session = Session()
            user = session.query(User).filter(User.username == username).first()
            return user.to_dict() if user else None
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None
        finally:
            session.close()

# Business Logic Helpers
class GamificationQueries:
    """Domain-specific query operations"""
    
    @staticmethod
    def get_team_members(team_id):
        """Get all members of a team"""
        with DatabaseManager() as session:
            return [
                user.to_dict()
                for user in session.query(User)
                .filter(User.team_id == team_id)
                .all()
            ]
    
    @staticmethod
    def get_active_sprints(team_id=None):
        """Get currently active sprints"""
        today = datetime.today().date()
        with DatabaseManager() as session:
            query = session.query(Sprint).filter(
                Sprint.start_date <= today,
                Sprint.end_date >= today
            )
            if team_id:
                query = query.filter(Sprint.team_id == team_id)
            return [sprint.to_dict() for sprint in query.all()]

    
    @staticmethod
    def get_user_badges(user_id):
        """Get all badges awarded to a user"""
        with DatabaseManager() as session:
            return [
                award.to_dict()
                for award in session.query(BadgeAward)
                .filter(BadgeAward.user_id == user_id)
                .all()
            ]

# Initialization
def initialize_database():
    try:
        Base.metadata.create_all(engine)
        print("Database schema initialized")
    except Exception as e:
        print(f"Failed to create tables: {e}")

initialize_database()