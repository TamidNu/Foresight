from sqlalchemy import Column, Integer, Text, Boolean, text
from app.repositories.database import Base

class User(Base):
    __tablename__ = 'Users'

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    clerk_user_id = Column(Text, unique=True, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    currently_staying = Column(Boolean, nullable=False, server_default=text("false"))

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"