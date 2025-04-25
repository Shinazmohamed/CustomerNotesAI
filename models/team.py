from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from db_base import Base

class Team(Base):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    department = Column(String(50))

    members = relationship('User', back_populates='team')
    sprints = relationship('Sprint', back_populates='team')

    def to_dict(self, include_members=False, include_sprints=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department': self.department
        }
        if include_members:
            data['members'] = [member.to_dict() for member in self.members]
        if include_sprints:
            data['sprints'] = [sprint.to_dict() for sprint in self.sprints]
        return data

    def get_stats(self, awards):
        """
        Calculate team stats based on awards and ORM members.

        Args:
            awards (list[dict]): List of award dicts with 'user_id' and 'awarded_at'.

        Returns:
            dict: Computed stats for this team.
        """
        total_badges = 0
        badges_per_member = {}
        recent_badges = 0

        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        for member in self.members:
            member_id = member.id
            member_awards = [a for a in awards if a['user_id'] == member_id]

            badge_count = len(member_awards)
            total_badges += badge_count
            badges_per_member[member_id] = badge_count

            for award in member_awards:
                if award.get('awarded_at', '1900-01-01') >= thirty_days_ago:
                    recent_badges += 1

        avg_badges = total_badges / len(self.members) if self.members else 0
        top_performer_id = max(badges_per_member.items(), key=lambda x: x[1])[0] if badges_per_member else None
        top_performer = next((m for m in self.members if m.id == top_performer_id), None)

        return {
            'total_badges': total_badges,
            'recent_badges': recent_badges,
            'avg_badges': round(avg_badges, 2),
            'top_performer': top_performer.name if top_performer else 'N/A',
            'member_count': len(self.members)
        }

    def __repr__(self):
        return f"<Team(name='{self.name}', department='{self.department}')>"
