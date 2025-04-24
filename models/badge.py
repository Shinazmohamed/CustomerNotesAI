class Badge:
    """
    Badge class representing achievement badges in the gamification system.
    
    Attributes:
        id (str): Unique identifier for the badge
        name (str): Name of the badge
        description (str): Description of what the badge represents
        category (str): Category of the badge (e.g., Technical, Leadership)
        how_to_achieve (str): Instructions on how to earn this badge
        eligible_roles (list): List of roles that can earn this badge
        expected_time_days (int): Expected time to earn in days
        validity (str): How long the badge remains valid
        badge_type (str): Type of badge (work or objective)
    """
    
    def __init__(self, badge_id, name, description, category,
                 how_to_achieve=None, eligible_roles=None, 
                 expected_time_days=30, validity="Permanent",
                 badge_type="work"):
        """
        Initialize a new Badge object.
        
        Args:
            badge_id (str): Unique identifier for the badge
            name (str): Name of the badge
            description (str): Description of what the badge represents
            category (str): Category of the badge
            how_to_achieve (str, optional): Instructions on how to earn this badge
            eligible_roles (list, optional): List of roles that can earn this badge
            expected_time_days (int, optional): Expected time to earn in days
            validity (str, optional): How long the badge remains valid
            badge_type (str, optional): Type of badge (work or objective)
        """
        self.id = badge_id
        self.name = name
        self.description = description
        self.category = category
        self.how_to_achieve = how_to_achieve or ""
        self.eligible_roles = eligible_roles or []
        self.expected_time_days = expected_time_days
        self.validity = validity
        self.badge_type = badge_type
    
    def to_dict(self):
        """
        Convert the Badge object to a dictionary.
        
        Returns:
            dict: Dictionary representation of the badge
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'how_to_achieve': self.how_to_achieve,
            'eligible_roles': self.eligible_roles,
            'expected_time_days': self.expected_time_days,
            'validity': self.validity,
            'badge_type': self.badge_type
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Badge object from a dictionary.
        
        Args:
            data (dict): Dictionary containing badge data
            
        Returns:
            Badge: New Badge object
        """
        return cls(
            badge_id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            how_to_achieve=data.get('how_to_achieve'),
            eligible_roles=data.get('eligible_roles'),
            expected_time_days=data.get('expected_time_days', 30),
            validity=data.get('validity', 'Permanent'),
            badge_type=data.get('badge_type', 'work')
        )


class BadgeAward:
    """
    BadgeAward class representing a badge awarded to a user.
    
    Attributes:
        id (str): Unique identifier for the award
        user_id (str): ID of the user receiving the badge
        badge_id (str): ID of the badge being awarded
        awarded_by (str): ID of the user who awarded the badge
        awarded_at (str): Date the badge was awarded
        reason (str): Reason for awarding the badge
        badge_type (str): Type of work the badge is for (work or objective)
        sprint_id (str, optional): ID of the sprint this award is associated with
    """
    
    def __init__(self, award_id, user_id, badge_id, awarded_by,
                 awarded_at, reason=None, badge_type="work", sprint_id=None):
        """
        Initialize a new BadgeAward object.
        
        Args:
            award_id (str): Unique identifier for the award
            user_id (str): ID of the user receiving the badge
            badge_id (str): ID of the badge being awarded
            awarded_by (str): ID of the user who awarded the badge
            awarded_at (str): Date the badge was awarded (YYYY-MM-DD)
            reason (str, optional): Reason for awarding the badge
            badge_type (str, optional): Type of work the badge is for
            sprint_id (str, optional): ID of the sprint this award is associated with
        """
        self.id = award_id
        self.user_id = user_id
        self.badge_id = badge_id
        self.awarded_by = awarded_by
        self.awarded_at = awarded_at
        self.reason = reason or ""
        self.badge_type = badge_type
        self.sprint_id = sprint_id
        self.recent = True  # Flag for filtering recent awards
    
    def to_dict(self):
        """
        Convert the BadgeAward object to a dictionary.
        
        Returns:
            dict: Dictionary representation of the badge award
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'awarded_by': self.awarded_by,
            'awarded_at': self.awarded_at,
            'reason': self.reason,
            'badge_type': self.badge_type,
            'sprint_id': self.sprint_id,
            'recent': self.recent
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a BadgeAward object from a dictionary.
        
        Args:
            data (dict): Dictionary containing badge award data
            
        Returns:
            BadgeAward: New BadgeAward object
        """
        award = cls(
            award_id=data.get('id'),
            user_id=data.get('user_id'),
            badge_id=data.get('badge_id'),
            awarded_by=data.get('awarded_by'),
            awarded_at=data.get('awarded_at'),
            reason=data.get('reason'),
            badge_type=data.get('badge_type', 'work'),
            sprint_id=data.get('sprint_id')
        )
        award.recent = data.get('recent', True)
        return award
