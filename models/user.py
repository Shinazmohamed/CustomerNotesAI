class User:
    """
    User class representing an employee in the gamification system.
    
    Attributes:
        id (str): Unique identifier for the user
        name (str): Full name of the user
        username (str): Username for login
        password (str): Password for login (in a real system, this would be hashed)
        email (str): Email address of the user
        role (str): Role of the user (Dev, QA, RMO, TL, Manager)
        team_id (str): ID of the team the user belongs to
        is_lead (bool): Whether the user is a team lead
    """
    
    def __init__(self, user_id, name, username, password, email=None,
                 role="Dev", team_id=None, is_lead=False):
        """
        Initialize a new User object.
        
        Args:
            user_id (str): Unique identifier for the user
            name (str): Full name of the user
            username (str): Username for login
            password (str): Password for login
            email (str, optional): Email address of the user
            role (str, optional): Role of the user
            team_id (str, optional): ID of the team the user belongs to
            is_lead (bool, optional): Whether the user is a team lead
        """
        self.id = user_id
        self.name = name
        self.username = username
        self.password = password  # In a real app, this would be hashed
        self.email = email or ""
        self.role = role
        self.team_id = team_id
        self.is_lead = is_lead
        
        # Additional attributes for UI display
        self.next_badge_progress = 0
        self.team_rank = "N/A"
    
    def to_dict(self):
        """
        Convert the User object to a dictionary.
        
        Returns:
            dict: Dictionary representation of the user
        """
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'role': self.role,
            'team_id': self.team_id,
            'is_lead': self.is_lead,
            'next_badge_progress': self.next_badge_progress,
            'team_rank': self.team_rank
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a User object from a dictionary.
        
        Args:
            data (dict): Dictionary containing user data
            
        Returns:
            User: New User object
        """
        user = cls(
            user_id=data.get('id'),
            name=data.get('name'),
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            role=data.get('role', 'Dev'),
            team_id=data.get('team_id'),
            is_lead=data.get('is_lead', False)
        )
        user.next_badge_progress = data.get('next_badge_progress', 0)
        user.team_rank = data.get('team_rank', 'N/A')
        return user
    
    def has_permission(self, feature):
        """
        Check if the user has permission for a specific feature.
        
        Args:
            feature (str): Name of the feature to check
            
        Returns:
            bool: Whether the user has permission
        """
        # Define access rules for different features
        access_rules = {
            'award_badges': ['TL', 'Manager'],
            'create_badges': ['TL', 'Manager'],
            'edit_teams': ['TL', 'Manager'],
            'create_sprints': ['TL', 'Manager'],
            'view_reports': ['TL', 'Manager', 'Dev', 'QA', 'RMO'],
            'export_data': ['TL', 'Manager']
        }
        
        if feature in access_rules:
            return self.role in access_rules[feature]
        
        # Default to not having access if feature not defined
        return False
