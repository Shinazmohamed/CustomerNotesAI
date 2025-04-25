from datetime import datetime
from models.user import User
from models.sprint import Sprint
from models.badge_award import BadgeAward
from database import Session, get_database_connection

class GamificationQueries:
    @staticmethod
    def get_team_members(team_id):
        with Session() as session:
            return [
                user.to_dict()
                for user in session.query(User)
                .filter(User.team_id == team_id)
                .all()
            ]
    
    @staticmethod
    def get_active_sprints(team_id=None):
        today = datetime.today().date()
        with Session() as session:
            query = session.query(Sprint).filter(
                Sprint.start_date <= today,
                Sprint.end_date >= today
            )
            if team_id:
                query = query.filter(Sprint.team_id == team_id)
            return [sprint.to_dict() for sprint in query.all()]

    @staticmethod
    def get_user_badges(user_id):
        with Session() as session:
            return [
                award.to_dict()
                for award in session.query(BadgeAward)
                .filter(BadgeAward.user_id == user_id)
                .all()
            ]
        
    @staticmethod
    def execute_query(query, params):
        connection = None
        cursor = None
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    