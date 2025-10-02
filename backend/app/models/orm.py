from sqlalchemy import Column, Integer, Text, BigInteger, Boolean, text
from app.repositories.database import Base

class User(Base):
    __tablename__ = 'Users'

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    username = Column(Text, nullable=False, unique=True, index=True)
    password = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    phone_number = Column(BigInteger, nullable=False, unique=True, index=True)
    currently_staying = Column(Boolean, nullable=False, server_default=text("false"))

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} username={self.username}>"