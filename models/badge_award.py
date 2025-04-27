from datetime import date, datetime
from sqlalchemy import Column, String, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class BadgeAward(Base):
    __tablename__ = 'badge_awards'
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    badge_id = Column(String(36), ForeignKey('badges.id'), nullable=False)
    awarded_at = Column(Date, default=lambda: datetime.utcnow().date())
    awarded_by = Column(String(36), ForeignKey('users.id'))
    reason = Column(Text)
    sprint_id = Column(String(36), ForeignKey('sprints.id'))
    recent = Column(Boolean, default=True)

    # Relationships
    user = relationship('User', back_populates='badges', foreign_keys=[user_id])
    badge = relationship('Badge', back_populates='awards')
    awarded_by_user = relationship('User', foreign_keys=[awarded_by])
    sprint = relationship('Sprint', backref='awards')

    def __init__(self, id, user_id, badge_id, awarded_by,
                 awarded_at=None, reason=None, sprint_id=None):
        if not user_id or not badge_id:
            raise ValueError("Both user_id and badge_id must be provided.")
        
        self.id = id
        self.user_id = user_id
        self.badge_id = badge_id
        self.awarded_by = awarded_by
        self.awarded_at = awarded_at if isinstance(awarded_at, (datetime, date)) else date.today()
        self.reason = reason or ""
        self.sprint_id = sprint_id
        self.recent = True

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'awarded_by': self.awarded_by,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None,
            'reason': self.reason,
            'sprint_id': self.sprint_id,
            'recent': self.recent
        }

    @classmethod
    def from_dict(cls, data):
        if not data.get('user_id') or not data.get('badge_id'):
            raise ValueError("BadgeAward must have user_id and badge_id.")
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            badge_id=data.get('badge_id'),
            awarded_by=data.get('awarded_by', 'System'),
            awarded_at=data.get('awarded_at', date.today()),
            reason=data.get('reason', ''),
            sprint_id=data.get('sprint_id')
        )

    def __repr__(self):
        return f"<BadgeAward(user_id='{self.user_id}', badge_id='{self.badge_id}')>"
