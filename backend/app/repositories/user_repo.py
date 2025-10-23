from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.orm import User

class DuplicateUserError(Exception):
    """Raised when email already exists."""

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_clerk_id(self, clerk_user_id: str) -> User | None:
        return self.db.query(User).filter(User.clerk_user_id == clerk_user_id).first()

    def create(self, *, clerk_user_id: str, first_name: str, last_name: str, 
               email: str) -> User:
        user = User(
            clerk_user_id=clerk_user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateUserError("email already exists")
        self.db.refresh(user)
        return user