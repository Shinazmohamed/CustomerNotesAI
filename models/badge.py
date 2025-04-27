import json
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from db_base import Base

class Badge(Base):
    __tablename__ = 'badges'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    how_to_achieve = Column(Text)
    eligible_roles = Column(Text)  # Stored as JSON string
    expected_time_days = Column(Integer)
    validity = Column(Text)
    badge_type = Column(Text)

    awards = relationship('BadgeAward', back_populates='badge')

    def __init__(self, id, name, description, category,
                 how_to_achieve=None, eligible_roles=None, 
                 expected_time_days=30, validity="Permanent", 
                 badge_type="work"):
        if not id or not name:
            raise ValueError("Badge must have an id and a name.")
        
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.how_to_achieve = how_to_achieve or ""
        self.eligible_roles = json.dumps(eligible_roles or [])
        self.expected_time_days = expected_time_days
        self.validity = validity
        self.badge_type = badge_type

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'how_to_achieve': self.how_to_achieve,
            'eligible_roles': json.loads(self.eligible_roles) if self.eligible_roles else [],
            'expected_time_days': self.expected_time_days,
            'validity': self.validity,
            'badge_type': self.badge_type
        }

    @classmethod
    def from_dict(cls, data):
        if not data.get('id') or not data.get('name'):
            raise ValueError("Badge must have an id and a name.")
        
        return cls(
            badge_id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'Uncategorized'),
            how_to_achieve=data.get('how_to_achieve', ''),
            eligible_roles=data.get('eligible_roles', []),
            expected_time_days=data.get('expected_time_days', 30),
            validity=data.get('validity', 'Permanent'),
            badge_type=data.get('badge_type', 'work')
        )

    def __repr__(self):
        return f"<Badge(name='{self.name}', category='{self.category}')>"
