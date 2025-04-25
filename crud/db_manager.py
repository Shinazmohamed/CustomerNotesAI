# crud/db_manager.py

from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User
from queries.gamification_queries import GamificationQueries

Session = sessionmaker(bind=engine)

class DatabaseManager:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        except Exception as e:
            print(f"Commit failed: {str(e)}")
            self.session.rollback()
        finally:
            self.session.close()

    @staticmethod
    def get_all(model):
        with DatabaseManager() as session:
            return [item.to_dict() for item in session.query(model).all()]
    
    @staticmethod
    def get_by_id(model, item_id):
        with DatabaseManager() as session:
            item = session.get(model, item_id)
            return item.to_dict() if item else None
    
    @staticmethod
    def create(model, data):
        with DatabaseManager() as session:
            item = model(**data)
            session.add(item)
            session.flush()
            return item.to_dict()
    
    @staticmethod
    def update(model, item_id, update_data):
        with DatabaseManager() as session:
            item = session.get(model, item_id)
            if not item:
                return None
            for key, value in update_data.items():
                setattr(item, key, value)
            return item.to_dict()
    
    @staticmethod
    def delete(model, item_id):
        with DatabaseManager() as session:
            item = session.get(model, item_id)
            if item:
                session.delete(item)
                return True
            return False

    @staticmethod
    def get_user_by_username(username):
        try:
            session = Session()
            user = session.query(User).filter(User.username == username).first()
            return user.to_dict() if user else None
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None
        finally:
            session.close()

    @staticmethod
    def filter_by(model_class, **filters):
        try:
            all_items = DatabaseManager.get_all(model_class)

            if isinstance(all_items, dict):
                all_items = list(all_items.values())
            elif not isinstance(all_items, list):
                raise ValueError("Unsupported data format. Expected list or dict.")

            filtered_items = []

            for item in all_items:
                if not isinstance(item, dict):
                    continue

                match = True
                for key, value in filters.items():
                    item_value = item.get(key)

                    if isinstance(value, list):
                        if item_value not in value:
                            match = False
                            break
                    else:
                        if item_value != value:
                            match = False
                            break

                if match:
                    filtered_items.append(item)

            return filtered_items

        except Exception as e:
            print(f"[filter_by] Error: {e}")
            return []
        
    @staticmethod
    def get_team_members_filtered(team_id):
        query = "SELECT * FROM users WHERE team_id = ? AND role NOT IN ('tl', 'rmo', 'manager')"
        team_members = GamificationQueries.execute_query(query, (team_id,))
        return team_members