"""
Sample data for initializing the IT Team Gamification Platform
"""

# Sample badges
sample_badges = {
    "badge_001": {
        "id": "badge_001",
        "name": "Code Quality Champion",
        "description": "Consistently delivers high-quality code with minimal defects",
        "category": "Technical",
        "how_to_achieve": "Maintain a code quality score above 95% for at least 3 consecutive sprints",
        "eligible_roles": ["Dev", "QA"],
        "expected_time_days": 60,
        "validity": "Permanent",
        "badge_type": "work"
    },
    "badge_002": {
        "id": "badge_002",
        "name": "Bug Hunter",
        "description": "Exceptional at finding and documenting critical bugs",
        "category": "Technical",
        "how_to_achieve": "Find and document 10 critical bugs that could have caused major issues",
        "eligible_roles": ["QA", "Dev"],
        "expected_time_days": 90,
        "validity": "Permanent",
        "badge_type": "work"
    },
    "badge_003": {
        "id": "badge_003",
        "name": "Mentorship Excellence",
        "description": "Demonstrated exceptional mentoring skills for new team members",
        "category": "Leadership",
        "how_to_achieve": "Successfully mentor at least 2 new team members and receive positive feedback",
        "eligible_roles": ["Dev", "QA", "RMO", "TL"],
        "expected_time_days": 120,
        "validity": "Permanent",
        "badge_type": "objective"
    },
    "badge_004": {
        "id": "badge_004",
        "name": "Innovation Star",
        "description": "Created an innovative solution that significantly improved team productivity",
        "category": "Innovation",
        "how_to_achieve": "Implement a new tool, process, or approach that measurably improves team efficiency",
        "eligible_roles": ["Dev", "QA", "RMO", "TL"],
        "expected_time_days": 90,
        "validity": "Permanent",
        "badge_type": "objective"
    },
    "badge_005": {
        "id": "badge_005",
        "name": "Sprint MVP",
        "description": "Most valuable player for a sprint",
        "category": "Teamwork",
        "how_to_achieve": "Make exceptional contributions during a sprint and be nominated by the team",
        "eligible_roles": ["Dev", "QA", "RMO"],
        "expected_time_days": 30,
        "validity": "Permanent",
        "badge_type": "work"
    },
    "badge_006": {
        "id": "badge_006",
        "name": "Technical Presenter",
        "description": "Effectively presented a technical topic to the team",
        "category": "Technical",
        "how_to_achieve": "Prepare and deliver a well-received technical presentation",
        "eligible_roles": ["Dev", "QA", "RMO", "TL"],
        "expected_time_days": 45,
        "validity": "Permanent",
        "badge_type": "objective"
    },
    "badge_007": {
        "id": "badge_007",
        "name": "Process Improver",
        "description": "Implemented a significant process improvement",
        "category": "Process",
        "how_to_achieve": "Identify a process bottleneck and implement an improvement that saves time",
        "eligible_roles": ["Dev", "QA", "RMO", "TL", "Manager"],
        "expected_time_days": 60,
        "validity": "Permanent",
        "badge_type": "objective"
    },
    "badge_008": {
        "id": "badge_008",
        "name": "Knowledge Sharer",
        "description": "Actively contributes to knowledge sharing in the team",
        "category": "Teamwork",
        "how_to_achieve": "Document at least 5 valuable knowledge articles in the team wiki",
        "eligible_roles": ["Dev", "QA", "RMO", "TL"],
        "expected_time_days": 30,
        "validity": "Permanent",
        "badge_type": "work"
    },
    "badge_009": {
        "id": "badge_009",
        "name": "Sprint Leader",
        "description": "Successfully led a sprint to completion",
        "category": "Leadership",
        "how_to_achieve": "Lead a sprint that meets all commitments and receives positive team feedback",
        "eligible_roles": ["TL", "Manager"],
        "expected_time_days": 15,
        "validity": "Permanent",
        "badge_type": "work"
    },
    "badge_010": {
        "id": "badge_010",
        "name": "Team Builder",
        "description": "Contributed significantly to team cohesion and morale",
        "category": "Leadership",
        "how_to_achieve": "Organize team building activities and receive positive feedback",
        "eligible_roles": ["Dev", "QA", "RMO", "TL", "Manager"],
        "expected_time_days": 90,
        "validity": "Permanent",
        "badge_type": "objective"
    },
    "badge_011": {
        "id": "badge_011",
        "name": "Security Champion",
        "description": "Demonstrated exceptional awareness of security best practices",
        "category": "Technical",
        "how_to_achieve": "Identify and fix at least 3 significant security vulnerabilities",
        "eligible_roles": ["Dev", "QA"],
        "expected_time_days": 60,
        "validity": "Permanent",
        "badge_type": "work"
    },
    "badge_012": {
        "id": "badge_012",
        "name": "Customer Advocate",
        "description": "Consistently considers and advocates for the customer perspective",
        "category": "Teamwork",
        "how_to_achieve": "Bring customer-focused insights that improve product decisions",
        "eligible_roles": ["Dev", "QA", "RMO", "TL"],
        "expected_time_days": 60,
        "validity": "Permanent",
        "badge_type": "work"
    }
}

# Sample teams
sample_teams = [
    {
        "id": "team_001",
        "name": "Blue Team",
        "description": "Core platform development team",
        "department": "Engineering"
    },
    {
        "id": "team_002",
        "name": "Jinan Team",
        "description": "Customer-facing applications team",
        "department": "Product"
    },
    {
        "id": "team_003",
        "name": "Red Team",
        "description": "Security and infrastructure team",
        "department": "Operations"
    }
]

# Sample users
sample_users = [
    {
        "id": "user_001",
        "name": "John Smith",
        "username": "johnsmith",
        "password": "password123",  # In a real app, this would be hashed
        "email": "john.smith@example.com",
        "role": "Manager",
        "team_id": "team_001",
        "is_lead": True,
        "next_badge_progress": 75,
        "team_rank": "1st"
    },
    {
        "id": "user_002",
        "name": "Sarah Johnson",
        "username": "sarahj",
        "password": "password123",
        "email": "sarah.johnson@example.com",
        "role": "TL",
        "team_id": "team_002",
        "is_lead": True,
        "next_badge_progress": 60,
        "team_rank": "1st"
    },
    {
        "id": "user_003",
        "name": "Michael Lee",
        "username": "mikel",
        "password": "password123",
        "email": "michael.lee@example.com",
        "role": "Dev",
        "team_id": "team_001",
        "is_lead": False,
        "next_badge_progress": 40,
        "team_rank": "2nd"
    },
    {
        "id": "user_004",
        "name": "Emily Chen",
        "username": "emilyc",
        "password": "password123",
        "email": "emily.chen@example.com",
        "role": "QA",
        "team_id": "team_001",
        "is_lead": False,
        "next_badge_progress": 30,
        "team_rank": "3rd"
    },
    {
        "id": "user_005",
        "name": "David Wilson",
        "username": "davidw",
        "password": "password123",
        "email": "david.wilson@example.com",
        "role": "Dev",
        "team_id": "team_001",
        "is_lead": False,
        "next_badge_progress": 85,
        "team_rank": "4th"
    },
    {
        "id": "user_006",
        "name": "Jessica Brown",
        "username": "jessb",
        "password": "password123",
        "email": "jessica.brown@example.com",
        "role": "RMO",
        "team_id": "team_002",
        "is_lead": False,
        "next_badge_progress": 55,
        "team_rank": "2nd"
    },
    {
        "id": "user_007",
        "name": "Ryan Garcia",
        "username": "ryang",
        "password": "password123",
        "email": "ryan.garcia@example.com",
        "role": "Dev",
        "team_id": "team_002",
        "is_lead": False,
        "next_badge_progress": 20,
        "team_rank": "3rd"
    },
    {
        "id": "user_008",
        "name": "Lisa Wang",
        "username": "lisaw",
        "password": "password123",
        "email": "lisa.wang@example.com",
        "role": "TL",
        "team_id": "team_003",
        "is_lead": True,
        "next_badge_progress": 70,
        "team_rank": "1st"
    },
    {
        "id": "user_009",
        "name": "Robert Kim",
        "username": "robertk",
        "password": "password123",
        "email": "robert.kim@example.com",
        "role": "Dev",
        "team_id": "team_003",
        "is_lead": False,
        "next_badge_progress": 45,
        "team_rank": "2nd"
    },
    {
        "id": "user_010",
        "name": "Amanda Singh",
        "username": "amandas",
        "password": "password123",
        "email": "amanda.singh@example.com",
        "role": "QA",
        "team_id": "team_003",
        "is_lead": False,
        "next_badge_progress": 50,
        "team_rank": "3rd"
    }
]

# Sample awards
sample_awards = [
    {
        "id": "award_001",
        "user_id": "user_003",
        "badge_id": "badge_001",
        "awarded_by": "user_001",
        "award_date": "2023-06-15",
        "reason": "Maintained code quality score of 98% for the last 4 sprints",
        "badge_type": "work",
        "sprint_id": "sprint_002",
        "recent": False
    },
    {
        "id": "award_002",
        "user_id": "user_004",
        "badge_id": "badge_002",
        "awarded_by": "user_001",
        "award_date": "2023-07-20",
        "reason": "Discovered a critical security vulnerability in the authentication module",
        "badge_type": "work",
        "sprint_id": "sprint_003",
        "recent": False
    },
    {
        "id": "award_003",
        "user_id": "user_002",
        "badge_id": "badge_009",
        "awarded_by": "user_001",
        "award_date": "2023-08-05",
        "reason": "Successfully led the Q2 planning sprint with excellent team feedback",
        "badge_type": "work",
        "sprint_id": "sprint_004",
        "recent": False
    },
    {
        "id": "award_004",
        "user_id": "user_005",
        "badge_id": "badge_004",
        "awarded_by": "user_001",
        "award_date": "2023-08-15",
        "reason": "Created an automated deployment pipeline that reduced deployment time by 60%",
        "badge_type": "objective",
        "sprint_id": "sprint_004",
        "recent": False
    },
    {
        "id": "award_005",
        "user_id": "user_006",
        "badge_id": "badge_008",
        "awarded_by": "user_002",
        "award_date": "2023-09-01",
        "reason": "Created comprehensive documentation for the new customer portal",
        "badge_type": "work",
        "sprint_id": "sprint_005",
        "recent": False
    },
    {
        "id": "award_006",
        "user_id": "user_007",
        "badge_id": "badge_005",
        "awarded_by": "user_002",
        "award_date": "2023-09-15",
        "reason": "Stepped up to solve critical issues during the release sprint",
        "badge_type": "work",
        "sprint_id": "sprint_005",
        "recent": False
    },
    {
        "id": "award_007",
        "user_id": "user_008",
        "badge_id": "badge_010",
        "awarded_by": "user_001",
        "award_date": "2023-10-01",
        "reason": "Organized team building activities that significantly improved team morale",
        "badge_type": "objective",
        "sprint_id": None,
        "recent": False
    },
    {
        "id": "award_008",
        "user_id": "user_009",
        "badge_id": "badge_006",
        "awarded_by": "user_008",
        "award_date": "2023-10-15",
        "reason": "Delivered an excellent presentation on the new security framework",
        "badge_type": "objective",
        "sprint_id": "sprint_006",
        "recent": False
    },
    {
        "id": "award_009",
        "user_id": "user_010",
        "badge_id": "badge_012",
        "awarded_by": "user_008",
        "award_date": "2023-11-01",
        "reason": "Consistently advocated for customer needs in feature planning",
        "badge_type": "work",
        "sprint_id": "sprint_007",
        "recent": True
    },
    {
        "id": "award_010",
        "user_id": "user_003",
        "badge_id": "badge_005",
        "awarded_by": "user_001",
        "award_date": "2023-11-15",
        "reason": "Exceptional contributions during the feature development sprint",
        "badge_type": "work",
        "sprint_id": "sprint_007",
        "recent": True
    },
    {
        "id": "award_011",
        "user_id": "user_004",
        "badge_id": "badge_008",
        "awarded_by": "user_001",
        "award_date": "2023-12-01",
        "reason": "Created detailed knowledge base articles for testing procedures",
        "badge_type": "work",
        "sprint_id": "sprint_008",
        "recent": True
    },
    {
        "id": "award_012",
        "user_id": "user_005",
        "badge_id": "badge_003",
        "awarded_by": "user_001",
        "award_date": "2023-12-15",
        "reason": "Successfully mentored two new team members who are now productive contributors",
        "badge_type": "objective",
        "sprint_id": None,
        "recent": True
    },
    {
        "id": "award_013",
        "user_id": "user_002",
        "badge_id": "badge_007",
        "awarded_by": "user_001",
        "award_date": "2024-01-05",
        "reason": "Implemented a new code review process that improved quality and reduced rework",
        "badge_type": "objective",
        "sprint_id": "sprint_009",
        "recent": True
    },
    {
        "id": "award_014",
        "user_id": "user_001",
        "badge_id": "badge_010",
        "awarded_by": "user_001",
        "award_date": "2024-01-15",
        "reason": "Led successful team integration activities after reorganization",
        "badge_type": "objective",
        "sprint_id": None,
        "recent": True
    }
]

# Sample sprints
sample_sprints = [
    {
        "id": "sprint_001",
        "name": "Sprint 23.1",
        "description": "Initial platform architecture sprint",
        "start_date": "2023-05-01",
        "end_date": "2023-05-14",
        "team_id": "team_001",
        "goals": [
            "Finalize architecture design",
            "Set up development environments",
            "Complete initial infrastructure setup"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_002",
        "name": "Sprint 23.2",
        "description": "Core platform development",
        "start_date": "2023-05-15",
        "end_date": "2023-05-28",
        "team_id": "team_001",
        "goals": [
            "Implement authentication system",
            "Create database schema",
            "Build API foundation"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_003",
        "name": "Sprint 23.3",
        "description": "Feature development",
        "start_date": "2023-05-29",
        "end_date": "2023-06-11",
        "team_id": "team_001",
        "goals": [
            "Implement user management",
            "Build notification system",
            "Create initial dashboard"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_004",
        "name": "Q2 Planning",
        "description": "Q2 Planning and Sprint 1",
        "start_date": "2023-07-03",
        "end_date": "2023-07-16",
        "team_id": "team_002",
        "goals": [
            "Plan Q2 objectives",
            "Define sprint cadence",
            "Allocate resources"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_005",
        "name": "Release Sprint",
        "description": "Final preparations for initial release",
        "start_date": "2023-08-14",
        "end_date": "2023-08-27",
        "team_id": "team_002",
        "goals": [
            "Complete all critical features",
            "Stabilize for release",
            "Prepare launch materials"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_006",
        "name": "Security Sprint",
        "description": "Focus on security enhancements",
        "start_date": "2023-09-25",
        "end_date": "2023-10-08",
        "team_id": "team_003",
        "goals": [
            "Complete security audit",
            "Address critical vulnerabilities",
            "Implement enhanced authentication"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_007",
        "name": "Feature Sprint",
        "description": "New feature development",
        "start_date": "2023-10-23",
        "end_date": "2023-11-05",
        "team_id": "team_001",
        "goals": [
            "Implement analytics dashboard",
            "Build reporting system",
            "Enhance user profiles"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_008",
        "name": "Integration Sprint",
        "description": "Integration with external systems",
        "start_date": "2023-11-20",
        "end_date": "2023-12-03",
        "team_id": "team_002",
        "goals": [
            "Implement API integrations",
            "Build data connectors",
            "Create documentation"
        ],
        "status": "completed"
    },
    {
        "id": "sprint_009",
        "name": "Current Sprint",
        "description": "Ongoing development sprint",
        "start_date": "2024-01-08",
        "end_date": "2024-01-21",
        "team_id": "team_001",
        "goals": [
            "Implement user feedback features",
            "Enhance performance",
            "Fix priority bugs"
        ],
        "status": "active"
    },
    {
        "id": "sprint_010",
        "name": "Next Sprint",
        "description": "Upcoming development sprint",
        "start_date": "2024-01-22",
        "end_date": "2024-02-04",
        "team_id": "team_001",
        "goals": [
            "Launch new dashboard features",
            "Implement advanced reporting",
            "Prepare for scale testing"
        ],
        "status": "upcoming"
    }
]
