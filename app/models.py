from sqlalchemy import Column, Integer, String
from app.database import Base


class Client(Base):

    __tablename__ = "client"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    client_id = Column(String, unique=True, index=True)
    client_secret = Column(String)




