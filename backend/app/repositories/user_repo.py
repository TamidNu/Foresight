from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.orm import User

class DuplicateUserError(Exception):
    """Raised when email or username already exists."""

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, *, first_name: str, last_name: str, username: str,
               password: str, email: str, phone_number: int) -> User:
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            email=email,
            phone_number=phone_number,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateUserError("email or username (or phone number) already exists")
        self.db.refresh(user)
        return user