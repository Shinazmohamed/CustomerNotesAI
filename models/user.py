from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db_base import Base
import hashlib

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100))
    role = Column(String(50), default='Developer', nullable=False)
    team_id = Column(String(36), ForeignKey('teams.id'))
    is_lead = Column(Boolean, default=False)

    team = relationship('Team', back_populates='members')
    badges = relationship('BadgeAward', back_populates='user', foreign_keys='BadgeAward.user_id')

    # Optional runtime-only fields
    next_badge_progress = 0
    team_rank = "N/A"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def has_permission(self, feature):
        access_rules = {
            'award_badges': ['TL', 'Manager'],
            'create_badges': ['TL', 'Manager'],
            'edit_teams': ['TL', 'Manager'],
            'create_sprints': ['TL', 'Manager'],
            'view_reports': ['TL', 'Manager', 'Dev', 'QA', 'RMO'],
            'export_data': ['TL', 'Manager']
        }
        return self.role in access_rules.get(feature, [])

    def update_user(self, name=None, username=None, password=None, email=None, role=None, team_id=None, is_lead=None):
        if name: self.name = name
        if username: self.username = username
        if password: self.password = self.hash_password(password)
        if email: self.email = email
        if role: self.role = role
        if team_id: self.team_id = team_id
        if is_lead is not None: self.is_lead = is_lead
