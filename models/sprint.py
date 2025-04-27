import json
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db_base import Base

class Sprint(Base):
    __tablename__ = 'sprints'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    team_id = Column(String(36), ForeignKey('teams.id'))
    goals = Column(JSON, default=list)  # Use real JSON
    status = Column(String(25), default='upcoming')

    team = relationship('Team', back_populates='sprints')

    def __init__(self, id, name, start_date, end_date, team_id=None,
                 description=None, goals=None, status="upcoming"):
        self.id = id
        self.name = name
        self.start_date = self._parse_date(start_date)
        self.end_date = self._parse_date(end_date)
        self.team_id = team_id
        self.description = description or ""
        self.goals = goals or []
        self.status = status

    @staticmethod
    def _parse_date(value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'team_id': self.team_id,
            'goals': self.goals,  # No need to load/dump
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            team_id=data.get('team_id'),
            description=data.get('description'),
            goals=data.get('goals', []),
            status=data.get('status', 'upcoming')
        )

    def is_active(self):
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == 'active'

    def get_days_remaining(self):
        if self.status == 'completed':
            return -1
        if not self.end_date:
            return 0
        days_remaining = (self.end_date - date.today()).days + 1
        return max(0, days_remaining)

    def __repr__(self):
        return f"<Sprint(name='{self.name}', status='{self.status}')>"

