class Team:
    """
    Team class representing a team in the gamification system.
    
    Attributes:
        id (str): Unique identifier for the team
        name (str): Name of the team
        description (str): Description of the team
        department (str): Department the team belongs to
    """
    
    def __init__(self, team_id, name, description=None, department=None):
        """
        Initialize a new Team object.
        
        Args:
            team_id (str): Unique identifier for the team
            name (str): Name of the team
            description (str, optional): Description of the team
            department (str, optional): Department the team belongs to
        """
        self.id = team_id
        self.name = name
        self.description = description or ""
        self.department = department or ""
    
    def to_dict(self):
        """
        Convert the Team object to a dictionary.
        
        Returns:
            dict: Dictionary representation of the team
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department': self.department
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Team object from a dictionary.
        
        Args:
            data (dict): Dictionary containing team data
            
        Returns:
            Team: New Team object
        """
        return cls(
            team_id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            department=data.get('department')
        )
    
    def get_members(self, users):
        """
        Get all members of this team.
        
        Args:
            users (list): List of all users in the system
            
        Returns:
            list: List of users in this team
        """
        return [user for user in users if user.get('team_id') == self.id]
    
    def get_stats(self, users, awards):
        """
        Calculate statistics for this team.
        
        Args:
            users (list): List of all users in the system
            awards (list): List of all badge awards
            
        Returns:
            dict: Dictionary of team statistics
        """
        team_members = self.get_members(users)
        
        total_badges = 0
        badges_per_member = {}
        recent_badges = 0
        
        # Calculate 30 days ago for "recent" badges
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        for member in team_members:
            member_id = member['id']
            member_awards = [a for a in awards if a['user_id'] == member_id]
            
            # Count total badges
            member_badge_count = len(member_awards)
            total_badges += member_badge_count
            badges_per_member[member_id] = member_badge_count
            
            # Count recent badges
            for award in member_awards:
                award_date = award.get('award_date', '1900-01-01')
                if award_date >= thirty_days_ago:
                    recent_badges += 1
        
        # Calculate average badges per member
        avg_badges = total_badges / len(team_members) if team_members else 0
        
        # Find top performer
        top_performer_id = max(badges_per_member.items(), key=lambda x: x[1])[0] if badges_per_member else None
        top_performer = next((m for m in team_members if m['id'] == top_performer_id), None)
        
        return {
            'total_badges': total_badges,
            'recent_badges': recent_badges,
            'avg_badges': round(avg_badges, 2),
            'top_performer': top_performer['name'] if top_performer else 'N/A',
            'member_count': len(team_members)
        }
