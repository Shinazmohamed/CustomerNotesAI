"""
Database module for the IT Team Gamification Platform.
Uses SQLAlchemy to interact with a PostgreSQL database.
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Text, ForeignKey, Date, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create engine and session
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///gamification.db"
    print("Using SQLite database instead of PostgreSQL")

# Add retry logic for database connections
def get_engine():
    """Get database engine with retry logic."""
    for i in range(3):  # Try 3 times
        try:
            return create_engine(DATABASE_URL)
        except Exception as e:
            print(f"Database connection attempt {i+1} failed: {str(e)}")
            if i == 2:  # Last attempt
                print("Using in-memory SQLite as fallback")
                return create_engine("sqlite:///:memory:")

engine = get_engine()
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    """User table schema."""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String)
    role = Column(String, nullable=False)
    team_id = Column(String, ForeignKey('teams.id'))
    is_lead = Column(Boolean, default=False)
    
    # Relationships
    team = relationship('Team', back_populates='members')
    badge_awards = relationship('BadgeAward', back_populates='user')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'role': self.role,
            'team_id': self.team_id,
            'is_lead': self.is_lead
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            role=data.get('role', 'Dev'),
            team_id=data.get('team_id'),
            is_lead=data.get('is_lead', False)
        )

class Team(Base):
    """Team table schema."""
    __tablename__ = 'teams'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    department = Column(String)
    
    # Relationships
    members = relationship('User', back_populates='team')
    sprints = relationship('Sprint', back_populates='team')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department': self.department
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            department=data.get('department')
        )

class Badge(Base):
    """Badge table schema."""
    __tablename__ = 'badges'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    how_to_achieve = Column(Text)
    eligible_roles = Column(Text)  # JSON list stored as text
    expected_time_days = Column(Integer)
    validity = Column(String)
    badge_type = Column(String)
    
    # Relationships
    awards = relationship('BadgeAward', back_populates='badge')
    
    def to_dict(self):
        """Convert to dictionary."""
        roles = json.loads(self.eligible_roles) if self.eligible_roles else []
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'how_to_achieve': self.how_to_achieve,
            'eligible_roles': roles,
            'expected_time_days': self.expected_time_days,
            'validity': self.validity,
            'badge_type': self.badge_type
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        roles = json.dumps(data.get('eligible_roles', [])) if data.get('eligible_roles') else None
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            how_to_achieve=data.get('how_to_achieve'),
            eligible_roles=roles,
            expected_time_days=data.get('expected_time_days', 30),
            validity=data.get('validity', 'Permanent'),
            badge_type=data.get('badge_type', 'work')
        )

class BadgeAward(Base):
    """BadgeAward table schema."""
    __tablename__ = 'badge_awards'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    badge_id = Column(String, ForeignKey('badges.id'), nullable=False)
    awarded_by = Column(String, nullable=False)
    award_date = Column(String, nullable=False)  # YYYY-MM-DD
    reason = Column(Text)
    badge_type = Column(String)
    sprint_id = Column(String, ForeignKey('sprints.id'))
    
    # Relationships
    user = relationship('User', back_populates='badge_awards')
    badge = relationship('Badge', back_populates='awards')
    sprint = relationship('Sprint', back_populates='badge_awards')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'awarded_by': self.awarded_by,
            'award_date': self.award_date,
            'reason': self.reason,
            'badge_type': self.badge_type,
            'sprint_id': self.sprint_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            badge_id=data.get('badge_id'),
            awarded_by=data.get('awarded_by'),
            award_date=data.get('award_date'),
            reason=data.get('reason'),
            badge_type=data.get('badge_type', 'work'),
            sprint_id=data.get('sprint_id')
        )

class Sprint(Base):
    """Sprint table schema."""
    __tablename__ = 'sprints'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    start_date = Column(String, nullable=False)  # YYYY-MM-DD
    end_date = Column(String, nullable=False)  # YYYY-MM-DD
    team_id = Column(String, ForeignKey('teams.id'))
    goals = Column(Text)  # JSON list stored as text
    status = Column(String)
    
    # Relationships
    team = relationship('Team', back_populates='sprints')
    badge_awards = relationship('BadgeAward', back_populates='sprint')
    
    def to_dict(self):
        """Convert to dictionary."""
        goals = json.loads(self.goals) if self.goals else []
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'team_id': self.team_id,
            'goals': goals,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        goals = json.dumps(data.get('goals', [])) if data.get('goals') else None
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            team_id=data.get('team_id'),
            goals=goals,
            status=data.get('status', 'upcoming')
        )

def init_db():
    """Initialize the database."""
    try:
        # Create tables
        Base.metadata.create_all(engine)
        
        # Check if we need to initialize with sample data
        session = get_session()
        user_count = session.query(User).count()
        session.close()
        
        if user_count == 0:
            print("Initializing database with sample data...")
            from data.sample_data import load_sample_data
            try:
                load_sample_data()
            except Exception as e:
                print(f"Error loading sample data: {str(e)}")
                # Create minimal sample data if sample data module fails
                create_minimal_sample_data()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        # Continue anyway - tables might already exist

def create_minimal_sample_data():
    """Create minimal sample data for the application to function."""
    try:
        session = get_session()
        
        # Create Blue Team
        blue_team = Team(
            id="team_001",
            name="Blue Team",
            description="Frontend development team",
            department="Engineering"
        )
        session.add(blue_team)
        
        # Create Manager user
        manager = User(
            id="user_001",
            name="John Smith",
            username="johnsmith",
            password="password123",
            email="john@example.com",
            role="Manager",
            team_id="team_001",
            is_lead=True
        )
        session.add(manager)
        
        # Create Technical Badge
        tech_badge = Badge(
            id="badge_001",
            name="Technical Excellence",
            description="Demonstrates exceptional technical skills",
            category="Technical",
            how_to_achieve="Complete a complex technical task with high quality",
            eligible_roles=json.dumps(["Dev", "QA", "RMO", "TL"]),
            expected_time_days=14,
            validity="Permanent",
            badge_type="work"
        )
        session.add(tech_badge)
        
        # Create a Sprint
        sprint = Sprint(
            id="sprint_001",
            name="Sprint 1",
            description="First sprint of the project",
            start_date="2025-04-01",
            end_date="2025-04-21",
            team_id="team_001",
            goals=json.dumps(["Complete frontend redesign", "Fix critical bugs"]),
            status="active"
        )
        session.add(sprint)
        
        session.commit()
        print("Created minimal sample data")
    except Exception as e:
        session.rollback()
        print(f"Error creating minimal sample data: {str(e)}")
    finally:
        session.close()

def get_session():
    """Get a database session with retry logic."""
    for i in range(3):  # Try 3 times
        try:
            return Session()
        except Exception as e:
            print(f"Session creation attempt {i+1} failed: {str(e)}")
            if i == 2:  # Last attempt
                print("Creating session with SQLite as fallback")
                # Create an in-memory SQLite engine as fallback
                fallback_engine = create_engine("sqlite:///:memory:")
                Base.metadata.create_all(fallback_engine)
                FallbackSession = sessionmaker(bind=fallback_engine)
                return FallbackSession()

# Database operation functions
def get_all(model_class):
    """Get all records of a model."""
    session = get_session()
    try:
        return [item.to_dict() for item in session.query(model_class).all()]
    finally:
        session.close()

def get_by_id(model_class, item_id):
    """Get a record by ID."""
    session = get_session()
    try:
        item = session.query(model_class).filter(model_class.id == item_id).first()
        return item.to_dict() if item else None
    finally:
        session.close()

def create(model_class, data):
    """Create a new record."""
    session = get_session()
    try:
        item = model_class.from_dict(data)
        session.add(item)
        session.commit()
        return item.to_dict()
    finally:
        session.close()

def update(model_class, item_id, data):
    """Update a record."""
    session = get_session()
    try:
        item = session.query(model_class).filter(model_class.id == item_id).first()
        if not item:
            return None
        
        for key, value in data.items():
            if hasattr(item, key):
                # Special handling for JSON fields
                if key in ['eligible_roles', 'goals'] and value is not None:
                    setattr(item, key, json.dumps(value))
                else:
                    setattr(item, key, value)
        
        session.commit()
        return item.to_dict()
    finally:
        session.close()

def delete(model_class, item_id):
    """Delete a record."""
    session = get_session()
    try:
        item = session.query(model_class).filter(model_class.id == item_id).first()
        if not item:
            return False
        
        session.delete(item)
        session.commit()
        return True
    finally:
        session.close()

def query_by_field(model_class, field_name, field_value):
    """Query records by a specific field."""
    session = get_session()
    try:
        items = session.query(model_class).filter(getattr(model_class, field_name) == field_value).all()
        return [item.to_dict() for item in items]
    finally:
        session.close()

# Model-specific functions
def get_user_by_username(username):
    """Get a user by username."""
    session = get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user.to_dict() if user else None
    finally:
        session.close()

def get_team_members(team_id):
    """Get all members of a team."""
    return query_by_field(User, 'team_id', team_id)

def get_user_badges(user_id):
    """Get all badges for a user."""
    session = get_session()
    try:
        awards = session.query(BadgeAward).filter(BadgeAward.user_id == user_id).all()
        return [award.to_dict() for award in awards]
    finally:
        session.close()

def get_active_sprints():
    """Get all active sprints."""
    session = get_session()
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        sprints = session.query(Sprint).filter(
            Sprint.start_date <= today,
            Sprint.end_date >= today
        ).all()
        return [sprint.to_dict() for sprint in sprints]
    finally:
        session.close()

# Initialize database tables if they don't exist
init_db()