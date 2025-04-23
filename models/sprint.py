class Sprint:
    """
    Sprint class representing a sprint in the gamification system.
    
    Attributes:
        id (str): Unique identifier for the sprint
        name (str): Name of the sprint
        description (str): Description of the sprint
        start_date (str): Start date of the sprint (YYYY-MM-DD)
        end_date (str): End date of the sprint (YYYY-MM-DD)
        team_id (str): ID of the team the sprint belongs to
        goals (list): List of goals for the sprint
        status (str): Status of the sprint (upcoming, active, completed)
    """
    
    def __init__(self, sprint_id, name, start_date, end_date, team_id=None,
                 description=None, goals=None, status="upcoming"):
        """
        Initialize a new Sprint object.
        
        Args:
            sprint_id (str): Unique identifier for the sprint
            name (str): Name of the sprint
            start_date (str): Start date of the sprint (YYYY-MM-DD)
            end_date (str): End date of the sprint (YYYY-MM-DD)
            team_id (str, optional): ID of the team the sprint belongs to
            description (str, optional): Description of the sprint
            goals (list, optional): List of goals for the sprint
            status (str, optional): Status of the sprint
        """
        self.id = sprint_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.team_id = team_id
        self.description = description or ""
        self.goals = goals or []
        self.status = status
    
    def to_dict(self):
        """
        Convert the Sprint object to a dictionary.
        
        Returns:
            dict: Dictionary representation of the sprint
        """
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'team_id': self.team_id,
            'description': self.description,
            'goals': self.goals,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Sprint object from a dictionary.
        
        Args:
            data (dict): Dictionary containing sprint data
            
        Returns:
            Sprint: New Sprint object
        """
        return cls(
            sprint_id=data.get('id'),
            name=data.get('name'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            team_id=data.get('team_id'),
            description=data.get('description'),
            goals=data.get('goals', []),
            status=data.get('status', 'upcoming')
        )
    
    def is_active(self):
        """
        Check if the sprint is currently active.
        
        Returns:
            bool: Whether the sprint is active
        """
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        return (self.start_date <= today <= self.end_date and 
                self.status == 'active')
    
    def get_days_remaining(self):
        """
        Calculate the number of days remaining in the sprint.
        
        Returns:
            int: Number of days remaining, or -1 if sprint is completed
        """
        from datetime import datetime
        
        if self.status == 'completed':
            return -1
        
        try:
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            current_date = datetime.now()
            days_remaining = (end_date - current_date).days + 1
            return max(0, days_remaining)
        except:
            return 0
